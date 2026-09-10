"""Orquestração atômica do erro inicial e da conclusão de revisões V0.3."""

import hashlib
import json
import uuid
from collections.abc import Callable
from typing import Any

from django.core.exceptions import ValidationError
from django.db import DatabaseError, IntegrityError, transaction
from django.db.models import F

from modules.accounts.models import Workspace
from modules.attempts.context import AnswerContext, ContextStore, InitialAttemptError, contexts
from modules.attempts.models import (
    Attempt,
    AttemptStatus,
    AttemptType,
    OperationKind,
    OperationReceipt,
    PerceivedEase,
)
from modules.attempts.persistence import run_sqlite_critical_write
from modules.attempts.services import AttemptService
from modules.errors.models import ErrorCategory, ErrorCategoryCode, ErrorClassification
from modules.operations.events import EventCode, EventOutcome
from modules.operations.structured_logging import emit_event
from modules.questions.models import Alternative, Question, QuestionRevision, QuestionStatus
from shared.domain.time import Calendar, Clock, LocalDate, SystemClock, TimeZoneId

from .models import Review, ReviewCycle, ReviewCycleState, ReviewState
from .policies import (
    ReviewSchedulePolicy,
    ReviewStage,
    ReviewStatusPolicy,
    ReviewStructuralState,
    ReviewTemporalStatus,
)


