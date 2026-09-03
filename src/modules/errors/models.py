"""Persistência mínima das categorias padrão da V0.1."""

import uuid
from typing import Any, ClassVar

from django.core.exceptions import ValidationError
from django.db import models

from modules.accounts.models import Workspace

from .catalog import normalize_name_key


class ErrorCategoryCode(models.TextChoices):
    """Identificadores históricos aprovados para as categorias padrão."""

    CONCEPTUAL = "CONCEPTUAL", "Conceitual"
    INTERPRETATION = "INTERPRETATION", "Interpretação"
    CALCULATION = "CALCULATION", "Cálculo"
    ATTENTION = "ATTENTION", "Atenção"
    FORMULA_RULE = "FORMULA_RULE", "Fórmula/regra"
    PROCEDURE = "PROCEDURE", "Procedimento"
    TRAP = "TRAP", "Pegadinha"
    TIME_SHORTAGE = "TIME_SHORTAGE", "Falta de tempo"
    GUESS = "GUESS", "Chute"
    OTHER = "OTHER", "Outra"


class ErrorCategoryQuerySet(models.QuerySet["ErrorCategory"]):
    """Bloqueie mutações incompatíveis com categorias canônicas."""

    def update(self, **kwargs: Any) -> int:
        if "code" in kwargs:
            raise ValidationError("O código canônico de uma categoria é imutável.")
        return super().update(**kwargs)

    def delete(self) -> tuple[int, dict[str, int]]:
        raise ValidationError("Categorias padrão não podem ser excluídas isoladamente.")


class ErrorCategory(models.Model):
    """Categoria padrão pertencente a exatamente um Workspace."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="error_categories",
    )
    code = models.CharField(max_length=64, choices=ErrorCategoryCode.choices)
    display_name = models.CharField(max_length=120)
    name_key = models.CharField(max_length=120)
    description = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ErrorCategoryQuerySet.as_manager()

    class Meta:
        db_table = "errors_error_category"
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=["workspace", "code"],
                name="error_category_workspace_code_uq",
            )
        ]

    def __str__(self) -> str:
        return self.display_name

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self._state.adding:
            stored_code = type(self).objects.only("code").get(pk=self.pk).code
            if stored_code != self.code:
                raise ValidationError({"code": "O código canônico de uma categoria é imutável."})
        self.name_key = normalize_name_key(self.display_name)
        self.full_clean()
        super().save(*args, **kwargs)

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        raise ValidationError("Categorias padrão não podem ser excluídas isoladamente.")
