"""S2R4: all required deterministic CEI invariants, shared rules and zero DML."""

import hashlib
import io
import json
import os
import re
import uuid
import zipfile
from collections.abc import Callable
from copy import deepcopy
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any, cast

import pytest
from django.db import connections
from django.db.migrations.executor import MigrationExecutor
from probe_v10_s6_cei_prewrite import snapshot
from test_cei_semantic_prewrite import semantic_package as semantic_package

from modules.accounts.services import LOCAL_USER_ID, LOCAL_WORKSPACE_ID
from modules.attempts.models import Attempt
from modules.data_management.portability import (
    ExportValidationError,
    ValidatedExport,
    export_bytes,
    export_workspace,
    import_into_empty,
    validate_export,
)
from modules.domain.models import MasteryStateEvent
from modules.errors.models import ErrorCategory, ErrorClassification, ErrorClassificationRevision
from modules.operations.integrity import run_integrity_check
from modules.operations.models import AuditEvent
from modules.questions.models import Alternative, Board, Exam, Question, QuestionOrigin, Source
from modules.questions.services import create_active
from modules.reviews.models import Review, ReviewScheduleChange
from modules.search.models import SavedFilter
from modules.taxonomy.models import Subsubject
from modules.taxonomy.services import create_discipline

A_CODES = (
    "WS-003",
    "QUE-001",
    "QUE-002",
    "ATT-002",
    "ATT-003",
    "REV-003",
    "REV-004",
    "ERR-002",
    "CAT-001",
    "REV-005",
    "REV-006",
    "AUD-001",
    "SAV-001",
    "DOM-001",
)
NEGATIVE_CASES = (
    *A_CODES,
    "ATT-002-invalid-zone",
    "ATT-003-cycle",
    "CAT-001-merge-cycle",
    "SAV-001-missing-reference",
    "DOM-001-manual-missing",
    "ERR-002-other",
    "REV-003-superseded-pending",
    "REV-006-multiple-active",
    "AUD-001-deleted-unsanitized",
)


