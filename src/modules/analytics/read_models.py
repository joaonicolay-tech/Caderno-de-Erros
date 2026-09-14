"""Tipos explícitos dos contratos analíticos V0.4-S1."""

import uuid
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum

from modules.attempts.models import AttemptType


@dataclass(frozen=True, slots=True)
class AnalyticsPeriod:
    """Intervalo civil inclusivo ou todo o histórico quando ambas as datas são nulas."""

    start: date | None = None
    end: date | None = None

    def __post_init__(self) -> None:
        if (self.start is None) != (self.end is None):
            raise ValueError("O período exige início e fim, ou nenhuma das duas datas.")
        if self.start is not None and self.end is not None and self.start > self.end:
            raise ValueError("O início do período não pode ser posterior ao fim.")


@dataclass(frozen=True, slots=True)
class AttemptFilters:
    """Filtros que apenas reduzem o universo de tentativas válidas."""

    period: AnalyticsPeriod = AnalyticsPeriod()
    attempt_type: str | None = None
    discipline_id: uuid.UUID | None = None
    subject_id: uuid.UUID | None = None

    def __post_init__(self) -> None:
        if self.attempt_type is not None and self.attempt_type not in AttemptType.values:
            raise ValueError("Tipo de tentativa não suportado.")


@dataclass(frozen=True, slots=True)
class Ratio:
    numerator: int
    denominator: int
    percent: Decimal | None


@dataclass(frozen=True, slots=True)
class ActivitySummary:
    registered_questions: int
    performed_questions: int
    attempts: int
    initial_attempts: int
    review_attempts: int
    correct_answers: int
    incorrect_answers: int
    accuracy: Ratio


@dataclass(frozen=True, slots=True)
class ReviewSummary:
    reference_date: date
    completed_today: int
    overdue: int
    due: int
    future: int


@dataclass(frozen=True, slots=True)
class PerformanceRow:
    group_id: uuid.UUID
    group_name: str
    parent_id: uuid.UUID | None
    attempts: int
    correct_answers: int
    incorrect_answers: int
    accuracy: Ratio


@dataclass(frozen=True, slots=True)
class PerformanceBreakdown:
    rows: tuple[PerformanceRow, ...]
    unlinked_attempts: int
    total_attempts: int


@dataclass(frozen=True, slots=True)
class ErrorCategoryRow:
    category_id: uuid.UUID
    code: str
    display_name: str
    errors: int
    share_of_classified: Ratio


@dataclass(frozen=True, slots=True)
class ErrorCategoryBreakdown:
    rows: tuple[ErrorCategoryRow, ...]
    classified_errors: int
    unclassified_errors: int
    eligible_errors: int


class CycleStatus(StrEnum):
    ARCHIVED = "ARCHIVED"
    IN_REVIEW = "IN_REVIEW"
    CYCLE_COMPLETED = "CYCLE_COMPLETED"
    WITHOUT_CYCLE = "WITHOUT_CYCLE"


class PerformanceLevel(StrEnum):
    DISCIPLINE = "discipline"
    SUBJECT = "subject"


@dataclass(frozen=True, slots=True)
class CycleStatusSummary:
    archived: int
    in_review: int
    cycle_completed: int
    without_cycle: int

    @property
    def total(self) -> int:
        return self.archived + self.in_review + self.cycle_completed + self.without_cycle
