"""V0.4-S2: reconciliação executável dos contratos analíticos S1."""

import uuid
from collections.abc import Callable
from contextlib import AbstractContextManager
from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from modules.accounts.models import User, Workspace
from modules.analytics.read_models import (
    AnalyticsPeriod,
    AttemptFilters,
    CycleStatus,
    PerformanceLevel,
)
from modules.analytics.services import AnalyticsService
from modules.attempts.models import Attempt, AttemptStatus, AttemptType
from modules.errors.models import ErrorCategory, ErrorCategoryCode, ErrorClassification
from modules.errors.services import seed_standard_error_categories
from modules.questions.models import Question
from modules.questions.services import QuestionCommandService, create_active, create_draft
from modules.reviews.models import Review, ReviewCycleState, ReviewState
from modules.reviews.policies import ReviewTemporalStatus
from modules.taxonomy.models import Discipline, Subject
from modules.taxonomy.services import create_discipline, create_subject
from shared.domain.time import FixedClock, Instant

REFERENCE_CLOCK = FixedClock(Instant(datetime(2026, 9, 10, 2, tzinfo=UTC)))


def _workspace(email: str, *, timezone_name: str = "America/Sao_Paulo") -> Workspace:
    user = User.objects.create_user(email=email)
    workspace = Workspace.objects.create(
        owner_user=user,
        name=email,
        timezone_name=timezone_name,
    )
    seed_standard_error_categories(workspace)
    return workspace


def _taxonomy(workspace: Workspace, name: str) -> tuple[Discipline, Subject]:
    discipline = create_discipline(workspace_id=workspace.id, name=name)
    subject = create_subject(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        name=f"{name} subject",
    )
    return discipline, subject


def _question(
    workspace: Workspace,
    discipline: Discipline,
    subject: Subject,
    suffix: str,
) -> Question:
    return create_active(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        subject_id=subject.id,
        stem=f"Question {suffix}",
        alternatives=["Wrong", "Correct"],
        correct_alternative_position=2,
        clock=REFERENCE_CLOCK,
    )


def _attempt(
    workspace: Workspace,
    question: Question,
    *,
    correct: bool,
    local_date: date,
    attempt_type: str = AttemptType.INITIAL,
    review: Review | None = None,
    status: str = AttemptStatus.VALID,
    occurred_at: datetime | None = None,
) -> Attempt:
    revision = question.revisions.get(is_current=True)
    voided = status == AttemptStatus.VOIDED
    return Attempt.objects.create(
        workspace=workspace,
        question=question,
        question_revision=revision,
        review=review,
        attempt_type=attempt_type,
        selected_alternative=revision.alternatives.get(position=2 if correct else 1),
        is_correct=correct,
        occurred_at=occurred_at
        or datetime(local_date.year, local_date.month, local_date.day, 15, tzinfo=UTC),
        timezone_name=workspace.timezone_name,
        local_date=local_date,
        status=status,
        voided_at=(
            datetime(local_date.year, local_date.month, local_date.day, 16, tzinfo=UTC)
            if voided
            else None
        ),
        void_reason="Voided fixture" if voided else None,
        idempotency_key=uuid.uuid4(),
    )


def _complete_activation_review(question: Question, *, completed_at: datetime) -> Review:
    review = question.reviews.get(state=ReviewState.PENDING)
    Review.objects.filter(pk=review.id).update(
        state=ReviewState.COMPLETED,
        completed_at=completed_at,
    )
    review.refresh_from_db()
    return review


@pytest.mark.django_db
def test_empty_state_and_filter_validation_preserve_unknown_ratio() -> None:
    workspace = _workspace("analytics-empty@example.test")
    summary = AnalyticsService(workspace_id=workspace.id, clock=REFERENCE_CLOCK).activity()

    assert summary.registered_questions == summary.performed_questions == summary.attempts == 0
    assert summary.correct_answers == summary.incorrect_answers == 0
    assert summary.accuracy.numerator == summary.accuracy.denominator == 0
    assert summary.accuracy.percent is None
    with pytest.raises(ValueError):
        AnalyticsPeriod(start=date(2026, 9, 10))
    with pytest.raises(ValueError):
        AnalyticsPeriod(start=date(2026, 9, 11), end=date(2026, 9, 10))
    with pytest.raises(ValueError):
        AttemptFilters(attempt_type="PENDING")


