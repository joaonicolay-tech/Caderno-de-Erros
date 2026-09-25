"""Priority reuses S5 and reads live Workspace facts without side effects."""

from datetime import UTC, datetime, timedelta

import pytest
from django.db import connection
from django.test import Client
from django.test.utils import CaptureQueriesContext
from test_v05_s5_domain import _dominated, _question, _workspace

from modules.attempts.corrections import AttemptCorrectionService
from modules.attempts.models import Attempt, AttemptType
from modules.domain.models import MasteryStateEvent
from modules.priority.services import list_subject_priorities
from modules.questions.corrections import AnswerKeyCorrectionService
from modules.questions.models import Question, QuestionRevision
from modules.questions.services import archive_question
from modules.reviews.models import Review, ReviewCycle
from modules.reviews.selectors import list_review_queue
from modules.taxonomy.services import create_subject
from shared.domain.time import FixedClock, Instant

CLOCK = FixedClock(Instant(datetime(2026, 9, 24, 15, tzinfo=UTC)))


@pytest.mark.django_db(transaction=True)
def test_ranked_subject_uses_s5_facts_and_read_has_no_mutation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workspace, discipline_id, subject_id = _workspace()
    questions = tuple(_dominated(workspace, discipline_id, subject_id) for _ in range(3))
    counts_before = (
        Question.objects.count(),
        Review.objects.count(),
        ReviewCycle.objects.count(),
        MasteryStateEvent.objects.count(),
    )
    with CaptureQueriesContext(connection) as queries:
        listing = list_subject_priorities(workspace_id=workspace.id, clock=CLOCK)
    assert len(queries) <= 18
    assert len(listing.ranked) == 1
    result = listing.ranked[0].result
    assert result.subject_id == subject_id
    assert result.score is not None
    assert result.r == result.d == 0
    assert result.recurrence_eligible_count == result.comparable_question_count == 3
    assert result.active_question_count == 3
    assert result.explanation_codes
    assert counts_before == (
        Question.objects.count(),
        Review.objects.count(),
        ReviewCycle.objects.count(),
        MasteryStateEvent.objects.count(),
    )

    # The new GET uses the same read-only service; UI still links to the operational queue.
    monkeypatch.setattr("modules.accounts.views._local_workspace", lambda: workspace)
    response = Client().get("/prioridades/")
    assert response.status_code == 200
    assert b"PRI-HEUR-1.0" in response.content
    assert b"/reviews/" in response.content
    assert counts_before == (
        Question.objects.count(),
        Review.objects.count(),
        ReviewCycle.objects.count(),
        MasteryStateEvent.objects.count(),
    )
    assert len(questions) == 3


