"""Querysets analíticos V0.4-S2, sempre read-only e Workspace-scoped."""

import uuid
from datetime import date

from django.db.models import Exists, OuterRef, Q, QuerySet

from modules.accounts.models import Workspace
from modules.attempts.models import Attempt, AttemptStatus, AttemptType
from modules.questions.models import Question, QuestionStatus
from modules.reviews.models import Review, ReviewCycle, ReviewCycleState, ReviewState
from modules.reviews.policies import ReviewStatusPolicy, ReviewTemporalStatus
from shared.domain.time import Calendar, Clock, SystemClock, TimeZoneId

from .read_models import AnalyticsPeriod, AttemptFilters, CycleStatus


def valid_attempts(*, workspace_id: uuid.UUID, filters: AttemptFilters) -> QuerySet[Attempt]:
    queryset = Attempt.objects.filter(
        workspace_id=workspace_id,
        question__workspace_id=workspace_id,
        status=AttemptStatus.VALID,
    ).filter(
        Q(attempt_type=AttemptType.INITIAL)
        | Q(attempt_type=AttemptType.REVIEW, review__workspace_id=workspace_id)
    )
    if filters.period.start is not None and filters.period.end is not None:
        queryset = queryset.filter(
            local_date__gte=filters.period.start,
            local_date__lte=filters.period.end,
        )
    if filters.attempt_type is not None:
        queryset = queryset.filter(attempt_type=filters.attempt_type)
    if filters.discipline_id is not None:
        queryset = queryset.filter(
            question__discipline_id=filters.discipline_id,
            question__discipline__workspace_id=workspace_id,
        )
    if filters.subject_id is not None:
        queryset = queryset.filter(
            question__subject_id=filters.subject_id,
            question__subject__workspace_id=workspace_id,
        )
    return queryset.order_by("local_date", "occurred_at", "id")


def registered_questions(
    *, workspace_id: uuid.UUID, status: str | None = None
) -> QuerySet[Question]:
    queryset = Question.objects.filter(workspace_id=workspace_id)
    if status is not None:
        if status not in QuestionStatus.values:
            raise ValueError("Estado de questão não suportado.")
        queryset = queryset.filter(status=status)
    return queryset.order_by("created_at", "id")


def performed_questions(*, workspace_id: uuid.UUID, period: AnalyticsPeriod) -> QuerySet[Question]:
    attempts = valid_attempts(
        workspace_id=workspace_id,
        filters=AttemptFilters(period=period, attempt_type=AttemptType.INITIAL),
    )
    return (
        Question.objects.filter(workspace_id=workspace_id, attempts__in=attempts)
        .distinct()
        .order_by("created_at", "id")
    )


def eligible_reviews(
    *,
    workspace_id: uuid.UUID,
    status: ReviewTemporalStatus,
    clock: Clock | None = None,
    reference_date: date | None = None,
) -> QuerySet[Review]:
    today = reference_date or review_reference_date(workspace_id=workspace_id, clock=clock)
    queryset = Review.objects.filter(
        workspace_id=workspace_id,
        question__workspace_id=workspace_id,
        review_cycle__workspace_id=workspace_id,
        state=ReviewState.PENDING,
        review_cycle__state=ReviewCycleState.ACTIVE,
        question__status=QuestionStatus.ACTIVE,
    )
    if status == ReviewTemporalStatus.OVERDUE:
        queryset = queryset.filter(current_due_date__lt=today)
    elif status == ReviewTemporalStatus.DUE:
        queryset = queryset.filter(current_due_date=today)
    elif status == ReviewTemporalStatus.FUTURE:
        queryset = queryset.filter(current_due_date__gt=today)
    else:
        raise ValueError("O drill-down aceita somente overdue, due ou future.")
    return queryset.select_related("question", "review_cycle").order_by(
        "current_due_date", "created_at", "id"
    )


def review_reference_date(*, workspace_id: uuid.UUID, clock: Clock | None = None) -> date:
    source = clock or SystemClock()
    workspace = Workspace.objects.only("timezone_name").get(pk=workspace_id)
    policy = ReviewStatusPolicy(clock=source, calendar=Calendar(source))
    return policy.reference_date(TimeZoneId(workspace.timezone_name)).value


def questions_by_cycle_status(
    *, workspace_id: uuid.UUID, status: CycleStatus
) -> QuerySet[Question]:
    active_cycles = ReviewCycle.objects.filter(
        workspace_id=workspace_id,
        question_id=OuterRef("pk"),
        state=ReviewCycleState.ACTIVE,
    )
    completed_cycles = ReviewCycle.objects.filter(
        workspace_id=workspace_id,
        question_id=OuterRef("pk"),
        state=ReviewCycleState.COMPLETED,
    )
    queryset = Question.objects.filter(workspace_id=workspace_id).annotate(
        has_active_cycle=Exists(active_cycles),
        has_completed_cycle=Exists(completed_cycles),
    )
    if status == CycleStatus.ARCHIVED:
        queryset = queryset.filter(status=QuestionStatus.ARCHIVED)
    elif status == CycleStatus.IN_REVIEW:
        queryset = queryset.exclude(status=QuestionStatus.ARCHIVED).filter(has_active_cycle=True)
    elif status == CycleStatus.CYCLE_COMPLETED:
        queryset = queryset.exclude(status=QuestionStatus.ARCHIVED).filter(
            has_active_cycle=False,
            has_completed_cycle=True,
        )
    elif status == CycleStatus.WITHOUT_CYCLE:
        queryset = queryset.exclude(status=QuestionStatus.ARCHIVED).filter(
            has_active_cycle=False,
            has_completed_cycle=False,
        )
    return queryset.order_by("created_at", "id")