@pytest.mark.django_db
def test_activity_rn057_period_result_and_workspace_reconcile() -> None:
    workspace = _workspace("analytics-activity@example.test")
    foreign = _workspace("analytics-activity-foreign@example.test")
    discipline, subject = _taxonomy(workspace, "Mathematics")
    foreign_discipline, foreign_subject = _taxonomy(foreign, "Foreign")
    first = _question(workspace, discipline, subject, "1")
    second = _question(workspace, discipline, subject, "2")
    never_performed = _question(workspace, discipline, subject, "3")
    foreign_question = _question(foreign, foreign_discipline, foreign_subject, "foreign")
    _attempt(workspace, first, correct=True, local_date=date(2026, 9, 8))
    initial_error = _attempt(workspace, second, correct=False, local_date=date(2026, 9, 9))
    review = _complete_activation_review(
        second,
        completed_at=datetime(2026, 9, 10, 1, tzinfo=UTC),
    )
    _attempt(
        workspace,
        second,
        correct=True,
        local_date=date(2026, 9, 9),
        attempt_type=AttemptType.REVIEW,
        review=review,
    )
    _attempt(
        workspace,
        never_performed,
        correct=False,
        local_date=date(2026, 9, 9),
        attempt_type=AttemptType.REVIEW,
        review=_complete_activation_review(
            never_performed,
            completed_at=datetime(2026, 9, 10, 1, tzinfo=UTC),
        ),
    )
    _attempt(foreign, foreign_question, correct=True, local_date=date(2026, 9, 9))
    _attempt(
        workspace,
        _question(workspace, discipline, subject, "voided"),
        correct=True,
        local_date=date(2026, 9, 9),
        status=AttemptStatus.VOIDED,
    )
    QuestionCommandService.archive(
        workspace_id=workspace.id,
        question_id=first.id,
        expected_lock_version=first.lock_version,
        clock=REFERENCE_CLOCK,
    )

    service = AnalyticsService(workspace_id=workspace.id)
    period = AnalyticsPeriod(date(2026, 9, 8), date(2026, 9, 10))
    summary = service.activity(period=period)

    assert summary.registered_questions == 4
    assert summary.performed_questions == 2
    assert summary.attempts == 4
    assert (summary.initial_attempts, summary.review_attempts) == (2, 2)
    assert (summary.correct_answers, summary.incorrect_answers) == (2, 2)
    assert summary.accuracy.percent == Decimal("50")
    assert service.registered_questions(status="ARCHIVED").count() == 1
    assert list(service.performed_questions(period=period)) == [first, second]
    assert list(service.attempts(filters=AttemptFilters(period=period))) == sorted(
        [
            initial_error,
            *service.attempts(filters=AttemptFilters(period=period)).exclude(pk=initial_error.pk),
        ],
        key=lambda item: (item.local_date, item.occurred_at, str(item.id)),
    )
    assert service.attempts(filters=AttemptFilters(period=period)).count() == summary.attempts
    assert (
        service.attempts(filters=AttemptFilters(period=period), is_correct=True).count()
        == summary.correct_answers
    )


