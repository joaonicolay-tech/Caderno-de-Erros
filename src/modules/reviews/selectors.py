"""Leituras E4: fila e histórico são sempre derivados dos fatos persistidos."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from math import ceil

from django.db.models import Prefetch, QuerySet

from modules.accounts.models import Workspace
from modules.attempts.models import Attempt
from modules.errors.models import ErrorClassification, ErrorClassificationRevision
from modules.questions.models import Question, QuestionRevision, QuestionStatus
from shared.domain.time import Calendar, Clock, LocalDate, SystemClock, TimeZoneId

from .models import Review, ReviewCycle, ReviewCycleState, ReviewState
from .policies import ReviewStatusPolicy, ReviewStructuralState, ReviewTemporalStatus


@dataclass(frozen=True, slots=True)
class ReviewQueueSection:
    """Uma página estável de uma única seção temporal da fila."""

    entries: tuple[Review, ...]
    page: int
    page_count: int
    total: int


@dataclass(frozen=True, slots=True)
class ReviewQueue:
    overdue: ReviewQueueSection
    due: ReviewQueueSection
    future: ReviewQueueSection


@dataclass(frozen=True, slots=True)
class TimelineEvent:
    """Projeção read-only; ``precedence`` documenta empates de instante."""

    occurred_at: datetime
    precedence: int
    source_id: uuid.UUID
    kind: str
    label: str
    timezone_name: str | None = None
    local_date: object | None = None
    revision_number: int | None = None


def _section(entries: list[Review], page: int, page_size: int) -> ReviewQueueSection:
    valid_page = max(1, page)
    pages = max(1, ceil(len(entries) / page_size))
    valid_page = min(valid_page, pages)
    start = (valid_page - 1) * page_size
    return ReviewQueueSection(
        tuple(entries[start : start + page_size]), valid_page, pages, len(entries)
    )


def list_review_queue(
    *,
    workspace_id: uuid.UUID,
    clock: Clock | None = None,
    overdue_page: int = 1,
    due_page: int = 1,
    future_page: int = 1,
    page_size: int = 20,
) -> ReviewQueue:
    """Liste pendências executáveis por status temporal, sem materializar fila."""
    if page_size < 1:
        raise ValueError("page_size deve ser positivo.")
    workspace = Workspace.objects.get(pk=workspace_id)
    policy = ReviewStatusPolicy(
        clock=clock or SystemClock(), calendar=Calendar(clock or SystemClock())
    )
    # A policy usa o Clock somente para tempo civil; mantenha uma fonte única por consulta.
    if clock is None:
        source = SystemClock()
        policy = ReviewStatusPolicy(clock=source, calendar=Calendar(source))
    reviews: QuerySet[Review] = (
        Review.objects.filter(
            workspace_id=workspace_id,
            state=ReviewState.PENDING,
            review_cycle__state=ReviewCycleState.ACTIVE,
            question__status=QuestionStatus.ACTIVE,
        )
        .select_related(
            "question",
            "question__discipline",
            "question__subject",
            "review_cycle",
        )
        .prefetch_related(
            Prefetch(
                "question__revisions",
                queryset=QuestionRevision.objects.filter(is_current=True).only(
                    "id", "question_id", "stem"
                ),
                to_attr="queue_current_revision",
            )
        )
        .order_by("current_due_date", "created_at", "id")
    )
    groups: dict[ReviewTemporalStatus, list[Review]] = {
        ReviewTemporalStatus.OVERDUE: [],
        ReviewTemporalStatus.DUE: [],
        ReviewTemporalStatus.FUTURE: [],
    }
    zone = TimeZoneId(workspace.timezone_name)
    for review in reviews:
        status = policy.evaluate(
            structural_state=ReviewStructuralState(review.state),
            current_due_date=LocalDate(review.current_due_date),
            time_zone_id=zone,
        )
        if status in groups:
            groups[status].append(review)
    return ReviewQueue(
        overdue=_section(groups[ReviewTemporalStatus.OVERDUE], overdue_page, page_size),
        due=_section(groups[ReviewTemporalStatus.DUE], due_page, page_size),
        future=_section(groups[ReviewTemporalStatus.FUTURE], future_page, page_size),
    )


def get_review_pending_detail(*, workspace_id: uuid.UUID, review_id: uuid.UUID) -> Review:
    """Recupere uma pendência executável sem revelar outro Workspace."""
    return Review.objects.select_related("question", "review_cycle").get(
        pk=review_id,
        workspace_id=workspace_id,
        state=ReviewState.PENDING,
        review_cycle__state=ReviewCycleState.ACTIVE,
        question__status=QuestionStatus.ACTIVE,
    )


def get_learning_timeline(
    *, workspace_id: uuid.UUID, question_id: uuid.UUID
) -> tuple[TimelineEvent, ...]:
    """Combine fatos imutáveis; empate = instante, precedência de tipo, id."""
    question = Question.objects.get(pk=question_id, workspace_id=workspace_id)
    events: list[TimelineEvent] = []
    attempts = Attempt.objects.filter(
        workspace_id=workspace_id, question_id=question_id
    ).select_related("question_revision")
    for attempt in attempts:
        events.append(
            TimelineEvent(
                attempt.occurred_at,
                10,
                attempt.id,
                f"attempt_{attempt.attempt_type.lower()}",
                "Tentativa",
                attempt.timezone_name,
                attempt.local_date,
                attempt.question_revision.version_number,
            )
        )
    classifications = ErrorClassification.objects.filter(
        workspace_id=workspace_id, attempt__question_id=question_id
    ).select_related("category")
    for classification in classifications:
        events.append(
            TimelineEvent(
                classification.created_at,
                20,
                classification.id,
                "diagnosis_created",
                f"Diagnóstico: {classification.category.display_name}",
            )
        )
    revisions = ErrorClassificationRevision.objects.filter(
        workspace_id=workspace_id, error_classification__attempt__question_id=question_id
    ).select_related("category")
    for revision in revisions:
        events.append(
            TimelineEvent(
                revision.created_at,
                20,
                revision.id,
                "diagnosis_revision",
                f"Diagnóstico r{revision.revision_number}: {revision.category.display_name}",
            )
        )
    reviews = Review.objects.filter(workspace_id=workspace_id, question_id=question_id)
    for review in reviews:
        events.append(
            TimelineEvent(
                review.created_at,
                30,
                review.id,
                "review_scheduled",
                f"{review.stage_code} agendada ({review.transition_code})",
            )
        )
        if review.completed_at:
            events.append(
                TimelineEvent(
                    review.completed_at,
                    40,
                    review.id,
                    "review_completed",
                    f"{review.stage_code} concluída",
                )
            )
        if review.suspended_at:
            events.append(
                TimelineEvent(
                    review.suspended_at,
                    40,
                    review.id,
                    "review_suspended",
                    f"{review.stage_code} suspensa",
                )
            )
    cycles = ReviewCycle.objects.filter(workspace_id=workspace_id, question_id=question_id)
    for cycle in cycles:
        events.append(
            TimelineEvent(cycle.started_at, 30, cycle.id, "cycle_started", "Ciclo iniciado")
        )
        if cycle.completed_at:
            events.append(
                TimelineEvent(
                    cycle.completed_at, 40, cycle.id, "cycle_completed", "Ciclo concluído"
                )
            )
        if cycle.suspended_at:
            events.append(
                TimelineEvent(cycle.suspended_at, 40, cycle.id, "cycle_suspended", "Ciclo suspenso")
            )
    if question.archived_at:
        events.append(
            TimelineEvent(
                question.archived_at, 50, question.id, "question_archived", "Questão arquivada"
            )
        )
    return tuple(
        sorted(
            events, key=lambda event: (event.occurred_at, event.precedence, str(event.source_id))
        )
    )
