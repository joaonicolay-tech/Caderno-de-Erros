"""Executor reproduzível do benchmark BCR-1/CT-107.

O módulo não faz parte do produto: ele prepara um banco SQLite descartável e
mede os comandos transacionais já existentes.  A preparação deliberadamente
fica fora da região cronometrada; somente a confirmação persistente de cada
operação é medida.
"""

from __future__ import annotations

import hashlib
import math
import time
import uuid
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime, timedelta
from typing import Any

from django.db import transaction

from modules.attempts.context import ContextStore
from modules.attempts.models import Attempt, AttemptStatus, AttemptType
from modules.attempts.services import AttemptService
from modules.questions.models import Alternative, Question, QuestionRevision, QuestionStatus
from modules.questions.services import create_active
from modules.reviews.models import Review, ReviewCycle, ReviewCycleState, ReviewState
from modules.reviews.services import CompleteReviewService
from modules.taxonomy.models import Discipline, Subject, Subsubject, TaxonomyStatus
from shared.application.bootstrap import bootstrap_local_workspace
from shared.domain.time import FixedClock, Instant

BCR1_SEED = 20_260_909
BCR1_LIMIT_SECONDS = 2.0
BCR1_WARMUPS = 20
BCR1_SAMPLES = 100
BCR1_REPETITIONS = 3
_NAMESPACE = uuid.UUID("a6da1d09-8554-48bd-8af1-4b2a8e5bb970")
_FIXED_NOW = datetime(2026, 9, 9, 15, tzinfo=UTC)
_HISTORY_START = date(2016, 9, 9)


@dataclass(frozen=True, slots=True)
class Bcr1DatasetConfig:
    """Composição autorizada do baseline sintético, sem dados pessoais."""

    seed: int = BCR1_SEED
    question_count: int = 10_000
    attempt_count: int = 100_000
    review_count: int = 100_000
    taxonomy_per_level: int = 200
    history_years: int = 10

    def validate(self) -> None:
        if self.question_count < 3 or self.question_count % 5:
            raise ValueError("BCR-1 exige quantidade de questões múltipla de cinco.")
        if self.review_count < self.question_count:
            raise ValueError("BCR-1 exige ao menos uma Review por questão ativa.")
        active_questions = self.active_question_count
        if self.attempt_count != active_questions + self.review_count - active_questions:
            raise ValueError("As contagens BCR-1 não permitem fatos de tentativa consistentes.")

    @property
    def active_question_count(self) -> int:
        return self.question_count * 4 // 5


DEFAULT_DATASET = Bcr1DatasetConfig()


@dataclass(frozen=True, slots=True)
class DatasetManifest:
    seed: int
    question_count: int
    attempt_count: int
    review_count: int
    taxonomy_per_level: int
    history_start: str
    history_end: str
    fingerprint: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class Sample:
    number: int
    seconds: float

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class OperationResult:
    operation: str
    warmups_excluded: int
    sample_count: int
    samples: tuple[Sample, ...]
    minimum_seconds: float
    median_seconds: float
    p95_seconds: float
    maximum_seconds: float
    limit_seconds: float
    status: str

    def as_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["samples"] = [sample.as_dict() for sample in self.samples]
        return result


@dataclass(frozen=True, slots=True)
class RunResult:
    run_number: int
    dataset: DatasetManifest
    operations: tuple[OperationResult, ...]
    status: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "run_number": self.run_number,
            "dataset": self.dataset.as_dict(),
            "operations": [operation.as_dict() for operation in self.operations],
            "status": self.status,
        }


def nearest_rank_p95(samples: list[float] | tuple[float, ...]) -> float:
    """Calcule p95 pelo nearest-rank: posição ceil(0.95 * N), base um."""
    if not samples:
        raise ValueError("O cálculo de p95 exige pelo menos uma amostra.")
    ordered = sorted(samples)
    return ordered[math.ceil(0.95 * len(ordered)) - 1]


