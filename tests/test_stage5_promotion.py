"""E5: demonstração integrada sintética do ciclo V0.3, sem capacidade nova."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from modules.attempts.context import ContextStore
from modules.attempts.models import Attempt
from modules.attempts.services import AttemptService
from modules.errors.models import ErrorCategoryCode
from modules.questions.models import Question
from modules.questions.services import create_active
from modules.reviews.models import Review, ReviewCycleState, ReviewState
from modules.reviews.selectors import get_learning_timeline, list_review_queue
from modules.reviews.services import CompleteReviewService
from modules.taxonomy.services import create_discipline, create_subject
from shared.application.bootstrap import bootstrap_local_workspace
from shared.domain.time import FixedClock, Instant


def _question(workspace_id: uuid.UUID, suffix: str) -> Question:
    discipline = create_discipline(workspace_id=workspace_id, name=f"E5 Disciplina {suffix}")
    subject = create_subject(
        workspace_id=workspace_id, discipline_id=discipline.id, name=f"E5 Assunto {suffix}"
    )
    return create_active(
        workspace_id=workspace_id,
        discipline_id=discipline.id,
        subject_id=subject.id,
        stem=f"Questão sintética E5 {suffix}",
        alternatives=["Incorreta", "Correta"],
        correct_alternative_position=2,
        explanation="Explicação sintética reservada",
        trap_note="Pegadinha sintética reservada",
    )


def _evaluate_initial(service: AttemptService, question: Question, *, correct: bool) -> str:
    shown = service.presentation(question.id)
    return service.evaluate(
        question_id=question.id,
        revision_id=shown["revision_id"],
        lock_version=shown["lock_version"],
        alternative_id=shown["alternatives"][int(correct)][0],
    )


def _complete_review(service: CompleteReviewService, review: Review, *, correct: bool) -> None:
    shown = service.presentation(review.id)
    token = service.evaluate(
        review_id=review.id,
        revision_id=shown["revision_id"],
        lock_version=shown["lock_version"],
        review_lock_version=shown["review_lock_version"],
        alternative_id=shown["alternatives"][int(correct)][0],
    )
    service.complete_review(
        token=token,
        key=uuid.uuid4(),
        category_id=(
            service.attempts.workspace().error_categories.get(code=ErrorCategoryCode.ATTENTION).id
            if not correct
            else None
        ),
    )


@pytest.mark.django_db
def test_e5_integrated_synthetic_flow_completes_cycle_and_resets_review_error() -> None:
    """CT-123: executa o fluxo presente em V0.3 em uma única base descartável."""
    workspace = bootstrap_local_workspace(timezone_id="America/Sao_Paulo").workspace
    clock = FixedClock(Instant(datetime(2026, 9, 8, 15, tzinfo=UTC)))
    store = ContextStore()
    attempts = AttemptService(
        actor_id=workspace.owner_user_id,
        workspace_id=workspace.id,
        session="stage5-integrated",
        clock=clock,
        store=store,
    )
    reviews = CompleteReviewService(attempts)

    complete_question = _question(workspace.id, "complete")
    token = _evaluate_initial(attempts, complete_question, correct=False)
    attempts.confirm(
        token=token,
        key=uuid.uuid4(),
        category_id=workspace.error_categories.get(code=ErrorCategoryCode.ATTENTION).id,
    )
    review = Review.objects.get(question=complete_question, state=ReviewState.PENDING)
    assert list_review_queue(workspace_id=workspace.id, clock=clock).future.entries == (review,)

    for expected_stage in ("D1", "D7", "D14", "D30"):
        review.refresh_from_db()
        assert review.stage_code == expected_stage
        clock.set(
            Instant(
                datetime(
                    review.current_due_date.year,
                    review.current_due_date.month,
                    review.current_due_date.day,
                    15,
                    tzinfo=UTC,
                )
            )
        )
        _complete_review(reviews, review, correct=True)
        if expected_stage != "D30":
            review = Review.objects.get(question=complete_question, state=ReviewState.PENDING)

    cycle = complete_question.review_cycles.get()
    assert cycle.state == ReviewCycleState.COMPLETED
    assert not Review.objects.filter(question=complete_question, state=ReviewState.PENDING).exists()
    timeline = get_learning_timeline(workspace_id=workspace.id, question_id=complete_question.id)
    assert [event.kind for event in timeline].count("attempt_initial") == 1
    assert [event.kind for event in timeline].count("attempt_review") == 4

    restart_question = _question(workspace.id, "restart")
    token = _evaluate_initial(attempts, restart_question, correct=False)
    attempts.confirm(
        token=token,
        key=uuid.uuid4(),
        category_id=workspace.error_categories.get(code=ErrorCategoryCode.ATTENTION).id,
    )
    review = Review.objects.get(question=restart_question, state=ReviewState.PENDING)
    clock.set(
        Instant(
            datetime(
                review.current_due_date.year,
                review.current_due_date.month,
                review.current_due_date.day,
                15,
                tzinfo=UTC,
            )
        )
    )
    _complete_review(reviews, review, correct=True)
    review = Review.objects.get(question=restart_question, state=ReviewState.PENDING)
    clock.set(
        Instant(
            datetime(
                review.current_due_date.year,
                review.current_due_date.month,
                review.current_due_date.day,
                15,
                tzinfo=UTC,
            )
        )
    )
    _complete_review(reviews, review, correct=False)
    restarted = Review.objects.get(question=restart_question, state=ReviewState.PENDING)
    assert (restarted.stage_code, restarted.current_due_date.isoformat()) == ("D1", "2026-11-08")
    assert restart_question.review_cycles.get().state == ReviewCycleState.ACTIVE

    correct_question = _question(workspace.id, "correct")
    attempts.confirm(
        token=_evaluate_initial(attempts, correct_question, correct=True), key=uuid.uuid4()
    )
    assert not Review.objects.filter(question=correct_question).exists()
    assert Attempt.objects.filter(workspace=workspace, status="VALID").count() == 9
