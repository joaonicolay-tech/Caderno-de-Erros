"""Persistência interna dos catálogos de origem e questões."""

import uuid
from typing import Any, ClassVar

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from modules.accounts.models import Workspace
from modules.taxonomy.models import Discipline, Subject, Subsubject, TaxonomyStatus

from .validators import (
    normalize_alternative_label,
    normalize_alternative_text,
    normalize_origin_name,
)


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


class QuestionType(models.TextChoices):
    """Tipos de questão efetivamente suportados na V0.2."""

    OBJECTIVE_SINGLE = "OBJECTIVE_SINGLE", "Objetiva de resposta única"


class QuestionStatus(models.TextChoices):
    """Estados principais de uma questão."""

    DRAFT = "DRAFT", "Rascunho"
    ACTIVE = "ACTIVE", "Ativa"
    ARCHIVED = "ARCHIVED", "Arquivada"


class QuestionDifficulty(models.TextChoices):
    """Dificuldades opcionais aprovadas."""

    EASY = "EASY", "Fácil"
    MEDIUM = "MEDIUM", "Média"
    HARD = "HARD", "Difícil"


class RevisionChangeKind(models.TextChoices):
    """Motivos estruturados para uma nova revisão de conteúdo."""

    INITIAL = "INITIAL", "Inicial"
    ENRICHMENT = "ENRICHMENT", "Enriquecimento"
    NON_CRITICAL_EDIT = "NON_CRITICAL_EDIT", "Edição não crítica"
    CRITICAL_CORRECTION = "CRITICAL_CORRECTION", "Correção crítica"


