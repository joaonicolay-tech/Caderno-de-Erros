"""V0.5-S2B: lifecycle, grafo, reconstrução e reconciliação de Attempt."""

import uuid
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from contextlib import AbstractContextManager
from datetime import UTC, date, datetime, timedelta
from threading import Barrier

import pytest
from django.core.exceptions import ValidationError
from django.db import close_old_connections, connection

from modules.accounts.models import User, Workspace
from modules.analytics.services import AnalyticsService
from modules.attempts.models import Attempt, AttemptStatus, AttemptType
from modules.attempts.selectors import resolve_attempt_chain
from modules.attempts.services import (
    AttemptCorrectionConflictError,
    AttemptCorrectionResult,
    AttemptCorrectionService,
)
from modules.errors.models import ErrorCategoryCode, ErrorClassification
from modules.errors.services import seed_standard_error_categories
from modules.operations.integrity import run_integrity_check
from modules.operations.models import AuditEntityType, AuditEvent, AuditEventCode
from modules.questions.models import Question
from modules.questions.services import create_active
from modules.reviews.models import (
    Review,
    ReviewCycle,
    ReviewCycleOriginKind,
    ReviewCycleState,
    ReviewState,
)
from modules.reviews.selectors import get_learning_timeline
from modules.reviews.services import ManualReviewInclusionService
from modules.taxonomy.services import create_discipline, create_subject
from shared.domain.time import FixedClock, Instant

CLOCK = FixedClock(Instant(datetime(2026, 9, 20, 15, tzinfo=UTC)))


def _replacement_id(result: AttemptCorrectionResult) -> uuid.UUID:
    assert result.replacement_attempt_id is not None
    return result.replacement_attempt_id


def _workspace(email: str) -> Workspace:
    user = User.objects.create_user(email=email)
    workspace = Workspace.objects.create(
        owner_user=user,
        name=email,
        timezone_name="America/Sao_Paulo",
    )
    seed_standard_error_categories(workspace)
    return workspace


def _question(workspace: Workspace, suffix: str) -> Question:
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
        stem=f"Questão {suffix}",
        alternatives=["incorreta", "correta"],
        correct_alternative_position=2,
        clock=CLOCK,
    )


def _attempt(
    workspace: Workspace,
    question: Question,
    *,
    correct: bool,
    attempt_type: str = AttemptType.INITIAL,
    review: Review | None = None,
    occurred_at: datetime | None = None,
) -> Attempt:
    revision = question.revisions.get(is_current=True)
    instant = occurred_at or CLOCK.now().value
    return Attempt.objects.create(
        workspace=workspace,
        question=question,
        question_revision=revision,
        review=review,
        attempt_type=attempt_type,
        selected_alternative=revision.alternatives.get(position=2 if correct else 1),
        is_correct=correct,
        occurred_at=instant,
        timezone_name=workspace.timezone_name,
        local_date=instant.date(),
        idempotency_key=uuid.uuid4(),
    )


def _completed_d1_with_pending_d7(
    workspace: Workspace, question: Question, *, correct: bool
) -> tuple[Attempt, Review, Review]:
    initial = _attempt(workspace, question, correct=False)
    cycle = question.review_cycles.get(state=ReviewCycleState.ACTIVE)
    d1 = cycle.reviews.get(state=ReviewState.PENDING)
    review_attempt = _attempt(
        workspace,
        question,
        correct=correct,
        attempt_type=AttemptType.REVIEW,
        review=d1,
        occurred_at=CLOCK.now().value + timedelta(minutes=1),
    )
    Review.objects.filter(pk=d1.id).update(
        state=ReviewState.COMPLETED,
        completed_at=review_attempt.occurred_at,
    )
    d7 = Review.objects.create(
        workspace=workspace,
        question=question,
        review_cycle=cycle,
        sequence_number=2,
        stage_code="D7" if correct else "D1",
        first_due_date=date(2026, 9, 27) if correct else date(2026, 9, 21),
        current_due_date=date(2026, 9, 27) if correct else date(2026, 9, 21),
        scheduled_from_attempt=review_attempt,
        transition_code="ADVANCE_D1_TO_D7" if correct else "RESET_TO_D1_AFTER_ERROR",
    )
    assert initial.status == AttemptStatus.VALID
    d1.refresh_from_db()
    return review_attempt, d1, d7


