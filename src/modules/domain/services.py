"""Current Domain queries and atomic recognition of mastery transitions."""

from __future__ import annotations

import uuid
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import date

from django.db import IntegrityError, transaction
from django.db.models import F

from modules.accounts.models import Workspace
from modules.attempts.models import Attempt, AttemptStatus, AttemptType
from modules.attempts.persistence import run_sqlite_critical_write
from modules.operations.validators import normalize_reason_code
from modules.questions.models import Question, QuestionStatus
from modules.reviews.models import (
    ManualCyclePurpose,
    Review,
    ReviewCycle,
    ReviewCycleOriginKind,
    ReviewCycleState,
    ReviewStageCode,
)
from modules.taxonomy.models import Discipline, Subject, Subsubject
from shared.domain.time import Calendar, Clock, SystemClock, TimeZoneId

from .models import MasteryEventType, MasteryStateEvent
from .policy import (
    POLICY_VERSION,
    DomainInput,
    DomainResult,
    HierarchyAggregate,
    MasteryCriterion,
    MasteryState,
    ReviewStage,
    aggregate_hierarchy,
    evaluate_domain,
)
from .selectors import domain_inputs

FaultHook = Callable[[str], None]


class DomainConflictError(RuntimeError):
    """A Question, evidence or transition changed before commit."""


@dataclass(frozen=True, slots=True)
class CurrentDomain:
    result: DomainResult
    evaluated_on: date
    current_mastery: MasteryState
    reason_codes: tuple[str, ...]
    last_event_id: uuid.UUID | None
    mastery_criteria: tuple[MasteryCriterion, ...]


@dataclass(frozen=True, slots=True)
class HierarchyDomain:
    level: str
    target_id: uuid.UUID
    aggregate: HierarchyAggregate
    considered_question_ids: tuple[uuid.UUID, ...]
    exclusions: tuple[tuple[uuid.UUID, str], ...]
    policy_version: str
    evaluated_on: date


def _last_events(
    *, workspace_id: uuid.UUID, question_ids: Sequence[uuid.UUID]
) -> dict[uuid.UUID, MasteryStateEvent]:
    events: dict[uuid.UUID, MasteryStateEvent] = {}
    for event in MasteryStateEvent.objects.filter(
        workspace_id=workspace_id, question_id__in=question_ids
    ).order_by("question_id", "-sequence"):
        events.setdefault(event.question_id, event)
    return events


def _current(input_: DomainInput, event: MasteryStateEvent | None) -> CurrentDomain:
    result = evaluate_domain(input_)
    criteria = (*result.mastery_criteria, MasteryCriterion("RN079_QUESTION_ACTIVE", True))
    if event is not None and event.event_type == MasteryEventType.MANUAL_REOPENED:
        progressed = tuple(
            item
            for item in input_.attempts
            if item.review_cycle_id == str(event.manual_cycle_id)
            and item.review_stage == ReviewStage.D30
            and item.is_correct
        )
        criteria += (
            MasteryCriterion(
                "MANUAL_REOPEN_NEW_CORRECT_D30",
                bool(progressed),
                tuple(item.evidence_id for item in progressed),
            ),
        )
    if result.mastery != MasteryState.DOMINATED:
        return CurrentDomain(
            result,
            input_.evaluated_on,
            MasteryState.NOT_DOMINATED,
            ("RN079_UNSATISFIED",),
            event.id if event else None,
            criteria,
        )
    if event is not None and event.event_type == MasteryEventType.MANUAL_REOPENED:
        if not progressed:
            return CurrentDomain(
                result,
                input_.evaluated_on,
                MasteryState.NOT_DOMINATED,
                ("MANUAL_REOPEN_REQUIRES_NEW_D30",),
                event.id,
                criteria,
            )
    return CurrentDomain(
        result,
        input_.evaluated_on,
        MasteryState.DOMINATED,
        ("RN079_SATISFIED",),
        event.id if event else None,
        criteria,
    )


def current_domains(
    *, workspace_id: uuid.UUID, question_ids: Sequence[uuid.UUID], clock: Clock | None = None
) -> dict[uuid.UUID, CurrentDomain]:
    """A read-only view of current facts; GET never creates an event."""
    inputs = domain_inputs(workspace_id=workspace_id, question_ids=question_ids, clock=clock)
    events = _last_events(workspace_id=workspace_id, question_ids=tuple(inputs))
    return {
        question_id: _current(input_, events.get(question_id))
        for question_id, input_ in inputs.items()
    }


def current_domain(
    *, workspace_id: uuid.UUID, question_id: uuid.UUID, clock: Clock | None = None
) -> CurrentDomain:
    assessment = current_domains(
        workspace_id=workspace_id, question_ids=(question_id,), clock=clock
    ).get(question_id)
    if assessment is None:
        raise Question.DoesNotExist("Question ativa não disponível neste Workspace.")
    return assessment


