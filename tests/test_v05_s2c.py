"""V0.5-S2C: correção prospectiva de gabarito por nova revisão."""

import uuid
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from threading import Barrier

import pytest
from django.core.exceptions import ValidationError
from django.db import close_old_connections

from modules.accounts.models import User, Workspace
from modules.analytics.read_models import PerformanceLevel
from modules.analytics.services import AnalyticsService
from modules.attempts.models import Attempt, AttemptStatus, AttemptType
from modules.attempts.services import AttemptCorrectionService, AttemptService
from modules.errors.models import ErrorCategoryCode, ErrorClassification
from modules.errors.services import seed_standard_error_categories
from modules.operations.integrity import run_integrity_check
from modules.operations.models import AuditEntityType, AuditEvent, AuditEventCode
from modules.questions.corrections import (
    AnswerKeyCorrectionConflictError,
    AnswerKeyCorrectionResult,
    AnswerKeyCorrectionService,
)
from modules.questions.exceptions import QuestionCatalogStateConflictError
from modules.questions.models import Alternative, Question, QuestionRevision, RevisionChangeKind
from modules.questions.services import AlternativeInput, create_active, save_revision
from modules.reviews.models import Review, ReviewCycle
from modules.reviews.selectors import get_learning_timeline
from modules.taxonomy.services import create_discipline, create_subject
from shared.domain.time import FixedClock, Instant

CLOCK = FixedClock(Instant(datetime(2026, 9, 20, 15, tzinfo=UTC)))


def _workspace(email: str) -> Workspace:
    user = User.objects.create_user(email=email)
    workspace = Workspace.objects.create(
        owner_user=user,
        name=email,
        timezone_name="America/Sao_Paulo",
    )
    seed_standard_error_categories(workspace)
    return workspace


def _question(workspace: Workspace, suffix: str = "base") -> Question:
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
        alternatives=[
            AlternativeInput("primeira", "A"),
            AlternativeInput("segunda", "B"),
            AlternativeInput("terceira", "C"),
            AlternativeInput("quarta", "D"),
            AlternativeInput("quinta", "E"),
        ],
        correct_alternative_position=2,
        explanation="Explicação preservada",
        trap_note="Pegadinha preservada",
        notes="Notas preservadas",
        clock=CLOCK,
    )


def _attempt(
    workspace: Workspace,
    question: Question,
    *,
    position: int,
    attempt_type: str = AttemptType.INITIAL,
    review: Review | None = None,
) -> Attempt:
    revision = question.revisions.get(is_current=True)
    alternative = revision.alternatives.get(position=position)
    return Attempt.objects.create(
        workspace=workspace,
        question=question,
        question_revision=revision,
        review=review,
        attempt_type=attempt_type,
        selected_alternative=alternative,
        is_correct=alternative.id == revision.correct_alternative_id,
        occurred_at=CLOCK.now().value,
        timezone_name=workspace.timezone_name,
        local_date=CLOCK.now().value.date(),
        idempotency_key=uuid.uuid4(),
    )


def _correct(
    workspace: Workspace,
    question: Question,
    *,
    expected: uuid.UUID,
    position: int,
    reason: str = "OFFICIAL_KEY_FIX",
    correlation: uuid.UUID | None = None,
    fault_hook: Callable[[str], None] | None = None,
) -> AnswerKeyCorrectionResult:
    return AnswerKeyCorrectionService(workspace_id=workspace.id, clock=CLOCK).correct(
        question_id=question.id,
        expected_revision_id=expected,
        correct_alternative_position=position,
        reason_code=reason,
        correlation_id=correlation,
        fault_hook=fault_hook,
    )