@pytest.mark.django_db
def test_review_states_use_workspace_civil_date_and_exclude_archived_and_foreign() -> None:
    workspace = _workspace("analytics-reviews@example.test")
    foreign = _workspace("analytics-reviews-foreign@example.test")
    discipline, subject = _taxonomy(workspace, "Review")
    foreign_discipline, foreign_subject = _taxonomy(foreign, "Foreign review")
    overdue_question = _question(workspace, discipline, subject, "overdue")
    due_question = _question(workspace, discipline, subject, "due")
    future_question = _question(workspace, discipline, subject, "future")
    archived_question = _question(workspace, discipline, subject, "archived")
    completed_question = _question(workspace, discipline, subject, "completed")
    foreign_question = _question(foreign, foreign_discipline, foreign_subject, "foreign overdue")
    for question, due_date in (
        (overdue_question, date(2026, 9, 8)),
        (due_question, date(2026, 9, 9)),
        (future_question, date(2026, 9, 10)),
        (archived_question, date(2026, 9, 8)),
        (foreign_question, date(2026, 9, 8)),
    ):
        Review.objects.filter(question=question, state=ReviewState.PENDING).update(
            first_due_date=due_date,
            current_due_date=due_date,
        )
    completed_review = _complete_activation_review(
        completed_question,
        completed_at=datetime(2026, 9, 10, 1, tzinfo=UTC),
    )
    _attempt(
        workspace,
        completed_question,
        correct=True,
        local_date=date(2026, 9, 9),
        attempt_type=AttemptType.REVIEW,
        review=completed_review,
        occurred_at=datetime(2026, 9, 10, 1, tzinfo=UTC),
    )
    QuestionCommandService.archive(
        workspace_id=workspace.id,
        question_id=archived_question.id,
        expected_lock_version=archived_question.lock_version,
        clock=REFERENCE_CLOCK,
    )

    service = AnalyticsService(workspace_id=workspace.id, clock=REFERENCE_CLOCK)
    summary = service.reviews()

    assert summary.reference_date == date(2026, 9, 9)
    assert (summary.completed_today, summary.overdue, summary.due, summary.future) == (1, 1, 1, 1)
    assert list(service.review_drilldown(status=ReviewTemporalStatus.OVERDUE)) == [
        overdue_question.reviews.get(state=ReviewState.PENDING)
    ]
    assert service.completed_reviews_today().count() == summary.completed_today


@pytest.mark.django_db
def test_performance_categories_residue_and_drilldowns_reconcile(
    django_assert_num_queries: Callable[[int], AbstractContextManager[None]],
) -> None:
    workspace = _workspace("analytics-breakdowns@example.test")
    foreign = _workspace("analytics-breakdowns-foreign@example.test")
    math, algebra = _taxonomy(workspace, "Mathematics")
    history, ancient = _taxonomy(workspace, "History")
    empty_discipline, empty_subject = _taxonomy(workspace, "No observations")
    foreign_discipline, foreign_subject = _taxonomy(foreign, "Foreign breakdown")
    q1 = _question(workspace, math, algebra, "math correct")
    q2 = _question(workspace, math, algebra, "math error")
    q3 = _question(workspace, history, ancient, "history error")
    foreign_question = _question(foreign, foreign_discipline, foreign_subject, "foreign error")
    first = _attempt(workspace, q1, correct=True, local_date=date(2026, 9, 9))
    review = _complete_activation_review(q1, completed_at=datetime(2026, 9, 10, 1, tzinfo=UTC))
    _attempt(
        workspace,
        q1,
        correct=True,
        local_date=date(2026, 9, 9),
        attempt_type=AttemptType.REVIEW,
        review=review,
    )
    classified_error = _attempt(workspace, q2, correct=False, local_date=date(2026, 9, 9))
    unclassified_error = _attempt(workspace, q3, correct=False, local_date=date(2026, 9, 9))
    foreign_error = _attempt(foreign, foreign_question, correct=False, local_date=date(2026, 9, 9))
    attention = ErrorCategory.objects.get(
        workspace=workspace,
        code=ErrorCategoryCode.ATTENTION,
    )
    foreign_attention = ErrorCategory.objects.get(
        workspace=foreign,
        code=ErrorCategoryCode.ATTENTION,
    )
    ErrorClassification.objects.create(
        workspace=workspace,
        attempt=classified_error,
        category=attention,
    )
    ErrorClassification.objects.create(
        workspace=foreign,
        attempt=foreign_error,
        category=foreign_attention,
    )

    service = AnalyticsService(workspace_id=workspace.id)
    period_filters = AttemptFilters(period=AnalyticsPeriod(date(2026, 9, 9), date(2026, 9, 9)))
    with django_assert_num_queries(2):
        discipline_rows = service.performance(
            level=PerformanceLevel.DISCIPLINE,
            filters=period_filters,
        )
    by_id = {row.group_id: row for row in discipline_rows.rows}
    assert (by_id[math.id].attempts, by_id[math.id].correct_answers) == (3, 2)
    assert by_id[math.id].accuracy.percent == Decimal(200) / Decimal(3)
    assert (by_id[history.id].attempts, by_id[history.id].correct_answers) == (1, 0)
    assert by_id[history.id].accuracy.percent == Decimal(0)
    assert by_id[empty_discipline.id].accuracy.percent is None
    assert discipline_rows.total_attempts == 4
    assert (
        service.performance_drilldown(
            level=PerformanceLevel.DISCIPLINE,
            group_id=math.id,
            filters=period_filters,
        ).count()
        == by_id[math.id].attempts
    )
    subject_rows = service.performance(
        level=PerformanceLevel.SUBJECT,
        filters=period_filters,
    )
    subject_by_id = {row.group_id: row for row in subject_rows.rows}
    assert subject_by_id[algebra.id].parent_id == math.id
    assert subject_by_id[empty_subject.id].attempts == 0
    assert subject_rows.total_attempts == 4

    with django_assert_num_queries(2):
        categories = service.error_categories(filters=period_filters)
    category_by_id = {row.category_id: row for row in categories.rows}
    assert category_by_id[attention.id].errors == 1
    assert categories.classified_errors == 1
    assert categories.unclassified_errors == 1
    assert categories.eligible_errors == 2
    assert (
        service.error_category_drilldown(
            category_id=attention.id,
            filters=period_filters,
        ).count()
        == 1
    )
    assert list(service.error_category_drilldown(category_id=None, filters=period_filters)) == [
        unclassified_error
    ]
    assert service.attempts(filters=period_filters).count() == 4
    assert first.workspace_id == workspace.id and ancient.discipline_id == history.id


