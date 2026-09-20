"""Projeções explícitas para o lifecycle de categorias pessoais."""

import uuid
from dataclasses import dataclass

from django.core.exceptions import ValidationError

from .models import ErrorCategory, ErrorCategoryState


@dataclass(frozen=True, slots=True)
class EffectiveCategoryProjection:
    categories: tuple[ErrorCategory, ...]
    target_by_source: dict[uuid.UUID, uuid.UUID]


def effective_category_projection(*, workspace_id: uuid.UUID) -> EffectiveCategoryProjection:
    """Resolva cada origem uma vez, detectando cadeia inválida sem N+1."""
    categories = tuple(
        ErrorCategory.objects.filter(workspace_id=workspace_id)
        .only(
            "id",
            "workspace_id",
            "code",
            "display_name",
            "category_kind",
            "state",
            "merged_into_id",
        )
        .order_by("code", "id")
    )
    by_id = {category.id: category for category in categories}
    target_by_source: dict[uuid.UUID, uuid.UUID] = {}
    for source in categories:
        current = source
        visited: set[uuid.UUID] = set()
        while current.state == ErrorCategoryState.MERGED:
            if current.id in visited:
                raise ValidationError("Ciclo detectado na consolidação de categorias.")
            visited.add(current.id)
            target_id = current.merged_into_id
            if target_id is None:
                raise ValidationError("Categoria MERGED sem alvo canônico.")
            target = by_id.get(target_id)
            if target is None:
                raise ValidationError("Alvo de consolidação ausente ou fora do Workspace.")
            current = target
        target_by_source[source.id] = current.id
    visible = tuple(
        category for category in categories if category.state != ErrorCategoryState.MERGED
    )
    return EffectiveCategoryProjection(visible, target_by_source)


def source_category_ids_for_target(
    *, workspace_id: uuid.UUID, target_id: uuid.UUID
) -> tuple[uuid.UUID, ...]:
    projection = effective_category_projection(workspace_id=workspace_id)
    if target_id not in {category.id for category in projection.categories}:
        return ()
    return tuple(
        source_id
        for source_id, effective_id in projection.target_by_source.items()
        if effective_id == target_id
    )