@pytest.mark.django_db
def test_r1_r2_r3_copy_only_answer_and_audit_idempotently() -> None:
    workspace = _workspace("s2c-lifecycle@example.test")
    question = _question(workspace)
    r1 = question.revisions.get(is_current=True)
    r1_snapshot = (
        r1.stem,
        r1.explanation,
        r1.trap_note,
        r1.notes,
        list(r1.alternatives.order_by("position").values_list("text", "label")),
        r1.correct_alternative_id,
    )
    correlation = uuid.uuid4()

    first = _correct(
        workspace,
        question,
        expected=r1.id,
        position=5,
        correlation=correlation,
    )
    retry = _correct(
        workspace,
        question,
        expected=r1.id,
        position=5,
        correlation=correlation,
    )
    r2 = QuestionRevision.objects.get(pk=first.new_revision_id)
    second = _correct(workspace, question, expected=r2.id, position=1, reason="SECOND_FIX")
    r3 = QuestionRevision.objects.get(pk=second.new_revision_id)
    r1.refresh_from_db()
    r2.refresh_from_db()

    assert retry == first
    assert [r1.is_current, r2.is_current, r3.is_current] == [False, False, True]
    assert [r1.version_number, r2.version_number, r3.version_number] == [1, 2, 3]
    assert QuestionRevision.objects.filter(question=question, is_current=True).count() == 1
    assert r1_snapshot == (
        r1.stem,
        r1.explanation,
        r1.trap_note,
        r1.notes,
        list(r1.alternatives.order_by("position").values_list("text", "label")),
        r1.correct_alternative_id,
    )
    for revision, position in ((r2, 5), (r3, 1)):
        alternatives = list(revision.alternatives.order_by("position"))
        assert len(alternatives) == 5
        assert revision.correct_alternative_id == alternatives[position - 1].id
        assert all(item.question_revision_id == revision.id for item in alternatives)
        assert revision.stem == r1.stem
        assert revision.explanation == r1.explanation
    event = AuditEvent.objects.get(correlation_id=correlation)
    assert (
        event.event_code,
        event.entity_type,
        event.entity_id,
        event.previous_entity_id,
        event.related_entity_id,
        event.reason_code,
    ) == (
        AuditEventCode.ANSWER_KEY_CORRECTED,
        AuditEntityType.QUESTION,
        question.id,
        r1.id,
        r2.id,
        "OFFICIAL_KEY_FIX",
    )
    assert not {
        "stem",
        "alternatives",
        "answer",
        "explanation",
        "payload",
        "snapshot",
    }.intersection(field.name for field in AuditEvent._meta.fields)
    with pytest.raises(ValidationError):
        AuditEvent.objects.create(
            workspace=workspace,
            event_code=AuditEventCode.ANSWER_KEY_CORRECTED,
            entity_type=AuditEntityType.QUESTION,
            entity_id=question.id,
            related_entity_id=r3.id,
            correlation_id=uuid.uuid4(),
            reason_code="MISSING_PREVIOUS",
        )
    integrity = run_integrity_check()
    assert (integrity.checks_executed, integrity.total_findings) == (25, 0)


@pytest.mark.django_db
def test_historical_attempt_analytics_review_and_classification_do_not_change() -> None:
    workspace = _workspace("s2c-history@example.test")
    question = _question(workspace, "history")
    r1 = question.revisions.get(is_current=True)
    historical = _attempt(workspace, question, position=1)
    category = workspace.error_categories.get(code=ErrorCategoryCode.CONCEPTUAL)
    classification = ErrorClassification.objects.create(
        workspace=workspace,
        attempt=historical,
        category=category,
    )
    analytics = AnalyticsService(workspace_id=workspace.id, clock=CLOCK)
    before = (
        analytics.activity(),
        analytics.performance_pair(),
        analytics.error_categories(),
        tuple(
            analytics.performance_drilldown(
                level=PerformanceLevel.DISCIPLINE,
                group_id=question.discipline_id,
            ).values_list("id", flat=True)
        ),
        tuple(
            analytics.performance_drilldown(
                level=PerformanceLevel.SUBJECT,
                group_id=question.subject_id,
            ).values_list("id", flat=True)
        ),
        tuple(
            analytics.error_category_drilldown(category_id=category.id).values_list("id", flat=True)
        ),
        tuple(Review.objects.filter(question=question).values()),
        tuple(ReviewCycle.objects.filter(question=question).values()),
        tuple(ErrorClassification.objects.filter(pk=classification.id).values()),
    )
    historical_values = tuple(
        getattr(historical, field)
        for field in (
            "question_revision_id",
            "selected_alternative_id",
            "is_correct",
            "status",
            "voided_at",
            "void_reason",
            "replaces_attempt_id",
        )
    )

    result = _correct(workspace, question, expected=r1.id, position=1)
    historical.refresh_from_db()
    after = (
        analytics.activity(),
        analytics.performance_pair(),
        analytics.error_categories(),
        tuple(
            analytics.performance_drilldown(
                level=PerformanceLevel.DISCIPLINE,
                group_id=question.discipline_id,
            ).values_list("id", flat=True)
        ),
        tuple(
            analytics.performance_drilldown(
                level=PerformanceLevel.SUBJECT,
                group_id=question.subject_id,
            ).values_list("id", flat=True)
        ),
        tuple(
            analytics.error_category_drilldown(category_id=category.id).values_list("id", flat=True)
        ),
        tuple(Review.objects.filter(question=question).values()),
        tuple(ReviewCycle.objects.filter(question=question).values()),
        tuple(ErrorClassification.objects.filter(pk=classification.id).values()),
    )

    assert after == before
    assert (
        tuple(
            getattr(historical, field)
            for field in (
                "question_revision_id",
                "selected_alternative_id",
                "is_correct",
                "status",
                "voided_at",
                "void_reason",
                "replaces_attempt_id",
            )
        )
        == historical_values
    )
    assert historical.question_revision_id == r1.id
    assert historical.is_correct is False

    r2 = QuestionRevision.objects.get(pk=result.new_revision_id)
    pending = Review.objects.get(question=question)
    future = _attempt(
        workspace,
        question,
        position=1,
        attempt_type=AttemptType.REVIEW,
        review=pending,
    )
    assert future.question_revision_id == r2.id
    assert future.is_correct is True
    summary = analytics.activity()
    assert (summary.performed_questions, summary.attempts) == (1, 2)
    assert (summary.correct_answers, summary.incorrect_answers) == (1, 1)

    timeline = get_learning_timeline(workspace_id=workspace.id, question_id=question.id)
    attempts = [item for item in timeline if item.kind.startswith("attempt_")]
    correction = next(item for item in timeline if item.kind == "answer_key_corrected")
    assert {item.revision_number for item in attempts} == {1, 2}
    assert correction.revision_number == 2
    assert "revisão 1 → 2" in correction.label


