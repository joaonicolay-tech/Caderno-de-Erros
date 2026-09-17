"""Fachada interna estável das leituras analíticas V0.4-S2."""

from __future__ import annotations

import uuid
from decimal import Decimal

from django.db.models import Count, Q, QuerySet

from modules.attempts.models import Attempt, AttemptStatus, AttemptType
from modules.errors.models import ErrorCategory
from modules.questions.models import Question
from modules.reviews.models import Review
from modules.reviews.policies import ReviewTemporalStatus
from modules.taxonomy.models import Discipline, Subject
from shared.domain.time import Clock

from .read_models import (
    ActivitySummary,
    AnalyticsPeriod,
    AttemptFilters,
    CycleStatus,
    CycleStatusSummary,
    ErrorCategoryBreakdown,
    ErrorCategoryRow,
    PerformanceBreakdown,
    PerformanceLevel,
    PerformanceRow,
    Ratio,
    ReviewSummary,
)
from .selectors import (
    eligible_reviews,
    performed_questions,
    questions_by_cycle_status,
    registered_questions,
    review_reference_date,
    valid_attempts,
)


def _ratio(numerator: int, denominator: int) -> Ratio:
    percent = None
    if denominator:
        percent = Decimal(numerator) * Decimal(100) / Decimal(denominator)
    return Ratio(numerator=numerator, denominator=denominator, percent=percent)


def _attempt_condition(*, workspace_id: uuid.UUID, filters: AttemptFilters, prefix: str) -> Q:
    condition = Q(
        **{
            f"{prefix}workspace_id": workspace_id,
            f"{prefix}question__workspace_id": workspace_id,
            f"{prefix}status": AttemptStatus.VALID,
        }
    )
    if filters.period.start is not None and filters.period.end is not None:
        condition &= Q(
            **{
                f"{prefix}local_date__gte": filters.period.start,
                f"{prefix}local_date__lte": filters.period.end,
            }
        )
    if filters.attempt_type is not None:
        condition &= Q(**{f"{prefix}attempt_type": filters.attempt_type})
    if filters.discipline_id is not None:
        condition &= Q(**{f"{prefix}question__discipline_id": filters.discipline_id})
    if filters.subject_id is not None:
        condition &= Q(**{f"{prefix}question__subject_id": filters.subject_id})
    return condition


