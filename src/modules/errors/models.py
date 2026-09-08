"""Persistência mínima das categorias padrão da V0.1."""

import uuid
from typing import Any, ClassVar

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from modules.accounts.models import Workspace
from modules.attempts.models import Attempt, AttemptStatus

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


def _normalized_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = " ".join(value.split())
    return normalized or None


def _validate_classification_context(
    *,
    workspace_id: uuid.UUID,
    attempt_id: uuid.UUID,
    category_id: uuid.UUID,
    other_description: str | None,
) -> None:
    attempt = (
        Attempt.objects.filter(pk=attempt_id).only("workspace_id", "is_correct", "status").first()
    )
    category = ErrorCategory.objects.filter(pk=category_id).only("workspace_id", "code").first()
    if attempt is not None and (
        attempt.workspace_id != workspace_id
        or attempt.is_correct
        or attempt.status != AttemptStatus.VALID
    ):
        raise ValidationError("Classificação exige tentativa incorreta válida do mesmo Workspace.")
    if category is not None and category.workspace_id != workspace_id:
        raise ValidationError("A categoria deve pertencer ao Workspace da classificação.")
    if (
        category is not None
        and category.code == ErrorCategoryCode.OTHER
        and other_description is None
    ):
        raise ValidationError({"other_description": "A categoria OTHER exige descrição."})


class ErrorClassification(models.Model):
    """Projeção atual do diagnóstico de uma tentativa incorreta."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.PROTECT,
        related_name="error_classifications",
    )
    attempt = models.OneToOneField(
        Attempt,
        on_delete=models.PROTECT,
        related_name="error_classification",
    )
    category = models.ForeignKey(
        ErrorCategory,
        on_delete=models.PROTECT,
        related_name="classifications",
    )
    other_description = models.CharField(  # noqa: DJ001
        max_length=500,
        null=True,
        blank=True,
    )
    lock_version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "errors_errorclassification"
        indexes: ClassVar[list[models.Index]] = [
            models.Index(
                fields=["workspace", "category", "updated_at"],
                name="err_class_ws_cat_upd_idx",
            )
        ]
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.CheckConstraint(
                condition=Q(lock_version__gte=1),
                name="err_class_lock_positive",
            ),
            models.CheckConstraint(
                condition=Q(other_description__isnull=True) | ~Q(other_description=""),
                name="err_class_other_not_empty",
            ),
        ]

    def __str__(self) -> str:
        return f"Classificação da tentativa {self.attempt_id}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.other_description = _normalized_optional_text(self.other_description)
        _validate_classification_context(
            workspace_id=self.workspace_id,
            attempt_id=self.attempt_id,
            category_id=self.category_id,
            other_description=self.other_description,
        )
        super().save(*args, **kwargs)


class ErrorClassificationRevisionQuerySet(models.QuerySet["ErrorClassificationRevision"]):
    """Impeça reescrita do histórico append-only."""

    def update(self, **kwargs: Any) -> int:
        raise ValidationError("ErrorClassificationRevision é append-only.")

    def delete(self) -> tuple[int, dict[str, int]]:
        raise ValidationError("ErrorClassificationRevision é append-only.")


class ErrorClassificationRevision(models.Model):
    """Revisão imutável e sequencial do diagnóstico."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.PROTECT,
        related_name="error_classification_revisions",
    )
    error_classification = models.ForeignKey(
        ErrorClassification,
        on_delete=models.PROTECT,
        related_name="revisions",
    )
    revision_number = models.PositiveIntegerField()
    category = models.ForeignKey(
        ErrorCategory,
        on_delete=models.PROTECT,
        related_name="classification_revisions",
    )
    other_description = models.CharField(  # noqa: DJ001
        max_length=500,
        null=True,
        blank=True,
    )
    change_reason = models.CharField(max_length=1000, null=True, blank=True)  # noqa: DJ001
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ErrorClassificationRevisionQuerySet.as_manager()

    class Meta:
        db_table = "errors_errorclassificationrevision"
        indexes: ClassVar[list[models.Index]] = [
            models.Index(
                fields=["workspace", "category", "created_at"],
                name="err_rev_ws_cat_time_idx",
            )
        ]
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=["error_classification", "revision_number"],
                name="err_class_revision_uq",
            ),
            models.CheckConstraint(
                condition=Q(revision_number__gte=1),
                name="err_revision_positive",
            ),
            models.CheckConstraint(
                condition=Q(other_description__isnull=True) | ~Q(other_description=""),
                name="err_revision_other_not_empty",
            ),
            models.CheckConstraint(
                condition=Q(change_reason__isnull=True) | ~Q(change_reason=""),
                name="err_revision_reason_not_empty",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.error_classification_id} r{self.revision_number}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self._state.adding:
            raise ValidationError("ErrorClassificationRevision é append-only.")
        self.other_description = _normalized_optional_text(self.other_description)
        self.change_reason = _normalized_optional_text(self.change_reason)
        classification = (
            ErrorClassification.objects.filter(pk=self.error_classification_id)
            .only("workspace_id", "attempt_id")
            .first()
        )
        category = (
            ErrorCategory.objects.filter(pk=self.category_id).only("workspace_id", "code").first()
        )
        if classification is not None and classification.workspace_id != self.workspace_id:
            raise ValidationError("A revisão deve pertencer ao Workspace da classificação.")
        if category is not None and category.workspace_id != self.workspace_id:
            raise ValidationError("A categoria deve pertencer ao Workspace da revisão.")
        if (
            category is not None
            and category.code == ErrorCategoryCode.OTHER
            and self.other_description is None
        ):
            raise ValidationError({"other_description": "A categoria OTHER exige descrição."})
        super().save(*args, **kwargs)

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        raise ValidationError("ErrorClassificationRevision é append-only.")
