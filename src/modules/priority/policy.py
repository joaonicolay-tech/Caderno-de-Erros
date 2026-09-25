"""Pure PRI-HEUR-1.0 calculation over selected Workspace facts."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum
from fractions import Fraction

POLICY_VERSION = "PRI-HEUR-1.0"


class PriorityState(StrEnum):
    ELIGIBLE = "ELIGIBLE"
    COLLECT_MORE_EVIDENCE = "COLLECT_MORE_EVIDENCE"


@dataclass(frozen=True, slots=True)
class RecurrenceEvidence:
    question_id: uuid.UUID
    review_count: int
    error_count: int


@dataclass(frozen=True, slots=True)
class DeclineEvidence:
    question_id: uuid.UUID
    baseline_count: int
    baseline_correct: int
    recent_count: int
    recent_correct: int


@dataclass(frozen=True, slots=True)
class PriorityInput:
    subject_id: uuid.UUID
    evaluated_on: date
    mastery: Decimal | None
    confidence: Decimal | None
    active_question_count: int
    overdue_question_count: int
    recurrence: tuple[RecurrenceEvidence, ...]
    decline: tuple[DeclineEvidence, ...]


@dataclass(frozen=True, slots=True)
class PriorityResult:
    subject_id: uuid.UUID
    evaluated_on: date
    policy_version: str
    state: PriorityState
    confidence: Decimal | None
    active_question_count: int
    overdue_question_count: int
    recurrence_eligible_count: int
    recurring_question_count: int
    comparable_question_count: int
    w: Fraction | None
    o: Fraction | None
    r: Fraction | None
    d: Fraction | None
    score: Fraction | None
    reason_codes: tuple[str, ...]
    explanation_codes: tuple[str, ...]


def _fraction(value: Decimal) -> Fraction:
    if not value.is_finite():
        raise ValueError("Valor finito obrigatório.")
    return Fraction(value)


def evaluate_priority(input_: PriorityInput) -> PriorityResult:
    """Preserve exact rational comparisons; unavailable evidence never becomes zero."""
    if (
        input_.active_question_count < 0
        or not 0 <= input_.overdue_question_count <= input_.active_question_count
    ):
        raise ValueError("Contagens de Questions inválidas.")
    active = input_.active_question_count
    w = None if input_.mastery is None else Fraction(100) - _fraction(input_.mastery)
    o = Fraction(100 * input_.overdue_question_count, active) if active else None
    if w is not None and not 0 <= w <= 100:
        raise ValueError("M_h fora de 0-100.")
    if input_.confidence is not None and not 0 <= _fraction(input_.confidence) <= 100:
        raise ValueError("C_h fora de 0-100.")

    seen_r: set[uuid.UUID] = set()
    eligible_r = recurring = 0
    for item in input_.recurrence:
        if item.question_id in seen_r or not 0 <= item.error_count <= item.review_count:
            raise ValueError("Evidência de recorrência inválida.")
        seen_r.add(item.question_id)
        if item.review_count >= 2:
            eligible_r += 1
            recurring += item.error_count >= 2
    r = Fraction(100 * recurring, eligible_r) if eligible_r >= 3 else None

    seen_d: set[uuid.UUID] = set()
    baseline_sum = recent_sum = Fraction(0)
    comparable = 0
    for decline_item in input_.decline:
        if decline_item.question_id in seen_d or not (
            0 <= decline_item.baseline_correct <= decline_item.baseline_count
            and 0 <= decline_item.recent_correct <= decline_item.recent_count
        ):
            raise ValueError("Evidência de queda inválida.")
        seen_d.add(decline_item.question_id)
        if decline_item.baseline_count and decline_item.recent_count:
            comparable += 1
            baseline_sum += Fraction(
                100 * decline_item.baseline_correct, decline_item.baseline_count
            )
            recent_sum += Fraction(100 * decline_item.recent_correct, decline_item.recent_count)
    d = (
        None
        if comparable < 3
        else min(Fraction(100), max(Fraction(0), (baseline_sum - recent_sum) / comparable))
    )

    reasons: list[str] = []
    if input_.confidence is None:
        reasons.append("MISSING_CONFIDENCE")
    elif input_.confidence < 40:
        reasons.append("LOW_CONFIDENCE")
    if w is None:
        reasons.append("MISSING_DOMAIN_EVIDENCE")
    if o is None:
        reasons.append("NO_ACTIVE_QUESTIONS")
    if r is None:
        reasons.append("MISSING_RECURRENCE_EVIDENCE")
    if d is None:
        reasons.append("MISSING_RECENT_DECLINE_BASELINE")

    score = (
        Fraction(40, 100) * w
        + Fraction(30, 100) * o
        + Fraction(20, 100) * r
        + Fraction(10, 100) * d
        if w is not None and o is not None and r is not None and d is not None and not reasons
        else None
    )
    contributions = (
        ("LOW_DOMAIN", Fraction(40, 100) * w if w is not None else Fraction(0)),
        ("OVERDUE_REVIEWS", Fraction(30, 100) * o if o is not None else Fraction(0)),
        ("RECURRING_ERRORS", Fraction(20, 100) * r if r is not None else Fraction(0)),
        ("RECENT_DECLINE", Fraction(10, 100) * d if d is not None else Fraction(0)),
    )
    explanations = tuple(code for code, value in contributions if value > 0)
    if score is not None and not explanations:
        explanations = ("NO_CONTRIBUTING_RISK",)
    return PriorityResult(
        input_.subject_id,
        input_.evaluated_on,
        POLICY_VERSION,
        PriorityState.COLLECT_MORE_EVIDENCE if reasons else PriorityState.ELIGIBLE,
        input_.confidence,
        active,
        input_.overdue_question_count,
        eligible_r,
        recurring,
        comparable,
        w,
        o,
        r,
        d,
        score,
        tuple(reasons),
        explanations if not reasons else (),
    )


def rank_priorities(results: tuple[PriorityResult, ...]) -> tuple[PriorityResult, ...]:
    def key(item: PriorityResult) -> tuple[Fraction, uuid.UUID]:
        if item.score is None:
            raise ValueError("Ranking requer score disponível.")
        return -item.score, item.subject_id

    return tuple(sorted((item for item in results if item.score is not None), key=key))