@pytest.mark.django_db
def test_void_initial_preserves_fact_and_reconciles_analytics_without_touching_activation() -> None:
    workspace = _workspace("s2b-void@example.test")
    question = _question(workspace, "void")
    attempt = _attempt(workspace, question, correct=True)
    activation_cycle = question.review_cycles.get()
    before = AnalyticsService(workspace_id=workspace.id, clock=CLOCK).activity()

    result = AttemptCorrectionService(workspace_id=workspace.id, clock=CLOCK).void(
        attempt_id=attempt.id,
        expected_tip_id=attempt.id,
        reason_code="SOURCE_EVENT_INVALID",
    )

    attempt.refresh_from_db()
    after = AnalyticsService(workspace_id=workspace.id, clock=CLOCK).activity()
    assert (attempt.status, attempt.void_reason, attempt.voided_at) == (
        AttemptStatus.VOIDED,
        "SOURCE_EVENT_INVALID",
        CLOCK.now().value,
    )
    assert Attempt.objects.filter(pk=attempt.id).exists()
    assert (before.performed_questions, before.attempts) == (1, 1)
    assert (after.performed_questions, after.attempts) == (0, 0)
    activation_cycle.refresh_from_db()
    assert activation_cycle.state == ReviewCycleState.ACTIVE
    event = AuditEvent.objects.get(correlation_id=result.correlation_id)
    assert (event.event_code, event.entity_type, event.entity_id) == (
        AuditEventCode.ATTEMPT_VOIDED,
        AuditEntityType.ATTEMPT,
        attempt.id,
    )


@pytest.mark.django_db
def test_replacement_and_second_correction_form_one_effective_chain() -> None:
    workspace = _workspace("s2b-chain@example.test")
    question = _question(workspace, "chain")
    original = _attempt(workspace, question, correct=False)
    revision = question.revisions.get(is_current=True)
    service = AttemptCorrectionService(workspace_id=workspace.id, clock=CLOCK)

    first = service.replace(
        attempt_id=original.id,
        expected_tip_id=original.id,
        selected_alternative_id=revision.alternatives.get(position=2).id,
        reason_code="WRONG_SELECTED_ALTERNATIVE",
    )
    replacement = Attempt.objects.get(pk=_replacement_id(first))
    second = service.replace(
        attempt_id=original.id,
        expected_tip_id=replacement.id,
        selected_alternative_id=revision.alternatives.get(position=1).id,
        reason_code="SECOND_SOURCE_CORRECTION",
    )
    final = Attempt.objects.get(pk=_replacement_id(second))
    chain = resolve_attempt_chain(workspace_id=workspace.id, attempt_id=original.id)
    same_chain_from_middle = resolve_attempt_chain(
        workspace_id=workspace.id,
        attempt_id=replacement.id,
    )

    assert [row.id for row in chain.attempts] == [original.id, replacement.id, final.id]
    assert [row.id for row in same_chain_from_middle.attempts] == [
        original.id,
        replacement.id,
        final.id,
    ]
    assert [row.status for row in chain.attempts] == [
        AttemptStatus.VOIDED,
        AttemptStatus.VOIDED,
        AttemptStatus.VALID,
    ]
    assert chain.tip == final
    assert Attempt.objects.filter(question=question, status=AttemptStatus.VALID).count() == 1
    assert AnalyticsService(workspace_id=workspace.id).activity().attempts == 1
    with pytest.raises(AttemptCorrectionConflictError, match="ponta efetiva mudou"):
        service.replace(
            attempt_id=original.id,
            expected_tip_id=replacement.id,
            selected_alternative_id=revision.alternatives.get(position=2).id,
            reason_code="STALE",
        )


