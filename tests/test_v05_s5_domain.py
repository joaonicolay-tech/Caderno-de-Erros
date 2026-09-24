"""S5 application: prospective transitions, manual reopening and batched reads."""

import uuid
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from pathlib import Path
from time import perf_counter

import pytest
from django.core.exceptions import ValidationError
from django.db import close_old_connections, connection
from django.test.utils import CaptureQueriesContext

from modules.accounts.models import User, Workspace
from modules.attempts.corrections import AttemptCorrectionService
from modules.attempts.models import Attempt, AttemptType
from modules.domain.models import MasteryEventType, MasteryStateEvent
from modules.domain.policy import MasteryState, aggregate_hierarchy
from modules.domain.services import (
    DomainConflictError,
    DomainLifecycleService,
    current_domain,
    current_domains,
    hierarchy_domain,
)
from modules.operations.integrity import run_integrity_check
from modules.questions.deletion import PermanentQuestionDeletionService
from modules.questions.exceptions import QuestionCatalogConcurrencyError
from modules.questions.models import Alternative, Question, QuestionRevision
from modules.questions.services import AlternativeInput, archive_question, create_active
from modules.reviews.models import (
    ManualCyclePurpose,
    Review,
    ReviewCycle,
    ReviewCycleOriginKind,
    ReviewCycleState,
    ReviewStageCode,
    ReviewState,
)
from modules.taxonomy.services import create_discipline, create_subject, create_subsubject
from shared.application.bootstrap import bootstrap_local_workspace
from shared.domain.time import Clock, FixedClock, Instant

NOW = datetime(2026, 9, 24, 15, tzinfo=UTC)
CLOCK = FixedClock(Instant(NOW))


def _workspace() -> tuple[Workspace, uuid.UUID, uuid.UUID]:
    owner = User.objects.create_user(email=f"s5-{uuid.uuid4()}@example.test")
    workspace = Workspace.objects.create(
        owner_user=owner, name="S5", timezone_name="America/Sao_Paulo"
    )
    discipline = create_discipline(workspace_id=workspace.id, name="Discipline")
    subject = create_subject(workspace_id=workspace.id, discipline_id=discipline.id, name="Subject")
    return workspace, discipline.id, subject.id


def _question(
    workspace: Workspace,
    discipline_id: uuid.UUID,
    subject_id: uuid.UUID,
    *,
    clock: Clock = CLOCK,
    subsubject_id: uuid.UUID | None = None,
) -> Question:
    return create_active(
        workspace_id=workspace.id,
        discipline_id=discipline_id,
        subject_id=subject_id,
        subsubject_id=subsubject_id,
        stem=f"S5 Question {uuid.uuid4()}",
        alternatives=[AlternativeInput("Correct", "A"), AlternativeInput("Wrong", "B")],
        correct_alternative_position=1,
        explanation="Explanation",
        clock=clock,
    )


def _attempt(
    workspace: Workspace,
    question: Question,
    *,
    at: datetime,
    correct: bool,
    review: Review | None = None,
) -> Attempt:
    revision = QuestionRevision.objects.get(question=question, is_current=True)
    alternative = Alternative.objects.get(question_revision=revision, position=1 if correct else 2)
    return Attempt.objects.create(
        workspace=workspace,
        question=question,
        question_revision=revision,
        review=review,
        attempt_type=AttemptType.REVIEW if review else AttemptType.INITIAL,
        selected_alternative=alternative,
        is_correct=correct,
        occurred_at=at,
        timezone_name=workspace.timezone_name,
        local_date=at.date(),
        idempotency_key=uuid.uuid4(),
    )


