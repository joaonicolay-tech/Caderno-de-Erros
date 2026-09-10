"""CT-023--029/037--042: conclusão determinística de REVIEW em banco descartável."""

import uuid
from datetime import UTC, datetime
from typing import Any

import pytest
from django.db import OperationalError
from django.test import Client
from django.urls import reverse

from modules.accounts.models import User, Workspace
from modules.attempts.context import ContextStore, InitialAttemptError
from modules.attempts.models import Attempt, AttemptType, OperationReceipt
from modules.attempts.services import AttemptService
from modules.errors.models import (
    ErrorCategoryCode,
    ErrorClassification,
    ErrorClassificationRevision,
)
from modules.errors.services import seed_standard_error_categories
from modules.questions.models import Question
from modules.questions.services import create_active
from modules.reviews.models import Review, ReviewCycleState, ReviewState
from modules.reviews.services import CompleteReviewService
from modules.taxonomy.services import create_discipline, create_subject
from shared.application.bootstrap import bootstrap_local_workspace
from shared.domain.time import FixedClock, Instant


def _question(workspace: Workspace, suffix: str = "", clock: FixedClock | None = None) -> Question:
    discipline = create_discipline(workspace_id=workspace.id, name=f"Disciplina revisão{suffix}")
    subject = create_subject(
        workspace_id=workspace.id, discipline_id=discipline.id, name="Assunto revisão"
    )
    return create_active(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        subject_id=subject.id,
        stem="Questão sintética de revisão",
        alternatives=["incorreta", "correta"],
        correct_alternative_position=2,
        explanation="explicação reservada",
        trap_note="pegadinha reservada",
        clock=clock,
    )


def _seed_pending_review() -> tuple[CompleteReviewService, Review, Workspace, FixedClock]:
    workspace = bootstrap_local_workspace(timezone_id="America/Sao_Paulo").workspace
    clock = FixedClock(Instant(datetime(2026, 9, 8, 15, tzinfo=UTC)))
    store = ContextStore()
    initial = AttemptService(
        actor_id=workspace.owner_user_id,
        workspace_id=workspace.id,
        session="review-session",
        store=store,
        clock=clock,
    )
    question = _question(workspace, clock=clock)
    shown = initial.presentation(question.id)
    token = initial.evaluate(
        question_id=question.id,
        revision_id=shown["revision_id"],
        lock_version=shown["lock_version"],
        alternative_id=shown["alternatives"][0][0],
    )
    initial.confirm(
        token=token,
        key=uuid.uuid4(),
        category_id=workspace.error_categories.get(code=ErrorCategoryCode.ATTENTION).id,
    )
    clock.set(Instant(datetime(2026, 9, 9, 15, tzinfo=UTC)))
    return (
        CompleteReviewService(
            actor_id=workspace.owner_user_id,
            workspace_id=workspace.id,
            session="review-session",
            store=store,
            clock=clock,
        ),
        Review.objects.get(),
        workspace,
        clock,
    )


def _complete(
    service: CompleteReviewService,
    review: Review,
    *,
    correct: bool,
    key: uuid.UUID | None = None,
    ease: str | None = None,
    category_id: uuid.UUID | None = None,
    description: str = "",
) -> tuple[str, uuid.UUID, Any]:
    shown = service.presentation(review.id)
    token = service.evaluate(
        review_id=review.id,
        revision_id=shown["revision_id"],
        lock_version=shown["lock_version"],
        review_lock_version=shown["review_lock_version"],
        alternative_id=shown["alternatives"][int(correct)][0],
    )
    key = key or uuid.uuid4()
    if not correct and category_id is None:
        category_id = (
            service.attempts.workspace().error_categories.get(code=ErrorCategoryCode.ATTENTION).id
        )
    return (
        token,
        key,
        service.complete_review(
            token=token,
            key=key,
            perceived_ease=ease,
            category_id=category_id,
            description=description,
        ),
    )


@pytest.mark.django_db
def test_ct023_initial_error_has_one_due_d1_in_active_cycle() -> None:
    _, review, workspace, _ = _seed_pending_review()
    assert (review.stage_code, review.state, review.current_due_date.isoformat()) == (
        "D1",
        ReviewState.PENDING,
        "2026-09-09",
    )
    assert workspace.review_cycles.get().state == ReviewCycleState.ACTIVE
    assert workspace.reviews.filter(state=ReviewState.PENDING).count() == 1


