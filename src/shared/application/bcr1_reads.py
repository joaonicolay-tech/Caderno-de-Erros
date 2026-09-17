"""Leituras V0.4 reproduzíveis sobre o dataset BCR-1 descartável."""

from __future__ import annotations

import hashlib
import math
import time
import uuid
from collections.abc import Callable
from dataclasses import asdict, dataclass, replace
from statistics import median
from typing import Any

from django.db import connection
from django.test import Client
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from modules.accounts.models import User, Workspace
from modules.analytics.services import AnalyticsService
from modules.questions.models import Question, QuestionStatus
from modules.questions.services import create_active
from modules.reviews.selectors import list_review_queue
from modules.search.selectors import PAGE_SIZE, list_questions, paginate_questions
from modules.taxonomy.services import create_discipline, create_subject

READ_WARMUPS = 5
READ_SAMPLES = 20
SCREEN_LIMIT_SECONDS = 3.0
QUERY_LIMIT_SECONDS = 2.0


def _evidence_digest(payload: str) -> str:
    """Preserve o SHA-256 completo sem parecer uma credencial hexadecimal."""
    digest = hashlib.sha256(payload.encode()).hexdigest()
    return ":".join(digest[index : index + 8] for index in range(0, len(digest), 8))


@dataclass(frozen=True, slots=True)
class ReadSample:
    number: int
    seconds: float
    query_count: int

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ReadOperationResult:
    operation: str
    requirement: str
    warmups_excluded: int
    sample_count: int
    cold_seconds: float
    cold_query_count: int
    samples: tuple[ReadSample, ...]
    minimum_seconds: float
    median_seconds: float
    p95_seconds: float
    maximum_seconds: float
    query_count_minimum: int
    query_count_maximum: int
    limit_seconds: float | None
    status: str

    def as_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["samples"] = [sample.as_dict() for sample in self.samples]
        return result


@dataclass(frozen=True, slots=True)
class PaginationValidation:
    expected_items: int
    observed_items: int
    unique_items: int
    page_size: int
    page_count: int
    query_count: int
    seconds: float
    ordered_ids_fingerprint: str
    status: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ReadBenchmarkResult:
    operations: tuple[ReadOperationResult, ...]
    pagination: PaginationValidation
    reconciliation: dict[str, int | bool]
    status: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "operations": [operation.as_dict() for operation in self.operations],
            "pagination": self.pagination.as_dict(),
            "reconciliation": self.reconciliation,
            "status": self.status,
        }


def _nearest_rank_p95(values: list[float]) -> float:
    ordered = sorted(values)
    return ordered[math.ceil(0.95 * len(ordered)) - 1]


def measure_read_operation(
    *,
    name: str,
    requirement: str,
    prepare: Callable[[bool, int], Callable[[], Any]],
    validate: Callable[[Any], None],
    warmups: int = READ_WARMUPS,
    samples: int = READ_SAMPLES,
    limit_seconds: float | None,
    clock_ns: Callable[[], int] = time.perf_counter_ns,
) -> ReadOperationResult:
    """Meça primeira leitura e amostras aquecidas, preservando queries por amostra."""
    if warmups < 0 or samples < 1:
        raise ValueError("Warm-ups devem ser não negativos e amostras devem ser positivas.")

    cold_operation = prepare(False, -1)
    with CaptureQueriesContext(connection) as cold_queries:
        started = clock_ns()
        cold_value = cold_operation()
        cold_seconds = (clock_ns() - started) / 1_000_000_000
    validate(cold_value)

    for index in range(warmups):
        validate(prepare(True, index)())

    measurements: list[ReadSample] = []
    for index in range(samples):
        operation = prepare(False, index)
        with CaptureQueriesContext(connection) as queries:
            started = clock_ns()
            value = operation()
            elapsed = (clock_ns() - started) / 1_000_000_000
        validate(value)
        measurements.append(ReadSample(index + 1, elapsed, len(queries)))

    values = [sample.seconds for sample in measurements]
    query_counts = [sample.query_count for sample in measurements]
    p95 = _nearest_rank_p95(values)
    return ReadOperationResult(
        operation=name,
        requirement=requirement,
        warmups_excluded=warmups,
        sample_count=samples,
        cold_seconds=cold_seconds,
        cold_query_count=len(cold_queries),
        samples=tuple(measurements),
        minimum_seconds=min(values),
        median_seconds=median(values),
        p95_seconds=p95,
        maximum_seconds=max(values),
        query_count_minimum=min(query_counts),
        query_count_maximum=max(query_counts),
        limit_seconds=limit_seconds,
        status=(
            "OBSERVED" if limit_seconds is None else "PASS" if p95 <= limit_seconds else "FAIL"
        ),
    )


