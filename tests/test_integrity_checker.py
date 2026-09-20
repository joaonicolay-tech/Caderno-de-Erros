"""V0.4-S5: checker read-only, sanitizado e operacionalmente confiável."""

import json
import logging
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, date, datetime, timedelta
from io import StringIO
from typing import Any, cast
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection, models

from modules.accounts.models import User, Workspace
from modules.attempts.models import Attempt, AttemptType, OperationKind, OperationReceipt
from modules.errors.models import ErrorCategoryCode, ErrorCategoryState, ErrorClassification
from modules.errors.services import PersonalCategoryService, seed_standard_error_categories
from modules.operations.integrity import (
    INVARIANT_CATALOG,
    IntegrityCheckOperationalError,
    InvariantSeverity,
    run_integrity_check,
)
from modules.operations.management.commands.check_integrity import (
    EXIT_FINDINGS,
    EXIT_OPERATIONAL_FAILURE,
)
from modules.operations.models import AuditEntityType, AuditEvent, AuditEventCode
from modules.operations.structured_logging import StructuredJsonFormatter
from modules.questions.models import Alternative, Question, QuestionRevision
from modules.questions.services import create_active
from modules.reviews.models import Review, ReviewCycle, ReviewState
from modules.taxonomy.models import Discipline, Subject
from modules.taxonomy.services import create_discipline, create_subject
from shared.domain.time import FixedClock, Instant

FIXED_CORRELATION_ID = "12345678-1234-4234-8234-123456789abc"
PRIVATE_SENTINEL = "PRIVATE-STEM-DO-NOT-LOG-92"
REFERENCE_INSTANT = datetime(2026, 9, 10, 15, tzinfo=UTC)


@contextmanager
def _captured_logger() -> Iterator[StringIO]:
    logger = logging.getLogger("cei")
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(StructuredJsonFormatter())
    previous_level = logger.level
    previous_propagate = logger.propagate
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    logger.addHandler(handler)
    try:
        yield stream
    finally:
        logger.removeHandler(handler)
        logger.setLevel(previous_level)
        logger.propagate = previous_propagate


def _events(stream: StringIO) -> list[dict[str, Any]]:
    return [cast(dict[str, Any], json.loads(line)) for line in stream.getvalue().splitlines()]


def _workspace(suffix: str) -> Workspace:
    user = User.objects.create_user(email=f"integrity-{suffix}@example.test")
    workspace = Workspace.objects.create(
        owner_user=user,
        name=f"Workspace {suffix}",
        timezone_name="America/Sao_Paulo",
    )
    seed_standard_error_categories(workspace)
    return workspace


def _question(workspace: Workspace, suffix: str, *, stem: str | None = None) -> Question:
    discipline = create_discipline(workspace_id=workspace.id, name=f"Disciplina {suffix}")
    subject = create_subject(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        name=f"Assunto {suffix}",
    )
    return create_active(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        subject_id=subject.id,
        stem=stem or f"Questão {suffix}",
        alternatives=[f"Errada {suffix}", f"Correta {suffix}"],
        correct_alternative_position=2,
        clock=FixedClock(Instant(REFERENCE_INSTANT)),
    )


def _attempt(
    workspace: Workspace,
    question: Question,
    *,
    correct: bool,
    attempt_type: str = AttemptType.INITIAL,
    review: Review | None = None,
    occurred_at: datetime = REFERENCE_INSTANT,
) -> Attempt:
    revision = question.revisions.get(is_current=True)
    return Attempt.objects.create(
        workspace=workspace,
        question=question,
        question_revision=revision,
        review=review,
        attempt_type=attempt_type,
        selected_alternative=revision.alternatives.get(position=2 if correct else 1),
        is_correct=correct,
        occurred_at=occurred_at,
        timezone_name=workspace.timezone_name,
        local_date=occurred_at.astimezone(ZoneInfo(workspace.timezone_name)).date(),
        idempotency_key=uuid.uuid4(),
    )


def _snapshot() -> dict[str, list[dict[str, object]]]:
    model_types: tuple[type[models.Model], ...] = (
        Workspace,
        Discipline,
        Subject,
        Question,
        QuestionRevision,
        Alternative,
        Attempt,
        ReviewCycle,
        Review,
        ErrorClassification,
        OperationReceipt,
    )
    return {model._meta.label: _model_rows(model) for model in model_types}


def _model_rows(model: type[models.Model]) -> list[dict[str, object]]:
    return cast(list[dict[str, object]], list(model._base_manager.order_by("pk").values()))


def _raw_update(sql: str, *parameters: Any) -> None:
    with connection.cursor() as cursor:
        cursor.execute(sql, list(parameters))


def _uuid(value: uuid.UUID) -> str:
    return value.hex


