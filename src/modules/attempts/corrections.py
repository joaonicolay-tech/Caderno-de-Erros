"""Void/replacement transacionais e Workspace-scoped de Attempt."""

from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.db import DatabaseError, IntegrityError, transaction

from modules.operations.models import AuditEntityType, AuditEvent, AuditEventCode
from modules.operations.services import record_audit_event
from modules.operations.validators import normalize_reason_code
from modules.questions.models import Alternative
from modules.reviews.reconstruction import AttemptDerivedStateRebuilder, ReconstructionResult
from shared.domain.time import Clock, SystemClock, TimeZoneId

from .models import Attempt, PerceivedEase
from .persistence import run_sqlite_critical_write
from .selectors import AttemptChainError, resolve_attempt_chain

FaultHook = Callable[[str], None]


class AttemptCorrectionConflictError(RuntimeError):
    """A correção perdeu a precondição, o contexto ou a ponta esperada."""


@dataclass(frozen=True, slots=True)
class AttemptCorrectionImpact:
    requested_attempt_id: uuid.UUID
    effective_tip_id: uuid.UUID
    question_id: uuid.UUID
    attempt_type: str
    has_classification: bool
    affected_active_cycles: int
    affected_pending_reviews: int


@dataclass(frozen=True, slots=True)
class AttemptCorrectionResult:
    voided_attempt_id: uuid.UUID
    replacement_attempt_id: uuid.UUID | None
    correlation_id: uuid.UUID
    reconstruction: ReconstructionResult


