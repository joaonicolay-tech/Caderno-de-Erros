"""S2R4: complete normative QUE-003, with measured destination writes."""

import hashlib
import io
import json
import re
import uuid
import zipfile
from collections.abc import Callable
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest
from django.db import connections
from django.db.migrations.executor import MigrationExecutor
from probe_v10_s6_cei_prewrite import snapshot

from modules.accounts.services import LOCAL_WORKSPACE_ID
from modules.data_management.portability import (
    ExportValidationError,
    ValidatedExport,
    export_bytes,
    import_into_empty,
    validate_export,
)
from modules.operations.integrity import run_integrity_check
from modules.questions.services import create_active
from modules.taxonomy.services import create_discipline, create_subject
from shared.application.bootstrap import bootstrap_local_workspace


@pytest.fixture
def question_package(transactional_db: None) -> bytes:
    del transactional_db
    bootstrap_local_workspace(timezone_id="UTC")
    discipline = create_discipline(workspace_id=LOCAL_WORKSPACE_ID, name="Question invariant")
    subject = create_subject(
        workspace_id=LOCAL_WORKSPACE_ID, discipline_id=discipline.id, name="Current revision"
    )
    create_active(
        workspace_id=LOCAL_WORKSPACE_ID,
        discipline_id=discipline.id,
        subject_id=subject.id,
        stem="A complete revision",
        alternatives=["Wrong", "Right"],
        correct_alternative_position=2,
    )
    return export_bytes(workspace_id=LOCAL_WORKSPACE_ID)


def mutate(rows: dict[str, list[dict[str, object]]], case: str) -> None:
    question = rows["questions"][0]
    revision = rows["question_revisions"][0]
    if case.startswith("archived"):
        question["status"] = "ARCHIVED"
        question["archived_at"] = question["activated_at"]
        for cycle in rows["review_cycles"]:
            cycle["state"] = "SUSPENDED"
            cycle["suspended_at"] = question["archived_at"]
            cycle["suspension_reason"] = "QUESTION_ARCHIVED"
        for review in rows["reviews"]:
            review["state"] = "SUSPENDED"
            review["suspended_at"] = question["archived_at"]
    if case.startswith("draft"):
        question["status"] = "DRAFT"
        question["activated_at"] = None
        # No historical attempts in this synthetic fixture; the activation-only
        # cycle is omitted when modeling a draft, rather than modifying facts.
        rows["reviews"] = []
        rows["review_cycles"] = []
    if case.endswith("zero_current"):
        revision["is_current"] = False
    elif case.endswith("two_current") or case in {"sequence_gap", "duplicate_version"}:
        other = deepcopy(revision)
        other["id"] = uuid.uuid4()
        other["version_number"] = (
            3 if case == "sequence_gap" else 1 if case == "duplicate_version" else 2
        )
        other["is_current"] = case.endswith("two_current")
        other["correct_alternative"] = None
        rows["question_revisions"].append(other)
    elif case == "sequence_start_two":
        revision["version_number"] = 2
    elif case == "active_missing_stem":
        revision["stem"] = None
    elif case == "active_missing_answer":
        revision["correct_alternative"] = None
    elif case == "active_one_alternative":
        rows["alternatives"] = [
            a for a in rows["alternatives"] if a["id"] == revision["correct_alternative"]
        ]
    elif case in {"draft_incomplete", "archived_incomplete"}:
        revision["stem"] = revision["correct_alternative"] = None
        rows["alternatives"] = []
    elif case == "draft_no_revision":
        rows["question_revisions"] = []
        rows["alternatives"] = []


def package_for(raw: bytes, case: str) -> tuple[ValidatedExport, bytes]:
    original = validate_export(io.BytesIO(raw))
    rows = deepcopy(original.rows)
    mutate(rows, case)
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        entries = {name: archive.read(name) for name in archive.namelist()}
    encoded = {
        name.removesuffix(".json"): json.loads(content)
        for name, content in entries.items()
        if name.endswith(".json") and name != "manifest.json"
    }
    mutate(encoded, case)
    manifest = json.loads(entries["manifest.json"])
    for entry in manifest["files"]:
        if not entry["name"].endswith(".json"):
            continue
        content = json.dumps(encoded[entry["name"].removesuffix(".json")], default=str).encode()
        entries[entry["name"]] = content
        entry["size_bytes"] = len(content)
        entry["count"] = len(encoded[entry["name"].removesuffix(".json")])
        entry["sha256"] = hashlib.sha256(content).hexdigest()
    entries["manifest.json"] = json.dumps(manifest).encode()
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, content in entries.items():
            archive.writestr(name, content)
    return ValidatedExport(original.manifest, rows), buffer.getvalue()