def _add_completed_d1_and_pending_d7(
    workspace: Workspace, question: Question
) -> tuple[Review, Review]:
    d1 = question.reviews.get(state=ReviewState.PENDING)
    completed_at = REFERENCE_INSTANT + timedelta(days=1)
    attempt = _attempt(
        workspace,
        question,
        correct=True,
        attempt_type=AttemptType.REVIEW,
        review=d1,
        occurred_at=completed_at,
    )
    Review.objects.filter(pk=d1.id).update(
        state=ReviewState.COMPLETED,
        completed_at=completed_at,
    )
    d1.refresh_from_db()
    due = attempt.local_date + timedelta(days=7)
    d7 = Review.objects.create(
        workspace=workspace,
        review_cycle=d1.review_cycle,
        question=question,
        sequence_number=2,
        stage_code="D7",
        first_due_date=due,
        current_due_date=due,
        scheduled_from_attempt=attempt,
        transition_code="ADVANCE_D1_TO_D7",
    )
    return d1, d7


def test_catalog_has_stable_complete_entries() -> None:
    ids = [spec.invariant_id for spec in INVARIANT_CATALOG]
    assert len(ids) == len(set(ids)) == 20
    assert ids == [
        "DB-001",
        "DB-002",
        "WS-001",
        "WS-002",
        "WS-003",
        "QUE-001",
        "QUE-002",
        "QUE-003",
        "ATT-001",
        "ATT-002",
        "REV-001",
        "REV-002",
        "REV-003",
        "REV-004",
        "ERR-001",
        "ERR-002",
        "OPS-001",
        "CAT-001",
        "REV-005",
        "AUD-001",
    ]
    for spec in INVARIANT_CATALOG:
        assert all(
            (
                spec.name,
                spec.description,
                spec.domain,
                spec.expected_condition,
                spec.evidence_type,
                spec.rationale,
                spec.impact,
                spec.detection_strategy,
                spec.false_positive_risk,
                spec.source_reference,
                spec.message,
                spec.operational_action,
            )
        )
        assert spec.severity in {InvariantSeverity.CRITICAL, InvariantSeverity.ERROR}


@pytest.mark.django_db(transaction=True)
def test_healthy_database_is_read_only_and_unclassified_error_is_valid() -> None:
    first = _workspace("healthy-a")
    second = _workspace("healthy-b")
    question = _question(first, "healthy-a", stem=PRIVATE_SENTINEL)
    _question(second, "healthy-b")
    residue = _attempt(first, question, correct=False)
    assert not ErrorClassification.objects.filter(attempt=residue).exists()
    before = _snapshot()

    result = run_integrity_check()

    assert result.total_findings == 0
    assert not result.has_blocking_findings
    assert result.findings == ()
    assert result.checks_executed == len(INVARIANT_CATALOG)
    assert result.queries_executed == len(INVARIANT_CATALOG) + 1
    assert _snapshot() == before


@pytest.mark.django_db(transaction=True)
def test_s2a_checker_detects_cross_workspace_merge_schedule_without_history_and_audit() -> None:
    first = _workspace("s2a-corrupt-a")
    second = _workspace("s2a-corrupt-b")
    source = PersonalCategoryService(workspace_id=first.id).create(display_name="Origem")
    foreign_target = PersonalCategoryService(workspace_id=second.id).create(display_name="Alvo")
    review = _question(first, "s2a schedule").reviews.get()
    _raw_update(
        "UPDATE errors_error_category SET state = %s, merged_into_id = %s WHERE id = %s",
        ErrorCategoryState.MERGED,
        _uuid(foreign_target.id),
        _uuid(source.id),
    )
    _raw_update(
        "UPDATE reviews_review SET current_due_date = %s WHERE id = %s",
        date(2026, 9, 30),
        _uuid(review.id),
    )
    AuditEvent.objects.create(
        workspace=first,
        event_code=AuditEventCode.PERSONAL_CATEGORY_ARCHIVED,
        entity_type=AuditEntityType.ERROR_CATEGORY,
        entity_id=foreign_target.id,
        correlation_id=uuid.uuid4(),
        reason_code="MAINTENANCE",
    )

    result = run_integrity_check()

    ids = {finding.invariant_id for finding in result.findings}
    assert {"CAT-001", "REV-005", "AUD-001"}.issubset(ids)


