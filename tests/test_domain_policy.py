import uuid
from datetime import UTC, date, datetime
from decimal import Decimal, localcontext

import pytest

from modules.domain.policy import (
    AttemptEvidence,
    AttemptKind,
    DomainInput,
    DomainMaturity,
    EvidenceSufficiency,
    ExcludedEvidence,
    MasteryState,
    PerceivedEase,
    ReviewStage,
    aggregate_hierarchy,
    calculate_aq,
    calculate_confidence_age_factor,
    calculate_confidence_base,
    calculate_eq,
    calculate_fq,
    calculate_known_vector,
    calculate_pq,
    evaluate_domain,
)


def _attempt(
    evidence_id: str,
    day: int,
    *,
    correct: bool,
    kind: AttemptKind = AttemptKind.INITIAL,
    stage: ReviewStage | None = None,
    ease: PerceivedEase | None = None,
    cycle_id: str | None = None,
) -> AttemptEvidence:
    local_date = date(2026, 9, day)
    return AttemptEvidence(
        evidence_id=evidence_id,
        occurred_at=datetime(2026, 9, day, 12, tzinfo=UTC),
        local_date=local_date,
        is_correct=correct,
        attempt_kind=kind,
        review_stage=stage,
        perceived_ease=ease,
        review_cycle_id=(cycle_id or "cycle") if kind == AttemptKind.REVIEW else None,
    )


def test_aq_uses_at_most_five_attempts_with_recent_weight_one() -> None:
    attempts = tuple(_attempt(str(index), index, correct=index >= 2) for index in range(1, 8))

    result = calculate_aq(attempts)

    assert result.evidence_ids == ("3", "4", "5", "6", "7")
    assert result.value == Decimal("100")
    assert result.reason_code == "WEIGHTED_RECENT_ACCURACY"


def test_pq_uses_highest_correct_stage_after_last_error() -> None:
    attempts = (
        _attempt("initial", 1, correct=False),
        _attempt("d1", 2, correct=True, kind=AttemptKind.REVIEW, stage=ReviewStage.D1),
        _attempt("d7", 3, correct=True, kind=AttemptKind.REVIEW, stage=ReviewStage.D7),
        _attempt("error", 4, correct=False, kind=AttemptKind.REVIEW, stage=ReviewStage.D14),
        _attempt("d1-again", 5, correct=True, kind=AttemptKind.REVIEW, stage=ReviewStage.D1),
    )

    result = calculate_pq(attempts)

    assert result.value == Decimal("25")
    assert result.evidence_ids == ("d1-again",)


def test_fq_uses_three_latest_correct_review_ease_values_only() -> None:
    attempts = (
        _attempt("initial", 1, correct=True),
        _attempt(
            "easy",
            2,
            correct=True,
            kind=AttemptKind.REVIEW,
            stage=ReviewStage.D1,
            ease=PerceivedEase.EASY,
        ),
        _attempt(
            "wrong",
            3,
            correct=False,
            kind=AttemptKind.REVIEW,
            stage=ReviewStage.D7,
            ease=PerceivedEase.HARD,
        ),
        _attempt(
            "medium",
            4,
            correct=True,
            kind=AttemptKind.REVIEW,
            stage=ReviewStage.D14,
            ease=PerceivedEase.MEDIUM,
        ),
        _attempt(
            "hard",
            5,
            correct=True,
            kind=AttemptKind.REVIEW,
            stage=ReviewStage.D30,
            ease=PerceivedEase.HARD,
        ),
        _attempt(
            "newest",
            6,
            correct=True,
            kind=AttemptKind.REVIEW,
            stage=ReviewStage.D30,
            ease=PerceivedEase.EASY,
        ),
    )

    result = calculate_fq(attempts)

    assert result.evidence_ids == ("medium", "hard", "newest")
    assert result.value == Decimal("75")


def test_fq_uses_normative_neutral_value_when_no_ease_is_recorded() -> None:
    result = calculate_fq((_attempt("initial", 1, correct=True),))

    assert result.value == Decimal("75")
    assert result.evidence_ids == ()
    assert result.reason_code == "NEUTRAL_EASE_WHEN_UNRECORDED"


@pytest.mark.parametrize(
    ("count", "expected"),
    ((0, Decimal("100")), (1, Decimal("50")), (2, Decimal("0")), (4, Decimal("0"))),
)
def test_eq_applies_explicit_current_cycle_error_count(count: int, expected: Decimal) -> None:
    attempts = (
        _attempt("initial", 1, correct=True),
        *(
            _attempt(
                f"review-{index}",
                index + 1,
                correct=index > count,
                kind=AttemptKind.REVIEW,
                stage=ReviewStage.D1,
            )
            for index in range(1, 5)
        ),
    )

    assert calculate_eq(attempts, current_cycle_review_errors=count).value == expected