def _dominated(workspace: Workspace, discipline_id: uuid.UUID, subject_id: uuid.UUID) -> Question:
    initial_at = NOW - timedelta(days=53)
    question = _question(
        workspace, discipline_id, subject_id, clock=FixedClock(Instant(initial_at))
    )
    initial = _attempt(workspace, question, at=initial_at, correct=True)
    cycle = ReviewCycle.objects.get(question=question, state=ReviewCycleState.ACTIVE)
    first_review = Review.objects.get(review_cycle=cycle, stage_code=ReviewStageCode.D1)
    prior = initial
    for number, stage, days in (
        (1, ReviewStageCode.D1, 52),
        (2, ReviewStageCode.D7, 45),
        (3, ReviewStageCode.D14, 31),
        (4, ReviewStageCode.D30, 1),
    ):
        at = NOW - timedelta(days=days)
        if number == 1:
            review = first_review
            Review.objects.filter(pk=review.id).update(state=ReviewState.COMPLETED, completed_at=at)
        else:
            review = Review.objects.create(
                workspace=workspace,
                question=question,
                review_cycle=cycle,
                sequence_number=number,
                stage_code=stage,
                state=ReviewState.COMPLETED,
                first_due_date=at.date(),
                current_due_date=at.date(),
                scheduled_from_attempt=prior,
                transition_code={
                    ReviewStageCode.D7: "ADVANCE_D1_TO_D7",
                    ReviewStageCode.D14: "ADVANCE_D7_TO_D14",
                    ReviewStageCode.D30: "ADVANCE_D14_TO_D30",
                }[stage],
                completed_at=at,
            )
        prior = _attempt(workspace, question, at=at, correct=True, review=review)
    ReviewCycle.objects.filter(pk=cycle.id).update(
        state=ReviewCycleState.COMPLETED, completed_at=NOW - timedelta(days=1)
    )
    return question


@pytest.mark.django_db(transaction=True)
def test_legacy_recognition_and_manual_reopen_are_prospective_atomic_and_idempotent() -> None:
    workspace, discipline_id, subject_id = _workspace()
    question = _dominated(workspace, discipline_id, subject_id)
    service = DomainLifecycleService(workspace_id=workspace.id, clock=CLOCK)
    assert (
        current_domain(
            workspace_id=workspace.id, question_id=question.id, clock=CLOCK
        ).current_mastery
        == MasteryState.DOMINATED
    )
    assert not MasteryStateEvent.objects.exists()
    recognized = current_domain(workspace_id=workspace.id, question_id=question.id, clock=CLOCK)
    assert len(recognized.mastery_criteria) == 6
    assert all(item.satisfied for item in recognized.mastery_criteria)
    assert recognized.mastery_criteria[0].evidence_ids

    service.reconcile(question_id=question.id)
    service.reconcile(question_id=question.id)
    first = MasteryStateEvent.objects.get(question=question)
    assert (first.event_type, first.sequence, first.occurred_at) == (
        MasteryEventType.DOMINATED,
        1,
        NOW,
    )
    result = service.manual_reopen(question_id=question.id, reason_code="REVISIT_TOPIC")
    assert result.current_mastery == MasteryState.NOT_DOMINATED
    assert result.reason_codes == ("MANUAL_REOPEN_REQUIRES_NEW_D30",)
    assert result.mastery_criteria[-1].code == "MANUAL_REOPEN_NEW_CORRECT_D30"
    assert not result.mastery_criteria[-1].satisfied
    cycle = ReviewCycle.objects.get(
        question=question, manual_purpose=ManualCyclePurpose.MASTERY_REOPEN
    )
    d1 = Review.objects.get(review_cycle=cycle)
    assert cycle.origin_kind == ReviewCycleOriginKind.MANUAL
    latest_attempt_id = (
        first.question.attempts.order_by("-occurred_at").values_list("id", flat=True).first()
    )
    assert cycle.origin_attempt_id == latest_attempt_id
    assert (d1.stage_code, d1.first_due_date, d1.current_due_date) == (
        ReviewStageCode.D1,
        (NOW + timedelta(days=1)).date(),
        (NOW + timedelta(days=1)).date(),
    )
    assert d1.scheduled_from_attempt_id == cycle.origin_attempt_id
    assert list(
        MasteryStateEvent.objects.filter(question=question)
        .order_by("sequence")
        .values_list("event_type", flat=True)
    ) == [MasteryEventType.DOMINATED, MasteryEventType.MANUAL_REOPENED]
    with pytest.raises(DomainConflictError):
        service.manual_reopen(question_id=question.id, reason_code="REVISIT_TOPIC")
    assert MasteryStateEvent.objects.filter(question=question).count() == 2
    assert (
        ReviewCycle.objects.filter(
            question=question, manual_purpose=ManualCyclePurpose.MASTERY_REOPEN
        ).count()
        == 1
    )


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("fault", ["after_cycle", "after_d1", "after_event"])
def test_manual_reopen_faults_roll_back_cycle_review_and_event(fault: str) -> None:
    workspace, discipline_id, subject_id = _workspace()
    question = _dominated(workspace, discipline_id, subject_id)
    service = DomainLifecycleService(workspace_id=workspace.id, clock=CLOCK)
    service.reconcile(question_id=question.id)
    before_version = Question.objects.get(pk=question.id).lock_version

    def inject(point: str) -> None:
        if point == fault:
            raise RuntimeError("injected")

    with pytest.raises(RuntimeError, match="injected"):
        service.manual_reopen(
            question_id=question.id, reason_code="REVISIT_TOPIC", fault_hook=inject
        )
    assert MasteryStateEvent.objects.filter(question=question).count() == 1
    assert not ReviewCycle.objects.filter(
        question=question, manual_purpose=ManualCyclePurpose.MASTERY_REOPEN
    ).exists()
    assert Question.objects.get(pk=question.id).lock_version == before_version