@pytest.mark.parametrize("entry_point", ["reader", "direct_mutated_object"])
@pytest.mark.parametrize(
    "case",
    [
        "active_zero_current",
        "archived_zero_current",
        "active_two_current",
        "archived_two_current",
        "sequence_start_two",
        "sequence_gap",
        "duplicate_version",
        "active_missing_stem",
        "active_missing_answer",
        "active_one_alternative",
    ],
)
def test_que003_rejected_before_first_write(
    question_package: bytes,
    tmp_path: Path,
    django_db_blocker: Any,
    record_property: Callable[[str, object], None],
    case: str,
    entry_point: str,
) -> None:
    direct, raw = package_for(question_package, case)
    alias = "que003_" + uuid.uuid4().hex
    path = tmp_path / "target.sqlite3"
    connections.databases[alias] = {**connections["default"].settings_dict, "NAME": str(path)}
    try:
        with django_db_blocker.unblock():
            database = connections[alias]
            executor = MigrationExecutor(database)
            executor.migrate(executor.loader.graph.leaf_nodes())
            database.close()
            before = snapshot(path)
            physical = hashlib.sha256(path.read_bytes()).hexdigest()
            database.ensure_connection()
            native = database.connection
            assert native is not None
            changes = native.total_changes
            attempts = dict.fromkeys(("INSERT", "UPDATE", "DELETE"), 0)
            completed = attempts.copy()

            def observe(execute: Any, sql: str, params: Any, many: bool, context: Any) -> Any:
                match = re.match(r"\s*(INSERT|UPDATE|DELETE)\b", sql, re.I)
                if match:
                    attempts[match[1].upper()] += 1
                result = execute(sql, params, many, context)
                if match:
                    completed[match[1].upper()] += 1
                return result

            with (
                database.execute_wrapper(observe),
                pytest.raises(ExportValidationError, match="QUE-003"),
            ):
                import_into_empty(
                    package=validate_export(io.BytesIO(raw)) if entry_point == "reader" else direct,
                    database_alias=alias,
                )
            delta = native.total_changes - changes
            database.close()
            assert attempts == completed == {"INSERT": 0, "UPDATE": 0, "DELETE": 0}
            assert delta == 0 and snapshot(path) == before
            assert hashlib.sha256(path.read_bytes()).hexdigest() == physical
            record_property(
                "que003_zero_write",
                json.dumps(
                    {
                        "case": case,
                        "entry_point": entry_point,
                        "attempted": attempts,
                        "completed": completed,
                        "total_changes_delta": delta,
                        "counts_semantic_schema_physical_equal": True,
                    }
                ),
            )
    finally:
        connections[alias].close()
        del connections[alias]
        del connections.databases[alias]


@pytest.mark.parametrize(
    "case",
    [
        "active_one_current",
        "archived_one_current",
        "draft_zero_current",
        "draft_no_revision",
        "draft_incomplete",
        "archived_incomplete",
    ],
)
def test_que003_normative_valid_edges_import(
    question_package: bytes,
    tmp_path: Path,
    django_db_blocker: Any,
    record_property: Callable[[str, object], None],
    case: str,
) -> None:
    _, raw = package_for(question_package, case)
    package = validate_export(io.BytesIO(raw))
    alias = "que003_valid_" + uuid.uuid4().hex
    connections.databases[alias] = {
        **connections["default"].settings_dict,
        "NAME": str(tmp_path / "valid.sqlite3"),
    }
    try:
        with django_db_blocker.unblock():
            database = connections[alias]
            executor = MigrationExecutor(database)
            executor.migrate(executor.loader.graph.leaf_nodes())
            counts = import_into_empty(package=package, database_alias=alias)
            checker = run_integrity_check(using=alias)
            assert checker.checks_executed == 25 and checker.total_findings == 0
            assert counts["questions"] == 1
            record_property(
                "que003_valid_edge",
                json.dumps({"case": case, "checks": 25, "findings": 0, "import": "PASS"}),
            )
    finally:
        connections[alias].close()
        del connections[alias]
        del connections.databases[alias]
