"""Persistência da hierarquia Discipline → Subject → Subsubject."""

import uuid
from typing import Any, ClassVar

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from modules.accounts.models import Workspace

from .validators import normalize_taxonomy_name


class TaxonomyStatus(models.TextChoices):
    """Estados persistidos dos itens acadêmicos."""

    ACTIVE = "ACTIVE", "Ativo"
    ARCHIVED = "ARCHIVED", "Arquivado"


class TaxonomyItem(models.Model):
    """Campos comuns dos três níveis mutáveis da taxonomia."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.PROTECT)
    name = models.CharField(max_length=120)
    name_key = models.CharField(max_length=120, editable=False)
    status = models.CharField(
        max_length=16,
        choices=TaxonomyStatus.choices,
        default=TaxonomyStatus.ACTIVE,
    )
    sort_order = models.IntegerField(null=True, blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    lock_version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def save(self, *args: Any, **kwargs: Any) -> None:
        normalized = normalize_taxonomy_name(self.name)
        self.name = normalized.display
        self.name_key = normalized.key
        self._validate_hierarchy()
        super().save(*args, **kwargs)

    def _validate_hierarchy(self) -> None:
        """Valide invariantes intertabelas especializadas pelos filhos."""


class Discipline(TaxonomyItem):
    """Primeiro nível acadêmico, isolado por Workspace."""

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.PROTECT,
        related_name="disciplines",
    )

    class Meta:
        db_table = "taxonomy_discipline"
        indexes: ClassVar[list[models.Index]] = [
            models.Index(fields=["workspace", "status"], name="tax_disc_ws_status_idx")
        ]
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=["workspace", "name_key"],
                condition=Q(status=TaxonomyStatus.ACTIVE),
                name="tax_disc_active_name_uq",
            ),
            models.CheckConstraint(
                condition=Q(status__in=TaxonomyStatus.values),
                name="tax_disc_status_valid",
            ),
            models.CheckConstraint(
                condition=(
                    Q(status=TaxonomyStatus.ACTIVE, archived_at__isnull=True)
                    | Q(status=TaxonomyStatus.ARCHIVED, archived_at__isnull=False)
                ),
                name="tax_disc_archive_valid",
            ),
            models.CheckConstraint(
                condition=Q(lock_version__gte=1),
                name="tax_disc_lock_positive",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class Subject(TaxonomyItem):
    """Segundo nível, obrigatoriamente pertencente a uma Discipline."""

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.PROTECT,
        related_name="subjects",
    )
    discipline = models.ForeignKey(
        Discipline,
        on_delete=models.PROTECT,
        related_name="subjects",
    )

    class Meta:
        db_table = "taxonomy_subject"
        indexes: ClassVar[list[models.Index]] = [
            models.Index(
                fields=["workspace", "discipline", "status"],
                name="tax_subj_ws_disc_st_idx",
            )
        ]
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=["workspace", "discipline", "name_key"],
                condition=Q(status=TaxonomyStatus.ACTIVE),
                name="tax_subj_active_name_uq",
            ),
            models.CheckConstraint(
                condition=Q(status__in=TaxonomyStatus.values),
                name="tax_subj_status_valid",
            ),
            models.CheckConstraint(
                condition=(
                    Q(status=TaxonomyStatus.ACTIVE, archived_at__isnull=True)
                    | Q(status=TaxonomyStatus.ARCHIVED, archived_at__isnull=False)
                ),
                name="tax_subj_archive_valid",
            ),
            models.CheckConstraint(
                condition=Q(lock_version__gte=1),
                name="tax_subj_lock_positive",
            ),
        ]

    def __str__(self) -> str:
        return self.name

    def _validate_hierarchy(self) -> None:
        if not self.discipline_id:
            return
        parent = (
            Discipline.objects.filter(pk=self.discipline_id).only("workspace_id", "status").first()
        )
        if parent is None:
            return
        if parent.workspace_id != self.workspace_id:
            raise ValidationError(
                {"discipline": "A Discipline deve pertencer ao mesmo Workspace do Subject."}
            )
        if self._state.adding and parent.status != TaxonomyStatus.ACTIVE:
            raise ValidationError({"discipline": "A Discipline precisa estar ativa."})


class Subsubject(TaxonomyItem):
    """Terceiro nível, cuja Discipline é derivada de Subject."""

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.PROTECT,
        related_name="subsubjects",
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        related_name="subsubjects",
    )

    class Meta:
        db_table = "taxonomy_subsubject"
        indexes: ClassVar[list[models.Index]] = [
            models.Index(
                fields=["workspace", "subject", "status"],
                name="tax_ssubj_ws_subj_st_idx",
            )
        ]
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=["workspace", "subject", "name_key"],
                condition=Q(status=TaxonomyStatus.ACTIVE),
                name="tax_ssubj_active_name_uq",
            ),
            models.CheckConstraint(
                condition=Q(status__in=TaxonomyStatus.values),
                name="tax_ssubj_status_valid",
            ),
            models.CheckConstraint(
                condition=(
                    Q(status=TaxonomyStatus.ACTIVE, archived_at__isnull=True)
                    | Q(status=TaxonomyStatus.ARCHIVED, archived_at__isnull=False)
                ),
                name="tax_ssubj_archive_valid",
            ),
            models.CheckConstraint(
                condition=Q(lock_version__gte=1),
                name="tax_ssubj_lock_positive",
            ),
        ]

    def __str__(self) -> str:
        return self.name

    def _validate_hierarchy(self) -> None:
        if not self.subject_id:
            return
        parent = (
            Subject.objects.filter(pk=self.subject_id)
            .select_related("discipline")
            .only("workspace_id", "status", "discipline__workspace_id", "discipline__status")
            .first()
        )
        if parent is None:
            return
        if (
            parent.workspace_id != self.workspace_id
            or parent.discipline.workspace_id != self.workspace_id
        ):
            raise ValidationError(
                {"subject": "O Subject e sua Discipline devem pertencer ao mesmo Workspace."}
            )
        if self._state.adding and (
            parent.status != TaxonomyStatus.ACTIVE
            or parent.discipline.status != TaxonomyStatus.ACTIVE
        ):
            raise ValidationError({"subject": "O Subject e sua Discipline precisam estar ativos."})
