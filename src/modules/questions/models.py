"""Persistência interna de Board, Exam e Source."""

import uuid
from typing import Any, ClassVar

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from modules.accounts.models import Workspace

from .validators import normalize_origin_name


class OriginStatus(models.TextChoices):
    """Estados persistidos das referências de origem."""

    ACTIVE = "ACTIVE", "Ativo"
    ARCHIVED = "ARCHIVED", "Arquivado"


class SourceType(models.TextChoices):
    """Tipos fechados de fonte aprovados no modelo de dados."""

    BOOK = "BOOK", "Livro"
    PDF = "PDF", "PDF"
    WEBSITE = "WEBSITE", "Site"
    COURSE = "COURSE", "Curso"
    QUESTION_BANK = "QUESTION_BANK", "Banco de questões"
    OTHER = "OTHER", "Outra"


class OriginCatalogItem(models.Model):
    """Campos comuns das referências mutáveis do catálogo."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.PROTECT)
    name = models.CharField(max_length=120)
    name_key = models.CharField(max_length=120, editable=False)
    status = models.CharField(
        max_length=16,
        choices=OriginStatus.choices,
        default=OriginStatus.ACTIVE,
    )
    archived_at = models.DateTimeField(null=True, blank=True)
    lock_version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def save(self, *args: Any, **kwargs: Any) -> None:
        normalized = normalize_origin_name(self.name)
        self.name = normalized.display
        self.name_key = normalized.key
        self._validate_references()
        super().save(*args, **kwargs)

    def _validate_references(self) -> None:
        """Valide invariantes intertabelas especializadas pelos filhos."""


class Board(OriginCatalogItem):
    """Banca isolada por Workspace."""

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.PROTECT,
        related_name="boards",
    )
    # NULL é a ausência canônica definida pelo Modelo de Dados (§3.5).
    website_url = models.URLField(max_length=2048, null=True, blank=True)  # noqa: DJ001

    class Meta:
        db_table = "questions_board"
        indexes: ClassVar[list[models.Index]] = [
            models.Index(
                fields=["workspace", "status", "name_key"],
                name="q_board_ws_st_name_idx",
            )
        ]
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=["workspace", "name_key"],
                condition=Q(status=OriginStatus.ACTIVE),
                name="q_board_active_name_uq",
            ),
            models.CheckConstraint(
                condition=Q(status__in=OriginStatus.values),
                name="q_board_status_valid",
            ),
            models.CheckConstraint(
                condition=(
                    Q(status=OriginStatus.ACTIVE, archived_at__isnull=True)
                    | Q(status=OriginStatus.ARCHIVED, archived_at__isnull=False)
                ),
                name="q_board_archive_valid",
            ),
            models.CheckConstraint(
                condition=Q(lock_version__gte=1),
                name="q_board_lock_positive",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class Exam(OriginCatalogItem):
    """Prova/concurso com banca e ano opcionais."""

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.PROTECT,
        related_name="exams",
    )
    board = models.ForeignKey(
        Board,
        on_delete=models.PROTECT,
        related_name="exams",
        null=True,
        blank=True,
    )
    year = models.SmallIntegerField(null=True, blank=True)

    class Meta:
        db_table = "questions_exam"
        indexes: ClassVar[list[models.Index]] = [
            models.Index(
                fields=["workspace", "board", "year"],
                name="q_exam_ws_board_year_idx",
            )
        ]
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=["workspace", "name_key"],
                condition=Q(
                    status=OriginStatus.ACTIVE,
                    board__isnull=True,
                    year__isnull=True,
                ),
                name="q_exam_active_none_uq",
            ),
            models.UniqueConstraint(
                fields=["workspace", "name_key", "year"],
                condition=Q(
                    status=OriginStatus.ACTIVE,
                    board__isnull=True,
                    year__isnull=False,
                ),
                name="q_exam_active_year_uq",
            ),
            models.UniqueConstraint(
                fields=["workspace", "board", "name_key"],
                condition=Q(
                    status=OriginStatus.ACTIVE,
                    board__isnull=False,
                    year__isnull=True,
                ),
                name="q_exam_active_board_uq",
            ),
            models.UniqueConstraint(
                fields=["workspace", "board", "name_key", "year"],
                condition=Q(
                    status=OriginStatus.ACTIVE,
                    board__isnull=False,
                    year__isnull=False,
                ),
                name="q_exam_active_full_uq",
            ),
            models.CheckConstraint(
                condition=Q(status__in=OriginStatus.values),
                name="q_exam_status_valid",
            ),
            models.CheckConstraint(
                condition=(
                    Q(status=OriginStatus.ACTIVE, archived_at__isnull=True)
                    | Q(status=OriginStatus.ARCHIVED, archived_at__isnull=False)
                ),
                name="q_exam_archive_valid",
            ),
            models.CheckConstraint(
                condition=Q(lock_version__gte=1),
                name="q_exam_lock_positive",
            ),
            models.CheckConstraint(
                condition=Q(year__isnull=True) | Q(year__gte=1900),
                name="q_exam_year_minimum",
            ),
        ]

    def __str__(self) -> str:
        return self.name

    def _validate_references(self) -> None:
        if not self.board_id:
            return
        board = Board.objects.filter(pk=self.board_id).only("workspace_id", "status").first()
        if board is None:
            return
        if board.workspace_id != self.workspace_id:
            raise ValidationError({"board": "A Board deve pertencer ao mesmo Workspace do Exam."})
        if self._state.adding and board.status != OriginStatus.ACTIVE:
            raise ValidationError({"board": "A Board precisa estar ativa."})


class Source(OriginCatalogItem):
    """Fonte bibliográfica ou digital reutilizável no Workspace."""

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.PROTECT,
        related_name="sources",
    )
    source_type = models.CharField(max_length=24, choices=SourceType.choices)
    # NULL é a ausência canônica definida pelo Modelo de Dados (§3.5).
    locator_url = models.URLField(max_length=2048, null=True, blank=True)  # noqa: DJ001
    notes = models.TextField(null=True, blank=True)  # noqa: DJ001

    class Meta:
        db_table = "questions_source"
        indexes: ClassVar[list[models.Index]] = [
            models.Index(
                fields=["workspace", "source_type", "status"],
                name="q_source_ws_type_st_idx",
            ),
            models.Index(
                fields=["workspace", "name_key"],
                name="q_source_ws_name_idx",
            ),
        ]
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=["workspace", "source_type", "name_key"],
                condition=Q(status=OriginStatus.ACTIVE),
                name="q_source_active_name_uq",
            ),
            models.CheckConstraint(
                condition=Q(source_type__in=SourceType.values),
                name="q_source_type_valid",
            ),
            models.CheckConstraint(
                condition=Q(status__in=OriginStatus.values),
                name="q_source_status_valid",
            ),
            models.CheckConstraint(
                condition=(
                    Q(status=OriginStatus.ACTIVE, archived_at__isnull=True)
                    | Q(status=OriginStatus.ARCHIVED, archived_at__isnull=False)
                ),
                name="q_source_archive_valid",
            ),
            models.CheckConstraint(
                condition=Q(lock_version__gte=1),
                name="q_source_lock_positive",
            ),
        ]

    def __str__(self) -> str:
        return self.name
