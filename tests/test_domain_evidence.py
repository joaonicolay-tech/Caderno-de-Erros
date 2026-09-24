"""Read-only DOM-HEUR-1.0 evidence adapter coverage."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest

from modules.accounts.models import User, Workspace
from modules.attempts.models import Attempt, AttemptType
from modules.domain.policy import DomainMaturity, EvidenceSufficiency
from modules.domain.selectors import evaluate_question_domain
from modules.questions.models import Alternative, Question, QuestionRevision
from modules.questions.services import AlternativeInput, create_active
from modules.reviews.models import (
    Review,
    ReviewCycle,
    ReviewCycleOriginKind,
    ReviewCycleState,
    ReviewStageCode,
    ReviewState,
)
from modules.taxonomy.services import create_discipline, create_subject
from shared.domain.time import FixedClock, Instant

NOW = datetime(2026, 9, 24, 15, tzinfo=UTC)
CLOCK = FixedClock(Instant(NOW))


def _question(workspace: Workspace, *, suffix: str) -> Question:
    discipline = create_discipline(workspace_id=workspace.id, name=f"Discipline {suffix}")
    subject = create_subject(
        workspace_id=workspace.id, discipline_id=discipline.id, name=f"Subject {suffix}"
    )
    return create_active(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        subject_id=subject.id,
        stem=f"Question {suffix}",
        alternatives=[
            AlternativeInput(f"Option {index}", chr(64 + index)) for index in range(1, 6)
        ],
        correct_alternative_position=1,
        explanation="Explanation",
        trap_note="Trap",
        notes="Notes",
        clock=CLOCK,
    )


def _attempt(
    workspace: Workspace,
    question: Question,
    *,
    at: datetime,
    position: int,
    attempt_type: str = AttemptType.INITIAL,
    review: Review | None = None,
) -> Attempt:
    revision = QuestionRevision.objects.get(question=question, is_current=True)
    alternative = Alternative.objects.get(question_revision=revision, position=position)
    return Attempt.objects.create(
        workspace=workspace,
        question=question,
        question_revision=revision,
        review=review,
        attempt_type=attempt_type,
        selected_alternative=alternative,
        is_correct=alternative.id == revision.correct_alternative_id,
        occurred_at=at,
        timezone_name=workspace.timezone_name,
        local_date=at.date(),
        idempotency_key=uuid.uuid4(),
    )


@pytest.mark.django_db
def test_adapter_returns_provisional_initial_and_excludes_archived_question() -> None:
    owner = User.objects.create_user(email="domain-adapter@example.test")
    workspace = Workspace.objects.create(
        owner_user=owner, name="Domain", timezone_name="America/Sao_Paulo"
    )
    question = _question(workspace, suffix="initial")
    _attempt(workspace, question, at=NOW, position=1)

    result = evaluate_question_domain(
        workspace_id=workspace.id, question_id=question.id, clock=CLOCK
    )

    assert result.sufficiency == EvidenceSufficiency.INSUFFICIENT
    assert result.maturity == DomainMaturity.PROVISIONAL
    assert result.domain_index is not None
    with pytest.raises(Question.DoesNotExist):
        evaluate_question_domain(workspace_id=uuid.uuid4(), question_id=question.id, clock=CLOCK)


@pytest.mark.django_db
def test_adapter_uses_latest_completed_effective_cycle_for_eq() -> None:
    owner = User.objects.create_user(email="domain-cycle@example.test")
    workspace = Workspace.objects.create(
        owner_user=owner, name="Cycle", timezone_name="America/Sao_Paulo"
    )
    question = _question(workspace, suffix="cycle")
    initial = _attempt(workspace, question, at=NOW - timedelta(days=10), position=2)
    cycle = ReviewCycle.objects.create(
        workspace=workspace,
        question=question,
        origin_attempt=initial,
        origin_question_revision=initial.question_revision,
        origin_kind=ReviewCycleOriginKind.INITIAL_ERROR,
        state=ReviewCycleState.COMPLETED,
        started_at=NOW,
        completed_at=NOW,
    )
    ReviewCycle.objects.create(
        workspace=workspace,
        question=question,
        origin_question_revision=initial.question_revision,
        origin_kind=ReviewCycleOriginKind.ATTEMPT_CORRECTION,
        state=ReviewCycleState.SUPERSEDED,
        started_at=NOW + timedelta(days=1),
        superseded_at=NOW + timedelta(days=1),
    )
    review = Review.objects.create(
        workspace=workspace,
        question=question,
        review_cycle=cycle,
        sequence_number=1,
        stage_code=ReviewStageCode.D1,
        state=ReviewState.COMPLETED,
        first_due_date=(NOW - timedelta(days=8)).date(),
        current_due_date=(NOW - timedelta(days=8)).date(),
        scheduled_from_attempt=initial,
        transition_code="COMPLETE_D1",
        completed_at=NOW - timedelta(days=8),
    )
    review_attempt = _attempt(
        workspace,
        question,
        at=NOW - timedelta(days=8),
        position=1,
        attempt_type=AttemptType.REVIEW,
        review=review,
    )
    assert review.review_cycle_id == cycle.id

    result = evaluate_question_domain(
        workspace_id=workspace.id, question_id=question.id, clock=CLOCK
    )

    assert result.sufficiency == EvidenceSufficiency.SUFFICIENT
    assert result.maturity == DomainMaturity.ESTABLISHED
    assert result.explanations[5].code == "EFFECTIVE_CYCLE_SELECTED"
    assert result.vector.eq.value == 100
    assert result.vector.eq.evidence_ids == (str(review_attempt.id),)
