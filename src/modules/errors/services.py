"""Seed idempotente das categorias padrão."""

import logging
import uuid
from dataclasses import dataclass

from django.db import transaction
from django.db.models import F, Max

from modules.accounts.models import Workspace
from modules.attempts.persistence import run_sqlite_critical_write
from modules.operations.correlation import correlation_scope
from modules.operations.events import EventCode, EventOutcome
from modules.operations.structured_logging import emit_event
from shared.domain.time import Clock, SystemClock

from .catalog import STANDARD_ERROR_CATEGORIES, normalize_name_key
from .models import (
    ErrorCategory,
    ErrorCategoryCode,
    ErrorClassification,
    ErrorClassificationRevision,
)


@dataclass(frozen=True, slots=True)
class StandardCategorySeedResult:
    """Categorias resultantes e quantidade criada nesta execução."""

    categories: tuple[ErrorCategory, ...]
    created_count: int


class ErrorDiagnosisConflictError(RuntimeError):
    """A projeção de diagnóstico mudou desde a versão apresentada."""


class ErrorDiagnosisService:
    """Corrija a projeção e acrescente revisões, sem tocar na Attempt."""

    def __init__(self, *, workspace_id: uuid.UUID, clock: Clock | None = None) -> None:
        self.workspace_id = workspace_id
        self.clock = clock or SystemClock()

    def correct(
        self,
        *,
        attempt_id: uuid.UUID,
        category_id: uuid.UUID,
        other_description: str = "",
        change_reason: str = "",
        expected_lock_version: int,
    ) -> ErrorClassification:
        """Faça a semeadura r1 e a correção rN em um commit curto e atômico."""
        description = " ".join(other_description.split()) or None
        reason = " ".join(change_reason.split()) or None
        if description is not None and len(description) > 500:
            raise ValueError("Descrição de diagnóstico excede o limite.")
        if reason is not None and len(reason) > 1000:
            raise ValueError("Razão de correção excede o limite.")

        def write() -> ErrorClassification:
            with transaction.atomic(durable=True):
                classification = (
                    ErrorClassification.objects.select_for_update()
                    .filter(workspace_id=self.workspace_id, attempt_id=attempt_id)
                    .select_related("attempt")
                    .first()
                )
                category = ErrorCategory.objects.filter(
                    pk=category_id, workspace_id=self.workspace_id
                ).first()
                if classification is None or category is None:
                    raise ErrorDiagnosisConflictError("Diagnóstico não disponível neste Workspace.")
                if classification.attempt.is_correct:
                    raise ErrorDiagnosisConflictError(
                        "Somente tentativa incorreta possui diagnóstico."
                    )
                if category.code == ErrorCategoryCode.OTHER and description is None:
                    raise ValueError("A categoria OTHER exige descrição.")
                if classification.lock_version != expected_lock_version:
                    raise ErrorDiagnosisConflictError(
                        "O diagnóstico mudou; recarregue a versão atual."
                    )

                maximum = ErrorClassificationRevision.objects.filter(
                    error_classification=classification
                ).aggregate(maximum=Max("revision_number"))["maximum"]
                next_number = 1 if maximum is None else maximum + 1
                if maximum is None:
                    ErrorClassificationRevision.objects.create(
                        workspace_id=self.workspace_id,
                        error_classification=classification,
                        revision_number=1,
                        category_id=classification.category_id,
                        other_description=classification.other_description,
                        change_reason="Diagnóstico inicial preservado.",
                    )
                    next_number = 2
                ErrorClassificationRevision.objects.create(
                    workspace_id=self.workspace_id,
                    error_classification=classification,
                    revision_number=next_number,
                    category=category,
                    other_description=description,
                    change_reason=reason,
                )
                changed = ErrorClassification.objects.filter(
                    pk=classification.id,
                    workspace_id=self.workspace_id,
                    lock_version=expected_lock_version,
                ).update(
                    category=category,
                    other_description=description,
                    lock_version=F("lock_version") + 1,
                    updated_at=self.clock.now().value,
                )
                if changed != 1:
                    raise ErrorDiagnosisConflictError(
                        "O diagnóstico mudou; recarregue a versão atual."
                    )
                classification.refresh_from_db()
                return classification

        return run_sqlite_critical_write(write)


@transaction.atomic
def seed_standard_error_categories(
    workspace: Workspace,
    *,
    correlation_id: str | None = None,
) -> StandardCategorySeedResult:
    """Crie ou atualize textos canônicos, usando código como identidade estável."""
    with correlation_scope(correlation_id):
        emit_event(
            EventCode.CATEGORY_SEED_STARTED,
            operation="error_category.seed",
            outcome=EventOutcome.STARTED,
            context={"workspace_id": str(workspace.id)},
        )
        categories: list[ErrorCategory] = []
        created_count = 0
        try:
            for definition in STANDARD_ERROR_CATEGORIES:
                category, created = ErrorCategory.objects.update_or_create(
                    workspace=workspace,
                    code=definition.code,
                    defaults={
                        "display_name": definition.display_name,
                        "name_key": normalize_name_key(definition.display_name),
                        "description": definition.description,
                    },
                )
                categories.append(category)
                created_count += int(created)
        except Exception as error:
            emit_event(
                EventCode.CATEGORY_SEED_FAILED,
                operation="error_category.seed",
                outcome=EventOutcome.FAILED,
                level=logging.ERROR,
                context={
                    "workspace_id": str(workspace.id),
                    "error_code": "CATEGORY_SEED_FAILURE",
                    "error_type": type(error).__name__,
                },
            )
            raise

        emit_event(
            EventCode.CATEGORY_SEED_SUCCEEDED,
            operation="error_category.seed",
            outcome=EventOutcome.SUCCEEDED,
            context={
                "workspace_id": str(workspace.id),
                "category_count": len(categories),
                "created_count": created_count,
            },
        )
        return StandardCategorySeedResult(tuple(categories), created_count)
