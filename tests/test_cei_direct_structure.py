"""S2R5: shared structure/type decisions on the effective private import snapshot."""

import hashlib
import io
import json
import re
import uuid
import zipfile
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from django.db import connections
from django.db.migrations.executor import MigrationExecutor
from probe_v10_s6_cei_prewrite import snapshot
from test_cei_semantic_matrix import rich_package as rich_package
from test_cei_semantic_prewrite import semantic_package as semantic_package

from modules.accounts.services import LOCAL_WORKSPACE_ID
from modules.data_management.portability import (
    SETS,
    ExportValidationError,
    ValidatedExport,
    export_workspace,
    import_into_empty,
    validate_export,
)
from modules.operations.integrity import run_integrity_check

TYPE_CASES = (
    "integer-string",
    "integer-bool",
    "integer-float",
    "boolean-integer",
    "boolean-string",
    "uuid-number",
    "uuid-malformed",
    "enum-unknown",
    "required-null",
    "datetime-naive",
    "datetime-offset",
    "date-invalid",
    "date-datetime",
    "string-number",
    "string-too-long",
    "decimal-number",
    "decimal-nonfinite",
    "json-scalar",
)
STRUCTURE_CASES = ("missing-set", "extra-set", "set-not-list", "row-not-object", "extra-field")


@contextmanager
def empty_destination(tmp_path: Path, django_db_blocker: Any) -> Iterator[tuple[str, Path]]:
    alias = "s2r5_" + uuid.uuid4().hex
    path = tmp_path / "destination.sqlite3"
    connections.databases[alias] = {**connections["default"].settings_dict, "NAME": str(path)}
    try:
        with django_db_blocker.unblock():
            database = connections[alias]
            executor = MigrationExecutor(database)
            executor.migrate(executor.loader.graph.leaf_nodes())
            database.close()
            yield alias, path
    finally:
        connections[alias].close()
        del connections[alias]
        del connections.databases[alias]


def damage(rows: dict[str, Any], case: str) -> None:
    fields: dict[str, tuple[str, str, object]] = {
        "integer-string": ("disciplines", "sort_order", "17"),
        "integer-bool": ("disciplines", "sort_order", True),
        "integer-float": ("disciplines", "sort_order", 17.5),
        "boolean-integer": ("question_revisions", "is_current", 1),
        "boolean-string": ("question_revisions", "is_current", "true"),
        "uuid-number": ("alternatives", "id", 17),
        "uuid-malformed": ("alternatives", "id", "not-a-uuid"),
        "enum-unknown": ("questions", "question_type", "UNSUPPORTED"),
        "required-null": ("workspace", "name", None),
        "date-invalid": ("attempts", "local_date", "2026-02-30"),
        "string-number": ("workspace", "name", 17),
        "string-too-long": ("workspace", "name", "x" * 1000),
        "decimal-number": ("mastery_events", "domain_index", 1.5),
        "decimal-nonfinite": ("mastery_events", "domain_index", "NaN"),
        "json-scalar": ("saved_filters", "payload", "{}"),
    }
    if case in fields:
        name, field, value = fields[case]
        rows[name][0][field] = value
    elif case in {"datetime-naive", "datetime-offset", "date-datetime"}:
        field = "local_date" if case == "date-datetime" else "occurred_at"
        observed = rows["attempts"][0]["occurred_at"]
        instant = datetime.fromisoformat(observed) if isinstance(observed, str) else observed
        if case == "datetime-naive":
            instant = instant.replace(tzinfo=None)
        elif case == "datetime-offset":
            instant = instant.astimezone(timezone(timedelta(hours=3)))
        rows["attempts"][0][field] = instant.isoformat() if isinstance(observed, str) else instant
    elif case.startswith("missing-field:"):
        del rows[case.split(":", 1)[1]][0]["id"]
    elif case == "missing-set":
        del rows["boards"]
    elif case == "extra-set":
        rows["unexpected"] = []
    elif case == "set-not-list":
        rows["boards"] = {"unexpected": "object"}
    elif case == "row-not-object":
        rows["boards"][0] = 17
    elif case == "extra-field":
        rows["boards"][0]["unexpected"] = "untrusted"
    else:
        raise AssertionError(case)


def invalid_inputs(raw: bytes, case: str) -> tuple[ValidatedExport, bytes]:
    original = validate_export(io.BytesIO(raw))
    direct = ValidatedExport(deepcopy(original.manifest), deepcopy(original.rows))
    damage(direct.rows, case)
    if case == "decimal-nonfinite":
        direct.rows["mastery_events"][0]["domain_index"] = Decimal("NaN")
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        entries = {name: archive.read(name) for name in archive.namelist()}
    rows = {spec.name: json.loads(entries[spec.name + ".json"]) for spec in SETS}
    damage(rows, case)
    manifest = json.loads(entries["manifest.json"])
    if case == "missing-set":
        del entries["boards.json"]
        manifest["files"] = [e for e in manifest["files"] if e["name"] != "boards.json"]
    elif case == "extra-set":
        content = b"[]"
        entries["unexpected.json"] = content
        manifest["files"].append(
            {
                "name": "unexpected.json",
                "count": 0,
                "size_bytes": 2,
                "sha256": hashlib.sha256(content).hexdigest(),
            }
        )
    for entry in manifest["files"]:
        name = entry["name"].removesuffix(".json")
        if name not in rows:
            continue
        content = json.dumps(rows[name]).encode()
        entries[entry["name"]] = content
        entry.update(
            size_bytes=len(content),
            count=len(rows[name]) if isinstance(rows[name], list) else 0,
            sha256=hashlib.sha256(content).hexdigest(),
        )
    entries["manifest.json"] = json.dumps(manifest).encode()
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, content in entries.items():
            archive.writestr(name, content)
    return direct, buffer.getvalue()