@pytest.mark.django_db
def test_future_presentation_uses_new_revision_and_historical_feedback_uses_old() -> None:
    workspace = _workspace("s2c-presentation@example.test")
    question = _question(workspace, "presentation")
    r1 = question.revisions.get(is_current=True)
    old_correct = r1.correct_alternative
    result = _correct(workspace, question, expected=r1.id, position=4)
    service = AttemptService(
        actor_id=workspace.owner_user_id,
        workspace_id=workspace.id,
        session="s2c-presentation",
        clock=CLOCK,
    )

    presentation = service.presentation(question.id)

    assert presentation["revision_id"] == result.new_revision_id
    assert old_correct is not None and old_correct.question_revision_id == r1.id
    assert r1.alternatives.get(position=2).id == old_correct.id


@pytest.mark.django_db
@pytest.mark.parametrize(
    "point",
    [
        "after_revision",
        "after_alternatives",
        "before_current",
        "after_current",
        "before_audit",
        "after_audit",
    ],
)
def test_fault_injection_rolls_back_every_correction_stage(point: str) -> None:
    workspace = _workspace(f"s2c-fault-{point}@example.test")
    question = _question(workspace, point)
    r1 = question.revisions.get(is_current=True)
    original_lock = question.lock_version

    def fail(current: str) -> None:
        if current == point:
            raise RuntimeError(point)

    with pytest.raises(RuntimeError, match=point):
        _correct(
            workspace,
            question,
            expected=r1.id,
            position=3,
            fault_hook=fail,
        )

    question.refresh_from_db()
    r1.refresh_from_db()
    assert question.lock_version == original_lock
    assert r1.is_current is True
    assert QuestionRevision.objects.filter(question=question).count() == 1
    assert Alternative.objects.filter(question_revision__question=question).count() == 5
    assert not AuditEvent.objects.filter(
        event_code=AuditEventCode.ANSWER_KEY_CORRECTED,
        entity_id=question.id,
    ).exists()


@pytest.mark.django_db
def test_stale_cross_workspace_and_correlation_conflicts_leave_no_partial_state() -> None:
    workspace = _workspace("s2c-conflict@example.test")
    foreign = _workspace("s2c-foreign@example.test")
    question = _question(workspace, "conflict")
    r1 = question.revisions.get(is_current=True)
    correlation = uuid.uuid4()
    result = _correct(
        workspace,
        question,
        expected=r1.id,
        position=3,
        correlation=correlation,
    )

    with pytest.raises(AnswerKeyCorrectionConflictError, match="corrente mudou"):
        _correct(workspace, question, expected=r1.id, position=4)
    with pytest.raises(AnswerKeyCorrectionConflictError, match="correlação"):
        _correct(
            workspace,
            question,
            expected=r1.id,
            position=4,
            correlation=correlation,
        )
    with pytest.raises(AnswerKeyCorrectionConflictError, match="Workspace"):
        AnswerKeyCorrectionService(workspace_id=foreign.id, clock=CLOCK).correct(
            question_id=question.id,
            expected_revision_id=result.new_revision_id,
            correct_alternative_position=4,
            reason_code="FOREIGN",
        )
    assert QuestionRevision.objects.filter(question=question).count() == 2
    assert (
        AuditEvent.objects.filter(
            event_code=AuditEventCode.ANSWER_KEY_CORRECTED,
            entity_id=question.id,
        ).count()
        == 1
    )


