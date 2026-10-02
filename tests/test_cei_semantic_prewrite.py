"""S2R3: normative semantic preflight before even an attempted destination DML."""

import hashlib
import io
import json
import re
import uuid
import zipfile
from collections.abc import Callable
from copy import deepcopy
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest
from django.db import connections
from django.db.migrations.executor import MigrationExecutor
from probe_v10_s6_cei_prewrite import snapshot

from modules.accounts.services import LOCAL_USER_ID, LOCAL_WORKSPACE_ID
from modules.attempts.context import ContextStore
from modules.attempts.models import Attempt
from modules.attempts.services import AttemptService
from modules.data_management.portability import (
    ExportValidationError,
    ValidatedExport,
    export_bytes,
    export_workspace,
    import_into_empty,
    validate_export,
)
from modules.operations.integrity import run_integrity_check
from modules.questions.services import create_active, create_draft
from modules.reviews.models import Review, ReviewCycle
from modules.taxonomy.services import create_discipline, create_subject
from shared.application.bootstrap import bootstrap_local_workspace


@pytest.fixture
def semantic_package(transactional_db: None) -> bytes:
    del transactional_db
    local = bootstrap_local_workspace(timezone_id="UTC")
    discipline = create_discipline(workspace_id=LOCAL_WORKSPACE_ID, name="Semantics")
    subject = create_subject(
        workspace_id=LOCAL_WORKSPACE_ID, discipline_id=discipline.id, name="Preflight"
    )
    question = create_active(
        workspace_id=LOCAL_WORKSPACE_ID,
        discipline_id=discipline.id,
        subject_id=subject.id,
        stem="Historical answer",
        alternatives=["Wrong", "Right"],
        correct_alternative_position=2,
    )
    service = AttemptService(
        actor_id=LOCAL_USER_ID,
        workspace_id=LOCAL_WORKSPACE_ID,
        session="s2r3-test",
        store=ContextStore(),
    )
    shown = service.presentation(question.id)
    token = service.evaluate(
        question_id=question.id,
        revision_id=shown["revision_id"],
        lock_version=shown["lock_version"],
        alternative_id=shown["alternatives"][0][0],
    )
    service.confirm(
        token=token,
        key=uuid.uuid4(),
        category_id=local.workspace.error_categories.get(code="ATTENTION").id,
    )
    # Model the supported legacy INITIAL_ERROR history from S6-F02. Current
    # creation starts a QUESTION_ACTIVATION cycle, whose missing anchor is valid.
    attempt = Attempt.objects.get(question=question)
    cycle = ReviewCycle.objects.get(question=question)
    ReviewCycle.objects.filter(pk=cycle.pk).update(
        origin_kind="INITIAL_ERROR",
        origin_attempt=attempt,
        started_at=attempt.occurred_at,
    )
    Review.objects.filter(review_cycle=cycle).update(
        scheduled_from_attempt=attempt,
        transition_code="INITIAL_ERROR_TO_D1",
        first_due_date=attempt.local_date + timedelta(days=1),
        current_due_date=attempt.local_date + timedelta(days=1),
    )
    create_draft(workspace_id=LOCAL_WORKSPACE_ID, draft_title="Other", stem="Another revision")
    return export_bytes(workspace_id=LOCAL_WORKSPACE_ID)


def _mutate(rows: dict[str, list[dict[str, object]]], case: str) -> None:
    attempt = rows["attempts"][0]
    if case == "combined":
        attempt["is_correct"] = True
    elif case == "ATT-001":
        revision = next(
            r for r in rows["question_revisions"] if r["id"] == attempt["question_revision"]
        )
        attempt["selected_alternative"] = revision["correct_alternative"]
    elif case == "ERR-001":
        category = next(r for r in rows["error_categories"] if r["code"] == "OTHER")
        rows["error_classifications"][0]["category"] = category["id"]
        rows["error_classifications"][0]["other_description"] = None
    elif case == "REV-001":
        other = next(r for r in rows["question_revisions"] if r["question"] != attempt["question"])
        rows["review_cycles"][0]["origin_question_revision"] = other["id"]
    elif case == "REV-002":
        rows["reviews"][0]["scheduled_from_attempt"] = None
    else:
        raise AssertionError(case)