@pytest.fixture
def rich_package(semantic_package: bytes) -> bytes:
    # The existing valid legacy INITIAL_ERROR fixture includes immutable Attempt
    # history; add normative rows for every category A, using synthetic data only.
    del semantic_package
    attempt = Attempt.objects.get()
    main = attempt.question
    assert main.subject is not None
    assert main.discipline_id is not None
    assert main.subject_id is not None
    Subsubject.objects.create(
        workspace_id=LOCAL_WORKSPACE_ID, subject=main.subject, name="Detail", name_key="detail"
    )
    other_discipline = create_discipline(workspace_id=LOCAL_WORKSPACE_ID, name="Other taxonomy")
    assert other_discipline.pk != main.discipline_id
    board = Board.objects.create(workspace_id=LOCAL_WORKSPACE_ID, name="Board", name_key="board")
    exam = Exam.objects.create(
        workspace_id=LOCAL_WORKSPACE_ID, board=board, name="Exam", name_key="exam", year=2026
    )
    source = Source.objects.create(
        workspace_id=LOCAL_WORKSPACE_ID, name="Source", name_key="source", source_type="BOOK"
    )
    QuestionOrigin.objects.create(
        workspace_id=LOCAL_WORKSPACE_ID, question=main, source=source, exam=exam
    )
    draft = Question.objects.get(status="DRAFT")
    Alternative.objects.create(
        workspace_id=LOCAL_WORKSPACE_ID,
        question_revision=draft.revisions.get(is_current=True),
        position=1,
        label="A",
        text="Draft option",
        text_key="draft option",
    )
    classification = ErrorClassification.objects.get(attempt=attempt)
    if not classification.revisions.exists():
        ErrorClassificationRevision.objects.create(
            workspace_id=LOCAL_WORKSPACE_ID,
            error_classification=classification,
            revision_number=1,
            category=classification.category,
        )
    ErrorCategory.objects.create(
        workspace_id=LOCAL_WORKSPACE_ID,
        code="PERSONAL_" + uuid.uuid4().hex.upper(),
        category_kind="PERSONAL",
        display_name="Personal",
        name_key="personal",
        state="ACTIVE",
    )
    review = Review.objects.get(question=main)
    previous = review.current_due_date
    changed = previous + timedelta(days=2)
    correlation = uuid.uuid4()
    Review.objects.filter(pk=review.pk).update(current_due_date=changed)
    ReviewScheduleChange.objects.create(
        workspace_id=LOCAL_WORKSPACE_ID,
        review=review,
        previous_due_date=previous,
        new_due_date=changed,
        timezone_name="UTC",
        reason_code="USER_REQUEST",
        correlation_id=correlation,
    )
    AuditEvent.objects.create(
        workspace_id=LOCAL_WORKSPACE_ID,
        event_code="REVIEW_RESCHEDULED",
        entity_type="REVIEW",
        entity_id=review.id,
        correlation_id=correlation,
        reason_code="USER_REQUEST",
        previous_date=previous,
        new_date=changed,
        timezone_name="UTC",
    )
    SavedFilter.objects.create(
        workspace_id=LOCAL_WORKSPACE_ID,
        owner_user_id=LOCAL_USER_ID,
        name="Matrix",
        name_key="matrix",
        context_code="QUESTIONS_LIST",
        schema_version=1,
        payload={
            "discipline": str(main.discipline_id),
            "subject": str(main.subject_id),
            "query": "history",
            "status": "ACTIVE",
            "error_category": "unclassified",
        },
    )
    MasteryStateEvent.objects.create(
        workspace_id=LOCAL_WORKSPACE_ID,
        question=main,
        sequence=1,
        event_type="DOMINATED",
        formula_code="DOM-HEUR-1.0",
        evaluated_on=attempt.local_date,
        occurred_at=attempt.occurred_at,
    )
    create_active(
        workspace_id=LOCAL_WORKSPACE_ID,
        discipline_id=main.discipline_id,
        subject_id=main.subject_id,
        stem="Modern activation",
        alternatives=["Left", "Right"],
        correct_alternative_position=2,
    )
    return export_bytes(workspace_id=LOCAL_WORKSPACE_ID)


def shift(value: Any, days: int) -> Any:
    if isinstance(value, str):
        parsed = datetime.fromisoformat(value) if len(value) > 10 else date.fromisoformat(value)
        return (parsed + timedelta(days=days)).isoformat()
    return value + timedelta(days=days)