def _http_validator(*, includes: str, excludes: str = "") -> Callable[[Any], None]:
    def validate(response: Any) -> None:
        if response.status_code != 200:
            raise RuntimeError(f"Leitura HTTP retornou {response.status_code}.")
        html = response.content.decode("utf-8")
        if includes not in html or (excludes and excludes in html):
            raise RuntimeError("Leitura HTTP divergiu da reconciliação esperada.")

    return validate


def _validate_pagination(*, workspace_id: uuid.UUID, expected_items: int) -> PaginationValidation:
    questions = list_questions(workspace_id=workspace_id, status=QuestionStatus.ACTIVE)
    observed: list[uuid.UUID] = []
    started = time.perf_counter_ns()
    with CaptureQueriesContext(connection) as queries:
        paginator = paginate_questions(questions=questions, requested_page="1").page.paginator
        for page_number in range(1, paginator.num_pages + 1):
            page = paginate_questions(questions=questions, requested_page=str(page_number)).page
            observed.extend(item.question.id for item in page.object_list)
    seconds = (time.perf_counter_ns() - started) / 1_000_000_000
    fingerprint = _evidence_digest("|".join(str(item) for item in observed))
    unique = len(set(observed))
    status = "PASS" if len(observed) == unique == expected_items else "FAIL"
    return PaginationValidation(
        expected_items=expected_items,
        observed_items=len(observed),
        unique_items=unique,
        page_size=PAGE_SIZE,
        page_count=paginator.num_pages,
        query_count=len(queries),
        seconds=seconds,
        ordered_ids_fingerprint=fingerprint,
        status=status,
    )


