"""Fixture S8 versionada: seed fixo, relógio injetado e oráculo semântico."""

import random
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, TypedDict

from modules.accounts.models import User, Workspace
from modules.attempts.context import ContextStore
from modules.attempts.models import Attempt, OperationReceipt
from modules.attempts.services import AttemptService
from modules.errors.models import ErrorClassification
from modules.errors.services import seed_standard_error_categories
from modules.questions.models import Question
from modules.questions.services import create_active
from modules.reviews.models import Review
from modules.reviews.services import CompleteReviewService
from modules.taxonomy.services import create_discipline, create_subject
from shared.application.bootstrap import bootstrap_local_workspace
from shared.domain.time import FixedClock, Instant

SEED = 81001
ORACLE = {
    "workspaces": 2,
    "questions": 4,
    "attempts": 3,
    "classifications": 1,
    "receipts": 3,
    "reviews": 5,
}


class InitialDiagnosis(TypedDict, total=False):
    category_id: uuid.UUID | None
    other_description: str


def create_fixture(
    *, start: datetime | None = None, expected_d1: str = "2026-11-09", secondary: bool = True
) -> dict[str, Any]:
    """Reproduza conteúdos/contagens/datas; UUIDs técnicos novos são registrados."""
    assert not Question.objects.exists() and not Attempt.objects.exists()
    start = start or datetime(2026, 11, 8, 15, tzinfo=UTC)
    clock = FixedClock(Instant(start))
    primary = bootstrap_local_workspace(timezone_id="America/Sao_Paulo").workspace
    other = None
    if secondary:
        owner = User.objects.create_user(
            email="local-r1-synthetic@example.test",
            id=uuid.uuid5(uuid.NAMESPACE_URL, "cei-local-r1-s8-owner-b"),
        )
        other = Workspace.objects.create(
            id=uuid.uuid5(uuid.NAMESPACE_URL, "cei-local-r1-s8-workspace-b"),
            owner_user=owner,
            name="Sintético B",
            timezone_name="America/Sao_Paulo",
        )
        seed_standard_error_categories(other)
    randomizer = random.Random(SEED)  # noqa: S311 -- fixture semântica determinística, sem segredo
    questions = []
    for workspace in (primary, other) if other is not None else (primary,):
        discipline = create_discipline(workspace_id=workspace.id, name="Disciplina sintética")
        subject = create_subject(
            workspace_id=workspace.id, discipline_id=discipline.id, name="Assunto sintético"
        )
        for number in range((3 if workspace.id == primary.id else 1) if secondary else 4):
            questions.append(
                create_active(
                    workspace_id=workspace.id,
                    discipline_id=discipline.id,
                    subject_id=subject.id,
                    stem=f"Questão sintética {number}: ação Unicode {randomizer.randrange(10000)} <script>sentinela-local</script>",
                    alternatives=["Alternativa incorreta", "Alternativa correta"],
                    correct_alternative_position=2,
                    explanation="Explicação sintética reservada antes da tentativa",
                    clock=clock,
                )
            )
    service = AttemptService(
        actor_id=primary.owner_user_id,
        workspace_id=primary.id,
        session="local-r1-s8-synthetic",
        store=ContextStore(),
        clock=clock,
    )
    for index in (0, 1):
        shown = service.presentation(questions[index].id)
        assert "explanation" not in shown and "correct_alternative" not in shown
        token = service.evaluate(
            question_id=questions[index].id,
            revision_id=shown["revision_id"],
            lock_version=shown["lock_version"],
            alternative_id=shown["alternatives"][index][0],
        )
        kwargs: InitialDiagnosis = (
            {}
            if index
            else {
                "category_id": primary.error_categories.get(code="OTHER").id,
                "other_description": "Diagnóstico gerado sinteticamente",
            }
        )
        service.confirm(
            token=token,
            key=uuid.uuid5(uuid.NAMESPACE_URL, f"cei-local-r1-s8-initial-{index}"),
            **kwargs,
        )
    due = Review.objects.get(question_id=questions[0].id, state="PENDING")
    assert (
        list(Review.objects.filter(stage_code="D1").values_list("current_due_date", flat=True))
        == [datetime.fromisoformat(expected_d1).date()] * 4
    )
    assert due.current_due_date.isoformat() == expected_d1
    clock.advance(timedelta(days=1))
    reviews = CompleteReviewService(service)
    shown = reviews.presentation(due.id)
    token = reviews.evaluate(
        review_id=due.id,
        revision_id=shown["revision_id"],
        lock_version=shown["lock_version"],
        review_lock_version=shown["review_lock_version"],
        alternative_id=shown["alternatives"][1][0],
    )
    reviews.complete_review(
        token=token, key=uuid.uuid5(uuid.NAMESPACE_URL, "cei-local-r1-s8-review")
    )
    observed = {
        "workspaces": Workspace.objects.count(),
        "questions": Question.objects.count(),
        "attempts": Attempt.objects.count(),
        "classifications": ErrorClassification.objects.count(),
        "receipts": OperationReceipt.objects.count(),
        "reviews": Review.objects.count(),
    }
    expected = {**ORACLE, "workspaces": 2 if secondary else 1}
    assert observed == expected, (observed, expected)
    due.refresh_from_db()
    assert due.state == "COMPLETED"
    return {
        "seed": SEED,
        "origin": "GENERATED_SYNTHETIC",
        "clock_start": start.isoformat(),
        "clock_end": (start + timedelta(days=1)).isoformat(),
        "expected": expected,
        "observed": observed,
        "primary": str(primary.id),
        "secondary": str(other.id) if other is not None else None,
        "question_ids": [str(q.id) for q in questions],
        "completed_review_id": str(due.id),
        "uuid_policy": "Fresh technical UUIDs; deterministic semantic vectors and operation keys.",
    }
