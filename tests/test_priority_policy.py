"""Independent vectors for the approved PRI-HEUR-1.0 decisions."""

import uuid
from dataclasses import replace
from datetime import date
from decimal import Decimal
from fractions import Fraction

import pytest

from modules.priority.policy import (
    DeclineEvidence,
    PriorityInput,
    PriorityState,
    RecurrenceEvidence,
    evaluate_priority,
    rank_priorities,
)


def _input() -> PriorityInput:
    ids = tuple(uuid.uuid4() for _ in range(3))
    return PriorityInput(
        subject_id=uuid.uuid4(),
        evaluated_on=date(2026, 9, 24),
        mastery=Decimal("20"),
        confidence=Decimal("40"),
        active_question_count=4,
        overdue_question_count=2,
        recurrence=tuple(
            RecurrenceEvidence(qid, 2, 2 if index == 0 else 0) for index, qid in enumerate(ids)
        ),
        decline=tuple(DeclineEvidence(qid, 1, 1, 1, 0) for qid in ids),
    )


def test_formula_components_explanations_and_boundary() -> None:
    result = evaluate_priority(_input())
    assert result.policy_version == "PRI-HEUR-1.0"
    assert result.state == PriorityState.ELIGIBLE
    assert (result.w, result.o, result.r, result.d) == (
        Fraction(80),
        Fraction(50),
        Fraction(100, 3),
        Fraction(100),
    )
    assert result.score == Fraction(32) + Fraction(15) + Fraction(20, 3) + Fraction(10)
    assert result.explanation_codes == (
        "LOW_DOMAIN",
        "OVERDUE_REVIEWS",
        "RECURRING_ERRORS",
        "RECENT_DECLINE",
    )
    low = evaluate_priority(replace(_input(), confidence=Decimal("39.99")))
    assert low.state == PriorityState.COLLECT_MORE_EVIDENCE
    assert low.score is None
    assert "LOW_CONFIDENCE" in low.reason_codes


@pytest.mark.parametrize("mastery,expected", [("0", 100), ("37.5", Fraction(125, 2)), ("100", 0)])
def test_w_boundaries(mastery: str, expected: int | Fraction) -> None:
    assert evaluate_priority(replace(_input(), mastery=Decimal(mastery))).w == expected


def test_unavailable_is_distinct_from_observed_zero() -> None:
    base = _input()
    missing_r = evaluate_priority(replace(base, recurrence=base.recurrence[:2]))
    assert missing_r.r is None and missing_r.score is None
    assert "MISSING_RECURRENCE_EVIDENCE" in missing_r.reason_codes
    missing_d = evaluate_priority(replace(base, decline=base.decline[:2]))
    assert missing_d.d is None and missing_d.score is None
    assert "MISSING_RECENT_DECLINE_BASELINE" in missing_d.reason_codes
    no_errors = evaluate_priority(
        replace(
            base,
            recurrence=tuple(replace(item, error_count=0) for item in base.recurrence),
            decline=tuple(replace(item, recent_correct=1) for item in base.decline),
        )
    )
    assert no_errors.r == no_errors.d == 0
    assert no_errors.score is not None
    assert evaluate_priority(replace(base, mastery=None, confidence=None)).score is None


def test_distinct_questions_equal_weight_and_improvement() -> None:
    base = _input()
    weighted = replace(
        base,
        decline=(
            replace(
                base.decline[0],
                baseline_count=4,
                baseline_correct=4,
                recent_count=4,
                recent_correct=2,
            ),
            replace(
                base.decline[1],
                baseline_count=1,
                baseline_correct=0,
                recent_count=1,
                recent_correct=1,
            ),
            replace(
                base.decline[2],
                baseline_count=1,
                baseline_correct=1,
                recent_count=1,
                recent_correct=1,
            ),
        ),
    )
    assert evaluate_priority(weighted).d == 0  # Mean baseline 2/3, recent 5/6.
    repeated = replace(
        base,
        recurrence=(
            replace(base.recurrence[0], review_count=7, error_count=7),
            *base.recurrence[1:],
        ),
    )
    assert evaluate_priority(repeated).r == Fraction(100, 3)


def test_unrounded_sort_then_uuid_for_exact_tie() -> None:
    base = _input()
    first = evaluate_priority(
        replace(base, subject_id=uuid.UUID(int=2), mastery=Decimal("20.0001"))
    )
    second = evaluate_priority(replace(base, subject_id=uuid.UUID(int=1)))
    assert first.score is not None and second.score is not None
    assert rank_priorities((first, second)) == (second, first)
    tied = evaluate_priority(replace(base, subject_id=uuid.UUID(int=3)))
    assert rank_priorities((tied, second)) == (second, tied)
