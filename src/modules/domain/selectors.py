"""Read-only evidence adapter for the pure DOM-HEUR-1.0 policy."""

from __future__ import annotations

import uuid

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


def evaluate_question_domain(
    *, workspace_id: uuid.UUID, question_id: uuid.UUID, clock: Clock | None = None
) -> DomainResult:
    """Build a bounded, Workspace-scoped snapshot and evaluate it in memory."""
    question = Question.objects.select_related("workspace").get(
        pk=question_id,
        workspace_id=workspace_id,
        status=QuestionStatus.ACTIVE,
    )
    rows = (
        valid_attempts(
            workspace_id=workspace_id,
            filters=AttemptFilters(),
        )
        .filter(question_id=question.id)
        .select_related("review", "review__review_cycle")
    )
    attempts_list: list[AttemptEvidence] = []
    for row in rows:
        review = row.review
        attempts_list.append(
            AttemptEvidence(
                evidence_id=str(row.id),
                occurred_at=row.occurred_at,
                local_date=row.local_date,
                is_correct=row.is_correct,
                attempt_kind=AttemptKind(row.attempt_type),
                review_stage=(ReviewStage(review.stage_code) if review is not None else None),
                perceived_ease=(PerceivedEase(row.perceived_ease) if row.perceived_ease else None),
                review_cycle_id=(str(review.review_cycle.id) if review is not None else None),
            )
        )
    attempts = tuple(attempts_list)
    voided = (
        Attempt.objects.filter(
            workspace_id=workspace_id,
            question_id=question.id,
            status=AttemptStatus.VOIDED,
        )
        .order_by("occurred_at", "id")
        .values_list("id", flat=True)
    )
    pending_reviews = (
        Review.objects.filter(
            workspace_id=workspace_id,
            question_id=question.id,
            state=ReviewState.PENDING,
        )
        .order_by("created_at", "id")
        .values_list("id", flat=True)
    )
    excluded = tuple(
        [ExcludedEvidence(str(item_id), "ATTEMPT_VOIDED") for item_id in voided]
        + [
            ExcludedEvidence(str(item_id), "PENDING_REVIEW_IS_NOT_ATTEMPT")
            for item_id in pending_reviews
        ]
    )
    effective_cycle = (
        ReviewCycle.objects.filter(
            workspace_id=workspace_id,
            question_id=question.id,
            state__in=(
                ReviewCycleState.ACTIVE,
                ReviewCycleState.COMPLETED,
                ReviewCycleState.SUSPENDED,
            ),
        )
        .order_by("-started_at", "-created_at", "-id")
        .first()
    )
    reference_date = review_reference_date(workspace_id=workspace_id, clock=clock)
    has_active_overdue = (
        eligible_reviews(
            workspace_id=workspace_id,
            status=ReviewTemporalStatus.OVERDUE,
            clock=clock,
            reference_date=reference_date,
        )
        .filter(question_id=question.id)
        .exists()
    )
    return evaluate_domain(
        DomainInput(
            question_id=question.id,
            attempts=attempts,
            evaluated_on=reference_date,
            effective_cycle_id=str(effective_cycle.id) if effective_cycle else None,
            has_active_overdue_review=has_active_overdue,
            excluded_evidence=excluded,
        )
    )