@pytest.mark.django_db
def test_direct_branch_self_and_cross_context_are_rejected() -> None:
    workspace = _workspace("s2b-graph@example.test")
    foreign = _workspace("s2b-graph-foreign@example.test")
    question = _question(workspace, "graph")
    other = _question(foreign, "foreign")
    original = _attempt(workspace, question, correct=False)
    service = AttemptCorrectionService(workspace_id=workspace.id, clock=CLOCK)
    revision = question.revisions.get(is_current=True)
    result = service.replace(
        attempt_id=original.id,
        expected_tip_id=original.id,
        selected_alternative_id=revision.alternatives.get(position=2).id,
        reason_code="FIRST",
    )

    with pytest.raises(AttemptCorrectionConflictError):
        service.replace(
            attempt_id=original.id,
            expected_tip_id=original.id,
            selected_alternative_id=revision.alternatives.get(position=1).id,
            reason_code="BRANCH",
        )
    with pytest.raises(AttemptCorrectionConflictError):
        service.replace(
            attempt_id=original.id,
            expected_tip_id=_replacement_id(result),
            selected_alternative_id=other.revisions.get().alternatives.get(position=1).id,
            reason_code="FOREIGN",
        )
    original.refresh_from_db()
    self_id = uuid.uuid4()
    with pytest.raises(ValidationError, match="si mesma"):
        Attempt.objects.create(
            id=self_id,
            workspace=workspace,
            question=question,
            question_revision=revision,
            attempt_type=AttemptType.INITIAL,
            selected_alternative=revision.alternatives.get(position=1),
            is_correct=False,
            occurred_at=CLOCK.now().value,
            timezone_name=workspace.timezone_name,
            local_date=CLOCK.now().value.date(),
            replaces_attempt_id=self_id,
            idempotency_key=uuid.uuid4(),
        )


@pytest.mark.django_db
def test_void_requires_reason_workspace_and_fresh_valid_tip() -> None:
    workspace = _workspace("s2b-guards@example.test")
    foreign = _workspace("s2b-guards-foreign@example.test")
    question = _question(workspace, "guards")
    attempt = _attempt(workspace, question, correct=True)
    service = AttemptCorrectionService(workspace_id=workspace.id, clock=CLOCK)

    with pytest.raises(AttemptCorrectionConflictError, match="obrigatório"):
        service.void(
            attempt_id=attempt.id,
            expected_tip_id=attempt.id,
            reason_code="",
        )
    with pytest.raises(AttemptCorrectionConflictError, match="Workspace"):
        AttemptCorrectionService(workspace_id=foreign.id, clock=CLOCK).void(
            attempt_id=attempt.id,
            expected_tip_id=attempt.id,
            reason_code="FOREIGN",
        )
    service.void(
        attempt_id=attempt.id,
        expected_tip_id=attempt.id,
        reason_code="FIRST_VOID",
    )
    with pytest.raises(AttemptCorrectionConflictError, match="ponta efetiva"):
        service.void(
            attempt_id=attempt.id,
            expected_tip_id=attempt.id,
            reason_code="DOUBLE_VOID",
        )


@pytest.mark.django_db
def test_review_replacement_preserves_completed_fact_and_rebuilds_current_projection() -> None:
    workspace = _workspace("s2b-review@example.test")
    question = _question(workspace, "review")
    attempt, completed_d1, old_pending = _completed_d1_with_pending_d7(
        workspace, question, correct=True
    )
    revision = question.revisions.get(is_current=True)

    result = AttemptCorrectionService(workspace_id=workspace.id, clock=CLOCK).replace(
        attempt_id=attempt.id,
        expected_tip_id=attempt.id,
        selected_alternative_id=revision.alternatives.get(position=1).id,
        reason_code="REVIEW_RESULT_CORRECTED",
    )

    completed_d1.refresh_from_db()
    old_pending.refresh_from_db()
    old_cycle = completed_d1.review_cycle
    old_cycle.refresh_from_db()
    replacement = Attempt.objects.get(pk=_replacement_id(result))
    current_cycle = ReviewCycle.objects.get(
        question=question,
        state=ReviewCycleState.ACTIVE,
    )
    current = current_cycle.reviews.get(state=ReviewState.PENDING)
    assert (completed_d1.state, completed_d1.completed_at) == (
        ReviewState.COMPLETED,
        attempt.occurred_at,
    )
    assert old_pending.state == ReviewState.CANCELLED
    assert (old_cycle.state, old_cycle.superseded_at) == (
        ReviewCycleState.SUPERSEDED,
        CLOCK.now().value,
    )
    assert (
        current_cycle.origin_kind,
        current_cycle.origin_attempt_id,
        current.stage_code,
        current.transition_code,
        current.scheduled_from_attempt_id,
    ) == (
        ReviewCycleOriginKind.ATTEMPT_CORRECTION,
        replacement.id,
        "D1",
        "RESET_TO_D1_AFTER_ERROR",
        replacement.id,
    )
    assert not hasattr(replacement, "error_classification")


