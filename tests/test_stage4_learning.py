"""CT-019/030--036/041/125: fila, histórico, diagnóstico e suspensão E4."""

import uuid
from datetime import UTC, date, datetime

import pytest
from django.core.exceptions import ValidationError
from django.test import Client
from django.urls import reverse

from modules.accounts.models import User, Workspace
from modules.attempts.context import InitialAttemptError
from modules.attempts.models import Attempt, AttemptType
from modules.errors.models import (
    ErrorCategoryCode,
    ErrorClassification,
    ErrorClassificationRevision,
)
from modules.errors.services import (
    ErrorDiagnosisConflictError,
    ErrorDiagnosisService,
    seed_standard_error_categories,
)
from modules.questions.models import Question, QuestionStatus
from modules.questions.services import QuestionCommandService, create_active
from modules.reviews.models import (
    Review,
    ReviewCycle,
    ReviewCycleState,
    ReviewState,
)
from modules.reviews.selectors import (
    get_learning_timeline,
    get_review_pending_detail,
    list_review_queue,
)
from modules.reviews.services import CompleteReviewService
from modules.taxonomy.services import create_discipline, create_subject
from shared.application.bootstrap import bootstrap_local_workspace
from shared.domain.time import FixedClock, Instant


def _workspace(email: str) -> Workspace:
    user = User.objects.create_user(email=email)
    workspace = Workspace.objects.create(
        owner_user=user, name=email, timezone_name="America/Sao_Paulo"
    )
    seed_standard_error_categories(workspace)
    return workspace


def _question(workspace: Workspace, suffix: str = "") -> Question:
    discipline = create_discipline(workspace_id=workspace.id, name=f"Disciplina E4 {suffix}")
    subject = create_subject(
        workspace_id=workspace.id, discipline_id=discipline.id, name="Assunto E4"
    )
    return create_active(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        subject_id=subject.id,
        stem="Questão E4",
        alternatives=["Errada", "Certa"],
        correct_alternative_position=2,
    )


def _learning(
    workspace: Workspace, question: Question, due: date
) -> tuple[Attempt, ReviewCycle, Review]:
    revision = question.revisions.get(is_current=True)
    attempt = Attempt.objects.create(
        workspace=workspace,
        question=question,
        question_revision=revision,
        attempt_type=AttemptType.INITIAL,
        selected_alternative=revision.alternatives.get(position=1),
        is_correct=False,
        occurred_at=datetime(2026, 9, 8, 15, tzinfo=UTC),
        timezone_name=workspace.timezone_name,
        local_date=date(2026, 9, 8),
        idempotency_key=uuid.uuid4(),
    )
    cycle = question.review_cycles.get(state=ReviewCycleState.ACTIVE)
    review = cycle.reviews.get(state=ReviewState.PENDING)
    Review.objects.filter(pk=review.id).update(first_due_date=due, current_due_date=due)
    review.refresh_from_db()
    return attempt, cycle, review


@pytest.mark.django_db
def test_ct030_to_ct036_queue_is_workspace_scoped_temporal_and_stably_ordered() -> None:
    workspace = _workspace("queue@example.test")
    foreign = _workspace("queue-foreign@example.test")
    clock = FixedClock(Instant(datetime(2026, 9, 10, 2, tzinfo=UTC)))  # dia 9 em São Paulo
    reviews = [
        _learning(workspace, _question(workspace, str(index)), due)[2]
        for index, due in enumerate(
            (date(2026, 9, 8), date(2026, 9, 8), date(2026, 9, 9), date(2026, 9, 10))
        )
    ]
    _learning(foreign, _question(foreign), date(2026, 9, 8))
    Review.objects.filter(pk=reviews[1].id).update(
        state=ReviewState.COMPLETED, completed_at=clock.now().value
    )
    queue = list_review_queue(workspace_id=workspace.id, clock=clock, page_size=1)
    assert [item.id for item in queue.overdue.entries] == [reviews[0].id]
    assert queue.overdue.total == 1 and queue.due.entries[0].id == reviews[2].id
    assert queue.future.entries[0].id == reviews[3].id
    with pytest.raises(Review.DoesNotExist):
        get_review_pending_detail(workspace_id=foreign.id, review_id=reviews[0].id)