def ct107_status(runs: list[RunResult] | tuple[RunResult, ...]) -> str:
    """Aplique literalmente a regra: três execuções e toda operação aprovada."""
    if len(runs) != BCR1_REPETITIONS:
        return "FAIL"
    return "PASS" if all(run.status == "PASS" for run in runs) else "FAIL"


def build_dataset_manifest(config: Bcr1DatasetConfig = DEFAULT_DATASET) -> DatasetManifest:
    """Descreva deterministicamente o dataset antes de qualquer escrita."""
    config.validate()
    history_end = _HISTORY_START + timedelta(days=config.history_years * 365 - 1)
    payload = "|".join(
        [
            str(config.seed),
            str(config.question_count),
            str(config.attempt_count),
            str(config.review_count),
            str(config.taxonomy_per_level),
            _stable_id(config.seed, "question", config.question_count).__str__(),
            _stable_id(config.seed, "review", config.review_count).__str__(),
            _HISTORY_START.isoformat(),
            history_end.isoformat(),
        ]
    )
    return DatasetManifest(
        seed=config.seed,
        question_count=config.question_count,
        attempt_count=config.attempt_count,
        review_count=config.review_count,
        taxonomy_per_level=config.taxonomy_per_level,
        history_start=_HISTORY_START.isoformat(),
        history_end=history_end.isoformat(),
        fingerprint=hashlib.sha256(payload.encode()).hexdigest(),
    )


def measure_operation(
    *,
    name: str,
    prepare: Callable[[bool, int], Callable[[], object]],
    warmups: int = BCR1_WARMUPS,
    samples: int = BCR1_SAMPLES,
    limit_seconds: float = BCR1_LIMIT_SECONDS,
    clock_ns: Callable[[], int] = time.perf_counter_ns,
) -> OperationResult:
    """Faça warm-ups separados e mantenha cada amostra, inclusive as lentas."""
    if warmups < 0 or samples < 1:
        raise ValueError("Warm-ups devem ser não negativos e amostras devem ser positivas.")
    for index in range(warmups):
        prepare(True, index)()
    measurements: list[Sample] = []
    for index in range(samples):
        operation = prepare(False, index)
        started = clock_ns()
        operation()
        measurements.append(
            Sample(number=index + 1, seconds=(clock_ns() - started) / 1_000_000_000)
        )
    values = tuple(sample.seconds for sample in measurements)
    ordered = sorted(values)
    middle = len(ordered) // 2
    median = ordered[middle] if len(ordered) % 2 else (ordered[middle - 1] + ordered[middle]) / 2
    p95 = nearest_rank_p95(values)
    return OperationResult(
        operation=name,
        warmups_excluded=warmups,
        sample_count=samples,
        samples=tuple(measurements),
        minimum_seconds=ordered[0],
        median_seconds=median,
        p95_seconds=p95,
        maximum_seconds=ordered[-1],
        limit_seconds=limit_seconds,
        status="PASS" if p95 <= limit_seconds else "FAIL",
    )


def prepare_dataset(config: Bcr1DatasetConfig = DEFAULT_DATASET) -> DatasetManifest:
    """Popule a composição BCR-1 antes da medição usando dados sintéticos fixos."""
    manifest = build_dataset_manifest(config)
    workspace = bootstrap_local_workspace(timezone_id="America/Sao_Paulo").workspace
    with transaction.atomic():
        _create_taxonomy(workspace.id, config)
        _create_questions(workspace.id, config)
        _create_history(workspace.id, config)
    _assert_dataset_counts(workspace.id, config)
    return manifest


def _stable_id(seed: int, kind: str, index: int) -> uuid.UUID:
    return uuid.uuid5(_NAMESPACE, f"bcr1:{seed}:{kind}:{index}")


def _chunks[T](items: list[T], size: int = 500) -> list[list[T]]:
    return [items[start : start + size] for start in range(0, len(items), size)]