def test_eq_does_not_infer_unresolved_current_cycle() -> None:
    attempts = (
        _attempt("initial", 1, correct=True),
        _attempt("d1", 2, correct=True, kind=AttemptKind.REVIEW, stage=ReviewStage.D1),
    )

    result = calculate_eq(attempts, current_cycle_review_errors=None)

    assert result.value is None
    assert result.reason_code == "CURRENT_REVIEW_CYCLE_UNRESOLVED"


@pytest.mark.parametrize(
    ("age", "factor"),
    (
        (0, "1.00"),
        (60, "1.00"),
        (61, "0.90"),
        (120, "0.90"),
        (121, "0.75"),
        (180, "0.75"),
        (181, "0.50"),
        (365, "0.50"),
        (366, "0.25"),
    ),
)
def test_confidence_age_factor_boundaries(age: int, factor: str) -> None:
    last_attempt_date = date(2025, 9, 1)
    evaluated_on = date.fromordinal(last_attempt_date.toordinal() + age)

    assert calculate_confidence_age_factor(
        last_attempt_date=last_attempt_date,
        evaluated_on=evaluated_on,
    ) == Decimal(factor)


def test_known_vector_keeps_score_confidence_and_sufficiency_separate() -> None:
    attempts = (
        _attempt("initial-error", 1, correct=False),
        _attempt(
            "d1-correct-1",
            2,
            correct=True,
            kind=AttemptKind.REVIEW,
            stage=ReviewStage.D1,
            ease=PerceivedEase.EASY,
        ),
        _attempt(
            "d1-correct-2",
            3,
            correct=True,
            kind=AttemptKind.REVIEW,
            stage=ReviewStage.D1,
            ease=PerceivedEase.EASY,
        ),
        _attempt(
            "d1-correct-3",
            4,
            correct=True,
            kind=AttemptKind.REVIEW,
            stage=ReviewStage.D1,
            ease=PerceivedEase.EASY,
        ),
        _attempt(
            "d1-correct-4",
            5,
            correct=True,
            kind=AttemptKind.REVIEW,
            stage=ReviewStage.D1,
            ease=PerceivedEase.EASY,
        ),
        _attempt(
            "d1-correct-5",
            6,
            correct=True,
            kind=AttemptKind.REVIEW,
            stage=ReviewStage.D1,
            ease=PerceivedEase.EASY,
        ),
    )

    result = calculate_known_vector(
        attempts,
        evaluated_on=date(2026, 9, 6),
        current_cycle_review_errors=0,
        confidence_base=Decimal("40"),
    )

    assert result.domain_index == Decimal("60")
    assert result.confidence == Decimal("40.00")
    assert result.sufficiency_code == "TO_BE_EVALUATED"
    assert result.recovery_cap == Decimal("60")


def test_empty_input_is_no_data_not_zero_domain() -> None:
    result = calculate_known_vector((), evaluated_on=date(2026, 9, 24))

    assert result.domain_index is None
    assert result.confidence is None
    assert result.sufficiency_code == "NO_DATA"
    assert result.aq.reason_code == "NO_ELIGIBLE_ATTEMPTS"


def test_known_arithmetic_is_stable_when_callers_decimal_context_differs() -> None:
    attempts = (
        _attempt("initial", 1, correct=False),
        _attempt("d1", 2, correct=True, kind=AttemptKind.REVIEW, stage=ReviewStage.D1),
    )
    baseline = calculate_known_vector(
        attempts,
        evaluated_on=date(2026, 9, 2),
        current_cycle_review_errors=0,
        confidence_base=Decimal("40"),
    )
    with localcontext() as context:
        context.prec = 3
        altered_context = calculate_known_vector(
            attempts,
            evaluated_on=date(2026, 9, 2),
            current_cycle_review_errors=0,
            confidence_base=Decimal("40"),
        )

    assert altered_context == baseline

    five = tuple(_attempt(str(index), index, correct=index in {1, 4, 5}) for index in range(1, 6))
    baseline_aq = calculate_aq(five)
    with localcontext() as context:
        context.prec = 3
        altered_aq = calculate_aq(five)
    assert altered_aq == baseline_aq


def test_duplicate_evidence_id_is_rejected_to_prevent_double_counting() -> None:
    attempt = _attempt("same", 1, correct=True)

    with pytest.raises(ValueError, match="único"):
        calculate_aq((attempt, attempt))


def test_future_evaluation_date_is_rejected() -> None:
    with pytest.raises(ValueError, match="anteceder"):
        calculate_confidence_age_factor(
            last_attempt_date=date(2026, 9, 2), evaluated_on=date(2026, 9, 1)
        )


