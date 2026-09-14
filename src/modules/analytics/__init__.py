"""Interface analítica read-only da V0.4."""

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
from .services import AnalyticsService

__all__ = [
    "ActivitySummary",
    "AnalyticsPeriod",
    "AnalyticsService",
    "AttemptFilters",
    "CycleStatus",
    "CycleStatusSummary",
    "ErrorCategoryBreakdown",
    "ErrorCategoryRow",
    "PerformanceBreakdown",
    "PerformanceLevel",
    "PerformanceRow",
    "Ratio",
    "ReviewSummary",
]