@pytest.mark.django_db(transaction=True)
def test_simultaneous_manual_reopen_has_one_event_cycle_and_d1() -> None:
    workspace, discipline_id, subject_id = _workspace()
    question = _dominated(workspace, discipline_id, subject_id)
    service = DomainLifecycleService(workspace_id=workspace.id, clock=CLOCK)
    service.reconcile(question_id=question.id)

    def reopen() -> str:
        close_old_connections()
        try:
            service.manual_reopen(question_id=question.id, reason_code="REVISIT_TOPIC")
            return "opened"
        except DomainConflictError:
            return "conflict"
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(lambda _: reopen(), range(2)))

    assert sorted(outcomes) == ["conflict", "opened"]
    assert (
        MasteryStateEvent.objects.filter(
            question=question, event_type=MasteryEventType.MANUAL_REOPENED
        ).count()
        == 1
    )
    cycles = ReviewCycle.objects.filter(
        question=question, manual_purpose=ManualCyclePurpose.MASTERY_REOPEN
    )
    assert cycles.count() == 1
    assert (
        Review.objects.filter(review_cycle__in=cycles, stage_code=ReviewStageCode.D1).count() == 1
    )


@pytest.mark.django_db(transaction=True)
def test_manual_reopen_and_archive_race_commits_only_one_path() -> None:
    workspace, discipline_id, subject_id = _workspace()
    question = _dominated(workspace, discipline_id, subject_id)
    DomainLifecycleService(workspace_id=workspace.id, clock=CLOCK).reconcile(
        question_id=question.id
    )
    question.refresh_from_db()

    def act(kind: str) -> str:
        close_old_connections()
        try:
            if kind == "manual":
                DomainLifecycleService(workspace_id=workspace.id, clock=CLOCK).manual_reopen(
                    question_id=question.id, reason_code="REVISIT_TOPIC"
                )
            else:
                archive_question(
                    workspace_id=workspace.id,
                    question_id=question.id,
                    expected_lock_version=question.lock_version,
                    clock=CLOCK,
                )
            return kind
        except (DomainConflictError, QuestionCatalogConcurrencyError):
            return "conflict"
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(act, ("manual", "archive")))
    assert sorted(outcomes) in (["archive", "conflict"], ["conflict", "manual"])
    question.refresh_from_db()
    manual_events = MasteryStateEvent.objects.filter(
        question=question, event_type=MasteryEventType.MANUAL_REOPENED
    ).count()
    manual_cycles = ReviewCycle.objects.filter(
        question=question, manual_purpose=ManualCyclePurpose.MASTERY_REOPEN
    ).count()
    if question.status == "ARCHIVED":
        assert manual_events == manual_cycles == 0
    else:
        assert manual_events == manual_cycles == 1


