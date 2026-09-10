"""Contrato do executor BCR-1/CT-107, sem rodar a carga completa no pytest."""

from __future__ import annotations

import pytest

from modules.attempts.models import Attempt
from modules.questions.models import Question
from modules.reviews.models import Review
from shared.application.bcr1 import (
    BCR1_REPETITIONS,
    Bcr1DatasetConfig,
    DatasetManifest,
    OperationResult,
    RunResult,
    Sample,
    build_dataset_manifest,
    ct107_status,
    execute_run,
    measure_operation,
    nearest_rank_p95,
    prepare_dataset,
)


def test_dataset_manifest_is_deterministic_for_fixed_seed() -> None:
    config = Bcr1DatasetConfig(
        seed=1234,
        question_count=10,
        attempt_count=100,
        review_count=100,
        taxonomy_per_level=2,
    )
    first = build_dataset_manifest(config)
    second = build_dataset_manifest(config)
    changed = build_dataset_manifest(
        Bcr1DatasetConfig(
            seed=1235,
            question_count=10,
            attempt_count=100,
            review_count=100,
            taxonomy_per_level=2,
        )
    )
    assert first == second
    assert first.fingerprint != changed.fingerprint
    assert first.history_start == "2016-09-09"
    assert first.history_end == "2026-09-06"


def test_nearest_rank_p95_uses_ceil_position() -> None:
    assert nearest_rank_p95(list(range(1, 101))) == 95
    assert nearest_rank_p95([1.0] * 94 + [3.0] * 6) == 3.0


def test_warmups_are_excluded_and_one_hundred_samples_are_recorded() -> None:
    calls: list[tuple[bool, int]] = []
    timestamps = iter(range(0, 240_000_000, 1_000_000))

    def prepare(warmup: bool, index: int):  # type: ignore[no-untyped-def]
        def operation() -> None:
            calls.append((warmup, index))

        return operation

    result = measure_operation(
        name="write",
        prepare=prepare,
        warmups=20,
        samples=100,
        clock_ns=lambda: next(timestamps),
    )
    assert calls[:20] == [(True, index) for index in range(20)]
    assert calls[20:] == [(False, index) for index in range(100)]
    assert result.warmups_excluded == 20
    assert result.sample_count == 100
    assert len(result.samples) == 100
    assert result.samples[0].number == 1


def test_measurement_fails_without_removing_slow_samples() -> None:
    timestamps = iter([0, 3_000_000_000] * 100)
    result = measure_operation(
        name="write",
        prepare=lambda _warmup, _index: lambda: None,
        warmups=0,
        samples=100,
        clock_ns=lambda: next(timestamps),
    )
    assert result.p95_seconds == 3.0
    assert result.maximum_seconds == 3.0
    assert result.status == "FAIL"
    assert len(result.samples) == 100


def _run(number: int, status: str) -> RunResult:
    operation = OperationResult(
        operation="write",
        warmups_excluded=20,
        sample_count=100,
        samples=(Sample(1, 0.01),),
        minimum_seconds=0.01,
        median_seconds=0.01,
        p95_seconds=0.01,
        maximum_seconds=0.01,
        limit_seconds=2.0,
        status=status,
    )
    return RunResult(
        run_number=number,
        dataset=DatasetManifest(1, 1, 1, 1, 1, "a", "b", "c"),
        operations=(operation,),
        status=status,
    )


def test_ct107_requires_exactly_three_passing_repetitions() -> None:
    passing = tuple(_run(index, "PASS") for index in range(1, BCR1_REPETITIONS + 1))
    assert ct107_status(passing) == "PASS"
    assert ct107_status(passing[:2]) == "FAIL"
    assert ct107_status((*passing[:2], _run(3, "FAIL"))) == "FAIL"


@pytest.mark.django_db
def test_reduced_dataset_uses_real_sqlite_and_matches_its_manifest_counts() -> None:
    config = Bcr1DatasetConfig(
        question_count=10,
        attempt_count=100,
        review_count=100,
        taxonomy_per_level=2,
    )
    manifest = prepare_dataset(config)
    assert manifest.question_count == Question.objects.count() == 10
    assert manifest.attempt_count == Attempt.objects.count() == 100
    assert manifest.review_count == Review.objects.count() == 100


@pytest.mark.django_db
def test_reduced_run_uses_the_three_real_persistent_operations() -> None:
    result = execute_run(
        run_number=1,
        dataset=Bcr1DatasetConfig(
            question_count=10,
            attempt_count=100,
            review_count=100,
            taxonomy_per_level=2,
        ),
        warmups=0,
        samples=1,
    )
    assert [operation.operation for operation in result.operations] == [
        "save_question",
        "save_attempt",
        "complete_review",
    ]
    assert all(operation.sample_count == 1 for operation in result.operations)