class AttemptCorrectionService:
    """Única fronteira de mutation para o lifecycle estrutural S2B."""

    def __init__(self, *, workspace_id: uuid.UUID, clock: Clock | None = None) -> None:
        self.workspace_id = workspace_id
        self.clock = clock or SystemClock()

    def preview(self, *, attempt_id: uuid.UUID) -> AttemptCorrectionImpact:
        try:
            chain = resolve_attempt_chain(
                workspace_id=self.workspace_id,
                attempt_id=attempt_id,
            )
        except AttemptChainError as error:
            raise AttemptCorrectionConflictError(str(error)) from error
        tip = chain.tip
        if tip is None:
            raise AttemptCorrectionConflictError("A cadeia não possui ponta VALID efetiva.")
        from modules.reviews.models import Review, ReviewCycle, ReviewCycleState, ReviewState

        return AttemptCorrectionImpact(
            requested_attempt_id=attempt_id,
            effective_tip_id=tip.id,
            question_id=tip.question_id,
            attempt_type=tip.attempt_type,
            has_classification=hasattr(tip, "error_classification"),
            affected_active_cycles=ReviewCycle.objects.filter(
                workspace_id=self.workspace_id,
                question_id=tip.question_id,
                state=ReviewCycleState.ACTIVE,
            ).count(),
            affected_pending_reviews=Review.objects.filter(
                workspace_id=self.workspace_id,
                question_id=tip.question_id,
                state=ReviewState.PENDING,
            ).count(),
        )

    def void(
        self,
        *,
        attempt_id: uuid.UUID,
        expected_tip_id: uuid.UUID,
        reason_code: str,
        correlation_id: uuid.UUID | None = None,
        fault_hook: FaultHook | None = None,
    ) -> AttemptCorrectionResult:
        correlation = correlation_id or uuid.uuid4()
        reason = self._reason(reason_code)

        def write() -> AttemptCorrectionResult:
            with transaction.atomic(durable=True):
                existing = self._existing(
                    correlation,
                    replacement=False,
                    reason=reason,
                    requested_attempt_id=attempt_id,
                )
                if existing is not None:
                    return existing
                tip = self._locked_tip(attempt_id, expected_tip_id)
                voided = self._void_tip(tip, reason)
                self._fault(fault_hook, "after_void")
                reconstruction = AttemptDerivedStateRebuilder(
                    workspace_id=self.workspace_id,
                    clock=self.clock,
                ).rebuild(voided=voided, replacement=None)
                from modules.domain.services import DomainLifecycleService

                DomainLifecycleService(
                    workspace_id=self.workspace_id, clock=self.clock
                ).reconcile_in_transaction(
                    question_id=voided.question_id,
                    trigger_code="ESSENTIAL_EVIDENCE_VOIDED",
                )
                self._fault(fault_hook, "after_reconstruction")
                self._fault(fault_hook, "before_audit")
                record_audit_event(
                    workspace_id=self.workspace_id,
                    event_code=AuditEventCode.ATTEMPT_VOIDED,
                    entity_type=AuditEntityType.ATTEMPT,
                    entity_id=voided.id,
                    correlation_id=str(correlation),
                    reason_code=reason,
                )
                self._fault(fault_hook, "after_audit")
                return AttemptCorrectionResult(voided.id, None, correlation, reconstruction)

        return self._persist(write)

    def replace(
        self,
        *,
        attempt_id: uuid.UUID,
        expected_tip_id: uuid.UUID,
        selected_alternative_id: uuid.UUID,
        reason_code: str,
        perceived_ease: str | None = None,
        idempotency_key: uuid.UUID | None = None,
        correlation_id: uuid.UUID | None = None,
        fault_hook: FaultHook | None = None,
    ) -> AttemptCorrectionResult:
        correlation = correlation_id or uuid.uuid4()
        key = idempotency_key or correlation
        reason = self._reason(reason_code)
        ease = self._ease(perceived_ease)

        def write() -> AttemptCorrectionResult:
            with transaction.atomic(durable=True):
                existing = self._existing(
                    correlation,
                    replacement=True,
                    reason=reason,
                    requested_attempt_id=attempt_id,
                    selected_alternative_id=selected_alternative_id,
                    perceived_ease=ease,
                    idempotency_key=key,
                )
                if existing is not None:
                    return existing
                tip = self._locked_tip(attempt_id, expected_tip_id)
                alternative = Alternative.objects.filter(
                    pk=selected_alternative_id,
                    workspace_id=self.workspace_id,
                    question_revision_id=tip.question_revision_id,
                ).first()
                if alternative is None:
                    raise AttemptCorrectionConflictError(
                        "A alternativa não pertence à revisão e ao Workspace da ponta."
                    )
                voided = self._void_tip(tip, reason)
                self._fault(fault_hook, "after_void")
                occurred_at = self.clock.now().value
                replacement = Attempt.objects.create(
                    workspace_id=self.workspace_id,
                    question_id=tip.question_id,
                    question_revision_id=tip.question_revision_id,
                    review_id=tip.review_id,
                    attempt_type=tip.attempt_type,
                    selected_alternative=alternative,
                    is_correct=alternative.id == tip.question_revision.correct_alternative_id,
                    perceived_ease=ease,
                    occurred_at=occurred_at,
                    timezone_name=tip.timezone_name,
                    local_date=occurred_at.astimezone(TimeZoneId(tip.timezone_name).zone).date(),
                    replaces_attempt=voided,
                    idempotency_key=key,
                )
                self._fault(fault_hook, "after_replacement")
                reconstruction = AttemptDerivedStateRebuilder(
                    workspace_id=self.workspace_id,
                    clock=self.clock,
                ).rebuild(voided=voided, replacement=replacement)
                from modules.domain.services import DomainLifecycleService

                DomainLifecycleService(
                    workspace_id=self.workspace_id, clock=self.clock
                ).reconcile_in_transaction(
                    question_id=voided.question_id,
                    trigger_code="NEW_VALID_ERROR"
                    if not replacement.is_correct
                    else "ESSENTIAL_EVIDENCE_VOIDED",
                )
                self._fault(fault_hook, "after_reconstruction")
                self._fault(fault_hook, "before_audit")
                record_audit_event(
                    workspace_id=self.workspace_id,
                    event_code=AuditEventCode.ATTEMPT_VOIDED,
                    entity_type=AuditEntityType.ATTEMPT,
                    entity_id=voided.id,
                    related_entity_id=replacement.id,
                    correlation_id=str(correlation),
                    reason_code=reason,
                )
                record_audit_event(
                    workspace_id=self.workspace_id,
                    event_code=AuditEventCode.ATTEMPT_REPLACED,
                    entity_type=AuditEntityType.ATTEMPT,
                    entity_id=voided.id,
                    related_entity_id=replacement.id,
                    correlation_id=str(correlation),
                    reason_code=reason,
                )
                self._fault(fault_hook, "after_audit")
                return AttemptCorrectionResult(
                    voided.id,
                    replacement.id,
                    correlation,
                    reconstruction,
                )

        return self._persist(write)

    def _locked_tip(self, attempt_id: uuid.UUID, expected_tip_id: uuid.UUID) -> Attempt:
        try:
            chain = resolve_attempt_chain(
                workspace_id=self.workspace_id,
                attempt_id=attempt_id,
                for_update=True,
            )
        except AttemptChainError as error:
            raise AttemptCorrectionConflictError(str(error)) from error
        tip = chain.tip
        if tip is None or tip.id != expected_tip_id:
            raise AttemptCorrectionConflictError("A ponta efetiva mudou; recarregue o impacto.")
        return tip

    def _void_tip(self, tip: Attempt, reason: str) -> Attempt:
        changed = Attempt.objects.mark_voided(
            attempt_id=tip.id,
            workspace_id=self.workspace_id,
            voided_at=self.clock.now().value,
            void_reason=reason,
        )
        if changed != 1:
            raise AttemptCorrectionConflictError("A Attempt mudou durante a correção.")
        tip.refresh_from_db()
        return tip

    def _existing(
        self,
        correlation: uuid.UUID,
        *,
        replacement: bool,
        reason: str,
        requested_attempt_id: uuid.UUID,
        selected_alternative_id: uuid.UUID | None = None,
        perceived_ease: str | None = None,
        idempotency_key: uuid.UUID | None = None,
    ) -> AttemptCorrectionResult | None:
        code = AuditEventCode.ATTEMPT_REPLACED if replacement else AuditEventCode.ATTEMPT_VOIDED
        event = AuditEvent.objects.filter(
            workspace_id=self.workspace_id,
            event_code=code,
            correlation_id=correlation,
        ).first()
        if event is None:
            return None
        try:
            chain = resolve_attempt_chain(
                workspace_id=self.workspace_id,
                attempt_id=requested_attempt_id,
            )
        except AttemptChainError as error:
            raise AttemptCorrectionConflictError(str(error)) from error
        if event.entity_id not in {row.id for row in chain.attempts}:
            raise AttemptCorrectionConflictError(
                "A correlação já foi usada por uma correção diferente."
            )
        if (
            event.reason_code != reason
            or (replacement and event.related_entity_id is None)
            or (not replacement and event.related_entity_id is not None)
        ):
            raise AttemptCorrectionConflictError(
                "A correlação já foi usada por uma correção diferente."
            )
        if replacement:
            related_id = event.related_entity_id
            if related_id is None:
                raise AttemptCorrectionConflictError(
                    "A correlação já foi usada por uma correção diferente."
                )
            target = Attempt.objects.filter(
                pk=related_id,
                workspace_id=self.workspace_id,
            ).first()
            if target is None or (
                target.selected_alternative_id != selected_alternative_id
                or target.perceived_ease != perceived_ease
                or target.idempotency_key != idempotency_key
            ):
                raise AttemptCorrectionConflictError(
                    "A correlação já foi usada por uma correção diferente."
                )
        return AttemptCorrectionResult(
            event.entity_id,
            event.related_entity_id if replacement else None,
            correlation,
            ReconstructionResult((), (), None, None),
        )

    @staticmethod
    def _reason(value: str) -> str:
        try:
            normalized = normalize_reason_code(value, required=True)
        except ValidationError as error:
            raise AttemptCorrectionConflictError(str(error)) from error
        if normalized is None:
            raise AttemptCorrectionConflictError("Um código de motivo é obrigatório.")
        return normalized

    @staticmethod
    def _ease(value: str | None) -> str | None:
        if value in (None, ""):
            return None
        if value not in PerceivedEase.values:
            raise AttemptCorrectionConflictError("Percepção de facilidade inválida.")
        return value

    @staticmethod
    def _fault(hook: FaultHook | None, point: str) -> None:
        if hook is not None:
            hook(point)

    @staticmethod
    def _persist(operation: Callable[[], AttemptCorrectionResult]) -> AttemptCorrectionResult:
        try:
            return run_sqlite_critical_write(operation)
        except AttemptCorrectionConflictError:
            raise
        except (IntegrityError, ValidationError) as error:
            raise AttemptCorrectionConflictError(
                "A correção conflita com o estado atual."
            ) from error
        except DatabaseError as error:
            raise AttemptCorrectionConflictError(
                "Falha de persistência durante a correção."
            ) from error