@pytest.mark.django_db(transaction=True)
def test_aging_read_does_not_write_but_mutable_reconciliation_records_real_time() -> None:
    workspace, discipline_id, subject_id = _workspace()
    question = _dominated(workspace, discipline_id, subject_id)
    DomainLifecycleService(workspace_id=workspace.id, clock=CLOCK).reconcile(
        question_id=question.id
    )
    later = FixedClock(Instant(NOW + timedelta(days=200)))
    current = current_domain(workspace_id=workspace.id, question_id=question.id, clock=later)
    assert current.current_mastery == MasteryState.NOT_DOMINATED
    assert current.result.confidence is not None and current.result.confidence < 80
    assert not {item.code: item.satisfied for item in current.mastery_criteria}[
        "RN079_CONFIDENCE_AT_LEAST_80"
    ]
    assert MasteryStateEvent.objects.filter(question=question).count() == 1
    service = DomainLifecycleService(workspace_id=workspace.id, clock=later)
    service.reconcile(question_id=question.id)
    service.reconcile(question_id=question.id)
    events = list(MasteryStateEvent.objects.filter(question=question).order_by("sequence"))
    assert [event.event_type for event in events] == [
        MasteryEventType.DOMINATED,
        MasteryEventType.AUTO_REOPENED,
    ]
    assert events[-1].occurred_at == later.now().value
    assert events[-1].reason_code == "CONFIDENCE_BELOW_80"


@pytest.mark.django_db(transaction=True)
def test_hierarchy_is_batched_workspace_scoped_and_excludes_archived() -> None:
    workspace, discipline_id, subject_id = _workspace()
    ids = []
    for _ in range(4):
        question = _question(workspace, discipline_id, subject_id)
        _attempt(workspace, question, at=NOW - timedelta(days=2), correct=True)
        ids.append(question.id)
    archived = _question(workspace, discipline_id, subject_id)
    unperformed = _question(workspace, discipline_id, subject_id)
    archive_question(
        workspace_id=workspace.id,
        question_id=archived.id,
        expected_lock_version=archived.lock_version,
        clock=CLOCK,
    )
    with CaptureQueriesContext(connection) as queries:
        batch = current_domains(workspace_id=workspace.id, question_ids=ids, clock=CLOCK)
    assert len(queries) <= 9
    assessment = hierarchy_domain(
        workspace_id=workspace.id, level="subject", target_id=subject_id, clock=CLOCK
    )
    expected = aggregate_hierarchy(tuple(item.result for item in batch.values()))
    assert assessment.aggregate.domain_index == expected.domain_index
    assert assessment.aggregate.confidence_hierarchical == expected.confidence_hierarchical
    assert set(assessment.aggregate.question_ids) == set(expected.question_ids)
    assert assessment.aggregate.question_count == 4
    assert set(assessment.exclusions) == {
        (archived.id, "QUESTION_NOT_ACTIVE"),
        (unperformed.id, "QUESTION_NOT_PERFORMED"),
    }
    assert not current_domains(workspace_id=uuid.uuid4(), question_ids=ids, clock=CLOCK)
    with pytest.raises(Question.DoesNotExist):
        current_domain(workspace_id=uuid.uuid4(), question_id=ids[0], clock=CLOCK)


@pytest.mark.django_db(transaction=True)
def test_hierarchy_subsubject_subject_and_discipline_membership() -> None:
    workspace, discipline_id, subject_id = _workspace()
    first = create_subsubject(workspace_id=workspace.id, subject_id=subject_id, name="First")
    second = create_subsubject(workspace_id=workspace.id, subject_id=subject_id, name="Second")
    first_q = _question(workspace, discipline_id, subject_id, subsubject_id=first.id)
    second_q = _question(workspace, discipline_id, subject_id, subsubject_id=second.id)
    for question in (first_q, second_q):
        _attempt(workspace, question, at=NOW - timedelta(days=1), correct=True)
    sub = hierarchy_domain(
        workspace_id=workspace.id, level="subsubject", target_id=first.id, clock=CLOCK
    )
    subject = hierarchy_domain(
        workspace_id=workspace.id, level="subject", target_id=subject_id, clock=CLOCK
    )
    discipline = hierarchy_domain(
        workspace_id=workspace.id, level="discipline", target_id=discipline_id, clock=CLOCK
    )
    assert sub.aggregate.question_ids == (first_q.id,)
    assert set(subject.aggregate.question_ids) == {first_q.id, second_q.id}
    assert subject.aggregate == discipline.aggregate
    with pytest.raises(type(first).DoesNotExist):
        hierarchy_domain(
            workspace_id=uuid.uuid4(), level="subsubject", target_id=first.id, clock=CLOCK
        )