@pytest.mark.django_db
def test_ct024_to_ct027_correct_path_uses_real_civil_dates() -> None:
    service, review, _, clock = _seed_pending_review()
    expected = [
        ("D1", "D7", "2026-09-16"),
        ("D7", "D14", "2026-09-30"),
        ("D14", "D30", "2026-10-30"),
    ]
    for stage, next_stage, due in expected:
        assert review.stage_code == stage
        _complete(service, review, correct=True)
        review.refresh_from_db()
        assert review.state == ReviewState.COMPLETED
        review = Review.objects.get(review_cycle=review.review_cycle, state=ReviewState.PENDING)
        assert (review.stage_code, review.current_due_date.isoformat()) == (next_stage, due)
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
    _complete(service, review, correct=True)
    review.refresh_from_db()
    cycle = review.review_cycle
    cycle.refresh_from_db()
    assert review.stage_code == "D30" and review.state == ReviewState.COMPLETED
    assert cycle.state == ReviewCycleState.COMPLETED and cycle.completed_at is not None
    assert not Review.objects.filter(review_cycle=cycle, state=ReviewState.PENDING).exists()
    assert Attempt.objects.filter(attempt_type=AttemptType.REVIEW).count() == 4


@pytest.mark.django_db
@pytest.mark.parametrize("advance", [0, 1, 2, 3])
def test_ct028_error_at_every_stage_resets_to_d1_same_cycle(advance: int) -> None:
    service, review, _, clock = _seed_pending_review()
    for _ in range(advance):
        _complete(service, review, correct=True)
        review = Review.objects.get(review_cycle=review.review_cycle, state=ReviewState.PENDING)
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
    cycle_id = review.review_cycle_id
    clock.set(Instant(datetime(2026, 11, 20, 15, tzinfo=UTC)))
    _complete(service, review, correct=False)
    review.refresh_from_db()
    next_review = Review.objects.get(review_cycle_id=cycle_id, state=ReviewState.PENDING)
    assert review.state == ReviewState.COMPLETED
    assert (next_review.stage_code, next_review.current_due_date.isoformat()) == (
        "D1",
        "2026-11-21",
    )
    assert next_review.sequence_number == review.sequence_number + 1
    assert next_review.review_cycle.state == ReviewCycleState.ACTIVE
    assert ErrorClassification.objects.filter(attempt__review=review).count() == 1
    assert not ErrorClassificationRevision.objects.filter(
        error_classification__attempt__review=review
    ).exists()


@pytest.mark.django_db
def test_ct037_ct038_replay_and_divergent_payload_are_safe() -> None:
    service, review, _, _ = _seed_pending_review()
    shown = service.presentation(review.id)
    token = service.evaluate(
        review_id=review.id,
        revision_id=shown["revision_id"],
        lock_version=shown["lock_version"],
        review_lock_version=shown["review_lock_version"],
        alternative_id=shown["alternatives"][1][0],
    )
    key = uuid.uuid4()
    receipt = service.complete_review(token=token, key=key, perceived_ease="EASY")
    assert service.complete_review(token=token, key=key, perceived_ease="EASY").id == receipt.id
    with pytest.raises(InitialAttemptError):
        service.complete_review(token=token, key=key, perceived_ease="HARD")
    assert Attempt.objects.filter(attempt_type=AttemptType.REVIEW).count() == 1
    assert OperationReceipt.objects.filter(operation_kind="REVIEW_COMPLETION").count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize("ease", [None, "EASY", "MEDIUM", "HARD"])
def test_ct042_perceived_ease_is_closed_and_never_changes_schedule(ease: str | None) -> None:
    service, review, _, _ = _seed_pending_review()
    _, _, _complete(service, review, correct=True, ease=ease)
    attempt = Attempt.objects.get(attempt_type=AttemptType.REVIEW)
    next_review = Review.objects.get(state=ReviewState.PENDING)
    assert attempt.perceived_ease == ease
    assert (next_review.stage_code, next_review.current_due_date.isoformat()) == (
        "D7",
        "2026-09-16",
    )


@pytest.mark.django_db
def test_future_review_has_no_context_or_persistent_effect() -> None:
    service, review, _, _ = _seed_pending_review()
    Review.objects.filter(pk=review.id).update(
        current_due_date=review.current_due_date.replace(day=20)
    )
    before = (Attempt.objects.count(), Review.objects.count(), OperationReceipt.objects.count())
    shown = service.presentation(review.id)
    with pytest.raises(InitialAttemptError, match="REVIEW_NOT_AVAILABLE"):
        service.evaluate(
            review_id=review.id,
            revision_id=shown["revision_id"],
            lock_version=shown["lock_version"],
            review_lock_version=shown["review_lock_version"],
            alternative_id=shown["alternatives"][0][0],
        )
    assert (
        Attempt.objects.count(),
        Review.objects.count(),
        OperationReceipt.objects.count(),
    ) == before