@pytest.mark.django_db
def test_ct019_diagnosis_correction_seeds_history_is_append_only_and_checks_lock() -> None:
    workspace = _workspace("diagnosis@example.test")
    attempt, _cycle, _review = _learning(workspace, _question(workspace), date(2026, 9, 9))
    original = workspace.error_categories.get(code=ErrorCategoryCode.ATTENTION)
    changed = workspace.error_categories.get(code=ErrorCategoryCode.OTHER)
    classification = ErrorClassification.objects.create(
        workspace=workspace, attempt=attempt, category=original
    )
    result = ErrorDiagnosisService(workspace_id=workspace.id).correct(
        attempt_id=attempt.id,
        category_id=changed.id,
        other_description="  leitura  ",
        change_reason="  correção  ",
        expected_lock_version=classification.lock_version,
    )
    history = list(result.revisions.order_by("revision_number"))
    assert [
        (item.revision_number, item.category_id, item.other_description) for item in history
    ] == [(1, original.id, None), (2, changed.id, "leitura")]
    assert result.lock_version == 2 and result.category_id == changed.id
    timeline = get_learning_timeline(workspace_id=workspace.id, question_id=attempt.question_id)
    assert [event.kind for event in timeline if event.kind.startswith("diagnosis")] == [
        "diagnosis_created",
        "diagnosis_revision",
        "diagnosis_revision",
    ]
    with pytest.raises(ErrorDiagnosisConflictError):
        ErrorDiagnosisService(workspace_id=workspace.id).correct(
            attempt_id=attempt.id, category_id=original.id, expected_lock_version=1
        )
    with pytest.raises(ValidationError):
        ErrorClassificationRevision.objects.filter(pk=history[0].id).update(change_reason="não")
    attempt.refresh_from_db()
    assert attempt.is_correct is False and attempt.occurred_at == datetime(
        2026, 9, 8, 15, tzinfo=UTC
    )


@pytest.mark.django_db
def test_ct041_archive_suspends_active_cycle_review_and_preserves_timeline() -> None:
    workspace = _workspace("archive@example.test")
    question = _question(workspace)
    _attempt, cycle, review = _learning(workspace, question, date(2026, 9, 9))
    archived = QuestionCommandService.archive(
        workspace_id=workspace.id,
        question_id=question.id,
        expected_lock_version=question.lock_version,
    )
    cycle.refresh_from_db()
    review.refresh_from_db()
    assert archived.status == QuestionStatus.ARCHIVED
    assert (cycle.state, cycle.suspension_reason, review.state) == (
        ReviewCycleState.SUSPENDED,
        "QUESTION_ARCHIVED",
        ReviewState.SUSPENDED,
    )
    assert (
        get_learning_timeline(workspace_id=workspace.id, question_id=question.id)[-1].kind
        == "question_archived"
    )


@pytest.mark.django_db
def test_ct041_archive_without_cycle_and_suspended_review_blocks_completion() -> None:
    workspace = _workspace("archive-review@example.test")
    question = _question(workspace)
    _attempt, _cycle, review = _learning(workspace, question, date(2026, 9, 9))
    QuestionCommandService.archive(
        workspace_id=workspace.id,
        question_id=question.id,
        expected_lock_version=question.lock_version,
    )
    service = CompleteReviewService(
        actor_id=workspace.owner_user_id, workspace_id=workspace.id, session="e4"
    )
    with pytest.raises(InitialAttemptError):
        service.presentation(review.id)
    standalone = _question(workspace, "sem-ciclo")
    assert (
        QuestionCommandService.archive(
            workspace_id=workspace.id,
            question_id=standalone.id,
            expected_lock_version=standalone.lock_version,
        ).status
        == QuestionStatus.ARCHIVED
    )


@pytest.mark.django_db
def test_ct125_queue_timeline_and_correction_views_keep_csrf_and_escaping() -> None:
    workspace = bootstrap_local_workspace(timezone_id="America/Sao_Paulo").workspace
    attempt, _cycle, _review = _learning(workspace, _question(workspace), date(2026, 9, 9))
    category = workspace.error_categories.get(code=ErrorCategoryCode.ATTENTION)
    classification = ErrorClassification.objects.create(
        workspace=workspace, attempt=attempt, category=category
    )
    client = Client()
    assert client.get(reverse("reviews:queue")).status_code == 200
    correction = reverse("reviews:correct-diagnosis", args=[attempt.id])
    protected = Client(enforce_csrf_checks=True).post(
        correction, {"lock_version": classification.lock_version}
    )
    assert protected.status_code == 403
    response = client.post(
        correction,
        {
            "lock_version": classification.lock_version,
            "category": category.id,
            "change_reason": "<script>x</script>",
        },
    )
    assert response.status_code == 302
    html = client.get(reverse("reviews:timeline", args=[attempt.question_id])).content.decode(
        "utf-8"
    )
    assert "<script>x</script>" not in html