def execute_read_benchmark(
    *,
    workspace_id: uuid.UUID,
    expected_questions: int,
    expected_attempts: int,
    warmups: int = READ_WARMUPS,
    samples: int = READ_SAMPLES,
) -> ReadBenchmarkResult:
    """Exercite telas, serviços, filtros e paginação V0.4 no BCR-1 real."""
    client = Client(HTTP_HOST="127.0.0.1")
    service = AnalyticsService(workspace_id=workspace_id)
    activity = service.activity()
    queue = list_review_queue(workspace_id=workspace_id)
    active_questions = Question.objects.filter(
        workspace_id=workspace_id, status=QuestionStatus.ACTIVE
    ).count()
    if (
        activity.registered_questions != expected_questions
        or activity.attempts != expected_attempts
    ):
        raise RuntimeError("Dashboard não reconciliou com o manifesto BCR-1.")
    if queue.overdue.total + queue.due.total + queue.future.total != active_questions:
        raise RuntimeError("Fila de revisão não reconciliou com as questões ativas.")

    target = (
        Question.objects.filter(workspace_id=workspace_id, status=QuestionStatus.ACTIVE)
        .select_related("discipline")
        .order_by("id")
        .first()
    )
    if target is None or target.discipline_id is None:
        raise RuntimeError("BCR-1 não forneceu questão ativa para as leituras.")
    target_revision = target.revisions.get(is_current=True)
    target_stem = target_revision.stem or ""
    if not target_stem:
        raise RuntimeError("BCR-1 não forneceu enunciado para as leituras.")
    target_token = target_stem.rsplit(" ", 1)[-1]
    discipline_total = Question.objects.filter(
        workspace_id=workspace_id,
        status=QuestionStatus.ACTIVE,
        discipline_id=target.discipline_id,
    ).count()

    foreign_user = User.objects.create_user(email=f"bcr1-foreign-{uuid.uuid4().hex}@example.test")
    foreign_workspace = Workspace.objects.create(
        owner_user=foreign_user,
        name="BCR-1 foreign workspace",
        timezone_name="America/Sao_Paulo",
    )
    foreign_discipline = create_discipline(workspace_id=foreign_workspace.id, name="Foreign")
    foreign_subject = create_subject(
        workspace_id=foreign_workspace.id,
        discipline_id=foreign_discipline.id,
        name="Foreign subject",
    )
    foreign_question = create_active(
        workspace_id=foreign_workspace.id,
        discipline_id=foreign_discipline.id,
        subject_id=foreign_subject.id,
        stem=target_stem,
        alternatives=["Incorreta", "Correta"],
        correct_alternative_position=2,
    )

    def get(path: str, data: dict[str, str] | None = None) -> Callable[[], Any]:
        return lambda: client.get(path, data or {})

    operations = [
        measure_read_operation(
            name="dashboard",
            requirement="CT-105 / RNF-001",
            prepare=lambda _warmup, _index: get(reverse("accounts:home")),
            validate=_http_validator(includes="Questões cadastradas"),
            warmups=warmups,
            samples=samples,
            limit_seconds=SCREEN_LIMIT_SECONDS,
        ),
        measure_read_operation(
            name="analytics_summary",
            requirement="V0.4-S2 observed read",
            prepare=lambda _warmup, _index: (
                lambda: (
                    service.activity(),
                    service.reviews(),
                    service.performance_pair(),
                    service.error_categories(),
                )
            ),
            validate=lambda value: (
                None
                if value[0].registered_questions == expected_questions
                else (_ for _ in ()).throw(RuntimeError("Analytics divergiu do BCR-1."))
            ),
            warmups=warmups,
            samples=samples,
            limit_seconds=None,
        ),
        measure_read_operation(
            name="review_queue",
            requirement="CT-105 / RNF-001",
            prepare=lambda _warmup, _index: get(reverse("reviews:queue")),
            validate=_http_validator(includes="Fila de revisões"),
            warmups=warmups,
            samples=samples,
            limit_seconds=SCREEN_LIMIT_SECONDS,
        ),
        measure_read_operation(
            name="question_list",
            requirement="CT-105 / RNF-001",
            prepare=lambda _warmup, _index: get(reverse("questions:list")),
            validate=_http_validator(includes=f"Total: {active_questions} "),
            warmups=warmups,
            samples=samples,
            limit_seconds=SCREEN_LIMIT_SECONDS,
        ),
        measure_read_operation(
            name="question_search",
            requirement="CT-106 / RNF-002",
            prepare=lambda _warmup, _index: get(reverse("questions:list"), {"query": target_token}),
            validate=_http_validator(
                includes=str(target.id),
                excludes=str(foreign_question.id),
            ),
            warmups=warmups,
            samples=samples,
            limit_seconds=QUERY_LIMIT_SECONDS,
        ),
        measure_read_operation(
            name="question_filters",
            requirement="CT-106 / RNF-002",
            prepare=lambda _warmup, _index: get(
                reverse("questions:list"),
                {
                    "discipline": str(target.discipline_id),
                    "initial_result": "incorrect",
                },
            ),
            validate=_http_validator(includes=f"Total: {discipline_total} "),
            warmups=warmups,
            samples=samples,
            limit_seconds=QUERY_LIMIT_SECONDS,
        ),
        measure_read_operation(
            name="question_search_filters",
            requirement="CT-106 / RNF-002",
            prepare=lambda _warmup, _index: get(
                reverse("questions:list"),
                {
                    "query": target_token,
                    "discipline": str(target.discipline_id),
                    "initial_result": "incorrect",
                },
            ),
            validate=_http_validator(
                includes=str(target.id),
                excludes=str(foreign_question.id),
            ),
            warmups=warmups,
            samples=samples,
            limit_seconds=QUERY_LIMIT_SECONDS,
        ),
        measure_read_operation(
            name="question_late_page",
            requirement="CT-105 / RNF-001; CT-110 / RNF-061",
            prepare=lambda _warmup, _index: get(
                reverse("questions:list"), {"page": str(max(1, active_questions // PAGE_SIZE))}
            ),
            validate=_http_validator(includes=f"Total: {active_questions} "),
            warmups=warmups,
            samples=samples,
            limit_seconds=SCREEN_LIMIT_SECONDS,
        ),
        measure_read_operation(
            name="question_detail",
            requirement="V0.4-S4 observed read",
            prepare=lambda _warmup, _index: get(reverse("questions:detail", args=[target.id])),
            validate=_http_validator(includes="Detalhe da questão"),
            warmups=warmups,
            samples=samples,
            limit_seconds=None,
        ),
        measure_read_operation(
            name="learning_timeline",
            requirement="V0.4-S4 observed read",
            prepare=lambda _warmup, _index: get(reverse("reviews:timeline", args=[target.id])),
            validate=_http_validator(includes="Linha do tempo"),
            warmups=warmups,
            samples=samples,
            limit_seconds=None,
        ),
    ]

    pagination = _validate_pagination(
        workspace_id=workspace_id,
        expected_items=active_questions,
    )

    threshold_results = [item for item in operations if item.limit_seconds is not None]
    status = (
        "PASS"
        if pagination.status == "PASS" and all(item.status == "PASS" for item in threshold_results)
        else "FAIL"
    )
    return ReadBenchmarkResult(
        operations=tuple(operations),
        pagination=pagination,
        reconciliation={
            "registered_questions": activity.registered_questions,
            "attempts": activity.attempts,
            "active_questions": active_questions,
            "pending_reviews": queue.overdue.total + queue.due.total + queue.future.total,
            "workspace_isolation": True,
        },
        status=status,
    )


def measure_dashboard_update(
    *,
    workspace_id: uuid.UUID,
    warmups: int = READ_WARMUPS,
    samples: int = READ_SAMPLES,
) -> ReadOperationResult:
    """Meça confirmação persistida seguida da próxima leitura do dashboard."""
    client = Client(HTTP_HOST="127.0.0.1")
    target = (
        Question.objects.filter(workspace_id=workspace_id, status=QuestionStatus.ACTIVE)
        .order_by("id")
        .first()
    )
    if target is None or target.discipline_id is None or target.subject_id is None:
        raise RuntimeError("BCR-1 não forneceu taxonomia para atualizar o dashboard.")
    discipline_id = target.discipline_id
    subject_id = target.subject_id
    baseline = Question.objects.filter(workspace_id=workspace_id).count()
    update_counter = 0

    def prepare(_warmup: bool, _index: int) -> Callable[[], Any]:
        nonlocal update_counter
        update_counter += 1
        create_active(
            workspace_id=workspace_id,
            discipline_id=discipline_id,
            subject_id=subject_id,
            stem=f"Atualização de dashboard BCR-1 {update_counter:04d}",
            alternatives=["Incorreta", "Correta"],
            correct_alternative_position=2,
        )
        expected = baseline + update_counter
        return lambda: (client.get(reverse("accounts:home")), expected)

    def validate(value: tuple[Any, int]) -> None:
        response, expected = value
        _http_validator(includes=f"<dd>{expected}</dd>")(response)

    return measure_read_operation(
        name="dashboard_update",
        requirement="CT-108 / RNF-004",
        prepare=prepare,
        validate=validate,
        warmups=warmups,
        samples=samples,
        limit_seconds=SCREEN_LIMIT_SECONDS,
    )


def append_dashboard_update(
    result: ReadBenchmarkResult, operation: ReadOperationResult
) -> ReadBenchmarkResult:
    operations = (*result.operations, operation)
    threshold_results = [item for item in operations if item.limit_seconds is not None]
    status = (
        "PASS"
        if result.pagination.status == "PASS"
        and all(item.status == "PASS" for item in threshold_results)
        else "FAIL"
    )
    return replace(result, operations=operations, status=status)