def _mutated_zip(raw: bytes, case: str) -> bytes:
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        entries = {name: archive.read(name) for name in archive.namelist()}
    rows = {
        name.removesuffix(".json"): json.loads(content)
        for name, content in entries.items()
        if name != "manifest.json" and name.endswith(".json")
    }
    _mutate(rows, case)
    manifest = json.loads(entries["manifest.json"])
    for entry in manifest["files"]:
        if entry["name"].endswith(".json"):
            content = json.dumps(rows[entry["name"].removesuffix(".json")]).encode()
            entries[entry["name"]] = content
            entry["size_bytes"] = len(content)
            entry["sha256"] = hashlib.sha256(content).hexdigest()
    entries["manifest.json"] = json.dumps(manifest).encode()
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        for name, content in entries.items():
            archive.writestr(name, content)
    return output.getvalue()


@pytest.mark.parametrize("entry_point", ["reader", "direct_mutated_object"])
@pytest.mark.parametrize("case", ["ATT-001", "ERR-001", "REV-001", "REV-002", "combined"])
def test_semantic_rejection_precedes_first_destination_write(
    semantic_package: bytes,
    tmp_path: Path,
    django_db_blocker: Any,
    record_property: Callable[[str, object], None],
    entry_point: str,
    case: str,
) -> None:
    validated = validate_export(io.BytesIO(semantic_package))
    mutated = ValidatedExport(validated.manifest, deepcopy(validated.rows))
    _mutate(mutated.rows, case)
    incompatible = _mutated_zip(semantic_package, case)
    alias = "s2r3_" + uuid.uuid4().hex
    path = tmp_path / "target.sqlite3"
    connections.databases[alias] = {**connections["default"].settings_dict, "NAME": str(path)}
    try:
        with django_db_blocker.unblock():
            connection = connections[alias]
            executor = MigrationExecutor(connection)
            executor.migrate(executor.loader.graph.leaf_nodes())
            connection.close()
            before = snapshot(path)
            physical = hashlib.sha256(path.read_bytes()).hexdigest()
            connection.ensure_connection()
            native = connection.connection
            assert native is not None
            start_changes = native.total_changes
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

            with (
                connection.execute_wrapper(observe),
                pytest.raises(ExportValidationError) as caught,
            ):
                import_into_empty(
                    package=validate_export(io.BytesIO(incompatible))
                    if entry_point == "reader"
                    else mutated,
                    database_alias=alias,
                )
            delta = native.total_changes - start_changes
            connection.close()
            assert attempted == completed == {"INSERT": 0, "UPDATE": 0, "DELETE": 0}
            assert delta == 0 and snapshot(path) == before
            assert hashlib.sha256(path.read_bytes()).hexdigest() == physical
            codes = re.findall(r"(?:ATT|ERR|REV)-\d{3}", str(caught.value))
            assert codes == (
                ["ATT-001", "ERR-001", "REV-001", "REV-002"] if case == "combined" else [case]
            )
            record_property(
                "zero_write",
                json.dumps(
                    {
                        "case": case,
                        "entry_point": entry_point,
                        "attempted": attempted,
                        "completed": completed,
                        "total_changes_delta": delta,
                        "counts_equal": True,
                        "semantic_schema_physical_equal": True,
                        "codes": codes,
                    }
                ),
            )
    finally:
        connections[alias].close()
        del connections[alias]
        del connections.databases[alias]


def test_valid_initial_error_history_all_sets_round_trip(
    semantic_package: bytes,
    tmp_path: Path,
    django_db_blocker: Any,
) -> None:
    package = validate_export(io.BytesIO(semantic_package))
    alias = "s2r3_valid_" + uuid.uuid4().hex
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
            assert counts["attempts"] == counts["error_classifications"] == counts["reviews"] == 1
            assert run_integrity_check(using=alias).total_findings == 0
            replay = io.BytesIO()
            export_workspace(
                workspace_id=LOCAL_WORKSPACE_ID, destination=replay, database_alias=alias
            )
            assert validate_export(io.BytesIO(replay.getvalue())).rows == package.rows
    finally:
        connections[alias].close()
        del connections[alias]
        del connections.databases[alias]