def mutate(rows: dict[str, list[dict[str, Any]]], case: str, negative: bool) -> None:
    attempt = rows["attempts"][0]
    main = next(q for q in rows["questions"] if q["id"] == attempt["question"])
    revision = next(
        r for r in rows["question_revisions"] if r["id"] == attempt["question_revision"]
    )
    cycle = next(c for c in rows["review_cycles"] if c["question"] == main["id"])
    review = next(r for r in rows["reviews"] if r["review_cycle"] == cycle["id"])
    if not negative:
        if case == "WS-003":
            rows["workspace"][0]["timezone_name"] = "Etc/UTC"
        elif case == "REV-003":
            main["status"] = "ARCHIVED"
            main["archived_at"] = main["activated_at"]
            cycle.update(
                state="SUSPENDED",
                suspended_at=main["archived_at"],
                suspension_reason="QUESTION_ARCHIVED",
            )
            review.update(state="SUSPENDED", suspended_at=main["archived_at"])
        elif case == "QUE-001":
            taxonomy = next(d for d in rows["disciplines"] if d["id"] == main["discipline"])
            taxonomy["status"] = "ARCHIVED"
            taxonomy["archived_at"] = main["activated_at"]
        elif case == "ATT-002":
            instant = datetime(2026, 9, 20, 2, 30, tzinfo=UTC)
            attempt["occurred_at"] = (
                instant if isinstance(attempt["occurred_at"], datetime) else instant.isoformat()
            )
            attempt["timezone_name"] = "America/Sao_Paulo"
            local = date(2026, 9, 19)
            attempt["local_date"] = (
                local if isinstance(attempt["local_date"], date) else local.isoformat()
            )
            old_first = review["first_due_date"]
            new_first = local + timedelta(days=1)
            review["first_due_date"] = (
                new_first if isinstance(old_first, date) else new_first.isoformat()
            )
            change = rows["review_schedule_changes"][0]
            change["previous_due_date"] = review["first_due_date"]
            rows["audit_events"][0]["previous_date"] = review["first_due_date"]
        return
    if case == "WS-003":
        rows["workspace"][0]["timezone_name"] = "Invalid/Not_IANA"
    elif case == "QUE-001":
        main["discipline"] = next(
            d["id"] for d in rows["disciplines"] if d["id"] != main["discipline"]
        )
    elif case == "QUE-002":
        revision["correct_alternative"] = next(
            a["id"] for a in rows["alternatives"] if a["question_revision"] != revision["id"]
        )
    elif case == "ATT-002":
        attempt["occurred_at"] = shift(attempt["occurred_at"], 1)
    elif case == "ATT-002-invalid-zone":
        attempt["timezone_name"] = "Invalid/Not_IANA"
    elif case == "ATT-003":
        attempt["voided_at"] = attempt["occurred_at"]
    elif case == "ATT-003-cycle":
        attempt["replaces_attempt"] = attempt["id"]
    elif case == "REV-003":
        main["status"] = "ARCHIVED"
        main["archived_at"] = main["activated_at"]
    elif case == "REV-003-superseded-pending":
        cycle["state"] = "SUPERSEDED"
        cycle["superseded_at"] = cycle["started_at"]
    elif case == "REV-004":
        review["first_due_date"] = shift(review["first_due_date"], 1)
    elif case == "REV-004-inaugural":
        modern_cycle = next(
            c for c in rows["review_cycles"] if c["origin_kind"] == "QUESTION_ACTIVATION"
        )
        modern = next(r for r in rows["reviews"] if r["review_cycle"] == modern_cycle["id"])
        modern["first_due_date"] = shift(modern["first_due_date"], 1)
        modern["current_due_date"] = modern["first_due_date"]
    elif case == "ERR-002":
        rows["error_classification_revisions"][0]["revision_number"] = 2
    elif case == "ERR-002-other":
        rows["error_classification_revisions"][0]["category"] = next(
            c["id"] for c in rows["error_categories"] if c["code"] == "OTHER"
        )
    elif case == "CAT-001":
        next(c for c in rows["error_categories"] if c["category_kind"] == "STANDARD")["state"] = (
            "ARCHIVED"
        )
    elif case == "CAT-001-merge-cycle":
        personal = next(c for c in rows["error_categories"] if c["category_kind"] == "PERSONAL")
        personal["state"] = "MERGED"
        personal["merged_into"] = personal["id"]
    elif case == "REV-005":
        rows["review_schedule_changes"][0]["new_due_date"] = rows["review_schedule_changes"][0][
            "previous_due_date"
        ]
    elif case == "REV-006":
        cycle["superseded_at"] = cycle["started_at"]
    elif case == "REV-006-multiple-active":
        clone = deepcopy(cycle)
        new_id = uuid.uuid4()
        clone["id"] = new_id if isinstance(cycle["id"], uuid.UUID) else str(new_id)
        rows["review_cycles"].append(clone)
    elif case == "AUD-001":
        rows["audit_events"][0]["reason_code"] = "bad-reason"
    elif case == "AUD-001-deleted-unsanitized":
        audit = rows["audit_events"][0]
        audit.update(
            event_code="QUESTION_PERMANENTLY_DELETED",
            entity_type="QUESTION",
            entity_id=main["id"],
            previous_date=None,
            new_date=None,
            timezone_name=None,
        )
    elif case == "SAV-001":
        rows["saved_filters"][0]["payload"]["status"] = "UNRECOGNIZED"
    elif case == "SAV-001-missing-reference":
        rows["saved_filters"][0]["payload"]["discipline"] = str(uuid.uuid4())
    elif case == "DOM-001":
        rows["mastery_events"][0]["sequence"] = 2
    elif case == "DOM-001-manual-missing":
        rows["mastery_events"][0]["event_type"] = "MANUAL_REOPENED"
    else:
        raise AssertionError(case)