def _create_taxonomy(workspace_id: uuid.UUID, config: Bcr1DatasetConfig) -> None:
    disciplines = [
        Discipline(
            id=_stable_id(config.seed, "discipline", index),
            workspace_id=workspace_id,
            name=f"Disciplina sintética {index:03d}",
            name_key=f"disciplina sintetica {index:03d}",
            status=TaxonomyStatus.ACTIVE,
            sort_order=index,
        )
        for index in range(config.taxonomy_per_level)
    ]
    Discipline.objects.bulk_create(disciplines, batch_size=500)
    subjects = [
        Subject(
            id=_stable_id(config.seed, "subject", index),
            workspace_id=workspace_id,
            discipline_id=_stable_id(config.seed, "discipline", index),
            name=f"Assunto sintético {index:03d}",
            name_key=f"assunto sintetico {index:03d}",
            status=TaxonomyStatus.ACTIVE,
            sort_order=index,
        )
        for index in range(config.taxonomy_per_level)
    ]
    Subject.objects.bulk_create(subjects, batch_size=500)
    subsubjects = [
        Subsubject(
            id=_stable_id(config.seed, "subsubject", index),
            workspace_id=workspace_id,
            subject_id=_stable_id(config.seed, "subject", index),
            name=f"Subassunto sintético {index:03d}",
            name_key=f"subassunto sintetico {index:03d}",
            status=TaxonomyStatus.ACTIVE,
            sort_order=index,
        )
        for index in range(config.taxonomy_per_level)
    ]
    Subsubject.objects.bulk_create(subsubjects, batch_size=500)


def _create_questions(workspace_id: uuid.UUID, config: Bcr1DatasetConfig) -> None:
    active = config.active_question_count
    questions: list[Question] = []
    revisions: list[QuestionRevision] = []
    alternatives: list[Alternative] = []
    for index in range(config.question_count):
        taxonomy = index % config.taxonomy_per_level
        question_id = _stable_id(config.seed, "question", index)
        status = (
            QuestionStatus.ACTIVE
            if index < active
            else QuestionStatus.ARCHIVED
            if index < active + (config.question_count - active) // 2
            else QuestionStatus.DRAFT
        )
        questions.append(
            Question(
                id=question_id,
                workspace_id=workspace_id,
                discipline_id=_stable_id(config.seed, "discipline", taxonomy),
                subject_id=_stable_id(config.seed, "subject", taxonomy),
                subsubject_id=_stable_id(config.seed, "subsubject", taxonomy),
                status=status,
                activated_at=_FIXED_NOW if status != QuestionStatus.DRAFT else None,
                archived_at=_FIXED_NOW if status == QuestionStatus.ARCHIVED else None,
                draft_title=f"Questão sintética {index:05d}"
                if status == QuestionStatus.DRAFT
                else None,
            )
        )
        revision_id = _stable_id(config.seed, "revision", index)
        revisions.append(
            QuestionRevision(
                id=revision_id,
                workspace_id=workspace_id,
                question_id=question_id,
                version_number=1,
                is_current=True,
                stem=f"Enunciado sintético BCR-1 {index:05d}",
                explanation="Explicação sintética reservada.",
                change_kind="INITIAL",
                correct_alternative_id=_stable_id(config.seed, "alternative:2", index),
            )
        )
        for position, text in enumerate(("Alternativa incorreta", "Alternativa correta"), start=1):
            alternatives.append(
                Alternative(
                    id=_stable_id(config.seed, f"alternative:{position}", index),
                    workspace_id=workspace_id,
                    question_revision_id=revision_id,
                    position=position,
                    text=f"{text} {index:05d}",
                    text_key=f"{text.lower()} {index:05d}",
                )
            )
    for question_batch in _chunks(questions):
        Question.objects.bulk_create(question_batch, batch_size=500)
    for revision_batch in _chunks(revisions):
        QuestionRevision.objects.bulk_create(revision_batch, batch_size=500)
    for alternative_batch in _chunks(alternatives):
        Alternative.objects.bulk_create(alternative_batch, batch_size=500)