@pytest.mark.django_db(transaction=True)
def test_workspace_attempt_classification_and_receipt_corruption_is_detected_and_sanitized() -> (
    None
):
    first = _workspace("corrupt-a")
    second = _workspace("corrupt-b")
    question_a = _question(first, "corrupt-a", stem=PRIVATE_SENTINEL)
    question_b = _question(second, "corrupt-b")
    attempt_a = _attempt(first, question_a, correct=False)
    attempt_b = _attempt(second, question_b, correct=False)
    classification = ErrorClassification.objects.create(
        workspace=first,
        attempt=attempt_a,
        category=first.error_categories.get(code=ErrorCategoryCode.ATTENTION),
    )
    receipt = OperationReceipt.objects.create(
        workspace=first,
        operation_kind=OperationKind.INITIAL_ERROR,
        idempotency_key=attempt_a.idempotency_key,
        request_hash="a" * 64,
        result_entity_type="ATTEMPT",
        result_entity_id=attempt_a.id,
    )
    _raw_update(
        "UPDATE attempts_attempt SET workspace_id = %s WHERE id = %s",
        _uuid(second.id),
        _uuid(attempt_a.id),
    )
    _raw_update(
        "UPDATE errors_errorclassification SET workspace_id = %s WHERE id = %s",
        _uuid(second.id),
        _uuid(classification.id),
    )
    _raw_update(
        "UPDATE attempts_operationreceipt SET result_entity_id = %s WHERE id = %s",
        _uuid(attempt_b.id),
        _uuid(receipt.id),
    )
    _raw_update(
        "UPDATE accounts_workspace SET timezone_name = %s WHERE id = %s",
        PRIVATE_SENTINEL,
        _uuid(first.id),
    )
    before = _snapshot()
    output = StringIO()

    with _captured_logger() as logs, pytest.raises(CommandError) as raised:
        call_command(
            "check_integrity",
            stdout=output,
            correlation_id=FIXED_CORRELATION_ID,
        )

    assert raised.value.returncode == EXIT_FINDINGS
    text = output.getvalue()
    assert "Integrity checker: BLOCKED" in text
    assert {"WS-003", "ATT-001", "ERR-001", "OPS-001"}.issubset(
        {finding.invariant_id for finding in run_integrity_check().findings}
    )
    assert PRIVATE_SENTINEL not in text
    assert PRIVATE_SENTINEL not in logs.getvalue()
    events = _events(logs)
    assert [event["event_code"] for event in events] == [
        "INTEGRITY_CHECK_STARTED",
        "INTEGRITY_CHECK_FINDINGS",
    ]
    assert {event["correlation_id"] for event in events} == {FIXED_CORRELATION_ID}
    assert _snapshot() == before


@pytest.mark.django_db(transaction=True)
def test_review_schedule_and_attempt_local_date_findings_are_specific() -> None:
    workspace = _workspace("temporal")
    question = _question(workspace, "temporal")
    _d1, d7 = _add_completed_d1_and_pending_d7(workspace, question)
    attempt = Attempt.objects.get(review__isnull=False)
    _raw_update(
        "UPDATE reviews_review SET first_due_date = %s WHERE id = %s",
        date(2026, 12, 31).isoformat(),
        _uuid(d7.id),
    )
    _raw_update(
        "UPDATE attempts_attempt SET local_date = %s WHERE id = %s",
        date(2026, 1, 1).isoformat(),
        _uuid(attempt.id),
    )
    _raw_update(
        "UPDATE reviews_review SET first_due_date = %s WHERE id = %s",
        date(2026, 12, 30).isoformat(),
        _uuid(_d1.id),
    )

    result = run_integrity_check()
    ids = {finding.invariant_id for finding in result.findings}

    assert {"ATT-002", "REV-004", "REV-005"}.issubset(ids)
    assert all(
        finding.severity == InvariantSeverity.ERROR
        for finding in result.findings
        if finding.invariant_id in {"ATT-002", "REV-004"}
    )
    assert all(
        finding.severity == InvariantSeverity.CRITICAL
        for finding in result.findings
        if finding.invariant_id == "REV-005"
    )


@pytest.mark.django_db(transaction=True)
def test_taxonomy_cycle_timezone_and_category_cross_workspace_are_detected() -> None:
    first = _workspace("relations-a")
    second = _workspace("relations-b")
    question_a = _question(first, "relations-a")
    question_b = _question(second, "relations-b")
    category = first.error_categories.get(code=ErrorCategoryCode.GUESS)
    foreign_category = second.error_categories.get(code=ErrorCategoryCode.GUESS)
    attempt = _attempt(first, question_a, correct=False)
    ErrorClassification.objects.create(
        workspace=first,
        attempt=attempt,
        category=category,
    )
    assert question_b.discipline_id is not None
    assert question_a.subject_id is not None
    _raw_update(
        "UPDATE taxonomy_subject SET discipline_id = %s WHERE id = %s",
        _uuid(question_b.discipline_id),
        _uuid(question_a.subject_id),
    )
    _raw_update(
        "UPDATE reviews_reviewcycle SET workspace_id = %s WHERE question_id = %s",
        _uuid(second.id),
        _uuid(question_a.id),
    )
    _raw_update(
        "UPDATE accounts_workspace SET timezone_name = 'Invalid/Zone' WHERE id = %s",
        _uuid(first.id),
    )
    _raw_update(
        "DELETE FROM errors_error_category WHERE id = %s",
        _uuid(foreign_category.id),
    )
    _raw_update(
        "UPDATE errors_error_category SET workspace_id = %s WHERE id = %s",
        _uuid(second.id),
        _uuid(category.id),
    )

    result = run_integrity_check()
    ids = {finding.invariant_id for finding in result.findings}

    assert {"WS-001", "WS-003", "QUE-001", "REV-001", "ERR-001"}.issubset(ids)
    assert any(
        finding.invariant_id == "REV-001" and finding.severity == InvariantSeverity.CRITICAL
        for finding in result.findings
    )