class AnalyticsService:
    """Serviço read-only, explicitamente vinculado a um único Workspace."""

    def __init__(self, *, workspace_id: uuid.UUID, clock: Clock | None = None) -> None:
        self.workspace_id = workspace_id
        self.clock = clock

    def activity(self, *, period: AnalyticsPeriod | None = None) -> ActivitySummary:
        period = period or AnalyticsPeriod()
        local_questions = Question.objects.filter(workspace_id=self.workspace_id).values("id")
        attempts = Attempt.objects.filter(
            workspace_id=self.workspace_id,
            question_id__in=local_questions,
            status=AttemptStatus.VALID,
            attempt_type__in=(AttemptType.INITIAL, AttemptType.REVIEW),
        )
        if period.start is not None and period.end is not None:
            attempts = attempts.filter(
                local_date__gte=period.start,
                local_date__lte=period.end,
            )
        counts = attempts.aggregate(
            attempts=Count("id"),
            initial_attempts=Count("id", filter=Q(attempt_type=AttemptType.INITIAL)),
            review_attempts=Count("id", filter=Q(attempt_type=AttemptType.REVIEW)),
            correct_answers=Count("id", filter=Q(is_correct=True)),
            incorrect_answers=Count("id", filter=Q(is_correct=False)),
        )
        total = int(counts["attempts"])
        correct = int(counts["correct_answers"])
        return ActivitySummary(
            registered_questions=registered_questions(workspace_id=self.workspace_id).count(),
            performed_questions=performed_questions(
                workspace_id=self.workspace_id, period=period
            ).count(),
            attempts=total,
            initial_attempts=int(counts["initial_attempts"]),
            review_attempts=int(counts["review_attempts"]),
            correct_answers=correct,
            incorrect_answers=int(counts["incorrect_answers"]),
            accuracy=_ratio(correct, total),
        )

    def performance_pair(self) -> tuple[PerformanceBreakdown, PerformanceBreakdown]:
        """Calcule os dois níveis do dashboard em uma única passagem pelos fatos."""
        local_questions = Question.objects.filter(workspace_id=self.workspace_id)
        attempts = (
            Attempt.objects.filter(
                workspace_id=self.workspace_id,
                question_id__in=local_questions.values("id"),
                status=AttemptStatus.VALID,
                attempt_type__in=(AttemptType.INITIAL, AttemptType.REVIEW),
            )
            .order_by()
            .values("question_id")
            .annotate(
                analytics_attempts=Count("id"),
                analytics_correct=Count("id", filter=Q(is_correct=True)),
            )
        )
        facts = {
            row["question_id"]: (int(row["analytics_attempts"]), int(row["analytics_correct"]))
            for row in attempts
        }
        discipline_counts: dict[uuid.UUID, list[int]] = {}
        subject_counts: dict[uuid.UUID, list[int]] = {}
        discipline_residue = 0
        subject_residue = 0
        for question in local_questions.only("id", "discipline_id", "subject_id"):
            total, correct = facts.get(question.id, (0, 0))
            if question.discipline_id is None:
                discipline_residue += total
            else:
                aggregate = discipline_counts.setdefault(question.discipline_id, [0, 0])
                aggregate[0] += total
                aggregate[1] += correct
            if question.subject_id is None:
                subject_residue += total
            else:
                aggregate = subject_counts.setdefault(question.subject_id, [0, 0])
                aggregate[0] += total
                aggregate[1] += correct

        discipline_rows = tuple(
            self._performance_row(
                group_id=discipline.id,
                group_name=discipline.name,
                parent_id=None,
                counts=discipline_counts.get(discipline.id, [0, 0]),
            )
            for discipline in Discipline.objects.filter(workspace_id=self.workspace_id).order_by(
                "sort_order", "name_key", "id"
            )
        )
        subject_rows = tuple(
            self._performance_row(
                group_id=subject.id,
                group_name=subject.name,
                parent_id=subject.discipline_id,
                counts=subject_counts.get(subject.id, [0, 0]),
            )
            for subject in Subject.objects.filter(
                workspace_id=self.workspace_id,
                discipline__workspace_id=self.workspace_id,
            ).order_by("discipline__sort_order", "name_key", "id")
        )
        return (
            PerformanceBreakdown(
                rows=discipline_rows,
                unlinked_attempts=discipline_residue,
                total_attempts=sum(row.attempts for row in discipline_rows) + discipline_residue,
            ),
            PerformanceBreakdown(
                rows=subject_rows,
                unlinked_attempts=subject_residue,
                total_attempts=sum(row.attempts for row in subject_rows) + subject_residue,
            ),
        )

    @staticmethod
    def _performance_row(
        *,
        group_id: uuid.UUID,
        group_name: str,
        parent_id: uuid.UUID | None,
        counts: list[int],
    ) -> PerformanceRow:
        total, correct = counts
        return PerformanceRow(
            group_id=group_id,
            group_name=group_name,
            parent_id=parent_id,
            attempts=total,
            correct_answers=correct,
            incorrect_answers=total - correct,
            accuracy=_ratio(correct, total),
        )

    def registered_questions(self, *, status: str | None = None) -> QuerySet[Question]:
        return registered_questions(workspace_id=self.workspace_id, status=status)

    def performed_questions(self, *, period: AnalyticsPeriod | None = None) -> QuerySet[Question]:
        period = period or AnalyticsPeriod()
        return performed_questions(workspace_id=self.workspace_id, period=period)

    def attempts(
        self, *, filters: AttemptFilters | None = None, is_correct: bool | None = None
    ) -> QuerySet[Attempt]:
        filters = filters or AttemptFilters()
        queryset = valid_attempts(workspace_id=self.workspace_id, filters=filters)
        if is_correct is not None:
            queryset = queryset.filter(is_correct=is_correct)
        return queryset.select_related("question", "question_revision", "review")

    def reviews(self) -> ReviewSummary:
        today = review_reference_date(workspace_id=self.workspace_id, clock=self.clock)
        completed = valid_attempts(
            workspace_id=self.workspace_id,
            filters=AttemptFilters(
                period=AnalyticsPeriod(today, today),
                attempt_type=AttemptType.REVIEW,
            ),
        ).count()
        return ReviewSummary(
            reference_date=today,
            completed_today=completed,
            overdue=eligible_reviews(
                workspace_id=self.workspace_id,
                status=ReviewTemporalStatus.OVERDUE,
                reference_date=today,
            ).count(),
            due=eligible_reviews(
                workspace_id=self.workspace_id,
                status=ReviewTemporalStatus.DUE,
                reference_date=today,
            ).count(),
            future=eligible_reviews(
                workspace_id=self.workspace_id,
                status=ReviewTemporalStatus.FUTURE,
                reference_date=today,
            ).count(),
        )

    def review_drilldown(self, *, status: ReviewTemporalStatus) -> QuerySet[Review]:
        return eligible_reviews(
            workspace_id=self.workspace_id,
            status=status,
            clock=self.clock,
        )

    def completed_reviews_today(self) -> QuerySet[Attempt]:
        today = review_reference_date(workspace_id=self.workspace_id, clock=self.clock)
        return self.attempts(
            filters=AttemptFilters(
                period=AnalyticsPeriod(today, today),
                attempt_type=AttemptType.REVIEW,
            )
        )

    def performance(
        self,
        *,
        level: PerformanceLevel,
        filters: AttemptFilters | None = None,
    ) -> PerformanceBreakdown:
        filters = filters or AttemptFilters()
        prefix = "questions__attempts__"
        base_condition = _attempt_condition(
            workspace_id=self.workspace_id,
            filters=filters,
            prefix=prefix,
        )
        correct_condition = base_condition & Q(questions__attempts__is_correct=True)
        output: list[PerformanceRow] = []
        if level == PerformanceLevel.DISCIPLINE:
            discipline_rows = (
                Discipline.objects.filter(workspace_id=self.workspace_id)
                .annotate(
                    analytics_attempts=Count("questions__attempts", filter=base_condition),
                    analytics_correct=Count("questions__attempts", filter=correct_condition),
                )
                .order_by("sort_order", "name_key", "id")
            )
            for discipline in discipline_rows:
                total = int(discipline.analytics_attempts)
                correct = int(discipline.analytics_correct)
                output.append(
                    PerformanceRow(
                        group_id=discipline.id,
                        group_name=discipline.name,
                        parent_id=None,
                        attempts=total,
                        correct_answers=correct,
                        incorrect_answers=total - correct,
                        accuracy=_ratio(correct, total),
                    )
                )
        else:
            subject_rows = (
                Subject.objects.filter(
                    workspace_id=self.workspace_id,
                    discipline__workspace_id=self.workspace_id,
                )
                .annotate(
                    analytics_attempts=Count("questions__attempts", filter=base_condition),
                    analytics_correct=Count("questions__attempts", filter=correct_condition),
                )
                .order_by("discipline__sort_order", "name_key", "id")
            )
            for subject in subject_rows:
                total = int(subject.analytics_attempts)
                correct = int(subject.analytics_correct)
                output.append(
                    PerformanceRow(
                        group_id=subject.id,
                        group_name=subject.name,
                        parent_id=subject.discipline_id,
                        attempts=total,
                        correct_answers=correct,
                        incorrect_answers=total - correct,
                        accuracy=_ratio(correct, total),
                    )
                )
        residue_filters = filters
        attempts = valid_attempts(workspace_id=self.workspace_id, filters=residue_filters)
        missing_field = (
            "question__discipline__isnull"
            if level == PerformanceLevel.DISCIPLINE
            else "question__subject__isnull"
        )
        residue = attempts.filter(**{missing_field: True}).count()
        return PerformanceBreakdown(
            rows=tuple(output),
            unlinked_attempts=residue,
            total_attempts=sum(row.attempts for row in output) + residue,
        )

    def performance_drilldown(
        self,
        *,
        level: PerformanceLevel,
        group_id: uuid.UUID | None,
        filters: AttemptFilters | None = None,
    ) -> QuerySet[Attempt]:
        filters = filters or AttemptFilters()
        queryset = valid_attempts(workspace_id=self.workspace_id, filters=filters)
        field = (
            "question__discipline_id"
            if level == PerformanceLevel.DISCIPLINE
            else "question__subject_id"
        )
        return queryset.filter(**{field: group_id}).select_related(
            "question", "question__discipline", "question__subject"
        )

    def error_categories(self, *, filters: AttemptFilters | None = None) -> ErrorCategoryBreakdown:
        filters = filters or AttemptFilters()
        prefix = "classifications__attempt__"
        eligible = _attempt_condition(
            workspace_id=self.workspace_id,
            filters=filters,
            prefix=prefix,
        ) & Q(
            classifications__workspace_id=self.workspace_id,
            classifications__attempt__is_correct=False,
        )
        categories = (
            ErrorCategory.objects.filter(workspace_id=self.workspace_id)
            .annotate(analytics_errors=Count("classifications", filter=eligible))
            .order_by("code", "id")
        )
        raw_rows: list[tuple[ErrorCategory, int]] = []
        classified = 0
        for category in categories:
            errors = int(category.__dict__["analytics_errors"])
            raw_rows.append((category, errors))
            classified += errors
        rows = tuple(
            ErrorCategoryRow(
                category_id=category.id,
                code=category.code,
                display_name=category.display_name,
                errors=errors,
                share_of_classified=_ratio(errors, classified),
            )
            for category, errors in raw_rows
        )
        unclassified_attempts = Attempt.objects.filter(
            workspace_id=self.workspace_id,
            question_id__in=Question.objects.filter(workspace_id=self.workspace_id).values("id"),
            status=AttemptStatus.VALID,
            attempt_type__in=(AttemptType.INITIAL, AttemptType.REVIEW),
            is_correct=False,
            error_classification__isnull=True,
        )
        if filters.period.start is not None and filters.period.end is not None:
            unclassified_attempts = unclassified_attempts.filter(
                local_date__gte=filters.period.start,
                local_date__lte=filters.period.end,
            )
        if filters.attempt_type is not None:
            unclassified_attempts = unclassified_attempts.filter(attempt_type=filters.attempt_type)
        if filters.discipline_id is not None:
            unclassified_attempts = unclassified_attempts.filter(
                question__discipline_id=filters.discipline_id,
                question__discipline__workspace_id=self.workspace_id,
            )
        if filters.subject_id is not None:
            unclassified_attempts = unclassified_attempts.filter(
                question__subject_id=filters.subject_id,
                question__subject__workspace_id=self.workspace_id,
            )
        unclassified = unclassified_attempts.count()
        return ErrorCategoryBreakdown(
            rows=rows,
            classified_errors=classified,
            unclassified_errors=unclassified,
            eligible_errors=classified + unclassified,
        )

    def error_category_drilldown(
        self,
        *,
        category_id: uuid.UUID | None,
        filters: AttemptFilters | None = None,
    ) -> QuerySet[Attempt]:
        filters = filters or AttemptFilters()
        queryset = valid_attempts(workspace_id=self.workspace_id, filters=filters).filter(
            is_correct=False
        )
        if category_id is None:
            queryset = queryset.filter(error_classification__isnull=True)
        else:
            queryset = queryset.filter(
                error_classification__workspace_id=self.workspace_id,
                error_classification__category_id=category_id,
                error_classification__category__workspace_id=self.workspace_id,
            )
        return queryset.select_related("question", "error_classification__category")

    def cycle_status(self) -> CycleStatusSummary:
        counts = {
            status: questions_by_cycle_status(
                workspace_id=self.workspace_id,
                status=status,
            ).count()
            for status in CycleStatus
        }
        return CycleStatusSummary(
            archived=counts[CycleStatus.ARCHIVED],
            in_review=counts[CycleStatus.IN_REVIEW],
            cycle_completed=counts[CycleStatus.CYCLE_COMPLETED],
            without_cycle=counts[CycleStatus.WITHOUT_CYCLE],
        )

    def cycle_status_drilldown(self, *, status: CycleStatus) -> QuerySet[Question]:
        return questions_by_cycle_status(workspace_id=self.workspace_id, status=status)