def hierarchy_domain(
    *, workspace_id: uuid.UUID, level: str, target_id: uuid.UUID, clock: Clock | None = None
) -> HierarchyDomain:
    """Select the current taxonomic membership, then use S4 aggregate math."""
    if level == "discipline":
        Discipline.objects.get(pk=target_id, workspace_id=workspace_id)
    elif level == "subject":
        Subject.objects.get(pk=target_id, workspace_id=workspace_id)
    elif level == "subsubject":
        Subsubject.objects.get(pk=target_id, workspace_id=workspace_id)
    else:
        raise ValueError("Nível hierárquico desconhecido.")
    questions = list(
        Question.objects.filter(workspace_id=workspace_id, **{f"{level}_id": target_id})
        .order_by("id")
        .only("id", "status")
    )
    active_ids = tuple(q.id for q in questions if q.status == QuestionStatus.ACTIVE)
    performed_ids = set(
        Attempt.objects.filter(
            workspace_id=workspace_id,
            question_id__in=active_ids,
            attempt_type=AttemptType.INITIAL,
            status=AttemptStatus.VALID,
        ).values_list("question_id", flat=True)
    )
    assessments = current_domains(workspace_id=workspace_id, question_ids=active_ids, clock=clock)
    results = tuple(
        assessments[qid].result for qid in active_ids if qid in assessments and qid in performed_ids
    )
    aggregate = aggregate_hierarchy(results)
    exclusions = (
        tuple((q.id, "QUESTION_NOT_ACTIVE") for q in questions if q.status != QuestionStatus.ACTIVE)
        + tuple((qid, "QUESTION_NOT_PERFORMED") for qid in active_ids if qid not in performed_ids)
        + tuple(
            (result.question_id, "NO_DOMAIN_DATA")
            for result in results
            if result.domain_index is None
        )
    )
    return HierarchyDomain(
        level=level,
        target_id=target_id,
        aggregate=aggregate,
        considered_question_ids=active_ids,
        exclusions=exclusions,
        policy_version=results[0].policy_version if results else POLICY_VERSION,
        evaluated_on=(
            next(iter(assessments.values())).evaluated_on
            if assessments
            else Calendar(clock or SystemClock())
            .today(TimeZoneId(Workspace.objects.get(pk=workspace_id).timezone_name))
            .value
        ),
    )


