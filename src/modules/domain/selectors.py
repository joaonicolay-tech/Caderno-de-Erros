"""Workspace-scoped, read-only evidence adapter for DOM-HEUR-1.0."""

from __future__ import annotations

import uuid
from collections import defaultdict
from collections.abc import Sequence

from modules.analytics.read_models import AttemptFilters
from modules.analytics.selectors import eligible_reviews, review_reference_date, valid_attempts
from modules.attempts.models import Attempt, AttemptStatus
from modules.questions.models import Question, QuestionStatus
from modules.reviews.models import Review, ReviewCycle, ReviewCycleState, ReviewState
from modules.reviews.policies import ReviewTemporalStatus
from shared.domain.time import Clock

from .policy import (
    AttemptEvidence,
    AttemptKind,
    DomainInput,
    DomainResult,
    ExcludedEvidence,
    PerceivedEase,
    ReviewStage,
    evaluate_domain,
)


def domain_inputs(
    *, workspace_id: uuid.UUID, question_ids: Sequence[uuid.UUID], clock: Clock | None = None
) -> dict[uuid.UUID, DomainInput]:
    """Select evidence once per table for distinct active Questions."""
    requested = tuple(dict.fromkeys(question_ids))
    if not requested:
        return {}
    active_ids = tuple(
        Question.objects.filter(
            pk__in=requested, workspace_id=workspace_id, status=QuestionStatus.ACTIVE
        ).values_list("id", flat=True)
    )
    if not active_ids:
        return {}
    reference_date = review_reference_date(workspace_id=workspace_id, clock=clock)
    attempts_by_question: dict[uuid.UUID, list[AttemptEvidence]] = defaultdict(list)
    rows = (
        valid_attempts(workspace_id=workspace_id, filters=AttemptFilters())
        .filter(question_id__in=active_ids)
        .select_related("review")
    )
    for row in rows:
        review = row.review
        attempts_by_question[row.question_id].append(
            AttemptEvidence(
                evidence_id=str(row.id),
                occurred_at=row.occurred_at,
                local_date=row.local_date,
                is_correct=row.is_correct,
                attempt_kind=AttemptKind(row.attempt_type),
                review_stage=ReviewStage(review.stage_code) if review is not None else None,
                perceived_ease=PerceivedEase(row.perceived_ease) if row.perceived_ease else None,
                review_cycle_id=str(review.review_cycle_id) if review is not None else None,
            )
        )
    excluded: dict[uuid.UUID, list[ExcludedEvidence]] = defaultdict(list)
    voided = (
        Attempt.objects.filter(
            workspace_id=workspace_id, question_id__in=active_ids, status=AttemptStatus.VOIDED
        )
        .order_by("occurred_at", "id")
        .values_list("question_id", "id")
    )
    for question_id, attempt_id in voided:
        excluded[question_id].append(ExcludedEvidence(str(attempt_id), "ATTEMPT_VOIDED"))
    pending = (
        Review.objects.filter(
            workspace_id=workspace_id, question_id__in=active_ids, state=ReviewState.PENDING
        )
        .order_by("created_at", "id")
        .values_list("question_id", "id")
    )
    for question_id, review_id in pending:
        excluded[question_id].append(
            ExcludedEvidence(str(review_id), "PENDING_REVIEW_IS_NOT_ATTEMPT")
        )
    cycle_ids: dict[uuid.UUID, uuid.UUID] = {}
    cycles = ReviewCycle.objects.filter(
        workspace_id=workspace_id,
        question_id__in=active_ids,
        state__in=(ReviewCycleState.ACTIVE, ReviewCycleState.COMPLETED, ReviewCycleState.SUSPENDED),
    ).order_by("-started_at", "-created_at", "-id")
    for cycle in cycles:
        cycle_ids.setdefault(cycle.question_id, cycle.id)
    overdue_ids = set(
        eligible_reviews(
            workspace_id=workspace_id,
            status=ReviewTemporalStatus.OVERDUE,
            clock=clock,
            reference_date=reference_date,
        )
        .filter(question_id__in=active_ids)
        .values_list("question_id", flat=True)
    )
    return {
        question_id: DomainInput(
            question_id=question_id,
            attempts=tuple(attempts_by_question[question_id]),
            evaluated_on=reference_date,
            effective_cycle_id=str(cycle_ids[question_id]) if question_id in cycle_ids else None,
            has_active_overdue_review=question_id in overdue_ids,
            excluded_evidence=tuple(excluded[question_id]),
        )
        for question_id in active_ids
    }


def evaluate_questions_domain(
    *, workspace_id: uuid.UUID, question_ids: Sequence[uuid.UUID], clock: Clock | None = None
) -> dict[uuid.UUID, DomainResult]:
    """Evaluate an active batch under the S4 policy without per-Question SQL."""
    return {
        question_id: evaluate_domain(input_)
        for question_id, input_ in domain_inputs(
            workspace_id=workspace_id, question_ids=question_ids, clock=clock
        ).items()
    }


def evaluate_question_domain(
    *, workspace_id: uuid.UUID, question_id: uuid.UUID, clock: Clock | None = None
) -> DomainResult:
    """Evaluate one active Question with the same adapter as a batch."""
    result = evaluate_questions_domain(
        workspace_id=workspace_id, question_ids=(question_id,), clock=clock
    ).get(question_id)
    if result is None:
        raise Question.DoesNotExist("Question ativa não disponível neste Workspace.")
    return result