@pytest.mark.django_db
def test_review_void_without_replacement_reoffers_same_stage_from_previous_valid_fact() -> None:
    workspace = _workspace("s2b-review-void@example.test")
    question = _question(workspace, "review-void")
    attempt, completed_d1, _old_pending = _completed_d1_with_pending_d7(
        workspace, question, correct=True
    )

    AttemptCorrectionService(workspace_id=workspace.id, clock=CLOCK).void(
        attempt_id=attempt.id,
        expected_tip_id=attempt.id,
        reason_code="EVENT_DID_NOT_EXIST",
    )

    completed_d1.refresh_from_db()
    current = Review.objects.get(
        question=question,
        state=ReviewState.PENDING,
        review_cycle__state=ReviewCycleState.ACTIVE,
    )
    assert completed_d1.state == ReviewState.COMPLETED
    assert (current.stage_code, current.current_due_date, current.transition_code) == (
        "D1",
        completed_d1.current_due_date,
        "CORRECTION_RETRY_VOIDED",
    )
    anchor = current.scheduled_from_attempt
    assert anchor is not None
    assert anchor.attempt_type == AttemptType.INITIAL


@pytest.mark.django_db
def test_correct_initial_replacement_preserves_manual_review_projection() -> None:
    workspace = _workspace("s2b-manual@example.test")
    question = _question(workspace, "manual")
    original = _attempt(workspace, question, correct=True)
    completed_at = CLOCK.now().value
    Review.objects.filter(question=question, state=ReviewState.PENDING).update(
        state=ReviewState.COMPLETED,
        completed_at=completed_at,
    )
    ReviewCycle.objects.filter(question=question, state=ReviewCycleState.ACTIVE).update(
        state=ReviewCycleState.COMPLETED,
        completed_at=completed_at,
    )
    manual = ManualReviewInclusionService(
        workspace_id=workspace.id,
        clock=CLOCK,
    ).include(question_id=question.id, reason_code="STUDY_PLAN")
    old_pending = manual.reviews.get(state=ReviewState.PENDING)
    revision = question.revisions.get(is_current=True)

    result = AttemptCorrectionService(workspace_id=workspace.id, clock=CLOCK).replace(
        attempt_id=original.id,
        expected_tip_id=original.id,
        selected_alternative_id=revision.alternatives.get(position=2).id,
        reason_code="CORRECT_SOURCE_METADATA",
    )

    manual.refresh_from_db()
    old_pending.refresh_from_db()
    replacement = Attempt.objects.get(pk=_replacement_id(result))
    current_cycle = ReviewCycle.objects.get(question=question, state=ReviewCycleState.ACTIVE)
    current = current_cycle.reviews.get(state=ReviewState.PENDING)
    assert (manual.state, old_pending.state) == (
        ReviewCycleState.SUPERSEDED,
        ReviewState.CANCELLED,
    )
    assert (
        current_cycle.origin_kind,
        current_cycle.origin_attempt_id,
        current.stage_code,
        current.current_due_date,
        current.transition_code,
    ) == (
        ReviewCycleOriginKind.ATTEMPT_CORRECTION,
        replacement.id,
        old_pending.stage_code,
        old_pending.current_due_date,
        "CORRECTION_PRESERVE_MANUAL",
    )
    assert run_integrity_check().total_findings == 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    "fault_point",
    ["after_void", "after_replacement", "after_reconstruction", "before_audit", "after_audit"],
)
def test_fault_injection_restores_original_state(fault_point: str) -> None:
    workspace = _workspace(f"s2b-fault-{fault_point}@example.test")
    question = _question(workspace, fault_point)
    attempt = _attempt(workspace, question, correct=False)
    revision = question.revisions.get(is_current=True)

    def fail(point: str) -> None:
        if point == fault_point:
            raise RuntimeError("fault injection")

    with pytest.raises(RuntimeError, match="fault injection"):
        AttemptCorrectionService(workspace_id=workspace.id, clock=CLOCK).replace(
            attempt_id=attempt.id,
            expected_tip_id=attempt.id,
            selected_alternative_id=revision.alternatives.get(position=2).id,
            reason_code="FAULT_TEST",
            fault_hook=fail,
        )
    attempt.refresh_from_db()
    assert (attempt.status, attempt.voided_at, attempt.void_reason) == (
        AttemptStatus.VALID,
        None,
        None,
    )
    assert Attempt.objects.filter(question=question).count() == 1
    assert not AuditEvent.objects.filter(workspace=workspace).exists()