class Question(models.Model):
    """Identidade estável, estado e classificação acadêmica atual."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.PROTECT,
        related_name="questions",
    )
    discipline = models.ForeignKey(
        Discipline,
        on_delete=models.PROTECT,
        related_name="questions",
        null=True,
        blank=True,
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        related_name="questions",
        null=True,
        blank=True,
    )
    subsubject = models.ForeignKey(
        Subsubject,
        on_delete=models.PROTECT,
        related_name="questions",
        null=True,
        blank=True,
    )
    question_type = models.CharField(
        max_length=24,
        choices=QuestionType.choices,
        default=QuestionType.OBJECTIVE_SINGLE,
    )
    status = models.CharField(
        max_length=16,
        choices=QuestionStatus.choices,
        default=QuestionStatus.DRAFT,
    )
    difficulty = models.CharField(  # noqa: DJ001
        max_length=16,
        choices=QuestionDifficulty.choices,
        null=True,
        blank=True,
    )
    draft_title = models.CharField(max_length=200, null=True, blank=True)  # noqa: DJ001
    activated_at = models.DateTimeField(null=True, blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    lock_version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "questions_question"
        indexes: ClassVar[list[models.Index]] = [
            models.Index(
                fields=["workspace", "status", "updated_at"],
                name="q_question_ws_st_upd_idx",
            ),
            models.Index(
                fields=[
                    "workspace",
                    "discipline",
                    "subject",
                    "subsubject",
                    "status",
                ],
                name="q_question_tax_st_idx",
            ),
            models.Index(
                fields=["workspace", "difficulty", "status"],
                name="q_question_diff_st_idx",
            ),
        ]
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.CheckConstraint(
                condition=Q(question_type__in=QuestionType.values),
                name="q_question_type_valid",
            ),
            models.CheckConstraint(
                condition=Q(status__in=QuestionStatus.values),
                name="q_question_status_valid",
            ),
            models.CheckConstraint(
                condition=Q(difficulty__isnull=True) | Q(difficulty__in=QuestionDifficulty.values),
                name="q_question_difficulty_valid",
            ),
            models.CheckConstraint(
                condition=Q(lock_version__gte=1),
                name="q_question_lock_positive",
            ),
            models.CheckConstraint(
                condition=Q(discipline__isnull=False) | Q(subject__isnull=True),
                name="q_question_subject_parent",
            ),
            models.CheckConstraint(
                condition=Q(subject__isnull=False) | Q(subsubject__isnull=True),
                name="q_question_subsubject_parent",
            ),
            models.CheckConstraint(
                condition=~Q(status=QuestionStatus.ACTIVE)
                | (Q(discipline__isnull=False) & Q(subject__isnull=False)),
                name="q_question_active_taxonomy",
            ),
            models.CheckConstraint(
                condition=(
                    Q(
                        status=QuestionStatus.DRAFT,
                        activated_at__isnull=True,
                        archived_at__isnull=True,
                    )
                    | Q(
                        status=QuestionStatus.ACTIVE,
                        activated_at__isnull=False,
                        archived_at__isnull=True,
                    )
                    | Q(status=QuestionStatus.ARCHIVED, archived_at__isnull=False)
                ),
                name="q_question_state_dates",
            ),
            models.CheckConstraint(
                condition=Q(draft_title__isnull=True) | ~Q(draft_title=""),
                name="q_question_title_not_empty",
            ),
        ]

    def __str__(self) -> str:
        return self.draft_title or str(self.id)

    def save(self, *args: Any, **kwargs: Any) -> None:
        self._validate_taxonomy()
        super().save(*args, **kwargs)

    def _validate_taxonomy(self) -> None:
        discipline = (
            Discipline.objects.filter(pk=self.discipline_id).only("workspace_id", "status").first()
            if self.discipline_id
            else None
        )
        subject = (
            Subject.objects.filter(pk=self.subject_id)
            .only("workspace_id", "discipline_id", "status")
            .first()
            if self.subject_id
            else None
        )
        subsubject = (
            Subsubject.objects.filter(pk=self.subsubject_id)
            .only("workspace_id", "subject_id", "status")
            .first()
            if self.subsubject_id
            else None
        )
        references = (discipline, subject, subsubject)
        if any(item is not None and item.workspace_id != self.workspace_id for item in references):
            raise ValidationError("Toda a taxonomia deve pertencer ao Workspace da questão.")
        if subject is not None and subject.discipline_id != self.discipline_id:
            raise ValidationError({"subject": "O Subject deve pertencer à Discipline informada."})
        if subsubject is not None and subsubject.subject_id != self.subject_id:
            raise ValidationError(
                {"subsubject": "O Subsubject deve pertencer ao Subject informado."}
            )
        if self._state.adding and any(
            item is not None and item.status != TaxonomyStatus.ACTIVE for item in references
        ):
            raise ValidationError("Novos vínculos exigem toda a taxonomia ativa.")


class QuestionRevision(models.Model):
    """Snapshot imutável do conteúdo e do gabarito de uma questão."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.PROTECT,
        related_name="question_revisions",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.PROTECT,
        related_name="revisions",
    )
    version_number = models.PositiveIntegerField()
    is_current = models.BooleanField(default=False)
    stem = models.TextField(null=True, blank=True)  # noqa: DJ001
    explanation = models.TextField(null=True, blank=True)  # noqa: DJ001
    trap_note = models.TextField(null=True, blank=True)  # noqa: DJ001
    notes = models.TextField(null=True, blank=True)  # noqa: DJ001
    correct_alternative = models.ForeignKey(
        "Alternative",
        on_delete=models.PROTECT,
        related_name="correct_for_revisions",
        null=True,
        blank=True,
    )
    change_kind = models.CharField(max_length=24, choices=RevisionChangeKind.choices)
    change_reason = models.CharField(max_length=1000, null=True, blank=True)  # noqa: DJ001
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "questions_questionrevision"
        indexes: ClassVar[list[models.Index]] = [
            models.Index(
                fields=["workspace", "question", "created_at"],
                name="q_revision_ws_q_cr_idx",
            )
        ]
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=["question", "version_number"],
                name="q_revision_version_uq",
            ),
            models.UniqueConstraint(
                fields=["question"],
                condition=Q(is_current=True),
                name="q_revision_current_uq",
            ),
            models.CheckConstraint(
                condition=Q(version_number__gte=1),
                name="q_revision_version_positive",
            ),
            models.CheckConstraint(
                condition=Q(change_kind__in=RevisionChangeKind.values),
                name="q_revision_change_valid",
            ),
            models.CheckConstraint(
                condition=~Q(change_kind=RevisionChangeKind.CRITICAL_CORRECTION)
                | (Q(change_reason__isnull=False) & ~Q(change_reason="")),
                name="q_revision_critical_reason",
            ),
            models.CheckConstraint(
                condition=Q(stem__isnull=True) | ~Q(stem=""),
                name="q_revision_stem_not_empty",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.question_id} v{self.version_number}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self._state.adding:
            raise ValidationError("QuestionRevision é imutável; crie uma nova revisão.")
        question = Question.objects.filter(pk=self.question_id).only("workspace_id").first()
        if question is not None and question.workspace_id != self.workspace_id:
            raise ValidationError("A revisão deve pertencer ao Workspace da questão.")
        if self.correct_alternative_id:
            alternative = (
                Alternative.objects.filter(pk=self.correct_alternative_id)
                .only("workspace_id", "question_revision_id")
                .first()
            )
            if alternative is not None and (
                alternative.workspace_id != self.workspace_id
                or alternative.question_revision_id != self.id
            ):
                raise ValidationError(
                    "A alternativa correta deve pertencer à própria revisão e ao Workspace."
                )
        super().save(*args, **kwargs)


