"""Preferências de filtros pertencentes ao usuário e ao Workspace."""

import uuid
from typing import ClassVar

from django.conf import settings
from django.db import models
from django.db.models import Q

from modules.accounts.models import Workspace


class SavedFilterContext(models.TextChoices):
    """Contextos de listagem suportados pela primeira versão."""

    QUESTIONS_LIST = "QUESTIONS_LIST", "Lista de questões"


class SavedFilter(models.Model):
    """Filtro nomeado com payload validado pela camada de busca."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="saved_filters",
    )
    owner_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_filters",
    )
    name = models.CharField(max_length=80)
    name_key = models.CharField(max_length=160)
    context_code = models.CharField(
        max_length=32,
        choices=SavedFilterContext.choices,
        default=SavedFilterContext.QUESTIONS_LIST,
    )
    schema_version = models.PositiveSmallIntegerField(default=1)
    payload = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "search_savedfilter"
        indexes: ClassVar[list[models.Index]] = [
            models.Index(
                fields=["workspace", "owner_user", "context_code"],
                name="search_saved_ws_owner_ctx_idx",
            )
        ]
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=["owner_user", "context_code", "name_key"],
                name="search_saved_owner_ctx_name_uq",
            ),
            models.CheckConstraint(
                condition=~Q(name=""),
                name="search_saved_name_not_empty",
            ),
            models.CheckConstraint(
                condition=Q(schema_version__gte=1),
                name="search_saved_schema_positive",
            ),
        ]

    def __str__(self) -> str:
        return self.name