def test_confidence_base_resets_at_latest_error_and_tracks_attempted_stage() -> None:
    attempts = (
        _attempt("initial", 1, correct=False),
        _attempt("d1", 2, correct=True, kind=AttemptKind.REVIEW, stage=ReviewStage.D1),
        _attempt("d7", 3, correct=True, kind=AttemptKind.REVIEW, stage=ReviewStage.D7),
        _attempt("error", 4, correct=False, kind=AttemptKind.REVIEW, stage=ReviewStage.D14),
        _attempt("new-d1", 5, correct=True, kind=AttemptKind.REVIEW, stage=ReviewStage.D1),
    )

    assert calculate_confidence_base(attempts) == Decimal("40")


def test_question_sufficiency_is_structural_and_independent_of_confidence() -> None:
    question_id = uuid.uuid4()
    initial = _attempt("initial", 1, correct=True)
    provisional = evaluate_domain(
        DomainInput(question_id, (initial,), date(2026, 9, 1), None, False)
    )
    established = evaluate_domain(
        DomainInput(
            question_id,
            (
                initial,
                _attempt("review", 2, correct=False, kind=AttemptKind.REVIEW, stage=ReviewStage.D1),
            ),
            date(2026, 9, 2),
            "cycle",
            False,
        )
    )

    assert provisional.domain_index is not None
    assert provisional.confidence == Decimal("20.00")
    assert provisional.sufficiency == EvidenceSufficiency.INSUFFICIENT
    assert provisional.maturity == DomainMaturity.PROVISIONAL
    assert established.sufficiency == EvidenceSufficiency.SUFFICIENT
    assert established.maturity == DomainMaturity.ESTABLISHED
    assert established.confidence == Decimal("20.00")


def test_eq_counts_errors_only_in_selected_effective_cycle() -> None:
    attempts = (
        _attempt("initial", 1, correct=False),
        _attempt(
            "old-error",
            2,
            correct=False,
            kind=AttemptKind.REVIEW,
            stage=ReviewStage.D1,
            cycle_id="old",
        ),
        _attempt(
            "new-correct",
            3,
            correct=True,
            kind=AttemptKind.REVIEW,
            stage=ReviewStage.D1,
            cycle_id="new",
        ),
    )

    result = evaluate_domain(DomainInput(uuid.uuid4(), attempts, date(2026, 9, 3), "new", False))

    assert result.vector.eq.value == Decimal("100")
    assert result.vector.eq.evidence_ids == ("new-correct",)
    assert result.excluded_evidence == (
        ExcludedEvidence("old-error", "NOT_EFFECTIVE_CYCLE_FOR_EQ"),
    )


def test_zero_attempts_is_no_data_and_not_dominated() -> None:
    result = evaluate_domain(DomainInput(uuid.uuid4(), (), date(2026, 9, 24), None, False))

    assert result.sufficiency == EvidenceSufficiency.NO_DATA
    assert result.domain_index is None
    assert result.mastery == MasteryState.NOT_DOMINATED


def test_hierarchy_aggregation_uses_each_question_once_and_keeps_c_h_separate() -> None:
    results = tuple(
        evaluate_domain(
            DomainInput(
                uuid.uuid4(),
                (_attempt(f"initial-{index}", 1, correct=True),),
                date(2026, 9, 1),
                None,
                False,
            )
        )
        for index in range(3)
    )

    aggregate = aggregate_hierarchy(results)

    assert aggregate.question_count == 3
    assert aggregate.quantity_factor == Decimal("40")
    assert aggregate.confidence == Decimal("20.00")
    assert aggregate.confidence_hierarchical == Decimal("32.0000")
    assert aggregate.state_code == "CALCULATED"


def test_hierarchy_aggregation_rejects_duplicate_questions() -> None:
    question_id = uuid.uuid4()
    result = evaluate_domain(
        DomainInput(
            question_id,
            (_attempt("initial", 1, correct=True),),
            date(2026, 9, 1),
            None,
            False,
        )
    )

    with pytest.raises(ValueError, match="uma vez"):
        aggregate_hierarchy((result, result))


def test_hierarchy_does_not_treat_missing_question_confidence_as_zero_or_drop_it() -> None:
    initial = evaluate_domain(
        DomainInput(
            uuid.uuid4(),
            (_attempt("initial", 1, correct=True),),
            date(2026, 9, 1),
            None,
            False,
        )
    )
    review_only = evaluate_domain(
        DomainInput(
            uuid.uuid4(),
            (
                _attempt(
                    "review-only",
                    2,
                    correct=True,
                    kind=AttemptKind.REVIEW,
                    stage=ReviewStage.D1,
                ),
            ),
            date(2026, 9, 2),
            "cycle",
            False,
        )
    )

    aggregate = aggregate_hierarchy((initial, review_only))

    assert aggregate.domain_index is not None
    assert aggregate.question_count == 2
    assert aggregate.coverage_average is None
    assert aggregate.confidence_hierarchical is None
    assert aggregate.state_code == "PROVISIONAL"