@pytest.mark.django_db
def test_retry_by_correlation_is_idempotent_and_timeline_explains_chain() -> None:
    workspace = _workspace("s2b-idempotent@example.test")
    question = _question(workspace, "idempotent")
    original = _attempt(workspace, question, correct=False)
    revision = question.revisions.get(is_current=True)
    correlation = uuid.uuid4()
    service = AttemptCorrectionService(workspace_id=workspace.id, clock=CLOCK)
    correct_id = revision.alternatives.get(position=2).id
    first = service.replace(
        attempt_id=original.id,
        expected_tip_id=original.id,
        selected_alternative_id=correct_id,
        reason_code="RETRY_SAFE",
        correlation_id=correlation,
    )
    second = service.replace(
        attempt_id=original.id,
        expected_tip_id=original.id,
        selected_alternative_id=correct_id,
        reason_code="RETRY_SAFE",
        correlation_id=correlation,
    )
    events = AuditEvent.objects.filter(correlation_id=correlation)
    timeline = get_learning_timeline(workspace_id=workspace.id, question_id=question.id)

    assert first.replacement_attempt_id == second.replacement_attempt_id
    assert Attempt.objects.filter(question=question).count() == 2
    assert set(events.values_list("event_code", flat=True)) == {
        AuditEventCode.ATTEMPT_VOIDED,
        AuditEventCode.ATTEMPT_REPLACED,
    }
    assert any(event.kind == "attempt_voided" for event in timeline)
    assert any(event.kind == "attempt_replaced" for event in timeline)
    with pytest.raises(AttemptCorrectionConflictError, match="correção diferente"):
        service.replace(
            attempt_id=original.id,
            expected_tip_id=original.id,
            selected_alternative_id=revision.alternatives.get(position=1).id,
            reason_code="RETRY_SAFE",
            correlation_id=correlation,
        )
    with pytest.raises(AttemptCorrectionConflictError, match="correção diferente"):
        service.void(
            attempt_id=original.id,
            expected_tip_id=original.id,
            reason_code="RETRY_SAFE",
            correlation_id=correlation,
        )


@pytest.mark.django_db
def test_old_classification_stays_historical_and_new_error_is_unclassified() -> None:
    workspace = _workspace("s2b-classification@example.test")
    question = _question(workspace, "classification")
    original = _attempt(workspace, question, correct=False)
    classification = ErrorClassification.objects.create(
        workspace=workspace,
        attempt=original,
        category=workspace.error_categories.get(code=ErrorCategoryCode.ATTENTION),
    )
    revision = question.revisions.get(is_current=True)

    result = AttemptCorrectionService(workspace_id=workspace.id, clock=CLOCK).replace(
        attempt_id=original.id,
        expected_tip_id=original.id,
        selected_alternative_id=revision.alternatives.get(position=1).id,
        reason_code="CLASSIFICATION_PROJECTION",
    )
    replacement = Attempt.objects.get(pk=_replacement_id(result))
    breakdown = AnalyticsService(workspace_id=workspace.id).error_categories()

    classification.refresh_from_db()
    assert classification.attempt_id == original.id
    assert not hasattr(replacement, "error_classification")
    assert (breakdown.classified_errors, breakdown.unclassified_errors) == (0, 1)