@pytest.mark.django_db(transaction=True)
def test_void_and_archive_reopen_only_current_mastery_and_keep_history() -> None:
    workspace, discipline_id, subject_id = _workspace()
    question = _dominated(workspace, discipline_id, subject_id)
    service = DomainLifecycleService(workspace_id=workspace.id, clock=CLOCK)
    service.reconcile(question_id=question.id)
    d30 = Attempt.objects.get(question=question, review__stage_code=ReviewStageCode.D30)
    AttemptCorrectionService(workspace_id=workspace.id, clock=CLOCK).void(
        attempt_id=d30.id,
        expected_tip_id=d30.id,
        reason_code="RESULT_CORRECTION",
    )
    assert (
        current_domain(
            workspace_id=workspace.id, question_id=question.id, clock=CLOCK
        ).current_mastery
        == MasteryState.NOT_DOMINATED
    )
    assert list(
        MasteryStateEvent.objects.filter(question=question)
        .order_by("sequence")
        .values_list("event_type", flat=True)
    ) == [MasteryEventType.DOMINATED, MasteryEventType.AUTO_REOPENED]
    assert MasteryStateEvent.objects.filter(
        question=question, event_type=MasteryEventType.DOMINATED
    ).exists()

    other = _dominated(workspace, discipline_id, subject_id)
    service.reconcile(question_id=other.id)
    other.refresh_from_db()
    archive_question(
        workspace_id=workspace.id,
        question_id=other.id,
        expected_lock_version=other.lock_version,
        clock=CLOCK,
    )
    assert not current_domains(workspace_id=workspace.id, question_ids=(other.id,), clock=CLOCK)
    assert list(
        MasteryStateEvent.objects.filter(question=other)
        .order_by("sequence")
        .values_list("event_type", flat=True)
    ) == [MasteryEventType.DOMINATED, MasteryEventType.AUTO_REOPENED]
    assert MasteryStateEvent.objects.filter(
        question=other, reason_code="QUESTION_ARCHIVED"
    ).exists()


@pytest.mark.django_db(transaction=True)
def test_replacement_with_new_valid_error_reopens_without_rewriting_history() -> None:
    workspace, discipline_id, subject_id = _workspace()
    question = _dominated(workspace, discipline_id, subject_id)
    service = DomainLifecycleService(workspace_id=workspace.id, clock=CLOCK)
    service.reconcile(question_id=question.id)
    d30 = Attempt.objects.get(question=question, review__stage_code=ReviewStageCode.D30)
    wrong = Alternative.objects.get(question_revision=d30.question_revision, position=2)
    replacement = AttemptCorrectionService(workspace_id=workspace.id, clock=CLOCK).replace(
        attempt_id=d30.id,
        expected_tip_id=d30.id,
        selected_alternative_id=wrong.id,
        reason_code="RESULT_CORRECTION",
    )
    assert replacement.replacement_attempt_id is not None
    assert (
        current_domain(
            workspace_id=workspace.id, question_id=question.id, clock=CLOCK
        ).current_mastery
        == MasteryState.NOT_DOMINATED
    )
    events = list(MasteryStateEvent.objects.filter(question=question).order_by("sequence"))
    assert [event.event_type for event in events] == [
        MasteryEventType.DOMINATED,
        MasteryEventType.AUTO_REOPENED,
    ]
    assert events[-1].reason_code == "NEW_VALID_ERROR"
    assert events[0].occurred_at == NOW


@pytest.mark.django_db(transaction=True)
def test_current_explanations_cover_no_data_and_provisional_without_writing() -> None:
    workspace, discipline_id, subject_id = _workspace()
    question = _question(workspace, discipline_id, subject_id)
    empty = current_domain(workspace_id=workspace.id, question_id=question.id, clock=CLOCK)
    assert empty.result.sufficiency.value == "NO_DATA"
    assert empty.result.domain_index is None
    assert empty.current_mastery == MasteryState.NOT_DOMINATED
    assert len(empty.mastery_criteria) == 6
    _attempt(workspace, question, at=NOW, correct=True)
    provisional = current_domain(workspace_id=workspace.id, question_id=question.id, clock=CLOCK)
    assert provisional.result.maturity.value == "PROVISIONAL"
    assert provisional.result.policy_version == "DOM-HEUR-1.0"
    assert provisional.result.included_attempt_ids
    assert not MasteryStateEvent.objects.filter(question=question).exists()