class Alternative(models.Model):
    """Alternativa textual imutável pertencente a uma única revisão."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.PROTECT,
        related_name="question_alternatives",
    )
    question_revision = models.ForeignKey(
        QuestionRevision,
        on_delete=models.PROTECT,
        related_name="alternatives",
    )
    position = models.PositiveSmallIntegerField()
    label = models.CharField(max_length=10, null=True, blank=True)  # noqa: DJ001
    text = models.TextField()
    text_key = models.TextField(editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "questions_alternative"
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=["question_revision", "position"],
                name="q_alternative_position_uq",
            ),
            models.UniqueConstraint(
                fields=["question_revision", "text_key"],
                name="q_alternative_text_uq",
            ),
            models.CheckConstraint(
                condition=Q(position__gte=1),
                name="q_alternative_position_positive",
            ),
            models.CheckConstraint(
                condition=~Q(text="") & ~Q(text_key=""),
                name="q_alternative_text_not_empty",
            ),
        ]

    def __str__(self) -> str:
        return self.text

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self._state.adding:
            raise ValidationError("Alternative é imutável; crie uma nova revisão.")
        revision = (
            QuestionRevision.objects.filter(pk=self.question_revision_id)
            .only("workspace_id")
            .first()
        )
        if revision is not None and revision.workspace_id != self.workspace_id:
            raise ValidationError("A alternativa deve pertencer ao Workspace da revisão.")
        normalized = normalize_alternative_text(self.text)
        self.text = normalized.text
        self.text_key = normalized.text_key
        self.label = normalize_alternative_label(self.label)
        super().save(*args, **kwargs)


class QuestionOrigin(models.Model):
    """Origem opcional e única de uma questão."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.PROTECT,
        related_name="question_origins",
    )
    question = models.OneToOneField(
        Question,
        on_delete=models.PROTECT,
        related_name="origin",
    )
    source = models.ForeignKey(
        Source,
        on_delete=models.PROTECT,
        related_name="question_origins",
        null=True,
        blank=True,
    )
    exam = models.ForeignKey(
        Exam,
        on_delete=models.PROTECT,
        related_name="question_origins",
        null=True,
        blank=True,
    )
    board = models.ForeignKey(
        Board,
        on_delete=models.PROTECT,
        related_name="question_origins",
        null=True,
        blank=True,
    )
    reference_year = models.SmallIntegerField(null=True, blank=True)
    reference_text = models.CharField(max_length=1000, null=True, blank=True)  # noqa: DJ001
    lock_version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "questions_questionorigin"
        indexes: ClassVar[list[models.Index]] = [
            models.Index(fields=["workspace", "source"], name="q_origin_ws_source_idx"),
            models.Index(fields=["workspace", "exam"], name="q_origin_ws_exam_idx"),
            models.Index(fields=["workspace", "board"], name="q_origin_ws_board_idx"),
        ]
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.CheckConstraint(
                condition=Q(exam__isnull=True) | Q(board__isnull=True),
                name="q_origin_exam_board_exclusive",
            ),
            models.CheckConstraint(
                condition=Q(exam__isnull=True) | Q(reference_year__isnull=True),
                name="q_origin_exam_year_derived",
            ),
            models.CheckConstraint(
                condition=Q(reference_year__isnull=True) | Q(reference_year__gte=1900),
                name="q_origin_year_minimum",
            ),
            models.CheckConstraint(
                condition=(
                    Q(source__isnull=False)
                    | Q(exam__isnull=False)
                    | Q(board__isnull=False)
                    | Q(reference_year__isnull=False)
                    | (Q(reference_text__isnull=False) & ~Q(reference_text=""))
                ),
                name="q_origin_has_data",
            ),
            models.CheckConstraint(
                condition=Q(reference_text__isnull=True) | ~Q(reference_text=""),
                name="q_origin_reference_not_empty",
            ),
            models.CheckConstraint(
                condition=Q(lock_version__gte=1),
                name="q_origin_lock_positive",
            ),
        ]

    def __str__(self) -> str:
        return f"Origem de {self.question_id}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        question = Question.objects.filter(pk=self.question_id).only("workspace_id").first()
        references = (
            Source.objects.filter(pk=self.source_id).only("workspace_id").first()
            if self.source_id
            else None,
            Exam.objects.filter(pk=self.exam_id).only("workspace_id").first()
            if self.exam_id
            else None,
            Board.objects.filter(pk=self.board_id).only("workspace_id").first()
            if self.board_id
            else None,
        )
        if question is not None and question.workspace_id != self.workspace_id:
            raise ValidationError("A origem deve pertencer ao Workspace da questão.")
        if any(item is not None and item.workspace_id != self.workspace_id for item in references):
            raise ValidationError("Todas as referências devem pertencer ao Workspace da origem.")
        super().save(*args, **kwargs)