def variant(raw: bytes, case: str, negative: bool) -> tuple[ValidatedExport, bytes]:
    original = validate_export(io.BytesIO(raw))
    rows = deepcopy(original.rows)
    mutate(rows, case, negative)
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        entries = {name: archive.read(name) for name in archive.namelist()}
    encoded = {
        name.removesuffix(".json"): json.loads(content)
        for name, content in entries.items()
        if name.endswith(".json") and name != "manifest.json"
    }
    mutate(encoded, case, negative)
    manifest = json.loads(entries["manifest.json"])
    manifest["workspace_timezone"] = encoded["workspace"][0]["timezone_name"]
    for entry in manifest["files"]:
        if not entry["name"].endswith(".json"):
            continue
        content = json.dumps(encoded[entry["name"].removesuffix(".json")]).encode()
        entries[entry["name"]] = content
        entry.update(
            size_bytes=len(content),
            count=len(encoded[entry["name"].removesuffix(".json")]),
            sha256=hashlib.sha256(content).hexdigest(),
        )
    entries["manifest.json"] = json.dumps(manifest).encode()
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, content in entries.items():
            archive.writestr(name, content)
    return ValidatedExport(original.manifest, rows), buffer.getvalue()


def artifact(case: str, entry: str, raw: bytes, result: dict[str, object]) -> None:
    selected = os.environ.get("CEI_S2R4_CASE_ARTIFACT_ROOT")
    if selected is None:
        return
    root = Path(selected)
    assert root.is_absolute() and root.name.startswith("s2r4-expanded-matrix-cases-")
    folder = root / (case + "-" + entry)
    folder.mkdir(parents=True, exist_ok=False)
    (folder / "package.zip").write_bytes(raw)
    (folder / "result.json").write_bytes((json.dumps(result, indent=2) + "\n").encode())


@pytest.mark.parametrize("entry_point", ["reader", "direct_mutated_object"])
@pytest.mark.parametrize("case", NEGATIVE_CASES)
def test_all_category_A_negatives_zero_destination_writes(
    rich_package: bytes,
    tmp_path: Path,
    django_db_blocker: Any,
    record_property: Callable[[str, object], None],
    case: str,
    entry_point: str,
) -> None:
    direct, raw = variant(rich_package, case, True)
    expected = case[:7]
    alias = "matrix_" + uuid.uuid4().hex
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
                pytest.raises(ExportValidationError, match=expected) as caught,
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
            result = {
                "case": case,
                "code": expected,
                "entry_point": entry_point,
                "status": "REJECTED_BEFORE_WRITE",
                "attempted": attempts,
                "completed": completed,
                "total_changes_delta": delta,
                "counts_semantic_schema_physical_equal": True,
                "error": str(caught.value),
            }
            record_property("matrix_negative", json.dumps(result))
            artifact(case, entry_point, raw, result)
    finally:
        connections[alias].close()
        del connections[alias]
        del connections.databases[alias]


@pytest.mark.parametrize("case", A_CODES)
def test_category_A_corresponding_positive_imports_all_sets(
    rich_package: bytes,
    tmp_path: Path,
    django_db_blocker: Any,
    record_property: Callable[[str, object], None],
    case: str,
) -> None:
    _, raw = variant(rich_package, case, False)
    package = validate_export(io.BytesIO(raw))
    assert len(package.rows) == 21 and all(package.rows.values())
    alias = "matrix_valid_" + uuid.uuid4().hex
    connections.databases[alias] = {
        **connections["default"].settings_dict,
        "NAME": str(tmp_path / "positive.sqlite3"),
    }
    try:
        with django_db_blocker.unblock():
            database = connections[alias]
            executor = MigrationExecutor(database)
            executor.migrate(executor.loader.graph.leaf_nodes())
            counts = import_into_empty(package=package, database_alias=alias)
            checker = run_integrity_check(using=alias)
            assert checker.checks_executed == 25 and checker.total_findings == 0
            replay = io.BytesIO()
            export_workspace(
                workspace_id=LOCAL_WORKSPACE_ID, destination=replay, database_alias=alias
            )
            assert validate_export(io.BytesIO(replay.getvalue())).rows == package.rows
            result = {
                "case": case,
                "status": "VALID_IMPORT_PASS",
                "sets": 21,
                "counts": counts,
                "all_rows_UUIDs_history_relationships_equal": True,
                "checker_checks": 25,
                "findings": 0,
                "local_owner_context_equal": True,
            }
            record_property("matrix_positive", json.dumps(result))
            artifact(case, "positive", raw, result)
    finally:
        connections[alias].close()
        del connections[alias]
        del connections.databases[alias]


