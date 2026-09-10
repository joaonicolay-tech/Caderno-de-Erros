"""Comando inicial: avaliação protegida e confirmação correta atômica."""

import hashlib
import json
import uuid
from collections.abc import Callable
from typing import Any

from django.core.exceptions import ValidationError
from django.db import DatabaseError, IntegrityError, transaction
from django.db.models import F

from modules.accounts.models import UserStatus, Workspace
from modules.operations.events import EventCode, EventOutcome
from modules.operations.structured_logging import emit_event
from modules.questions.models import Alternative, Question, QuestionRevision, QuestionStatus
from shared.domain.time import Clock, SystemClock, TimeZoneId

from .context import AnswerContext, ContextStore, InitialAttemptError, contexts
from .models import Attempt, AttemptStatus, AttemptType, OperationKind, OperationReceipt
from .persistence import run_sqlite_critical_write


class AttemptService:
    """Único comando inicial, com identidade local fornecida pelo adaptador servidor."""

    def __init__(
        self,
        *,
        actor_id: uuid.UUID,
        workspace_id: uuid.UUID,
        session: str,
        clock: Clock | None = None,
        store: ContextStore = contexts,
    ) -> None:
        self.actor_id = actor_id
        self.workspace_id = workspace_id
        self.session = session
        self.clock = clock or SystemClock()
        self.store = store

    def workspace(self) -> Workspace:
        workspace = Workspace.objects.filter(
            pk=self.workspace_id,
            owner_user_id=self.actor_id,
            owner_user__status=UserStatus.ACTIVE,
        ).first()
        if workspace is None or not self.session:
            raise InitialAttemptError("ACCESS_DENIED")
        return workspace

    def presentation(self, question_id: uuid.UUID) -> dict[str, Any]:
        """Projeção permitida: nunca passar model de revisão ao template inicial."""
        self.workspace()
        question, revision = self._current(question_id)
        self._no_initial(question_id)
        return {
            "question_id": question.id,
            "revision_id": revision.id,
            "lock_version": question.lock_version,
            "stem": revision.stem,
            "alternatives": list(
                revision.alternatives.order_by("position").values_list("id", "text")
            ),
        }

    def _current(self, question_id: uuid.UUID) -> tuple[Question, QuestionRevision]:
        question = Question.objects.filter(
            pk=question_id, workspace_id=self.workspace_id, status=QuestionStatus.ACTIVE
        ).first()
        revision = QuestionRevision.objects.filter(
            question_id=question_id, workspace_id=self.workspace_id, is_current=True
        ).first()
        if question is None or revision is None or revision.correct_alternative_id is None:
            raise InitialAttemptError()
        return question, revision

    def _no_initial(self, question_id: uuid.UUID) -> None:
        if Attempt.objects.filter(
            workspace_id=self.workspace_id,
            question_id=question_id,
            attempt_type=AttemptType.INITIAL,
            status=AttemptStatus.VALID,
        ).exists():
            raise InitialAttemptError()

    def evaluate(
        self,
        *,
        question_id: uuid.UUID,
        revision_id: uuid.UUID,
        lock_version: int,
        alternative_id: uuid.UUID,
    ) -> str:
        workspace = self.workspace()
        question, revision = self._current(question_id)
        self._no_initial(question_id)
        if revision.id != revision_id or question.lock_version != lock_version:
            raise InitialAttemptError()
        if not Alternative.objects.filter(
            pk=alternative_id, question_revision=revision, workspace_id=self.workspace_id
        ).exists():
            raise InitialAttemptError()
        token = self.store.put(
            AnswerContext(
                actor_id=self.actor_id,
                session=self.session,
                workspace_id=self.workspace_id,
                workspace_version=workspace.lock_version,
                question_id=question.id,
                revision_id=revision.id,
                lock_version=question.lock_version,
                alternative_id=alternative_id,
                is_correct=alternative_id == revision.correct_alternative_id,
                evaluated_at=self.clock.now().value,
                timezone_name=workspace.timezone_name,
            )
        )
        emit_event(
            EventCode.INITIAL_EVALUATED,
            operation="initial.evaluate",
            outcome=EventOutcome.SUCCEEDED,
        )
        return token

    def context(self, token: str, *, allow_completed: bool = False) -> AnswerContext:
        workspace = self.workspace()
        context = self.store.get(token, self.clock.now().value)
        if (context.actor_id, context.session, context.workspace_id) != (
            self.actor_id,
            self.session,
            self.workspace_id,
        ):
            raise InitialAttemptError("INVALID_CONTEXT")
        if not allow_completed:
            question, revision = self._current(context.question_id)
            if (revision.id, question.lock_version, workspace.lock_version) != (
                context.revision_id,
                context.lock_version,
                context.workspace_version,
            ):
                raise InitialAttemptError("INVALID_CONTEXT")
            self._no_initial(context.question_id)
        return context

    def feedback(self, token: str) -> dict[str, Any]:
        context = self.context(token)
        revision = QuestionRevision.objects.get(pk=context.revision_id)
        if revision.correct_alternative is None:
            raise InitialAttemptError()
        return {
            "is_correct": context.is_correct,
            "correction": revision.correct_alternative.text,
            "explanation": revision.explanation,
            "trap_note": revision.trap_note,
            "notes": revision.notes,
        }

    def cancel(self, token: str) -> None:
        self.context(token)
        self.store.discard(token)

    def confirm(
        self,
        *,
        token: str,
        key: uuid.UUID,
        category_id: uuid.UUID | None = None,
        other_description: str = "",
    ) -> OperationReceipt:
        context = self.context(token, allow_completed=True)
        description = " ".join(other_description.split())
        if context.is_correct and (category_id is not None or description):
            raise InitialAttemptError("INVALID_DIAGNOSIS")
        if not context.is_correct:
            from modules.reviews.services import CompleteReviewService

            return CompleteReviewService(self).complete_initial_error(
                token=token,
                key=key,
                category_id=category_id,
                description=description,
            )
        request_hash = self._request_hash(context, category_id, description)
        self.store.claim(token, key, request_hash, self.clock.now().value)
        return self._persist(lambda: self._correct(token, context, key, request_hash))

    def _request_hash(
        self,
        context: AnswerContext,
        category_id: uuid.UUID | None,
        description: str,
    ) -> str:
        payload = {
            "nonce": context.nonce,
            "actor": str(self.actor_id),
            "workspace": str(self.workspace_id),
            "revision": str(context.revision_id),
            "alternative": str(context.alternative_id),
            "version": context.lock_version,
            "correct": context.is_correct,
            "category": str(category_id) if category_id else None,
            "description": description,
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
        ).hexdigest()

    def _persist(self, operation: Callable[[], OperationReceipt]) -> OperationReceipt:
        try:
            receipt: OperationReceipt = run_sqlite_critical_write(operation)
        except (IntegrityError, ValidationError) as error:
            raise InitialAttemptError() from error
        except DatabaseError as error:
            emit_event(
                EventCode.INITIAL_FAILED, operation="initial.confirm", outcome=EventOutcome.FAILED
            )
            raise InitialAttemptError("PERSISTENCE_FAILURE") from error
        emit_event(
            EventCode.INITIAL_CONFIRMED, operation="initial.confirm", outcome=EventOutcome.SUCCEEDED
        )
        return receipt

    def _existing(
        self, context: AnswerContext, key: uuid.UUID, digest: str
    ) -> OperationReceipt | None:
        receipt = OperationReceipt.objects.filter(
            workspace_id=self.workspace_id, operation_kind=self._kind(context), idempotency_key=key
        ).first()
        if receipt is not None and receipt.request_hash != digest:
            raise InitialAttemptError()
        return receipt

    def _lock(self, token: str, context: AnswerContext) -> None:
        self.context(token)
        # CAS obtains SQLite's write lock before any facts are inserted.
        changed = Question.objects.filter(
            pk=context.question_id,
            workspace_id=self.workspace_id,
            status=QuestionStatus.ACTIVE,
            lock_version=context.lock_version,
        ).update(lock_version=F("lock_version") + 1)
        if changed != 1:
            raise InitialAttemptError()
        self._no_initial(context.question_id)

    @staticmethod
    def _kind(context: AnswerContext) -> str:
        return OperationKind.INITIAL_CORRECT if context.is_correct else OperationKind.INITIAL_ERROR

    def _create_attempt(self, context: AnswerContext, key: uuid.UUID) -> Attempt:
        return Attempt.objects.create(
            workspace_id=self.workspace_id,
            question_id=context.question_id,
            question_revision_id=context.revision_id,
            attempt_type=AttemptType.INITIAL,
            selected_alternative_id=context.alternative_id,
            is_correct=context.is_correct,
            occurred_at=context.evaluated_at,
            timezone_name=context.timezone_name,
            local_date=context.evaluated_at.astimezone(
                TimeZoneId(context.timezone_name).zone
            ).date(),
            idempotency_key=key,
        )

    def _receipt(
        self, context: AnswerContext, key: uuid.UUID, digest: str, attempt: Attempt
    ) -> OperationReceipt:
        return OperationReceipt.objects.create(
            workspace_id=self.workspace_id,
            operation_kind=self._kind(context),
            idempotency_key=key,
            request_hash=digest,
            result_entity_type="ATTEMPT",
            result_entity_id=attempt.id,
        )

    def _correct(
        self, token: str, context: AnswerContext, key: uuid.UUID, digest: str
    ) -> OperationReceipt:
        with transaction.atomic(durable=True):
            existing = self._existing(context, key, digest)
            if existing is not None:
                return existing
            self._lock(token, context)
            attempt = self._create_attempt(context, key)
            return self._receipt(context, key, digest, attempt)