def _create_history(workspace_id: uuid.UUID, config: Bcr1DatasetConfig) -> None:
    active = config.active_question_count
    review_counts = [config.review_count // active] * active
    for index in range(config.review_count % active):
        review_counts[index] += 1
    initial_attempts: list[Attempt] = []
    cycles: list[ReviewCycle] = []
    for question_index in range(active):
        occurred = _history_instant(question_index, config)
        initial_id = _stable_id(config.seed, "initial-attempt", question_index)
        question_id = _stable_id(config.seed, "question", question_index)
        revision_id = _stable_id(config.seed, "revision", question_index)
        initial_attempts.append(
            Attempt(
                id=initial_id,
                workspace_id=workspace_id,
                question_id=question_id,
                question_revision_id=revision_id,
                attempt_type=AttemptType.INITIAL,
                selected_alternative_id=_stable_id(config.seed, "alternative:1", question_index),
                is_correct=False,
                occurred_at=occurred,
                timezone_name="America/Sao_Paulo",
                local_date=occurred.date(),
                status=AttemptStatus.VALID,
                idempotency_key=_stable_id(config.seed, "initial-key", question_index),
            )
        )
        cycles.append(
            ReviewCycle(
                id=_stable_id(config.seed, "cycle", question_index),
                workspace_id=workspace_id,
                question_id=question_id,
                origin_attempt_id=initial_id,
                state=ReviewCycleState.ACTIVE,
                started_at=occurred,
            )
        )
    for initial_attempt_batch in _chunks(initial_attempts):
        Attempt.objects.bulk_create(initial_attempt_batch, batch_size=500)
    for cycle_batch in _chunks(cycles):
        ReviewCycle.objects.bulk_create(cycle_batch, batch_size=500)
    prior_attempt_ids = [
        _stable_id(config.seed, "initial-attempt", index) for index in range(active)
    ]
    stages = ("D1", "D7", "D14", "D30")
    for sequence in range(1, max(review_counts) + 1):
        reviews: list[Review] = []
        completed_attempts: list[Attempt] = []
        for question_index, total in enumerate(review_counts):
            if sequence > total:
                continue
            due = _history_instant(question_index * 17 + sequence, config).date()
            review_id = _stable_id(config.seed, f"review:{sequence}", question_index)
            completed = sequence < total
            reviews.append(
                Review(
                    id=review_id,
                    workspace_id=workspace_id,
                    review_cycle_id=_stable_id(config.seed, "cycle", question_index),
                    question_id=_stable_id(config.seed, "question", question_index),
                    sequence_number=sequence,
                    stage_code=stages[(sequence - 1) % len(stages)],
                    state=ReviewState.COMPLETED if completed else ReviewState.PENDING,
                    first_due_date=due,
                    current_due_date=due,
                    scheduled_from_attempt_id=prior_attempt_ids[question_index],
                    transition_code="BCR1_BOOTSTRAP",
                    completed_at=_history_instant(question_index * 17 + sequence + 1, config)
                    if completed
                    else None,
                )
            )
            if completed:
                attempt_id = _stable_id(config.seed, f"review-attempt:{sequence}", question_index)
                completed_attempts.append(
                    Attempt(
                        id=attempt_id,
                        workspace_id=workspace_id,
                        question_id=_stable_id(config.seed, "question", question_index),
                        question_revision_id=_stable_id(config.seed, "revision", question_index),
                        review_id=review_id,
                        attempt_type=AttemptType.REVIEW,
                        selected_alternative_id=_stable_id(
                            config.seed, "alternative:2", question_index
                        ),
                        is_correct=True,
                        occurred_at=_history_instant(question_index * 17 + sequence + 1, config),
                        timezone_name="America/Sao_Paulo",
                        local_date=due,
                        status=AttemptStatus.VALID,
                        idempotency_key=_stable_id(
                            config.seed, f"review-key:{sequence}", question_index
                        ),
                    )
                )
                prior_attempt_ids[question_index] = attempt_id
        for review_batch in _chunks(reviews):
            Review.objects.bulk_create(review_batch, batch_size=500)
        for completed_attempt_batch in _chunks(completed_attempts):
            Attempt.objects.bulk_create(completed_attempt_batch, batch_size=500)


def _history_instant(index: int, config: Bcr1DatasetConfig) -> datetime:
    days = config.history_years * 365
    return datetime.combine(_HISTORY_START + timedelta(days=index % days), datetime.min.time(), UTC)


def _assert_dataset_counts(workspace_id: uuid.UUID, config: Bcr1DatasetConfig) -> None:
    actual = {
        "questions": Question.objects.filter(workspace_id=workspace_id).count(),
        "attempts": Attempt.objects.filter(workspace_id=workspace_id).count(),
        "reviews": Review.objects.filter(workspace_id=workspace_id).count(),
        "disciplines": Discipline.objects.filter(
            workspace_id=workspace_id, status="ACTIVE"
        ).count(),
        "subjects": Subject.objects.filter(workspace_id=workspace_id, status="ACTIVE").count(),
        "subsubjects": Subsubject.objects.filter(
            workspace_id=workspace_id, status="ACTIVE"
        ).count(),
    }
    expected = {
        "questions": config.question_count,
        "attempts": config.attempt_count,
        "reviews": config.review_count,
        "disciplines": config.taxonomy_per_level,
        "subjects": config.taxonomy_per_level,
        "subsubjects": config.taxonomy_per_level,
    }
    if actual != expected:
        raise RuntimeError(f"Dataset BCR-1 inconsistente: esperado={expected}, obtido={actual}")


def execute_run(
    *,
    run_number: int,
    dataset: Bcr1DatasetConfig = DEFAULT_DATASET,
    warmups: int = BCR1_WARMUPS,
    samples: int = BCR1_SAMPLES,
) -> RunResult:
    """Prepare um BCR-1 completo e execute as três escritas reais uma vez."""
    manifest = prepare_dataset(dataset)
    workspace = bootstrap_local_workspace(timezone_id="America/Sao_Paulo").workspace
    operations = (
        measure_operation(
            name="save_question",
            prepare=_question_operation(workspace.id),
            warmups=warmups,
            samples=samples,
        ),
        measure_operation(
            name="save_attempt",
            prepare=_attempt_operation(workspace),
            warmups=warmups,
            samples=samples,
        ),
        measure_operation(
            name="complete_review",
            prepare=_review_operation(workspace),
            warmups=warmups,
            samples=samples,
        ),
    )
    return RunResult(
        run_number=run_number,
        dataset=manifest,
        operations=operations,
        status="PASS" if all(operation.status == "PASS" for operation in operations) else "FAIL",
    )


def _question_operation(workspace_id: uuid.UUID) -> Callable[[bool, int], Callable[[], object]]:
    counter = 0
    discipline = Discipline.objects.filter(workspace_id=workspace_id, status="ACTIVE").first()
    if discipline is None:
        raise RuntimeError("BCR-1 exige Discipline ativa para salvar questão.")
    subject = Subject.objects.filter(
        workspace_id=workspace_id, discipline_id=discipline.id, status="ACTIVE"
    ).first()
    if subject is None:
        raise RuntimeError("BCR-1 exige Subject ativo da Discipline selecionada.")
    discipline_id = discipline.id
    subject_id = subject.id

    def prepare(warmup: bool, index: int) -> Callable[[], object]:
        nonlocal counter
        counter += 1
        suffix = f"{'warmup' if warmup else 'sample'}-{counter:04d}"
        return lambda: create_active(
            workspace_id=workspace_id,
            discipline_id=discipline_id,
            subject_id=subject_id,
            stem=f"Questão de medição BCR-1 {suffix}",
            alternatives=[f"Incorreta {suffix}", f"Correta {suffix}"],
            correct_alternative_position=2,
            explanation="Conteúdo sintético de benchmark.",
        )

    return prepare


def _attempt_operation(workspace: Any) -> Callable[[bool, int], Callable[[], object]]:
    counter = 0
    discipline = Discipline.objects.filter(workspace_id=workspace.id, status="ACTIVE").first()
    if discipline is None:
        raise RuntimeError("BCR-1 exige Discipline ativa para salvar tentativa.")
    subject = Subject.objects.filter(
        workspace_id=workspace.id, discipline_id=discipline.id, status="ACTIVE"
    ).first()
    if subject is None:
        raise RuntimeError("BCR-1 exige Subject ativo da Discipline selecionada.")
    discipline_id = discipline.id
    subject_id = subject.id

    def prepare(warmup: bool, index: int) -> Callable[[], object]:
        nonlocal counter
        counter += 1
        suffix = f"attempt-{'warmup' if warmup else 'sample'}-{counter:04d}"
        question = create_active(
            workspace_id=workspace.id,
            discipline_id=discipline_id,
            subject_id=subject_id,
            stem=f"Pré-condição BCR-1 {suffix}",
            alternatives=[f"Incorreta {suffix}", f"Correta {suffix}"],
            correct_alternative_position=2,
        )
        service = AttemptService(
            actor_id=workspace.owner_user_id,
            workspace_id=workspace.id,
            session=f"bcr1-attempt-{counter}",
            clock=FixedClock(Instant(_FIXED_NOW)),
            store=ContextStore(),
        )
        presented = service.presentation(question.id)
        token = service.evaluate(
            question_id=question.id,
            revision_id=presented["revision_id"],
            lock_version=presented["lock_version"],
            alternative_id=presented["alternatives"][1][0],
        )
        key = _stable_id(BCR1_SEED, "measured-attempt", counter)
        return lambda: service.confirm(token=token, key=key)

    return prepare


def _review_operation(workspace: Any) -> Callable[[bool, int], Callable[[], object]]:
    counter = 0
    discipline = Discipline.objects.filter(workspace_id=workspace.id, status="ACTIVE").first()
    if discipline is None:
        raise RuntimeError("BCR-1 exige Discipline ativa para concluir revisão.")
    subject = Subject.objects.filter(
        workspace_id=workspace.id, discipline_id=discipline.id, status="ACTIVE"
    ).first()
    if subject is None:
        raise RuntimeError("BCR-1 exige Subject ativo da Discipline selecionada.")
    discipline_id = discipline.id
    subject_id = subject.id
    category_id = workspace.error_categories.get(code="ATTENTION").id

    def prepare(warmup: bool, index: int) -> Callable[[], object]:
        nonlocal counter
        counter += 1
        suffix = f"review-{'warmup' if warmup else 'sample'}-{counter:04d}"
        clock = FixedClock(Instant(_FIXED_NOW))
        store = ContextStore()
        question = create_active(
            workspace_id=workspace.id,
            discipline_id=discipline_id,
            subject_id=subject_id,
            stem=f"Pré-condição de revisão BCR-1 {suffix}",
            alternatives=[f"Incorreta {suffix}", f"Correta {suffix}"],
            correct_alternative_position=2,
        )
        initial = AttemptService(
            actor_id=workspace.owner_user_id,
            workspace_id=workspace.id,
            session=f"bcr1-review-{counter}",
            clock=clock,
            store=store,
        )
        shown = initial.presentation(question.id)
        token = initial.evaluate(
            question_id=question.id,
            revision_id=shown["revision_id"],
            lock_version=shown["lock_version"],
            alternative_id=shown["alternatives"][0][0],
        )
        initial.confirm(
            token=token,
            key=_stable_id(BCR1_SEED, "review-initial", counter),
            category_id=category_id,
        )
        clock.set(Instant(_FIXED_NOW + timedelta(days=1)))
        service = CompleteReviewService(
            actor_id=workspace.owner_user_id,
            workspace_id=workspace.id,
            session=f"bcr1-review-{counter}",
            clock=clock,
            store=store,
        )
        review = Review.objects.filter(question_id=question.id, state=ReviewState.PENDING).get()
        presented = service.presentation(review.id)
        review_token = service.evaluate(
            review_id=review.id,
            revision_id=presented["revision_id"],
            lock_version=presented["lock_version"],
            review_lock_version=presented["review_lock_version"],
            alternative_id=presented["alternatives"][1][0],
        )
        key = _stable_id(BCR1_SEED, "measured-review", counter)
        return lambda: service.complete_review(token=review_token, key=key, perceived_ease="EASY")

    return prepare