@pytest.mark.django_db
def test_ct039_rollback_restores_attempt_review_cycle_and_receipt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service, review, _, _ = _seed_pending_review()
    shown = service.presentation(review.id)
    token = service.evaluate(
        review_id=review.id,
        revision_id=shown["revision_id"],
        lock_version=shown["lock_version"],
        review_lock_version=shown["review_lock_version"],
        alternative_id=shown["alternatives"][1][0],
    )
    original = Review.save

    def fail_next(self: Review, *args: object, **kwargs: object) -> None:
        if self.sequence_number == 2:
            raise OperationalError("injected failure")
        original(self, *args, **kwargs)

    monkeypatch.setattr(Review, "save", fail_next)
    with pytest.raises(InitialAttemptError, match="PERSISTENCE_FAILURE"):
        service.complete_review(token=token, key=uuid.uuid4())
    review.refresh_from_db()
    assert review.state == ReviewState.PENDING and review.lock_version == 1
    assert not Attempt.objects.filter(attempt_type=AttemptType.REVIEW).exists()
    assert not OperationReceipt.objects.filter(operation_kind="REVIEW_COMPLETION").exists()


@pytest.mark.django_db
def test_workspace_crossing_and_second_tab_do_not_duplicate_review() -> None:
    service, review, workspace, _ = _seed_pending_review()
    user = User.objects.create_user()
    foreign = Workspace.objects.create(
        owner_user=user, name="Workspace estrangeiro", timezone_name="Asia/Tokyo"
    )
    seed_standard_error_categories(foreign)
    foreign_service = CompleteReviewService(
        actor_id=user.id,
        workspace_id=foreign.id,
        session="review-session",
        store=service.attempts.store,
    )
    with pytest.raises(InitialAttemptError):
        foreign_service.presentation(review.id)
    token, _, _ = _complete(service, review, correct=True)
    with pytest.raises(InitialAttemptError):
        service.complete_review(token=token, key=uuid.uuid4())
    assert workspace.attempts.filter(attempt_type=AttemptType.REVIEW).count() == 1
    assert workspace.reviews.filter(state=ReviewState.PENDING).count() == 1


@pytest.mark.django_db
def test_ct093_ct101_review_http_hides_answer_and_validates_context() -> None:
    _, review, _, _ = _seed_pending_review()
    client = Client(enforce_csrf_checks=True)
    url = reverse("reviews:complete", args=[review.id])
    page = client.get(url)
    html = page.content.decode()
    assert page.status_code == 200
    assert page["Referrer-Policy"] == "same-origin"
    assert "explicação reservada" not in html and "pegadinha reservada" not in html
    assert "correct_alternative" not in html and "is_correct" not in html
    answer = page.context["answer"]
    data = {
        "action": "answer",
        "revision_id": str(answer.initial["revision_id"]),
        "lock_version": answer.initial["lock_version"],
        "review_lock_version": answer.initial["review_lock_version"],
        "alternative_id": str(answer.fields["alternative_id"].choices[1][0]),
        "csrfmiddlewaretoken": client.cookies["csrftoken"].value,
    }
    page = client.post(url, data, follow=True)
    assert page.status_code == 200 and b"explica\xc3\xa7\xc3\xa3o reservada" in page.content
    feedback_html = page.content.decode()
    assert "explanation-title" in feedback_html and "trap-note-title" in feedback_html
    assert "notes-title" not in feedback_html
    confirmation = page.context["confirmation"]
    submit = {
        "action": "confirm",
        **confirmation.initial,
        "perceived_ease": "EASY",
        "csrfmiddlewaretoken": client.cookies["csrftoken"].value,
    }
    assert client.post(url, {**submit, "is_correct": "true"}).status_code == 409
    completed = client.post(url, submit)
    completed_html = completed.content.decode()
    assert completed.status_code == 200
    assert "Revis&atilde;o conclu&iacute;da" in completed_html
    assert "Sua revis&atilde;o foi registrada com sucesso." in completed_html
    assert "Voltar &agrave;s revis&otilde;es" in completed_html
    assert str(completed.context["receipt"]) not in completed_html
    assert "Recibo:" not in completed_html
    assert Attempt.objects.filter(review=review, attempt_type=AttemptType.REVIEW).count() == 1