@pytest.mark.django_db
def test_s2b_voided_valid_chain_and_events_are_unchanged_by_answer_key_fix() -> None:
    workspace = _workspace("s2c-chain@example.test")
    question = _question(workspace, "chain")
    r1 = question.revisions.get(is_current=True)
    root = _attempt(workspace, question, position=1)
    replacement_result = AttemptCorrectionService(workspace_id=workspace.id, clock=CLOCK).replace(
        attempt_id=root.id,
        expected_tip_id=root.id,
        selected_alternative_id=r1.alternatives.get(position=2).id,
        reason_code="S2B_CHAIN_FIX",
    )
    replacement_id = replacement_result.replacement_attempt_id
    assert replacement_id is not None
    replacement = Attempt.objects.get(pk=replacement_id)
    before = (
        tuple(Attempt.objects.filter(question=question).values()),
        tuple(Review.objects.filter(question=question).values()),
        tuple(ReviewCycle.objects.filter(question=question).values()),
        AuditEvent.objects.filter(
            event_code__in=(AuditEventCode.ATTEMPT_VOIDED, AuditEventCode.ATTEMPT_REPLACED)
        ).count(),
    )

    _correct(workspace, question, expected=r1.id, position=1)

    after = (
        tuple(Attempt.objects.filter(question=question).values()),
        tuple(Review.objects.filter(question=question).values()),
        tuple(ReviewCycle.objects.filter(question=question).values()),
        AuditEvent.objects.filter(
            event_code__in=(AuditEventCode.ATTEMPT_VOIDED, AuditEventCode.ATTEMPT_REPLACED)
        ).count(),
    )
    root.refresh_from_db()
    replacement.refresh_from_db()
    assert after == before
    assert root.status == AttemptStatus.VOIDED
    assert replacement.status == AttemptStatus.VALID
    assert replacement.replaces_attempt_id == root.id


@pytest.mark.django_db
def test_published_rows_and_conventional_critical_edit_cannot_bypass_s2c() -> None:
    workspace = _workspace("s2c-immutability@example.test")
    question = _question(workspace, "immutability")
    revision = question.revisions.get(is_current=True)
    alternative = revision.alternatives.get(position=1)
    _attempt(workspace, question, position=1)

    with pytest.raises(ValidationError, match="imutável"):
        QuestionRevision.objects.filter(pk=revision.id).update(stem="mutação")
    with pytest.raises(ValidationError, match="imutável"):
        Alternative.objects.filter(pk=alternative.id).update(text="mutação")
    with pytest.raises(ValidationError, match="imutável"):
        alternative.delete()
    with pytest.raises(QuestionCatalogStateConflictError, match="serviço auditado"):
        save_revision(
            workspace_id=workspace.id,
            question_id=question.id,
            expected_lock_version=question.lock_version,
            stem=revision.stem,
            alternatives=[item.text for item in revision.alternatives.order_by("position")],
            correct_alternative_position=3,
            change_kind=RevisionChangeKind.CRITICAL_CORRECTION,
            change_reason="bypass",
        )
    with pytest.raises(QuestionCatalogStateConflictError, match="serviço auditado"):
        save_revision(
            workspace_id=workspace.id,
            question_id=question.id,
            expected_lock_version=question.lock_version,
            stem=revision.stem,
            alternatives=[item.text for item in revision.alternatives.order_by("position")],
            correct_alternative_position=3,
            change_kind=RevisionChangeKind.NON_CRITICAL_EDIT,
        )


@pytest.mark.django_db(transaction=True)
def test_two_simultaneous_corrections_create_one_new_current_revision() -> None:
    workspace = _workspace("s2c-concurrency@example.test")
    question = _question(workspace, "concurrency")
    r1 = question.revisions.get(is_current=True)
    barrier = Barrier(2)

    def correct(position: int) -> str:
        close_old_connections()
        try:
            barrier.wait(timeout=10)
            _correct(
                workspace,
                question,
                expected=r1.id,
                position=position,
                reason=f"CONCURRENT_{position}",
            )
            return "success"
        except AnswerKeyCorrectionConflictError:
            return "conflict"
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(correct, (3, 4)))

    assert outcomes.count("success") == 1
    assert outcomes.count("conflict") == 1
    assert QuestionRevision.objects.filter(question=question).count() == 2
    assert QuestionRevision.objects.filter(question=question, is_current=True).count() == 1
    assert (
        AuditEvent.objects.filter(
            event_code=AuditEventCode.ANSWER_KEY_CORRECTED,
            entity_id=question.id,
        ).count()
        == 1
    )