@pytest.mark.django_db
def test_cycle_status_is_exclusive_reconciled_and_workspace_scoped() -> None:
    workspace = _workspace("analytics-cycle@example.test")
    foreign = _workspace("analytics-cycle-foreign@example.test")
    discipline, subject = _taxonomy(workspace, "Cycle")
    foreign_discipline, foreign_subject = _taxonomy(foreign, "Foreign cycle")
    in_review = _question(workspace, discipline, subject, "active")
    completed = _question(workspace, discipline, subject, "completed")
    archived = _question(workspace, discipline, subject, "archived")
    without_cycle = create_draft(
        workspace_id=workspace.id,
        draft_title="Draft without cycle",
    )
    _question(foreign, foreign_discipline, foreign_subject, "foreign")
    completed_review = _complete_activation_review(
        completed,
        completed_at=datetime(2026, 9, 10, 1, tzinfo=UTC),
    )
    completed.review_cycles.filter(state=ReviewCycleState.ACTIVE).update(
        state=ReviewCycleState.COMPLETED,
        completed_at=datetime(2026, 9, 10, 1, tzinfo=UTC),
    )
    QuestionCommandService.archive(
        workspace_id=workspace.id,
        question_id=archived.id,
        expected_lock_version=archived.lock_version,
        clock=REFERENCE_CLOCK,
    )

    service = AnalyticsService(workspace_id=workspace.id)
    summary = service.cycle_status()

    assert (
        summary.archived,
        summary.in_review,
        summary.cycle_completed,
        summary.without_cycle,
    ) == (
        1,
        1,
        1,
        1,
    )
    assert summary.total == service.activity().registered_questions == 4
    assert list(service.cycle_status_drilldown(status=CycleStatus.ARCHIVED)) == [archived]
    assert list(service.cycle_status_drilldown(status=CycleStatus.IN_REVIEW)) == [in_review]
    assert list(service.cycle_status_drilldown(status=CycleStatus.CYCLE_COMPLETED)) == [completed]
    assert list(service.cycle_status_drilldown(status=CycleStatus.WITHOUT_CYCLE)) == [without_cycle]
    assert completed_review.state == ReviewState.COMPLETED
