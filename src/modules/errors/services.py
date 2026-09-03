"""Seed idempotente das categorias padrão."""

from dataclasses import dataclass

from django.db import transaction

from modules.accounts.models import Workspace

from .catalog import STANDARD_ERROR_CATEGORIES, normalize_name_key
from .models import ErrorCategory


@dataclass(frozen=True, slots=True)
class StandardCategorySeedResult:
    """Categorias resultantes e quantidade criada nesta execução."""

    categories: tuple[ErrorCategory, ...]
    created_count: int


@transaction.atomic
def seed_standard_error_categories(workspace: Workspace) -> StandardCategorySeedResult:
    """Crie ou atualize textos canônicos, usando código como identidade estável."""
    categories: list[ErrorCategory] = []
    created_count = 0
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
    return StandardCategorySeedResult(tuple(categories), created_count)