def test_retention_is_not_invented_as_package_semantic_rule(rich_package: bytes) -> None:
    with zipfile.ZipFile(io.BytesIO(rich_package)) as archive:
        entries = {name: archive.read(name) for name in archive.namelist()}
    events = json.loads(entries["audit_events.json"])
    deleted = deepcopy(events[0])
    deleted.update(
        id=str(uuid.uuid4()),
        event_code="QUESTION_PERMANENTLY_DELETED",
        entity_type="QUESTION",
        entity_id=None,
        previous_entity_id=None,
        related_entity_id=None,
        previous_date=None,
        new_date=None,
        timezone_name=None,
        correlation_id=str(uuid.uuid4()),
        created_at="2000-01-01T00:00:00+00:00",
    )
    events.append(deleted)
    content = json.dumps(events).encode()
    entries["audit_events.json"] = content
    manifest = json.loads(entries["manifest.json"])
    entry = next(e for e in manifest["files"] if e["name"] == "audit_events.json")
    entry.update(
        size_bytes=len(content), count=len(events), sha256=hashlib.sha256(content).hexdigest()
    )
    entries["manifest.json"] = json.dumps(manifest).encode()
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, data in entries.items():
            archive.writestr(name, data)
    package = validate_export(io.BytesIO(buffer.getvalue()))
    assert len(package.rows["audit_events"]) == len(events)


@pytest.mark.parametrize("entry_point", ["reader", "direct_mutated_object"])
def test_s8r1_inaugural_date_without_context_reports_limitation_not_exact_pass(
    rich_package: bytes,
    tmp_path: Path,
    django_db_blocker: Any,
    caplog: pytest.LogCaptureFixture,
    entry_point: str,
) -> None:
    # H1 supersedes the old false-negative label: the persisted columns cannot
    # prove this changed date invalid independently of mutable Workspace context.
    direct, raw = variant(rich_package, "REV-004-inaugural", True)
    package = validate_export(io.BytesIO(raw)) if entry_point == "reader" else direct
    validated = validate_export(io.BytesIO(raw))
    assert len(validated.limited_verifications) == 1
    limited = validated.limited_verifications[0]
    assert limited.outcome == "LIMITED_VERIFICATION"
    assert limited.reason_code == "TIMEZONE_CONTEXT_UNAVAILABLE"
    alias = "s8r1_limited_" + uuid.uuid4().hex
    connections.databases[alias] = {
        **connections["default"].settings_dict,
        "NAME": str(tmp_path / "limited.sqlite3"),
    }
    try:
        with django_db_blocker.unblock():
            database = connections[alias]
            executor = MigrationExecutor(database)
            executor.migrate(executor.loader.graph.leaf_nodes())
            import_into_empty(package=package, database_alias=alias)
            checked = run_integrity_check(using=alias)
            assert checked.checks_executed == 25 and checked.total_findings == 0
            assert checked.total_limited_verifications == 1
            reports = [
                record
                for record in caplog.records
                if getattr(record, "operation", None) == "cei.import.integrity"
            ]
            assert (
                reports and cast(Any, reports[-1]).technical_context["limited_verifications"] == 1
            )
            replay = io.BytesIO()
            export_workspace(
                workspace_id=LOCAL_WORKSPACE_ID, destination=replay, database_alias=alias
            )
            assert validate_export(io.BytesIO(replay.getvalue())).rows == validated.rows
    finally:
        connections[alias].close()
        del connections[alias]
        del connections.databases[alias]