@pytest.mark.django_db(transaction=True)
def test_checker_accepts_reconstructed_state_and_detects_graph_and_projection_corruption() -> None:
    workspace = _workspace("s2b-checker@example.test")
    question = _question(workspace, "checker")
    attempt, _completed, _pending = _completed_d1_with_pending_d7(workspace, question, correct=True)
    revision = question.revisions.get(is_current=True)
    AttemptCorrectionService(workspace_id=workspace.id, clock=CLOCK).replace(
        attempt_id=attempt.id,
        expected_tip_id=attempt.id,
        selected_alternative_id=revision.alternatives.get(position=1).id,
        reason_code="CHECKER_HEALTHY",
    )
    assert run_integrity_check().total_findings == 0

    replacement = Attempt.objects.get(replaces_attempt=attempt)
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE attempts_attempt SET replaces_attempt_id = %s WHERE id = %s",
            [replacement.id.hex, replacement.id.hex],
        )
    active = ReviewCycle.objects.get(question=question, state=ReviewCycleState.ACTIVE)
    ReviewCycle.objects.filter(pk=active.id).update(
        state=ReviewCycleState.SUPERSEDED,
        superseded_at=CLOCK.now().value,
    )

    ids = {finding.invariant_id for finding in run_integrity_check().findings}
    assert {"ATT-003", "REV-006"}.issubset(ids)


@pytest.mark.django_db(transaction=True)
def test_two_simultaneous_replacements_create_only_one_successor() -> None:
    workspace = _workspace("s2b-concurrency@example.test")
    question = _question(workspace, "concurrency")
    original = _attempt(workspace, question, correct=False)
    alternative_id = question.revisions.get(is_current=True).alternatives.get(position=2).id
    barrier = Barrier(2)

    def correct(index: int) -> str:
        close_old_connections()
        try:
            barrier.wait(timeout=10)
            AttemptCorrectionService(workspace_id=workspace.id, clock=CLOCK).replace(
                attempt_id=original.id,
                expected_tip_id=original.id,
                selected_alternative_id=alternative_id,
                reason_code=f"CONCURRENT_{index}",
            )
            return "success"
        except AttemptCorrectionConflictError:
            return "conflict"
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(correct, range(2)))

    assert outcomes.count("success") == 1
    assert outcomes.count("conflict") == 1
    assert Attempt.objects.filter(replaces_attempt=original).count() == 1
    assert Attempt.objects.filter(question=question, status=AttemptStatus.VALID).count() == 1


@pytest.mark.django_db
def test_effective_tip_resolution_uses_constant_query_count(
    django_assert_num_queries: Callable[[int], AbstractContextManager[None]],
) -> None:
    workspace = _workspace("s2b-query-count@example.test")
    question = _question(workspace, "query-count")
    root = _attempt(workspace, question, correct=False)
    revision = question.revisions.get(is_current=True)
    service = AttemptCorrectionService(workspace_id=workspace.id, clock=CLOCK)
    tip = root
    for index in range(5):
        result = service.replace(
            attempt_id=root.id,
            expected_tip_id=tip.id,
            selected_alternative_id=revision.alternatives.get(position=2 - index % 2).id,
            reason_code=f"CHAIN_{index}",
        )
        tip = Attempt.objects.get(pk=_replacement_id(result))

    with django_assert_num_queries(2):
        chain = resolve_attempt_chain(workspace_id=workspace.id, attempt_id=root.id)
    assert len(chain.attempts) == 6
    resolved_tip = chain.tip
    assert resolved_tip is not None
    assert resolved_tip.id == tip.id
