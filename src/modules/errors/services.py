"""Seed idempotente das categorias padrão."""

import logging
from dataclasses import dataclass

from django.db import transaction

from modules.accounts.models import Workspace
from modules.operations.correlation import correlation_scope
from modules.operations.events import EventCode, EventOutcome
from modules.operations.structured_logging import emit_event

from .catalog import STANDARD_ERROR_CATEGORIES, normalize_name_key
from .models import ErrorCategory


@dataclass(frozen=True, slots=True)
class StandardCategorySeedResult:
    """Categorias resultantes e quantidade criada nesta execução."""

    categories: tuple[ErrorCategory, ...]
    created_count: int


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