class CompleteReviewService:
    """Único orquestrador dos fatos iniciais incorretos e de uma REVIEW."""

    def __init__(
        self,
        attempts: AttemptService | None = None,
        *,
        actor_id: uuid.UUID | None = None,
        workspace_id: uuid.UUID | None = None,
        session: str = "",
        clock: Clock | None = None,
        store: ContextStore = contexts,
    ) -> None:
        if attempts is None:
            if actor_id is None or workspace_id is None:
                raise ValueError("Identidade e Workspace do servidor são obrigatórios.")
            attempts = AttemptService(
                actor_id=actor_id,
                workspace_id=workspace_id,
                session=session,
                clock=clock or SystemClock(),
                store=store,
            )
        self.attempts = attempts
        self.clock = attempts.clock
        self.calendar = Calendar(self.clock)
        self.schedule = ReviewSchedulePolicy(clock=self.clock, calendar=self.calendar)
        self.status = ReviewStatusPolicy(clock=self.clock, calendar=self.calendar)

    def complete_initial_error(
        self,
        *,
        token: str,
        key: uuid.UUID,
        category_id: uuid.UUID | None,
        description: str,
    ) -> OperationReceipt:
        service = self.attempts
        context = service.context(token, allow_completed=True)
        description = " ".join(description.split())
        if context.is_correct:
            raise InitialAttemptError()
        if category_id is None:
            raise InitialAttemptError("INVALID_DIAGNOSIS")
        category = ErrorCategory.objects.filter(
            pk=category_id, workspace_id=service.workspace_id
        ).first()
        if (
            category is None
            or len(description) > 500
            or (category.code == ErrorCategoryCode.OTHER and not description)
        ):
            raise InitialAttemptError("INVALID_DIAGNOSIS")
        request_hash = service._request_hash(context, category_id, description)
        service.store.claim(token, key, request_hash, service.clock.now().value)

        def write() -> OperationReceipt:
            with transaction.atomic(durable=True):
                existing = service._existing(context, key, request_hash)
                if existing is not None:
                    return existing
                service._lock(token, context)
                attempt = service._create_attempt(context, key)
                ErrorClassification.objects.create(
                    workspace_id=service.workspace_id,
                    attempt=attempt,
                    category=category,
                    other_description=description or None,
                )
                cycle = ReviewCycle.objects.create(
                    workspace_id=service.workspace_id,
                    question_id=context.question_id,
                    origin_attempt=attempt,
                    started_at=attempt.occurred_at,
                )
                due = Calendar.add_days(LocalDate(attempt.local_date), 1).value
                Review.objects.create(
                    workspace_id=service.workspace_id,
                    question_id=context.question_id,
                    review_cycle=cycle,
                    sequence_number=1,
                    stage_code="D1",
                    first_due_date=due,
                    current_due_date=due,
                    scheduled_from_attempt=attempt,
                    transition_code="INITIAL_ERROR_TO_D1",
                )
                return service._receipt(context, key, request_hash, attempt)

        return service._persist(write)

    def presentation(self, review_id: uuid.UUID) -> dict[str, Any]:
        """Projete uma Review conhecida sem antecipar gabarito ou explicação."""
        review, question, revision = self._review_current(review_id, require_pending=True)
        return {
            "review_id": review.id,
            "revision_id": revision.id,
            "lock_version": question.lock_version,
            "review_lock_version": review.lock_version,
            "stem": revision.stem,
            "alternatives": list(
                revision.alternatives.order_by("position").values_list("id", "text")
            ),
        }

    def evaluate(
        self,
        *,
        review_id: uuid.UUID,
        revision_id: uuid.UUID,
        lock_version: int,
        review_lock_version: int,
        alternative_id: uuid.UUID,
    ) -> str:
        """Valide a apresentação e crie somente o contexto efêmero de REVIEW."""
        workspace = self.attempts.workspace()
        review, question, revision = self._review_current(review_id, require_pending=True)
        if self._temporal_status(review, workspace.timezone_name) == ReviewTemporalStatus.FUTURE:
            raise InitialAttemptError("REVIEW_NOT_AVAILABLE")
        if (
            revision.id != revision_id
            or question.lock_version != lock_version
            or review.lock_version != review_lock_version
            or not Alternative.objects.filter(
                pk=alternative_id, question_revision=revision, workspace_id=workspace.id
            ).exists()
        ):
            raise InitialAttemptError("INVALID_CONTEXT")
        token = self.attempts.store.put(
            AnswerContext(
                actor_id=self.attempts.actor_id,
                session=self.attempts.session,
                workspace_id=workspace.id,
                workspace_version=workspace.lock_version,
                question_id=question.id,
                revision_id=revision.id,
                lock_version=question.lock_version,
                alternative_id=alternative_id,
                is_correct=alternative_id == revision.correct_alternative_id,
                evaluated_at=self.clock.now().value,
                timezone_name=workspace.timezone_name,
                review_id=review.id,
                review_lock_version=review.lock_version,
            )
        )
        emit_event(
            EventCode.REVIEW_EVALUATED, operation="review.evaluate", outcome=EventOutcome.SUCCEEDED
        )
        return token

    def feedback(self, token: str) -> dict[str, Any]:
        context = self._review_context(token)
        revision = QuestionRevision.objects.filter(pk=context.revision_id).first()
        if revision is None or revision.correct_alternative is None:
            raise InitialAttemptError("INVALID_CONTEXT")
        return {
            "is_correct": context.is_correct,
            "correction": revision.correct_alternative.text,
            "explanation": revision.explanation,
            "trap_note": revision.trap_note,
            "notes": revision.notes,
        }

    def cancel(self, token: str) -> None:
        self._review_context(token)
        self.attempts.store.discard(token)

    def complete_review(
        self,
        *,
        token: str,
        key: uuid.UUID,
        perceived_ease: str | None = None,
        category_id: uuid.UUID | None = None,
        description: str = "",
    ) -> OperationReceipt:
        """Conclua a Review validada, seu avanço/reinício e recibo em um commit."""
        context = self._review_context(token, allow_completed=True)
        ease = self._validate_ease(perceived_ease)
        description = " ".join(description.split())
        category = self._validate_diagnosis(context, category_id, description)
        digest = self._review_request_hash(context, ease, category_id, description)
        self.attempts.store.claim(token, key, digest, self.clock.now().value)

        def write() -> OperationReceipt:
            with transaction.atomic(durable=True):
                existing = self._existing_review(key, digest)
                if existing is not None:
                    return existing
                review, _question, workspace = self._lock_review(context)
                attempt = self._create_review_attempt(context, key, ease, workspace.timezone_name)
                if category is not None:
                    ErrorClassification.objects.create(
                        workspace_id=workspace.id,
                        attempt=attempt,
                        category=category,
                        other_description=description or None,
                    )
                decision = self.schedule.decide(
                    current_stage=ReviewStage(review.stage_code),
                    is_correct=attempt.is_correct,
                    time_zone_id=TimeZoneId(workspace.timezone_name),
                    policy_code=review.policy_code,
                )
                self._complete_review_row(review, decision.evaluated_at.value)
                self._advance_cycle_and_review(review, attempt, decision)
                return OperationReceipt.objects.create(
                    workspace=workspace,
                    operation_kind=OperationKind.REVIEW_COMPLETION,
                    idempotency_key=key,
                    request_hash=digest,
                    result_entity_type="ATTEMPT",
                    result_entity_id=attempt.id,
                )

        return self._persist_review(write)

    def _review_current(
        self, review_id: uuid.UUID, *, require_pending: bool
    ) -> tuple[Review, Question, QuestionRevision]:
        self.attempts.workspace()
        review = Review.objects.filter(
            pk=review_id,
            workspace_id=self.attempts.workspace_id,
            review_cycle__state=ReviewCycleState.ACTIVE,
        ).first()
        if review is None or (require_pending and review.state != ReviewState.PENDING):
            raise InitialAttemptError("CONFLICT")
        question = Question.objects.filter(
            pk=review.question_id,
            workspace_id=self.attempts.workspace_id,
            status=QuestionStatus.ACTIVE,
        ).first()
        revision = QuestionRevision.objects.filter(
            question_id=review.question_id,
            workspace_id=self.attempts.workspace_id,
            is_current=True,
        ).first()
        if question is None or revision is None or revision.correct_alternative_id is None:
            raise InitialAttemptError("CONFLICT")
        return review, question, revision

    def _temporal_status(self, review: Review, timezone_name: str) -> ReviewTemporalStatus:
        return self.status.evaluate(
            structural_state=ReviewStructuralState(review.state),
            current_due_date=LocalDate(review.current_due_date),
            time_zone_id=TimeZoneId(timezone_name),
        )

    def _review_context(self, token: str, *, allow_completed: bool = False) -> AnswerContext:
        workspace = self.attempts.workspace()
        context = self.attempts.store.get(token, self.clock.now().value)
        if (
            context.review_id is None
            or context.review_lock_version is None
            or (context.actor_id, context.session, context.workspace_id)
            != (self.attempts.actor_id, self.attempts.session, self.attempts.workspace_id)
        ):
            raise InitialAttemptError("INVALID_CONTEXT")
        if not allow_completed:
            review, question, revision = self._review_current(
                context.review_id, require_pending=True
            )
            if (
                context.workspace_version != workspace.lock_version
                or context.revision_id != revision.id
                or context.lock_version != question.lock_version
                or context.review_lock_version != review.lock_version
            ):
                raise InitialAttemptError("INVALID_CONTEXT")
        return context

    @staticmethod
    def _validate_ease(value: str | None) -> str | None:
        if value in {None, ""}:
            return None
        try:
            return PerceivedEase(value).value
        except ValueError as error:
            raise InitialAttemptError("INVALID_EASE") from error

    def _validate_diagnosis(
        self, context: AnswerContext, category_id: uuid.UUID | None, description: str
    ) -> ErrorCategory | None:
        if context.is_correct:
            if category_id is not None or description:
                raise InitialAttemptError("INVALID_DIAGNOSIS")
            return None
        if category_id is None:
            raise InitialAttemptError("INVALID_DIAGNOSIS")
        category = ErrorCategory.objects.filter(
            pk=category_id, workspace_id=self.attempts.workspace_id
        ).first()
        if (
            category is None
            or len(description) > 500
            or (category.code == ErrorCategoryCode.OTHER and not description)
        ):
            raise InitialAttemptError("INVALID_DIAGNOSIS")
        return category

    def _review_request_hash(
        self,
        context: AnswerContext,
        ease: str | None,
        category_id: uuid.UUID | None,
        description: str,
    ) -> str:
        payload = {
            "nonce": context.nonce,
            "actor": str(self.attempts.actor_id),
            "workspace": str(self.attempts.workspace_id),
            "review": str(context.review_id),
            "revision": str(context.revision_id),
            "alternative": str(context.alternative_id),
            "question_version": context.lock_version,
            "review_version": context.review_lock_version,
            "correct": context.is_correct,
            "ease": ease,
            "category": str(category_id) if category_id else None,
            "description": description,
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
        ).hexdigest()

    def _existing_review(self, key: uuid.UUID, digest: str) -> OperationReceipt | None:
        receipt = OperationReceipt.objects.filter(
            workspace_id=self.attempts.workspace_id,
            operation_kind=OperationKind.REVIEW_COMPLETION,
            idempotency_key=key,
        ).first()
        if receipt is not None and receipt.request_hash != digest:
            raise InitialAttemptError("CONFLICT")
        return receipt

    def _lock_review(self, context: AnswerContext) -> tuple[Review, Question, Workspace]:
        workspace = self.attempts.workspace()
        review, question, revision = self._review_current(context.review_id, require_pending=True)  # type: ignore[arg-type]
        if (
            context.workspace_version != workspace.lock_version
            or context.revision_id != revision.id
            or context.lock_version != question.lock_version
            or context.review_lock_version != review.lock_version
            or self._temporal_status(review, workspace.timezone_name)
            not in {ReviewTemporalStatus.DUE, ReviewTemporalStatus.OVERDUE}
            or Attempt.objects.filter(review_id=review.id, status=AttemptStatus.VALID).exists()
        ):
            raise InitialAttemptError("CONFLICT")
        review_changed = Review.objects.filter(
            pk=review.id, state=ReviewState.PENDING, lock_version=context.review_lock_version
        ).update(lock_version=F("lock_version") + 1)
        question_changed = Question.objects.filter(
            pk=question.id,
            workspace_id=workspace.id,
            status=QuestionStatus.ACTIVE,
            lock_version=context.lock_version,
        ).update(lock_version=F("lock_version") + 1)
        if review_changed != 1 or question_changed != 1:
            raise InitialAttemptError("CONFLICT")
        review.refresh_from_db()
        question.refresh_from_db()
        return review, question, workspace

    def _create_review_attempt(
        self,
        context: AnswerContext,
        key: uuid.UUID,
        ease: str | None,
        timezone_name: str,
    ) -> Attempt:
        occurred_at = self.clock.now().value
        return Attempt.objects.create(
            workspace_id=self.attempts.workspace_id,
            question_id=context.question_id,
            question_revision_id=context.revision_id,
            review_id=context.review_id,
            attempt_type=AttemptType.REVIEW,
            selected_alternative_id=context.alternative_id,
            is_correct=context.is_correct,
            perceived_ease=ease,
            occurred_at=occurred_at,
            timezone_name=timezone_name,
            local_date=occurred_at.astimezone(TimeZoneId(timezone_name).zone).date(),
            idempotency_key=key,
        )

    @staticmethod
    def _complete_review_row(review: Review, completed_at: object) -> None:
        updated = Review.objects.filter(
            pk=review.id, state=ReviewState.PENDING, lock_version=review.lock_version
        ).update(
            state=ReviewState.COMPLETED,
            completed_at=completed_at,
            lock_version=F("lock_version") + 1,
        )
        if updated != 1:
            raise InitialAttemptError("CONFLICT")

    def _advance_cycle_and_review(self, review: Review, attempt: Attempt, decision: object) -> None:
        # The policy's immutable decision is intentionally the only source of transition data.
        from .policies import ReviewScheduleDecision

        if not isinstance(decision, ReviewScheduleDecision):
            raise InitialAttemptError("CONFLICT")
        cycle = ReviewCycle.objects.filter(
            pk=review.review_cycle_id,
            workspace_id=self.attempts.workspace_id,
            state=ReviewCycleState.ACTIVE,
        ).first()
        if cycle is None:
            raise InitialAttemptError("CONFLICT")
        if decision.next_stage is None:
            updated = ReviewCycle.objects.filter(
                pk=cycle.id, state=ReviewCycleState.ACTIVE, lock_version=cycle.lock_version
            ).update(
                state=ReviewCycleState.COMPLETED,
                completed_at=decision.evaluated_at.value,
                lock_version=F("lock_version") + 1,
            )
            if updated != 1:
                raise InitialAttemptError("CONFLICT")
            return
        updated = ReviewCycle.objects.filter(
            pk=cycle.id, state=ReviewCycleState.ACTIVE, lock_version=cycle.lock_version
        ).update(lock_version=F("lock_version") + 1)
        if updated != 1 or decision.next_due_date is None:
            raise InitialAttemptError("CONFLICT")
        Review.objects.create(
            workspace_id=self.attempts.workspace_id,
            question_id=review.question_id,
            review_cycle_id=cycle.id,
            sequence_number=review.sequence_number + 1,
            stage_code=decision.next_stage.value,
            first_due_date=decision.next_due_date.value,
            current_due_date=decision.next_due_date.value,
            scheduled_from_attempt=attempt,
            transition_code=decision.transition_code,
            policy_code=decision.policy_code,
        )

    def _persist_review(self, operation: Callable[[], OperationReceipt]) -> OperationReceipt:
        try:
            receipt: OperationReceipt = run_sqlite_critical_write(operation)
        except (IntegrityError, ValidationError) as error:
            raise InitialAttemptError("CONFLICT") from error
        except DatabaseError as error:
            emit_event(
                EventCode.REVIEW_FAILED, operation="review.confirm", outcome=EventOutcome.FAILED
            )
            raise InitialAttemptError("PERSISTENCE_FAILURE") from error
        emit_event(
            EventCode.REVIEW_CONFIRMED, operation="review.confirm", outcome=EventOutcome.SUCCEEDED
        )
        return receipt
