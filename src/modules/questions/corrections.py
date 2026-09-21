"""Correção prospectiva e auditável do gabarito de uma Question."""

from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.db import DatabaseError, IntegrityError, transaction
from django.db.models import F

from modules.attempts.persistence import run_sqlite_critical_write
from modules.operations.models import AuditEntityType, AuditEvent, AuditEventCode
from modules.operations.services import record_audit_event
from modules.operations.validators import normalize_reason_code
from shared.domain.time import Clock, SystemClock

from .models import Question, QuestionRevision, QuestionStatus, RevisionChangeKind
from .services import _create_revision

FaultHook = Callable[[str], None]


class AnswerKeyCorrectionConflictError(RuntimeError):
    """A correção perdeu sua precondição ou conflita com estado persistido."""


@dataclass(frozen=True, slots=True)
class AnswerKeyCorrectionResult:
    question_id: uuid.UUID
    previous_revision_id: uuid.UUID
    new_revision_id: uuid.UUID
    correlation_id: uuid.UUID


class AnswerKeyCorrectionService:
    """Única fronteira S2C para mudar gabarito depois de fatos históricos."""

    def __init__(self, *, workspace_id: uuid.UUID, clock: Clock | None = None) -> None:
        self.workspace_id = workspace_id
        self.clock = clock or SystemClock()

    def correct(
        self,
        *,
        question_id: uuid.UUID,
        expected_revision_id: uuid.UUID,
        correct_alternative_position: int,
        reason_code: str,
        correlation_id: uuid.UUID | None = None,
        fault_hook: FaultHook | None = None,
    ) -> AnswerKeyCorrectionResult:
        correlation = correlation_id or uuid.uuid4()
        reason = self._reason(reason_code)
        self._position(correct_alternative_position)

        def write() -> AnswerKeyCorrectionResult:
            with transaction.atomic(durable=True):
                question = self._locked_question(question_id)
                existing = self._existing(
                    question=question,
                    expected_revision_id=expected_revision_id,
                    correct_alternative_position=correct_alternative_position,
                    reason=reason,
                    correlation=correlation,
                )
                if existing is not None:
                    return existing
                previous = self._current_revision(question)
                if previous.id != expected_revision_id:
                    raise AnswerKeyCorrectionConflictError(
                        "A revisão corrente mudou; recarregue antes de corrigir."
                    )
                alternatives = list(previous.alternatives.order_by("position"))
                if len(alternatives) < 2 or correct_alternative_position > len(alternatives):
                    raise AnswerKeyCorrectionConflictError(
                        "A posição do novo gabarito deve identificar uma alternativa vigente."
                    )
                previous_position = next(
                    (
                        alternative.position
                        for alternative in alternatives
                        if alternative.id == previous.correct_alternative_id
                    ),
                    None,
                )
                if previous_position is None:
                    raise AnswerKeyCorrectionConflictError(
                        "A revisão corrente não possui gabarito íntegro."
                    )
                if previous_position == correct_alternative_position:
                    raise AnswerKeyCorrectionConflictError(
                        "A correção deve alterar efetivamente o gabarito."
                    )
                new_revision = _create_revision(
                    question=question,
                    stem=previous.stem,
                    alternatives=[(item.text, item.label, item.text_key) for item in alternatives],
                    correct_alternative_position=correct_alternative_position,
                    explanation=previous.explanation,
                    trap_note=previous.trap_note,
                    notes=previous.notes,
                    change_kind=RevisionChangeKind.CRITICAL_CORRECTION,
                    change_reason=reason,
                    fault_hook=fault_hook,
                )
                changed = Question.objects.filter(
                    pk=question.id,
                    workspace_id=self.workspace_id,
                    lock_version=question.lock_version,
                ).update(
                    lock_version=F("lock_version") + 1,
                    updated_at=self.clock.now().value,
                )
                if changed != 1:
                    raise AnswerKeyCorrectionConflictError("A Question mudou durante a correção.")
                self._fault(fault_hook, "before_audit")
                record_audit_event(
                    workspace_id=self.workspace_id,
                    event_code=AuditEventCode.ANSWER_KEY_CORRECTED,
                    entity_type=AuditEntityType.QUESTION,
                    entity_id=question.id,
                    previous_entity_id=previous.id,
                    related_entity_id=new_revision.id,
                    correlation_id=correlation,
                    reason_code=reason,
                )
                self._fault(fault_hook, "after_audit")
                return AnswerKeyCorrectionResult(
                    question.id,
                    previous.id,
                    new_revision.id,
                    correlation,
                )

        return self._persist(write)

    def _locked_question(self, question_id: uuid.UUID) -> Question:
        question = (
            Question.objects.select_for_update()
            .filter(
                pk=question_id,
                workspace_id=self.workspace_id,
                status=QuestionStatus.ACTIVE,
            )
            .first()
        )
        if question is None:
            raise AnswerKeyCorrectionConflictError("Question ativa não encontrada no Workspace.")
        return question

    def _current_revision(self, question: Question) -> QuestionRevision:
        revision = (
            question.revisions.filter(is_current=True).select_related("correct_alternative").first()
        )
        if revision is None or revision.correct_alternative_id is None:
            raise AnswerKeyCorrectionConflictError(
                "A Question não possui revisão corrente completa."
            )
        return revision

    def _existing(
        self,
        *,
        question: Question,
        expected_revision_id: uuid.UUID,
        correct_alternative_position: int,
        reason: str,
        correlation: uuid.UUID,
    ) -> AnswerKeyCorrectionResult | None:
        event = AuditEvent.objects.filter(
            workspace_id=self.workspace_id,
            event_code=AuditEventCode.ANSWER_KEY_CORRECTED,
            correlation_id=correlation,
        ).first()
        if event is None:
            return None
        if event.related_entity_id is None:
            raise AnswerKeyCorrectionConflictError(
                "A correlação já foi usada por uma correção diferente."
            )
        new_revision = (
            QuestionRevision.objects.filter(
                pk=event.related_entity_id,
                workspace_id=self.workspace_id,
                question=question,
            )
            .select_related("correct_alternative")
            .first()
        )
        new_position = (
            new_revision.correct_alternative.position
            if new_revision is not None and new_revision.correct_alternative is not None
            else None
        )
        if (
            event.entity_type != AuditEntityType.QUESTION
            or event.entity_id != question.id
            or event.previous_entity_id != expected_revision_id
            or event.reason_code != reason
            or new_revision is None
            or new_position != correct_alternative_position
        ):
            raise AnswerKeyCorrectionConflictError(
                "A correlação já foi usada por uma correção diferente."
            )
        return AnswerKeyCorrectionResult(
            question.id,
            expected_revision_id,
            new_revision.id,
            correlation,
        )

    @staticmethod
    def _reason(value: str) -> str:
        try:
            normalized = normalize_reason_code(value, required=True)
        except ValidationError as error:
            raise AnswerKeyCorrectionConflictError(str(error)) from error
        if normalized is None:
            raise AnswerKeyCorrectionConflictError("Um código de motivo é obrigatório.")
        return normalized

    @staticmethod
    def _position(value: int) -> None:
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise AnswerKeyCorrectionConflictError("A posição do novo gabarito é inválida.")

    @staticmethod
    def _fault(hook: FaultHook | None, point: str) -> None:
        if hook is not None:
            hook(point)

    @staticmethod
    def _persist(
        operation: Callable[[], AnswerKeyCorrectionResult],
    ) -> AnswerKeyCorrectionResult:
        try:
            return run_sqlite_critical_write(operation)
        except AnswerKeyCorrectionConflictError:
            raise
        except (IntegrityError, ValidationError) as error:
            raise AnswerKeyCorrectionConflictError(
                "A correção conflita com o estado atual."
            ) from error
        except DatabaseError as error:
            raise AnswerKeyCorrectionConflictError(
                "Falha de persistência durante a correção."
            ) from error
