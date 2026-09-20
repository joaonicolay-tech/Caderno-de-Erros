"""Reconstrução mínima das projeções de revisão após correção de Attempt."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from django.core.exceptions import ValidationError
from django.db.models import F, Q

from modules.accounts.models import Workspace
from modules.attempts.models import Attempt, AttemptStatus, AttemptType
from shared.domain.time import Calendar, Clock, LocalDate, TimeZoneId

from .models import (
    Review,
    ReviewCycle,
    ReviewCycleOriginKind,
    ReviewCycleState,
    ReviewState,
)
from .policies import ReviewSchedulePolicy, ReviewStage


@dataclass(frozen=True, slots=True)
class ReconstructionResult:
    superseded_cycle_ids: tuple[uuid.UUID, ...]
    cancelled_review_ids: tuple[uuid.UUID, ...]
    current_cycle_id: uuid.UUID | None
    current_review_id: uuid.UUID | None


class AttemptDerivedStateRebuilder:
    """Preserve fatos concluídos e substitua somente a projeção operacional."""

    def __init__(self, *, workspace_id: uuid.UUID, clock: Clock) -> None:
        self.workspace_id = workspace_id
        self.clock = clock
        self.calendar = Calendar(clock)
        self.schedule = ReviewSchedulePolicy(clock=clock, calendar=self.calendar)

    def rebuild(
        self,
        *,
        voided: Attempt,
        replacement: Attempt | None,
    ) -> ReconstructionResult:
        if voided.workspace_id != self.workspace_id or (
            replacement is not None and replacement.workspace_id != self.workspace_id
        ):
            raise ValidationError("A reconstrução não pode atravessar Workspace.")
        if voided.attempt_type == AttemptType.INITIAL:
            return self._rebuild_initial(voided=voided, replacement=replacement)
        return self._rebuild_review(voided=voided, replacement=replacement)

    def _rebuild_initial(
        self,
        *,
        voided: Attempt,
        replacement: Attempt | None,
    ) -> ReconstructionResult:
        affected = tuple(
            ReviewCycle.objects.select_for_update()
            .filter(
                workspace_id=self.workspace_id,
                question_id=voided.question_id,
                state__in=(ReviewCycleState.ACTIVE, ReviewCycleState.COMPLETED),
            )
            .filter(
                Q(origin_attempt_id=voided.id)
                | Q(
                    reviews__state=ReviewState.PENDING, reviews__scheduled_from_attempt_id=voided.id
                )
            )
            .distinct()
        )
        manual_cycle_ids = [
            cycle.id for cycle in affected if cycle.origin_kind == ReviewCycleOriginKind.MANUAL
        ]
        manual_pending = (
            Review.objects.filter(
                review_cycle_id__in=manual_cycle_ids,
                state=ReviewState.PENDING,
            )
            .order_by("created_at", "id")
            .first()
        )
        superseded, cancelled = self._supersede(affected)
        if replacement is not None and replacement.is_correct and manual_pending is not None:
            cycle, review = self._correction_projection(
                anchor=replacement,
                revision_id=replacement.question_revision_id,
                question_id=replacement.question_id,
                stage_code=manual_pending.stage_code,
                due_date=manual_pending.current_due_date,
                transition_code="CORRECTION_PRESERVE_MANUAL",
                policy_code=manual_pending.policy_code,
                started_at=self.clock.now().value,
            )
            return ReconstructionResult(superseded, cancelled, cycle.id, review.id)
        if replacement is None or replacement.is_correct:
            return ReconstructionResult(superseded, cancelled, None, None)
        if ReviewCycle.objects.filter(
            workspace_id=self.workspace_id,
            question_id=voided.question_id,
            state=ReviewCycleState.ACTIVE,
        ).exists():
            return ReconstructionResult(superseded, cancelled, None, None)
        cycle, review = self._initial_error_projection(replacement)
        return ReconstructionResult(superseded, cancelled, cycle.id, review.id)

    def _rebuild_review(
        self,
        *,
        voided: Attempt,
        replacement: Attempt | None,
    ) -> ReconstructionResult:
        if voided.review_id is None:
            raise ValidationError("A Attempt de REVIEW não possui Review válida no contexto.")
        target = (
            Review.objects.select_related("review_cycle")
            .filter(
                pk=voided.review_id,
                workspace_id=self.workspace_id,
                question_id=voided.question_id,
            )
            .first()
        )
        if target is None:
            raise ValidationError("A Attempt de REVIEW não possui Review válida no contexto.")
        affected = (
            ReviewCycle.objects.select_for_update()
            .filter(
                workspace_id=self.workspace_id,
                question_id=voided.question_id,
            )
            .filter(
                Q(state=ReviewCycleState.ACTIVE)
                | Q(
                    pk=target.review_cycle_id,
                    state=ReviewCycleState.COMPLETED,
                )
                | Q(
                    origin_attempt_id=voided.id,
                    state=ReviewCycleState.COMPLETED,
                )
            )
        )
        superseded, cancelled = self._supersede(tuple(affected.distinct()))
        if replacement is None:
            cycle, review = self._retry_projection(voided=voided, target=target)
            return ReconstructionResult(superseded, cancelled, cycle.id, review.id)

        workspace = Workspace.objects.only("timezone_name").get(pk=self.workspace_id)
        decision = self.schedule.decide(
            current_stage=ReviewStage(target.stage_code),
            is_correct=replacement.is_correct,
            time_zone_id=TimeZoneId(workspace.timezone_name),
            policy_code=target.policy_code,
        )
        if decision.next_stage is None:
            cycle = ReviewCycle.objects.create(
                workspace_id=self.workspace_id,
                question_id=voided.question_id,
                origin_attempt=replacement,
                origin_question_revision_id=replacement.question_revision_id,
                origin_kind=ReviewCycleOriginKind.ATTEMPT_CORRECTION,
                policy_code=decision.policy_code,
                state=ReviewCycleState.COMPLETED,
                started_at=decision.evaluated_at.value,
                completed_at=decision.evaluated_at.value,
            )
            return ReconstructionResult(superseded, cancelled, cycle.id, None)
        if decision.next_due_date is None:
            raise ValidationError("A policy não produziu data para a próxima Review.")
        cycle, review = self._correction_projection(
            anchor=replacement,
            revision_id=replacement.question_revision_id,
            question_id=voided.question_id,
            stage_code=decision.next_stage.value,
            due_date=decision.next_due_date.value,
            transition_code=decision.transition_code,
            policy_code=decision.policy_code,
            started_at=decision.evaluated_at.value,
        )
        return ReconstructionResult(superseded, cancelled, cycle.id, review.id)

    def _supersede(
        self, cycles: tuple[ReviewCycle, ...]
    ) -> tuple[tuple[uuid.UUID, ...], tuple[uuid.UUID, ...]]:
        now = self.clock.now().value
        cycle_ids = tuple(cycle.id for cycle in cycles)
        if not cycle_ids:
            return (), ()
        pending_ids = tuple(
            Review.objects.filter(
                review_cycle_id__in=cycle_ids,
                state=ReviewState.PENDING,
            ).values_list("id", flat=True)
        )
        if pending_ids:
            Review.objects.filter(id__in=pending_ids, state=ReviewState.PENDING).update(
                state=ReviewState.CANCELLED,
                lock_version=F("lock_version") + 1,
                updated_at=now,
            )
        changed = ReviewCycle.objects.filter(
            id__in=cycle_ids,
            state__in=(ReviewCycleState.ACTIVE, ReviewCycleState.COMPLETED),
        ).update(
            state=ReviewCycleState.SUPERSEDED,
            superseded_at=now,
            lock_version=F("lock_version") + 1,
            updated_at=now,
        )
        if changed != len(cycle_ids):
            raise ValidationError("O ciclo mudou durante a reconstrução.")
        return cycle_ids, pending_ids

    def _initial_error_projection(self, replacement: Attempt) -> tuple[ReviewCycle, Review]:
        due = replacement.local_date + timedelta(days=1)
        cycle = ReviewCycle.objects.create(
            workspace_id=self.workspace_id,
            question_id=replacement.question_id,
            origin_attempt=replacement,
            origin_question_revision_id=replacement.question_revision_id,
            origin_kind=ReviewCycleOriginKind.INITIAL_ERROR,
            started_at=replacement.occurred_at,
        )
        review = Review.objects.create(
            workspace_id=self.workspace_id,
            question_id=replacement.question_id,
            review_cycle=cycle,
            sequence_number=1,
            stage_code="D1",
            first_due_date=due,
            current_due_date=due,
            scheduled_from_attempt=replacement,
            transition_code="INITIAL_ERROR_TO_D1",
        )
        return cycle, review

    def _retry_projection(self, *, voided: Attempt, target: Review) -> tuple[ReviewCycle, Review]:
        anchor = (
            Attempt.objects.filter(
                workspace_id=self.workspace_id,
                question_id=voided.question_id,
                status=AttemptStatus.VALID,
                occurred_at__lte=voided.occurred_at,
            )
            .exclude(pk=voided.id)
            .order_by("-occurred_at", "-created_at", "-id")
            .first()
        )
        if anchor is None and target.stage_code != "D1":
            raise ValidationError("Não existe fato válido anterior para reconstruir a etapa.")
        revision_id = anchor.question_revision_id if anchor else voided.question_revision_id
        return self._correction_projection(
            anchor=anchor,
            revision_id=revision_id,
            question_id=voided.question_id,
            stage_code=target.stage_code,
            due_date=target.current_due_date,
            transition_code="CORRECTION_RETRY_VOIDED",
            policy_code=target.policy_code,
            started_at=self.clock.now().value,
        )

    def _correction_projection(
        self,
        *,
        anchor: Attempt | None,
        revision_id: uuid.UUID,
        question_id: uuid.UUID,
        stage_code: str,
        due_date: date | LocalDate,
        transition_code: str,
        policy_code: str,
        started_at: datetime,
    ) -> tuple[ReviewCycle, Review]:
        due_value = due_date.value if isinstance(due_date, LocalDate) else due_date
        cycle = ReviewCycle.objects.create(
            workspace_id=self.workspace_id,
            question_id=question_id,
            origin_attempt=anchor,
            origin_question_revision_id=revision_id,
            origin_kind=ReviewCycleOriginKind.ATTEMPT_CORRECTION,
            policy_code=policy_code,
            started_at=started_at,
        )
        review = Review.objects.create(
            workspace_id=self.workspace_id,
            question_id=question_id,
            review_cycle=cycle,
            sequence_number=1,
            stage_code=stage_code,
            first_due_date=due_value,
            current_due_date=due_value,
            scheduled_from_attempt=anchor,
            transition_code=transition_code,
            policy_code=policy_code,
        )
        return cycle, review