@pytest.mark.django_db(transaction=True)
def test_manual_reopen_requires_new_correct_d30_before_domination_returns() -> None:
    workspace, discipline_id, subject_id = _workspace()
    question = _dominated(workspace, discipline_id, subject_id)
    service = DomainLifecycleService(workspace_id=workspace.id, clock=CLOCK)
    service.manual_reopen(question_id=question.id, reason_code="REVISIT_TOPIC")
    cycle = ReviewCycle.objects.get(
        question=question, manual_purpose=ManualCyclePurpose.MASTERY_REOPEN
    )
    first = Review.objects.get(review_cycle=cycle, stage_code=ReviewStageCode.D1)
    prior = cycle.origin_attempt
    assert prior is not None
    for number, stage in enumerate(
        (ReviewStageCode.D1, ReviewStageCode.D7, ReviewStageCode.D14), 1
    ):
        review = (
            first
            if number == 1
            else Review.objects.create(
                workspace=workspace,
                question=question,
                review_cycle=cycle,
                sequence_number=number,
                stage_code=stage,
                first_due_date=(NOW + timedelta(days=number)).date(),
                current_due_date=(NOW + timedelta(days=number)).date(),
                scheduled_from_attempt=prior,
                transition_code=f"TEST_{stage}",
            )
        )
        at = NOW + timedelta(days=number)
        Review.objects.filter(pk=review.id).update(state=ReviewState.COMPLETED, completed_at=at)
        prior = _attempt(workspace, question, at=at, correct=True, review=review)
    assert (
        current_domain(
            workspace_id=workspace.id,
            question_id=question.id,
            clock=FixedClock(Instant(NOW + timedelta(days=4))),
        ).current_mastery
        == MasteryState.NOT_DOMINATED
    )
    at = NOW + timedelta(days=4)
    d30 = Review.objects.create(
        workspace=workspace,
        question=question,
        review_cycle=cycle,
        sequence_number=4,
        stage_code=ReviewStageCode.D30,
        state=ReviewState.COMPLETED,
        completed_at=at,
        first_due_date=at.date(),
        current_due_date=at.date(),
        scheduled_from_attempt=prior,
        transition_code="TEST_D30",
    )
    _attempt(workspace, question, at=at, correct=True, review=d30)
    ReviewCycle.objects.filter(pk=cycle.id).update(
        state=ReviewCycleState.COMPLETED, completed_at=at
    )
    later = DomainLifecycleService(workspace_id=workspace.id, clock=FixedClock(Instant(at)))
    assert later.reconcile(question_id=question.id).current_mastery == MasteryState.DOMINATED
    later.reconcile(question_id=question.id)
    assert list(
        MasteryStateEvent.objects.filter(question=question)
        .order_by("sequence")
        .values_list("event_type", flat=True)
    ) == [MasteryEventType.DOMINATED, MasteryEventType.MANUAL_REOPENED, MasteryEventType.DOMINATED]


@pytest.mark.django_db(transaction=True)
def test_event_is_append_only_and_foreign_manual_reopen_has_no_effect() -> None:
    workspace, discipline_id, subject_id = _workspace()
    foreign, _, _ = _workspace()
    question = _dominated(workspace, discipline_id, subject_id)
    service = DomainLifecycleService(workspace_id=workspace.id, clock=CLOCK)
    service.reconcile(question_id=question.id)
    event = MasteryStateEvent.objects.get(question=question)
    event.reason_code = "CHANGE"
    with pytest.raises(ValidationError):
        event.save()
    with pytest.raises(ValidationError):
        MasteryStateEvent.objects.filter(pk=event.id).update(reason_code="CHANGE")
    with pytest.raises(ValidationError):
        event.delete()
    with pytest.raises(DomainConflictError):
        DomainLifecycleService(workspace_id=foreign.id, clock=CLOCK).manual_reopen(
            question_id=question.id, reason_code="REVISIT_TOPIC"
        )
    with pytest.raises(ValidationError):
        service.manual_reopen(question_id=question.id, reason_code="")
    assert MasteryStateEvent.objects.filter(question=question).count() == 1


