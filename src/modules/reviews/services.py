"""Orquestração exclusiva do erro inicial; conclusão REVIEW pertence à E3."""

import uuid

from django.db import transaction

from modules.attempts.context import InitialAttemptError
from modules.attempts.models import OperationReceipt
from modules.attempts.services import AttemptService
from modules.errors.models import ErrorCategory, ErrorCategoryCode, ErrorClassification
from shared.domain.time import Calendar, LocalDate

from .models import Review, ReviewCycle


class CompleteReviewService:
    """Componha os cinco fatos do erro inicial em uma única transação."""

    def __init__(self, attempts: AttemptService) -> None:
        self.attempts = attempts

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
