"""Normative, pure policy for a Question-level DOM-HEUR-1.0 estimate."""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from dataclasses import dataclass, replace
from datetime import date, datetime
from decimal import Decimal, localcontext
from enum import StrEnum
from fractions import Fraction

POLICY_VERSION = "DOM-HEUR-1.0"
_ZERO = Decimal("0")
_HUNDRED = Decimal("100")
_CONFIDENCE_BASES = {
    Decimal("20"),
    Decimal("40"),
    Decimal("60"),
    Decimal("80"),
    Decimal("100"),
}
_CALCULATION_PRECISION = 28


class AttemptKind(StrEnum):
    INITIAL = "INITIAL"
    REVIEW = "REVIEW"


class ReviewStage(StrEnum):
    D1 = "D1"
    D7 = "D7"
    D14 = "D14"
    D30 = "D30"


class PerceivedEase(StrEnum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class DomainBand(StrEnum):
    FRAGILE = "FRAGILE"
    IN_DEVELOPMENT = "IN_DEVELOPMENT"
    INTERMEDIATE = "INTERMEDIATE"
    GOOD = "GOOD"
    STRONG = "STRONG"


class EvidenceSufficiency(StrEnum):
    NO_DATA = "NO_DATA"
    INSUFFICIENT = "INSUFFICIENT"
    SUFFICIENT = "SUFFICIENT"


class DomainMaturity(StrEnum):
    NOT_APPLICABLE = "NOT_APPLICABLE"
    PROVISIONAL = "PROVISIONAL"
    ESTABLISHED = "ESTABLISHED"


class MasteryState(StrEnum):
    NOT_DOMINATED = "NOT_DOMINATED"
    DOMINATED = "DOMINATED"


@dataclass(frozen=True, slots=True)
class AttemptEvidence:
    """A preselected eligible fact; ORM selection is outside this pure module."""

    evidence_id: str
    occurred_at: datetime
    local_date: date
    is_correct: bool
    attempt_kind: AttemptKind
    review_stage: ReviewStage | None = None
    perceived_ease: PerceivedEase | None = None
    review_cycle_id: str | None = None

    def __post_init__(self) -> None:
        if not self.evidence_id:
            raise ValueError("evidence_id deve ser preenchido.")
        if self.occurred_at.utcoffset() is None:
            raise ValueError("occurred_at deve incluir fuso horário.")
        if self.attempt_kind == AttemptKind.INITIAL and self.review_stage is not None:
            raise ValueError("Attempt INITIAL não pode carregar etapa Review.")
        if self.attempt_kind == AttemptKind.REVIEW and self.review_stage is None:
            raise ValueError("Attempt REVIEW exige etapa Review.")
        if self.attempt_kind == AttemptKind.REVIEW and self.review_cycle_id is None:
            raise ValueError("Attempt REVIEW exige o ciclo da Review.")


@dataclass(frozen=True, slots=True)
class ComponentEvidence:
    value: Decimal | None
    evidence_ids: tuple[str, ...]
    reason_code: str
    exact_value: Fraction | None = None


@dataclass(frozen=True, slots=True)
class KnownDomainVector:
    """Component results plus the exact unrounded Question index."""

    policy_version: str
    valid_attempt_count: int
    aq: ComponentEvidence
    pq: ComponentEvidence
    fq: ComponentEvidence
    eq: ComponentEvidence
    recovery_cap: Decimal | None
    domain_index: Decimal | None
    confidence_base: Decimal | None
    confidence_age_factor: Decimal | None
    confidence: Decimal | None
    sufficiency_code: str
    limitation_codes: tuple[str, ...]
    domain_index_exact: Fraction | None = None


@dataclass(frozen=True, slots=True)
class ExcludedEvidence:
    evidence_id: str
    reason_code: str


@dataclass(frozen=True, slots=True)
class DomainInput:
    question_id: uuid.UUID
    attempts: tuple[AttemptEvidence, ...]
    evaluated_on: date
    effective_cycle_id: str | None
    has_active_overdue_review: bool
    excluded_evidence: tuple[ExcludedEvidence, ...] = ()


@dataclass(frozen=True, slots=True)
class PolicyExplanation:
    code: str
    evidence_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class DomainResult:
    question_id: uuid.UUID
    policy_version: str
    domain_index: Decimal | None
    domain_band: DomainBand | None
    confidence: Decimal | None
    confidence_base: Decimal | None
    confidence_age_factor: Decimal | None
    sufficiency: EvidenceSufficiency
    maturity: DomainMaturity
    mastery: MasteryState
    vector: KnownDomainVector
    included_attempt_ids: tuple[str, ...]
    excluded_evidence: tuple[ExcludedEvidence, ...]
    explanations: tuple[PolicyExplanation, ...]
    limitation_codes: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class HierarchyAggregate:
    """Pure aggregate for an already selected set of distinct active Questions."""

    question_ids: tuple[uuid.UUID, ...]
    question_count: int
    domain_index: Decimal | None
    confidence: Decimal | None
    quantity_factor: Decimal
    coverage_average: Decimal | None
    confidence_hierarchical: Decimal | None
    state_code: str


_STAGE_SCORE: dict[ReviewStage, Decimal] = {
    ReviewStage.D1: Decimal("25"),
    ReviewStage.D7: Decimal("50"),
    ReviewStage.D14: Decimal("75"),
    ReviewStage.D30: Decimal("100"),
}
_RECOVERY_CAP: dict[ReviewStage | None, Decimal] = {
    None: Decimal("40"),
    ReviewStage.D1: Decimal("60"),
    ReviewStage.D7: Decimal("75"),
    ReviewStage.D14: Decimal("90"),
    ReviewStage.D30: Decimal("100"),
}
_EASE_SCORE: dict[PerceivedEase, Decimal] = {
    PerceivedEase.EASY: Decimal("100"),
    PerceivedEase.MEDIUM: Decimal("75"),
    PerceivedEase.HARD: Decimal("50"),
}
_STAGE_ORDER = {stage: index for index, stage in enumerate(ReviewStage)}


def _ordered(attempts: Sequence[AttemptEvidence]) -> tuple[AttemptEvidence, ...]:
    ids = [attempt.evidence_id for attempt in attempts]
    if len(ids) != len(set(ids)):
        raise ValueError("evidence_id deve ser único no vetor de evidências.")
    return tuple(sorted(attempts, key=lambda item: (item.occurred_at, item.evidence_id)))


def calculate_aq(attempts: Sequence[AttemptEvidence]) -> ComponentEvidence:
    """Calculate recent accuracy from up to five eligible attempts."""
    ordered = _ordered(attempts)
    recent = ordered[-5:]
    if not recent:
        return ComponentEvidence(None, (), "NO_ELIGIBLE_ATTEMPTS")
    weights = tuple(Fraction(7, 10) ** index for index in range(len(recent)))
    # The newest attempt receives 1.00, then 0.70, 0.49, and so on.
    numerator = sum(
        (
            weight
            for weight, attempt in zip(weights, reversed(recent), strict=True)
            if attempt.is_correct
        ),
        start=Fraction(0),
    )
    denominator = sum(weights, start=Fraction(0))
    exact_value = numerator * 100 / denominator
    value = _decimal(exact_value)
    return ComponentEvidence(
        value, tuple(item.evidence_id for item in recent), "WEIGHTED_RECENT_ACCURACY", exact_value
    )


def calculate_pq(attempts: Sequence[AttemptEvidence]) -> ComponentEvidence:
    """Return the highest correct Review stage after the latest valid error."""
    ordered = _ordered(attempts)
    last_error_index = max(
        (index for index, attempt in enumerate(ordered) if not attempt.is_correct),
        default=-1,
    )
    recovery = tuple(
        attempt
        for attempt in ordered[last_error_index + 1 :]
        if attempt.attempt_kind == AttemptKind.REVIEW
        and attempt.is_correct
        and attempt.review_stage is not None
    )
    if not recovery:
        return ComponentEvidence(_ZERO, (), "NO_CORRECT_SPACED_RECOVERY", Fraction(0))

    def stage_rank(item: AttemptEvidence) -> int:
        stage = item.review_stage
        if stage is None:
            raise ValueError("Evidência de Review sem etapa não pode contribuir para Pq.")
        return _STAGE_ORDER[stage]

    highest = max(recovery, key=stage_rank)
    highest_stage = highest.review_stage
    if highest_stage is None:
        raise ValueError("Evidência de Review sem etapa não pode contribuir para Pq.")
    matching_ids = tuple(
        item.evidence_id for item in recovery if item.review_stage == highest_stage
    )
    return ComponentEvidence(
        _STAGE_SCORE[highest_stage],
        matching_ids,
        "HIGHEST_CORRECT_STAGE_AFTER_LAST_ERROR",
        Fraction(_STAGE_SCORE[highest_stage]),
    )


def calculate_fq(attempts: Sequence[AttemptEvidence]) -> ComponentEvidence:
    """Average ease for up to three recent correct Reviews with recorded ease."""
    ordered = _ordered(attempts)
    observations = tuple(
        attempt
        for attempt in ordered
        if attempt.attempt_kind == AttemptKind.REVIEW
        and attempt.is_correct
        and attempt.perceived_ease is not None
    )[-3:]
    if not observations:
        return ComponentEvidence(Decimal("75"), (), "NEUTRAL_EASE_WHEN_UNRECORDED", Fraction(75))
    exact_value = sum(
        (
            Fraction(_EASE_SCORE[item.perceived_ease])
            for item in observations
            if item.perceived_ease is not None
        ),
        start=Fraction(0),
    ) / len(observations)
    value = _decimal(exact_value)
    return ComponentEvidence(
        value, tuple(item.evidence_id for item in observations), "RECENT_REVIEW_EASE", exact_value
    )


def calculate_eq(
    attempts: Sequence[AttemptEvidence], *, current_cycle_review_errors: int | None
) -> ComponentEvidence:
    """Apply the recurrence table when the current-cycle count is resolved."""
    ordered = _ordered(attempts)
    if current_cycle_review_errors is not None and current_cycle_review_errors < 0:
        raise ValueError("current_cycle_review_errors não pode ser negativo.")
    review_count = sum(attempt.attempt_kind == AttemptKind.REVIEW for attempt in ordered)
    if current_cycle_review_errors is not None and current_cycle_review_errors > review_count:
        raise ValueError("A contagem de erros supera as Attempts REVIEW fornecidas.")
    if len(ordered) < 2:
        return ComponentEvidence(
            Decimal("50"),
            tuple(item.evidence_id for item in ordered),
            "FEWER_THAN_TWO_VALID_ATTEMPTS",
            Fraction(50),
        )
    if current_cycle_review_errors is None:
        return ComponentEvidence(None, (), "CURRENT_REVIEW_CYCLE_UNRESOLVED")
    value = (
        Decimal("100")
        if current_cycle_review_errors == 0
        else Decimal("50")
        if current_cycle_review_errors == 1
        else _ZERO
    )
    error_ids = tuple(
        attempt.evidence_id
        for attempt in ordered
        if attempt.attempt_kind == AttemptKind.REVIEW and not attempt.is_correct
    )
    return ComponentEvidence(value, error_ids, "CURRENT_CYCLE_REVIEW_ERROR_COUNT", Fraction(value))


def calculate_confidence_base(attempts: Sequence[AttemptEvidence]) -> Decimal | None:
    """Calculate C_q base from the INITIAL anchor and attempted stages since last error."""
    ordered = _ordered(attempts)
    if not ordered:
        return None
    last_error_index = max(
        (index for index, attempt in enumerate(ordered) if not attempt.is_correct),
        default=-1,
    )
    if last_error_index >= 0:
        anchor_index = last_error_index
        base = Decimal("20")
    else:
        initial_indices = tuple(
            index
            for index, attempt in enumerate(ordered)
            if attempt.attempt_kind == AttemptKind.INITIAL
        )
        if not initial_indices:
            return None
        anchor_index = initial_indices[0]
        base = Decimal("20")
    stage_bases = {
        ReviewStage.D1: Decimal("40"),
        ReviewStage.D7: Decimal("60"),
        ReviewStage.D14: Decimal("80"),
        ReviewStage.D30: Decimal("100"),
    }
    attempted_stages = (
        attempt.review_stage
        for attempt in ordered[anchor_index + 1 :]
        if attempt.attempt_kind == AttemptKind.REVIEW
    )
    return max((base, *(stage_bases[stage] for stage in attempted_stages if stage is not None)))


def _fraction(value: Decimal | None) -> Fraction | None:
    return None if value is None else Fraction(value)


def _decimal(value: Fraction) -> Decimal:
    with localcontext() as context:
        context.prec = _CALCULATION_PRECISION
        return Decimal(value.numerator) / Decimal(value.denominator)


def calculate_confidence_age_factor(*, last_attempt_date: date, evaluated_on: date) -> Decimal:
    """Apply the normative C_q age factor without choosing its evidence base."""
    age_days = (evaluated_on - last_attempt_date).days
    if age_days < 0:
        raise ValueError("A data de avaliação não pode anteceder a última evidência.")
    if age_days <= 60:
        return Decimal("1.00")
    if age_days <= 120:
        return Decimal("0.90")
    if age_days <= 180:
        return Decimal("0.75")
    if age_days <= 365:
        return Decimal("0.50")
    return Decimal("0.25")


def calculate_known_vector(
    attempts: Sequence[AttemptEvidence],
    *,
    evaluated_on: date,
    current_cycle_review_errors: int | None = None,
    confidence_base: Decimal | None = None,
) -> KnownDomainVector:
    """Calculate formula pieces from preselected valid Question facts.

    Attempts must already be selected as eligible/current facts. The caller
    may explicitly supply the selected-cycle error count and confidence base;
    omitting either leaves that dependent result unset and explains why.
    """
    ordered = _ordered(attempts)
    aq = calculate_aq(ordered)
    pq = calculate_pq(ordered)
    fq = calculate_fq(ordered)
    eq = calculate_eq(ordered, current_cycle_review_errors=current_cycle_review_errors)
    has_error = any(not item.is_correct for item in ordered)
    last_error_index = max(
        (index for index, item in enumerate(ordered) if not item.is_correct), default=-1
    )
    recovery = tuple(
        item
        for item in ordered[last_error_index + 1 :]
        if item.attempt_kind == AttemptKind.REVIEW
        and item.is_correct
        and item.review_stage is not None
    )
    highest_stage = max(
        (item.review_stage for item in recovery if item.review_stage is not None),
        key=lambda stage: _STAGE_ORDER[stage],
        default=None,
    )
    cap = _RECOVERY_CAP[highest_stage] if has_error else None
    raw_index_exact: Fraction | None = None
    if aq.exact_value is not None and eq.exact_value is not None:
        raw_index_exact = (
            Fraction(45, 100) * aq.exact_value
            + Fraction(30, 100) * (pq.exact_value or Fraction(0))
            + Fraction(15, 100) * (fq.exact_value or Fraction(0))
            + Fraction(10, 100) * eq.exact_value
        )
    if raw_index_exact is not None and cap is not None:
        raw_index_exact = min(raw_index_exact, Fraction(cap))
    domain_index = _decimal(raw_index_exact) if raw_index_exact is not None else None

    confidence_age_factor: Decimal | None = None
    confidence: Decimal | None = None
    if ordered:
        confidence_age_factor = calculate_confidence_age_factor(
            last_attempt_date=ordered[-1].local_date, evaluated_on=evaluated_on
        )
        if confidence_base is not None:
            if confidence_base not in _CONFIDENCE_BASES:
                raise ValueError("confidence_base deve estar em um valor definido pela regra.")
            with localcontext() as context:
                context.prec = _CALCULATION_PRECISION
                confidence = confidence_base * confidence_age_factor
    elif confidence_base is not None:
        raise ValueError("Não há base de confiança sem tentativa elegível.")

    limitations: list[str] = []
    if len(ordered) >= 2 and current_cycle_review_errors is None:
        limitations.append("CURRENT_REVIEW_CYCLE_UNRESOLVED")
    if ordered and confidence_base is None:
        limitations.append("CONFIDENCE_BASE_UNAVAILABLE")
    return KnownDomainVector(
        policy_version=POLICY_VERSION,
        valid_attempt_count=len(ordered),
        aq=aq,
        pq=pq,
        fq=fq,
        eq=eq,
        recovery_cap=cap,
        domain_index=domain_index,
        confidence_base=confidence_base,
        confidence_age_factor=confidence_age_factor,
        confidence=confidence,
        sufficiency_code=("NO_DATA" if not ordered else "TO_BE_EVALUATED"),
        limitation_codes=tuple(limitations),
        domain_index_exact=raw_index_exact,
    )


def evaluate_domain(input_: DomainInput) -> DomainResult:
    """Evaluate one Question's selected valid facts and return a structured explanation."""
    attempts = _ordered(input_.attempts)
    initial_attempts = tuple(
        attempt for attempt in attempts if attempt.attempt_kind == AttemptKind.INITIAL
    )
    later_reviews = tuple(
        attempt
        for attempt in attempts
        if attempt.attempt_kind == AttemptKind.REVIEW
        and any(attempt.occurred_at > initial.occurred_at for initial in initial_attempts)
    )
    if not attempts:
        sufficiency = EvidenceSufficiency.NO_DATA
        maturity = DomainMaturity.NOT_APPLICABLE
        sufficiency_code = "NO_VALID_ATTEMPTS"
    elif initial_attempts and later_reviews:
        sufficiency = EvidenceSufficiency.SUFFICIENT
        maturity = DomainMaturity.ESTABLISHED
        sufficiency_code = "INITIAL_AND_LATER_VALID_REVIEW_PRESENT"
    else:
        sufficiency = EvidenceSufficiency.INSUFFICIENT
        maturity = DomainMaturity.PROVISIONAL
        sufficiency_code = "INITIAL_OR_LATER_VALID_REVIEW_MISSING"

    cycle_errors = sum(
        attempt.attempt_kind == AttemptKind.REVIEW
        and str(attempt.review_cycle_id) == str(input_.effective_cycle_id)
        and not attempt.is_correct
        for attempt in attempts
    )
    effective_errors = cycle_errors if input_.effective_cycle_id is not None else 0
    confidence_base = calculate_confidence_base(attempts)
    vector = calculate_known_vector(
        attempts,
        evaluated_on=input_.evaluated_on,
        current_cycle_review_errors=effective_errors,
        confidence_base=confidence_base,
    )
    current_cycle_reviews = tuple(
        attempt
        for attempt in attempts
        if attempt.attempt_kind == AttemptKind.REVIEW
        and input_.effective_cycle_id is not None
        and str(attempt.review_cycle_id) == str(input_.effective_cycle_id)
    )
    vector = replace(
        vector,
        eq=replace(
            vector.eq,
            evidence_ids=(
                vector.eq.evidence_ids
                if len(attempts) < 2
                else tuple(item.evidence_id for item in current_cycle_reviews)
            ),
        ),
    )
    vector = replace(
        vector,
        sufficiency_code=sufficiency.value,
        limitation_codes=(
            ("INSUFFICIENT_EVIDENCE",) if sufficiency == EvidenceSufficiency.INSUFFICIENT else ()
        )
        + vector.limitation_codes,
    )
    band = _domain_band(vector.domain_index_exact)
    mastery = _mastery_state(
        attempts=attempts,
        vector=vector,
        active_overdue=input_.has_active_overdue_review,
    )
    explanations = (
        PolicyExplanation("A_Q", vector.aq.evidence_ids),
        PolicyExplanation("P_Q", vector.pq.evidence_ids),
        PolicyExplanation("F_Q", vector.fq.evidence_ids),
        PolicyExplanation("E_Q", vector.eq.evidence_ids),
        PolicyExplanation(sufficiency_code),
        PolicyExplanation(
            "EFFECTIVE_CYCLE_SELECTED" if input_.effective_cycle_id else "NO_EFFECTIVE_CYCLE"
        ),
        PolicyExplanation(
            "CONFIDENCE_BASE_AND_AGE_FACTOR"
            if vector.confidence is not None
            else "CONFIDENCE_UNAVAILABLE",
            tuple(item.evidence_id for item in attempts),
        ),
    )
    excluded = input_.excluded_evidence + tuple(
        ExcludedEvidence(item.evidence_id, "NOT_EFFECTIVE_CYCLE_FOR_EQ")
        for item in attempts
        if item.attempt_kind == AttemptKind.REVIEW
        and (
            input_.effective_cycle_id is None
            or str(item.review_cycle_id) != str(input_.effective_cycle_id)
        )
    )
    return DomainResult(
        question_id=input_.question_id,
        policy_version=POLICY_VERSION,
        domain_index=vector.domain_index,
        domain_band=band,
        confidence=vector.confidence,
        confidence_base=vector.confidence_base,
        confidence_age_factor=vector.confidence_age_factor,
        sufficiency=sufficiency,
        maturity=maturity,
        mastery=mastery,
        vector=vector,
        included_attempt_ids=tuple(item.evidence_id for item in attempts),
        excluded_evidence=excluded,
        explanations=explanations,
        limitation_codes=vector.limitation_codes,
    )


def aggregate_hierarchy(results: Sequence[DomainResult]) -> HierarchyAggregate:
    """Aggregate selected active Question results under RN-074/075, without queries."""
    ids = tuple(result.question_id for result in results)
    if len(ids) != len(set(ids)):
        raise ValueError("Cada Question deve aparecer uma vez na agrega\u00e7\u00e3o.")
    eligible = tuple(result for result in results if result.domain_index is not None)
    question_ids = tuple(result.question_id for result in eligible)
    count = len(question_ids)
    quantity_factor = (
        Decimal("0")
        if count == 0
        else Decimal("20")
        if count <= 2
        else Decimal("40")
        if count <= 5
        else Decimal("60")
        if count <= 10
        else Decimal("80")
        if count <= 20
        else Decimal("100")
    )
    domain_exact = (
        sum(
            (item.vector.domain_index_exact or Fraction(0) for item in eligible),
            Fraction(0),
        )
        / count
        if count
        else None
    )
    domain_index = _decimal(domain_exact) if domain_exact is not None else None
    confidence_values = tuple(item.confidence for item in eligible if item.confidence is not None)
    coverage_is_complete = len(confidence_values) == count
    with localcontext() as context:
        context.prec = _CALCULATION_PRECISION
        coverage_average = (
            sum(confidence_values, start=_ZERO) / Decimal(len(confidence_values))
            if coverage_is_complete and confidence_values
            else None
        )
        confidence_hierarchical = (
            quantity_factor * Decimal("0.60") + coverage_average * Decimal("0.40")
            if coverage_average is not None
            else None
        )
    return HierarchyAggregate(
        question_ids=question_ids,
        question_count=count,
        domain_index=domain_index,
        confidence=coverage_average,
        quantity_factor=quantity_factor,
        coverage_average=coverage_average,
        confidence_hierarchical=confidence_hierarchical,
        state_code="NO_DATA" if not count else "PROVISIONAL" if count <= 2 else "CALCULATED",
    )


def _domain_band(value: Fraction | None) -> DomainBand | None:
    if value is None:
        return None
    if value < 40:
        return DomainBand.FRAGILE
    if value < 60:
        return DomainBand.IN_DEVELOPMENT
    if value < 75:
        return DomainBand.INTERMEDIATE
    if value < 90:
        return DomainBand.GOOD
    return DomainBand.STRONG


def _mastery_state(
    *, attempts: Sequence[AttemptEvidence], vector: KnownDomainVector, active_overdue: bool
) -> MasteryState:
    errors = tuple(index for index, attempt in enumerate(attempts) if not attempt.is_correct)
    last_error = errors[-1] if errors else -1
    has_correct_d30_after_error = any(
        attempt.attempt_kind == AttemptKind.REVIEW
        and attempt.review_stage == ReviewStage.D30
        and attempt.is_correct
        for attempt in attempts[last_error + 1 :]
    )
    reviews = tuple(attempt for attempt in attempts if attempt.attempt_kind == AttemptKind.REVIEW)
    last_two_correct = len(reviews) >= 2 and all(item.is_correct for item in reviews[-2:])
    index_exact = vector.domain_index_exact or _fraction(vector.domain_index)
    confidence = vector.confidence
    dominated = (
        has_correct_d30_after_error
        and index_exact is not None
        and index_exact >= 85
        and confidence is not None
        and confidence >= 80
        and last_two_correct
        and not active_overdue
    )
    return MasteryState.DOMINATED if dominated else MasteryState.NOT_DOMINATED