@pytest.mark.django_db(transaction=True)
def test_limit_preserves_total_order_and_query_count_at_proportional_volume() -> None:
    workspace = _workspace("volume")
    Question.objects.bulk_create(
        [Question(workspace=workspace, draft_title=f"Draft {index}") for index in range(250)]
    )
    questions = [_question(workspace, f"volume-{index}") for index in range(3)]
    for question in questions:
        revision = question.revisions.get(is_current=True)
        _raw_update(
            "UPDATE questions_questionrevision SET is_current = 0 WHERE id = %s",
            _uuid(revision.id),
        )

    result = run_integrity_check(finding_limit=2)

    assert result.total_findings == 3
    assert len(result.findings) == 2
    assert result.truncated
    assert [finding.technical_id for finding in result.findings] == sorted(
        finding.technical_id for finding in result.findings
    )
    assert result.queries_executed == len(INVARIANT_CATALOG) + 1


@pytest.mark.django_db(transaction=True)
def test_foreign_key_violation_is_detected_and_fixture_is_restored() -> None:
    workspace = _workspace("foreign-key")
    question = _question(workspace, "foreign-key")
    unknown_workspace = uuid.uuid4()
    try:
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA foreign_keys = OFF")
            cursor.execute(
                "UPDATE questions_question SET workspace_id = %s WHERE id = %s",
                [_uuid(unknown_workspace), _uuid(question.id)],
            )

        result = run_integrity_check()

        assert "DB-002" in {finding.invariant_id for finding in result.findings}
    finally:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE questions_question SET workspace_id = %s WHERE id = %s",
                [_uuid(workspace.id), _uuid(question.id)],
            )
            cursor.execute("PRAGMA foreign_keys = ON")


@pytest.mark.django_db(transaction=True)
def test_command_exit_zero_and_summary_logging_on_healthy_database() -> None:
    workspace = _workspace("command")
    _question(workspace, "command")
    output = StringIO()

    with _captured_logger() as logs:
        call_command(
            "check_integrity",
            stdout=output,
            correlation_id=FIXED_CORRELATION_ID,
        )

    assert "Integrity checker: HEALTHY" in output.getvalue()
    assert "Findings: 0" in output.getvalue()
    assert "Modo read-only" in output.getvalue()
    events = _events(logs)
    assert [event["event_code"] for event in events] == [
        "INTEGRITY_CHECK_STARTED",
        "INTEGRITY_CHECK_SUCCEEDED",
    ]
    assert events[-1]["context"]["total_findings"] == 0


@pytest.mark.django_db(transaction=True)
def test_operational_failure_has_distinct_exit_and_never_leaks_exception() -> None:
    output = StringIO()
    error = IntegrityCheckOperationalError(f"path={PRIVATE_SENTINEL}")

    with (
        patch(
            "modules.operations.management.commands.check_integrity.run_integrity_check",
            side_effect=error,
        ),
        _captured_logger() as logs,
        pytest.raises(CommandError) as raised,
    ):
        call_command(
            "check_integrity",
            stdout=output,
            correlation_id=FIXED_CORRELATION_ID,
        )

    assert raised.value.returncode == EXIT_OPERATIONAL_FAILURE
    assert PRIVATE_SENTINEL not in output.getvalue()
    assert PRIVATE_SENTINEL not in str(raised.value)
    assert PRIVATE_SENTINEL not in logs.getvalue()
    assert "Traceback" not in logs.getvalue()
    assert [event["event_code"] for event in _events(logs)] == [
        "INTEGRITY_CHECK_STARTED",
        "INTEGRITY_CHECK_FAILED",
    ]


@pytest.mark.django_db(transaction=True)
def test_invalid_limit_is_operational_failure_before_database_read() -> None:
    with pytest.raises(CommandError) as raised:
        call_command("check_integrity", limit=0)
    assert raised.value.returncode == EXIT_OPERATIONAL_FAILURE