def assert_zero_write(alias: str, path: Path, operation: Callable[[], object]) -> dict[str, object]:
    database = connections[alias]
    database.close()
    before = snapshot(path)
    physical_before = hashlib.sha256(path.read_bytes()).hexdigest()
    database.ensure_connection()
    native = database.connection
    assert native is not None
    initial_changes = native.total_changes
    attempted = dict.fromkeys(("INSERT", "UPDATE", "DELETE"), 0)
    completed = attempted.copy()

    def observe(execute: Any, sql: str, params: Any, many: bool, context: Any) -> Any:
        match = re.match(r"\s*(INSERT|UPDATE|DELETE)\b", sql, re.I)
        if match:
            attempted[match[1].upper()] += 1
        result = execute(sql, params, many, context)
        if match:
            completed[match[1].upper()] += 1
        return result

    with database.execute_wrapper(observe), pytest.raises(ExportValidationError) as caught:
        operation()
    delta = native.total_changes - initial_changes
    database.close()
    assert attempted == completed == {"INSERT": 0, "UPDATE": 0, "DELETE": 0}
    assert delta == 0 and snapshot(path) == before
    assert hashlib.sha256(path.read_bytes()).hexdigest() == physical_before
    return {
        "status": "REJECTED_BEFORE_WRITE",
        "attempted": attempted,
        "completed": completed,
        "total_changes_delta": delta,
        "counts_semantic_schema_physical_equal": True,
        "error_type": type(caught.value).__name__,
        "error": str(caught.value),
    }


def test_cp01_numeric_string_direct_rejected_before_dml(
    rich_package: bytes,
    tmp_path: Path,
    django_db_blocker: Any,
    record_property: Callable[[str, object], None],
) -> None:
    direct, _ = invalid_inputs(rich_package, "integer-string")
    with empty_destination(tmp_path, django_db_blocker) as (alias, path):
        result = assert_zero_write(
            alias, path, lambda: import_into_empty(package=direct, database_alias=alias)
        )
        assert re.search("tipo|estrutur", str(result["error"]), re.I)
        record_property("cp01", json.dumps(result))


@pytest.mark.parametrize(
    "case", (*TYPE_CASES, *STRUCTURE_CASES, *("missing-field:" + spec.name for spec in SETS))
)
def test_invalid_structure_and_types_same_rejection_before_dml(
    rich_package: bytes,
    tmp_path: Path,
    django_db_blocker: Any,
    record_property: Callable[[str, object], None],
    case: str,
) -> None:
    direct, raw = invalid_inputs(rich_package, case)
    with empty_destination(tmp_path, django_db_blocker) as (alias, path):
        results = {}
        results["ZIP"] = assert_zero_write(
            alias,
            path,
            lambda: import_into_empty(
                package=validate_export(io.BytesIO(raw)), database_alias=alias
            ),
        )
        results["direct"] = assert_zero_write(
            alias, path, lambda: import_into_empty(package=direct, database_alias=alias)
        )
        record_property("entrypoint_parity", json.dumps({"case": case, **results}))


@pytest.mark.parametrize("mutate_caller", [False, True])
def test_valid_private_snapshot_imports_all_sets_even_if_caller_mutates(
    rich_package: bytes,
    tmp_path: Path,
    django_db_blocker: Any,
    mutate_caller: bool,
) -> None:
    package = validate_export(io.BytesIO(rich_package))
    # Valid native Decimal facts must retain precision through the shared decoder.
    package.rows["mastery_events"][0]["domain_index"] = Decimal("90.25")
    package.rows["mastery_events"][0]["confidence"] = Decimal("0.75")
    expected = deepcopy(package.rows)
    assert len(expected) == 21 and all(expected.values())
    with empty_destination(tmp_path, django_db_blocker) as (alias, _):
        observed_mutation = False
        database = connections[alias]

        def observe(execute: Any, sql: str, params: Any, many: bool, context: Any) -> Any:
            nonlocal observed_mutation
            if mutate_caller and not observed_mutation and sql.startswith("SELECT"):
                damage(package.rows, "integer-string")
                package.manifest["workspace_id"] = "not-a-uuid"
                observed_mutation = True
            return execute(sql, params, many, context)

        with database.execute_wrapper(observe):
            counts = import_into_empty(package=package, database_alias=alias)
        assert observed_mutation == mutate_caller
        assert counts == {spec.name: len(expected[spec.name]) for spec in SETS}
        checker = run_integrity_check(using=alias)
        assert checker.checks_executed == 25 and checker.total_findings == 0
        replay = io.BytesIO()
        export_workspace(workspace_id=LOCAL_WORKSPACE_ID, destination=replay, database_alias=alias)
        assert validate_export(io.BytesIO(replay.getvalue())).rows == expected