@pytest.mark.django_db(transaction=True)
def test_permanent_delete_removes_mastery_history_with_isolated_recovery(tmp_path: Path) -> None:
    workspace = bootstrap_local_workspace(timezone_id="America/Sao_Paulo").workspace
    discipline_id = create_discipline(workspace_id=workspace.id, name="Recovery").id
    subject_id = create_subject(
        workspace_id=workspace.id, discipline_id=discipline_id, name="Recovery"
    ).id
    question = _dominated(workspace, discipline_id, subject_id)
    DomainLifecycleService(workspace_id=workspace.id, clock=CLOCK).reconcile(
        question_id=question.id
    )
    integrity = run_integrity_check()
    assert not integrity.findings, [(f.invariant_id, f.message) for f in integrity.findings]
    service = PermanentQuestionDeletionService(workspace_id=workspace.id, clock=CLOCK)
    preview = service.preview(question_id=question.id)
    assert preview.eligible and preview.backup_required
    assert dict(preview.impact)["mastery_events"] == 1
    service.delete(
        question_id=question.id,
        expected_fingerprint=preview.fingerprint,
        confirmation_token=preview.confirmation_token,
        reason_code="USER_REQUEST",
        correlation_id=uuid.uuid4(),
        backup_path=tmp_path / "before.sqlite3",
        isolated_restore_path=tmp_path / "restored.sqlite3",
    )
    assert not MasteryStateEvent.objects.filter(question_id=question.id).exists()
    assert not Question.objects.filter(pk=question.id).exists()
    assert not current_domains(workspace_id=workspace.id, question_ids=(question.id,), clock=CLOCK)


@pytest.mark.django_db(transaction=True)
def test_on_demand_batch_subject_and_discipline_query_counts() -> None:
    workspace, discipline_id, subject_id = _workspace()
    second_subject = create_subject(
        workspace_id=workspace.id, discipline_id=discipline_id, name="Second subject"
    )
    second_discipline = create_discipline(workspace_id=workspace.id, name="Second discipline")
    third_subject = create_subject(
        workspace_id=workspace.id, discipline_id=second_discipline.id, name="Third subject"
    )
    fourth_subject = create_subject(
        workspace_id=workspace.id, discipline_id=second_discipline.id, name="Fourth subject"
    )
    subjects = (
        (discipline_id, subject_id),
        (discipline_id, second_subject.id),
        (second_discipline.id, third_subject.id),
        (second_discipline.id, fourth_subject.id),
    )
    question_ids = tuple(
        _dominated(workspace, did, sid).id for did, sid in subjects for _ in range(10)
    )

    def measure(call: Callable[[], object]) -> tuple[int, float]:
        started = perf_counter()
        with CaptureQueriesContext(connection) as captured:
            call()
        return len(captured), round((perf_counter() - started) * 1000, 2)

    one = measure(
        lambda: current_domain(workspace_id=workspace.id, question_id=question_ids[0], clock=CLOCK)
    )
    batch = measure(
        lambda: current_domains(workspace_id=workspace.id, question_ids=question_ids, clock=CLOCK)
    )
    subject = measure(
        lambda: hierarchy_domain(
            workspace_id=workspace.id, level="subject", target_id=subject_id, clock=CLOCK
        )
    )
    discipline = measure(
        lambda: hierarchy_domain(
            workspace_id=workspace.id, level="discipline", target_id=discipline_id, clock=CLOCK
        )
    )
    print(
        {
            "fixture": "40 Questions, 5 VALID Attempts each, 2 disciplines x 2 subjects x 10 Questions",
            "one": one,
            "batch": batch,
            "subject": subject,
            "discipline": discipline,
        }
    )
    assert batch[0] <= one[0] + 1
    assert subject[0] <= 14 and discipline[0] <= 14