class DomainLifecycleService:
    """Reconcile under Question CAS; callers may join an existing transaction."""

    def __init__(self, *, workspace_id: uuid.UUID, clock: Clock | None = None) -> None:
        self.workspace_id = workspace_id
        self.clock = clock or SystemClock()

    def reconcile(
        self, *, question_id: uuid.UUID, trigger_code: str | None = None
    ) -> CurrentDomain:
        def write() -> CurrentDomain:
            with transaction.atomic(durable=True):
                return self.reconcile_in_transaction(
                    question_id=question_id, trigger_code=trigger_code
                )

        return run_sqlite_critical_write(write)

    def reconcile_in_transaction(
        self, *, question_id: uuid.UUID, trigger_code: str | None = None
    ) -> CurrentDomain:
        question = (
            Question.objects.select_for_update()
            .filter(pk=question_id, workspace_id=self.workspace_id, status=QuestionStatus.ACTIVE)
            .first()
        )
        if question is None:
            raise DomainConflictError("Question ativa não disponível neste Workspace.")
        input_ = domain_inputs(
            workspace_id=self.workspace_id, question_ids=(question_id,), clock=self.clock
        )[question_id]
        latest = _last_events(workspace_id=self.workspace_id, question_ids=(question_id,)).get(
            question_id
        )
        current = _current(input_, latest)
        transition: str | None = None
        if current.current_mastery == MasteryState.DOMINATED and (
            latest is None or latest.event_type != MasteryEventType.DOMINATED
        ):
            transition = MasteryEventType.DOMINATED
        elif (
            latest is not None
            and latest.event_type == MasteryEventType.DOMINATED
            and current.current_mastery != MasteryState.DOMINATED
            and (
                trigger_code in {"NEW_VALID_ERROR", "ESSENTIAL_EVIDENCE_VOIDED"}
                or (current.result.confidence is not None and current.result.confidence < 80)
            )
        ):
            transition = MasteryEventType.AUTO_REOPENED
        if transition is not None:
            reason = trigger_code or (
                "CONFIDENCE_BELOW_80" if transition == MasteryEventType.AUTO_REOPENED else None
            )
            self._append(
                question=question,
                current=current,
                latest=latest,
                event_type=transition,
                reason_code=reason,
            )
        return current

    def manual_reopen(
        self, *, question_id: uuid.UUID, reason_code: str, fault_hook: FaultHook | None = None
    ) -> CurrentDomain:
        reason = normalize_reason_code(reason_code, required=True)
        if reason is None:
            raise DomainConflictError("Motivo obrigatório.")

        def write() -> CurrentDomain:
            with transaction.atomic(durable=True):
                question = (
                    Question.objects.select_for_update()
                    .filter(
                        pk=question_id, workspace_id=self.workspace_id, status=QuestionStatus.ACTIVE
                    )
                    .first()
                )
                if question is None:
                    raise DomainConflictError("Question ativa não disponível neste Workspace.")
                before = self.reconcile_in_transaction(question_id=question_id)
                question.refresh_from_db(fields=["lock_version"])
                if before.current_mastery != MasteryState.DOMINATED:
                    raise DomainConflictError("Question não está DOMINATED.")
                if ReviewCycle.objects.filter(
                    workspace_id=self.workspace_id,
                    question_id=question_id,
                    state=ReviewCycleState.ACTIVE,
                ).exists():
                    raise DomainConflictError("Question já possui ciclo ativo.")
                initial = domain_inputs(
                    workspace_id=self.workspace_id, question_ids=(question_id,), clock=self.clock
                )[question_id]
                if not initial.attempts:
                    raise DomainConflictError("Question sem Attempt válida.")
                latest_evidence = max(
                    initial.attempts, key=lambda item: (item.occurred_at, item.evidence_id)
                )
                latest_attempt = Attempt.objects.select_related("question_revision").get(
                    pk=uuid.UUID(latest_evidence.evidence_id), workspace_id=self.workspace_id
                )
                workspace = Workspace.objects.get(pk=self.workspace_id)
                now = self.clock.now().value
                due = Calendar.add_days(
                    Calendar(self.clock).today(TimeZoneId(workspace.timezone_name)), 1
                ).value
                cycle = ReviewCycle.objects.create(
                    workspace=workspace,
                    question=question,
                    origin_attempt=latest_attempt,
                    origin_question_revision=latest_attempt.question_revision,
                    origin_kind=ReviewCycleOriginKind.MANUAL,
                    manual_purpose=ManualCyclePurpose.MASTERY_REOPEN,
                    started_at=now,
                )
                self._fault(fault_hook, "after_cycle")
                Review.objects.create(
                    workspace=workspace,
                    question=question,
                    review_cycle=cycle,
                    sequence_number=1,
                    stage_code=ReviewStageCode.D1,
                    first_due_date=due,
                    current_due_date=due,
                    scheduled_from_attempt=latest_attempt,
                    transition_code="MANUAL_REOPEN_D1",
                )
                self._fault(fault_hook, "after_d1")
                latest_event = _last_events(
                    workspace_id=self.workspace_id, question_ids=(question_id,)
                ).get(question_id)
                self._append(
                    question=question,
                    current=before,
                    latest=latest_event,
                    event_type=MasteryEventType.MANUAL_REOPENED,
                    reason_code=reason,
                    manual_cycle=cycle,
                )
                self._fault(fault_hook, "after_event")
                return current_domain(
                    workspace_id=self.workspace_id, question_id=question_id, clock=self.clock
                )

        try:
            return run_sqlite_critical_write(write)
        except IntegrityError as error:
            raise DomainConflictError("O ciclo ou evento mudou concorrentemente.") from error

    def archive_in_transaction(self, *, question: Question) -> None:
        latest = _last_events(workspace_id=self.workspace_id, question_ids=(question.id,)).get(
            question.id
        )
        if latest is None or latest.event_type != MasteryEventType.DOMINATED:
            return
        input_ = domain_inputs(
            workspace_id=self.workspace_id, question_ids=(question.id,), clock=self.clock
        )[question.id]
        current = _current(input_, latest)
        self._append(
            question=question,
            current=current,
            latest=latest,
            event_type=MasteryEventType.AUTO_REOPENED,
            reason_code="QUESTION_ARCHIVED",
            cas=False,
        )

    def _append(
        self,
        *,
        question: Question,
        current: CurrentDomain,
        latest: MasteryStateEvent | None,
        event_type: str,
        reason_code: str | None,
        manual_cycle: ReviewCycle | None = None,
        cas: bool = True,
    ) -> MasteryStateEvent:
        if cas:
            updated = Question.objects.filter(
                pk=question.id, workspace_id=self.workspace_id, lock_version=question.lock_version
            ).update(lock_version=F("lock_version") + 1)
            if updated != 1:
                raise DomainConflictError("Question mudou durante a reconciliação.")
            question.lock_version += 1
        return MasteryStateEvent.objects.create(
            workspace_id=self.workspace_id,
            question=question,
            sequence=latest.sequence + 1 if latest else 1,
            event_type=event_type,
            formula_code=current.result.policy_version,
            evaluated_on=current.evaluated_on,
            domain_index=current.result.domain_index,
            confidence=current.result.confidence,
            reason_code=reason_code,
            manual_cycle=manual_cycle,
            occurred_at=self.clock.now().value,
        )

    @staticmethod
    def _fault(hook: FaultHook | None, point: str) -> None:
        if hook is not None:
            hook(point)