@pytest.mark.django_db(transaction=True)
def test_insufficient_subject_and_foreign_workspace_stay_out_of_ranking(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workspace, discipline_id, subject_id = _workspace()
    _question(
        workspace,
        discipline_id,
        subject_id,
        clock=FixedClock(Instant(datetime(2026, 9, 20, 15, tzinfo=UTC))),
    )
    second = create_subject(workspace_id=workspace.id, discipline_id=discipline_id, name="Empty")
    foreign, foreign_discipline, foreign_subject = _workspace()
    for _ in range(3):
        _dominated(foreign, foreign_discipline, foreign_subject)
    listing = list_subject_priorities(workspace_id=workspace.id, clock=CLOCK)
    assert not listing.ranked
    assert {row.subject.id for row in listing.collect_more_evidence} == {subject_id, second.id}
    assert all(row.result.score is None for row in listing.collect_more_evidence)
    sparse = next(
        row.result for row in listing.collect_more_evidence if row.subject.id == subject_id
    )
    assert sparse.overdue_question_count == 1
    assert sparse.o == 100
    # The independent operational queue is still callable and scoped.
    queue = list_review_queue(workspace_id=workspace.id, clock=CLOCK)
    assert queue.overdue.total == 1
    monkeypatch.setattr("modules.accounts.views._local_workspace", lambda: workspace)
    response = Client().get("/prioridades/")
    assert response.status_code == 200
    assert "Coletar mais evidências" in response.content.decode()
    assert "fila" in response.content.decode()


@pytest.mark.django_db(transaction=True)
def test_priority_empty_state_is_readable(monkeypatch: pytest.MonkeyPatch) -> None:
    workspace, _, _ = _workspace()
    monkeypatch.setattr("modules.accounts.views._local_workspace", lambda: workspace)
    response = Client().get("/prioridades/")
    assert response.status_code == 200
    assert "Ainda não há assuntos com evidência suficiente" in response.content.decode()
    assert "Coletar mais evidências" in response.content.decode()


@pytest.mark.django_db(transaction=True)
def test_void_archive_and_prospective_key_correction_change_only_current_facts() -> None:
    workspace, discipline_id, subject_id = _workspace()
    questions = tuple(_dominated(workspace, discipline_id, subject_id) for _ in range(4))
    before = list_subject_priorities(workspace_id=workspace.id, clock=CLOCK).ranked[0].result
    assert before.comparable_question_count == 4

    revision = QuestionRevision.objects.get(question=questions[0], is_current=True)
    AnswerKeyCorrectionService(workspace_id=workspace.id, clock=CLOCK).correct(
        question_id=questions[0].id,
        expected_revision_id=revision.id,
        correct_alternative_position=2,
        reason_code="OFFICIAL_KEY_FIX",
    )
    after_key = list_subject_priorities(workspace_id=workspace.id, clock=CLOCK).ranked[0].result
    assert after_key.score == before.score
    assert after_key.comparable_question_count == 4

    latest = (
        Attempt.objects.filter(question=questions[1], attempt_type=AttemptType.REVIEW)
        .order_by("-occurred_at")
        .first()
    )
    assert latest is not None
    AttemptCorrectionService(workspace_id=workspace.id, clock=CLOCK).void(
        attempt_id=latest.id,
        expected_tip_id=latest.id,
        reason_code="RESULT_CORRECTION",
    )
    after_void = list_subject_priorities(workspace_id=workspace.id, clock=CLOCK).ranked[0].result
    assert after_void.comparable_question_count == 3
    assert after_void.d == 0

    questions[2].refresh_from_db()
    archive_question(
        workspace_id=workspace.id,
        question_id=questions[2].id,
        expected_lock_version=questions[2].lock_version,
        clock=CLOCK,
    )
    after_archive = list_subject_priorities(workspace_id=workspace.id, clock=CLOCK)
    assert not after_archive.ranked
    assert after_archive.collect_more_evidence[0].result.comparable_question_count == 2


@pytest.mark.django_db(transaction=True)
def test_civil_windows_expire_without_rewriting_attempts() -> None:
    workspace, discipline_id, subject_id = _workspace()
    for _ in range(3):
        _dominated(workspace, discipline_id, subject_id)
    later = FixedClock(Instant(datetime(2026, 12, 24, 15, tzinfo=UTC)))
    result = (
        list_subject_priorities(workspace_id=workspace.id, clock=later)
        .collect_more_evidence[0]
        .result
    )
    assert result.subject_id == subject_id
    assert result.recurrence_eligible_count == 0
    assert result.comparable_question_count == 0
    assert result.r is result.d is result.score is None


@pytest.mark.django_db(transaction=True)
def test_window_boundaries_are_inclusive_and_use_one_civil_reference_date() -> None:
    workspace, discipline_id, subject_id = _workspace()
    for _ in range(3):
        _dominated(workspace, discipline_id, subject_id)
    recent_boundary = FixedClock(
        Instant(datetime(2026, 9, 24, 15, tzinfo=UTC) + timedelta(days=28))
    )
    in_window = list_subject_priorities(workspace_id=workspace.id, clock=recent_boundary)
    assert in_window.ranked[0].result.comparable_question_count == 3
    after_recent_boundary = FixedClock(
        Instant(datetime(2026, 9, 24, 15, tzinfo=UTC) + timedelta(days=29))
    )
    out_window = list_subject_priorities(workspace_id=workspace.id, clock=after_recent_boundary)
    assert out_window.collect_more_evidence[0].result.comparable_question_count == 0
    recurrence_boundary = FixedClock(
        Instant(datetime(2026, 9, 24, 15, tzinfo=UTC) + timedelta(days=58))
    )
    assert (
        list_subject_priorities(workspace_id=workspace.id, clock=recurrence_boundary)
        .collect_more_evidence[0]
        .result.recurrence_eligible_count
        == 3
    )
    after_recurrence_boundary = FixedClock(
        Instant(datetime(2026, 9, 24, 15, tzinfo=UTC) + timedelta(days=59))
    )
    assert (
        list_subject_priorities(workspace_id=workspace.id, clock=after_recurrence_boundary)
        .collect_more_evidence[0]
        .result.recurrence_eligible_count
        == 0
    )


@pytest.mark.django_db(transaction=True)
def test_subject_list_batches_domain_and_priority_across_four_subjects() -> None:
    workspace, discipline_id, first_subject_id = _workspace()
    subject_ids = [first_subject_id]
    subject_ids.extend(
        create_subject(
            workspace_id=workspace.id, discipline_id=discipline_id, name=f"Subject {index}"
        ).id
        for index in range(2, 5)
    )
    for subject_id in subject_ids:
        for _ in range(3):
            _dominated(workspace, discipline_id, subject_id)
    with CaptureQueriesContext(connection) as queries:
        listing = list_subject_priorities(workspace_id=workspace.id, clock=CLOCK)
    print({"subjects": 4, "questions": 12, "queries": len(queries)})
    assert len(listing.ranked) == 4
    assert len(queries) <= 18
