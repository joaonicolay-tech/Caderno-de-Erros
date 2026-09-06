"""Consultas do catálogo de origem sempre limitadas ao Workspace atual."""

import uuid

from django.db.models import Q, QuerySet

from .exceptions import OriginCatalogNotFoundError, QuestionCatalogNotFoundError
from .models import (
    Board,
    Exam,
    OriginStatus,
    Question,
    QuestionRevision,
    Source,
)


def list_boards(*, workspace_id: uuid.UUID) -> QuerySet[Board]:
    """Liste Boards ativas em ordem estável."""
    return Board.objects.filter(
        workspace_id=workspace_id,
        status=OriginStatus.ACTIVE,
    ).order_by("name_key", "id")


def list_archived_boards(*, workspace_id: uuid.UUID) -> QuerySet[Board]:
    """Liste Boards arquivadas do Workspace para consulta histórica."""
    return Board.objects.filter(
        workspace_id=workspace_id,
        status=OriginStatus.ARCHIVED,
    ).order_by("name_key", "id")


def list_exams(*, workspace_id: uuid.UUID) -> QuerySet[Exam]:
    """Liste Exams ativos cuja Board opcional também esteja disponível."""
    return (
        Exam.objects.filter(
            Q(board__isnull=True)
            | Q(board__workspace_id=workspace_id, board__status=OriginStatus.ACTIVE),
            workspace_id=workspace_id,
            status=OriginStatus.ACTIVE,
        )
        .select_related("board")
        .order_by("name_key", "year", "id")
    )


def list_archived_exams(*, workspace_id: uuid.UUID) -> QuerySet[Exam]:
    """Liste Exams explicitamente arquivados, independentemente da Board."""
    return (
        Exam.objects.filter(
            workspace_id=workspace_id,
            status=OriginStatus.ARCHIVED,
        )
        .select_related("board")
        .order_by("name_key", "year", "id")
    )


def list_sources(*, workspace_id: uuid.UUID) -> QuerySet[Source]:
    """Liste Sources ativas do Workspace."""
    return Source.objects.filter(
        workspace_id=workspace_id,
        status=OriginStatus.ACTIVE,
    ).order_by("source_type", "name_key", "id")


def list_archived_sources(*, workspace_id: uuid.UUID) -> QuerySet[Source]:
    """Liste Sources arquivadas do Workspace."""
    return Source.objects.filter(
        workspace_id=workspace_id,
        status=OriginStatus.ARCHIVED,
    ).order_by("source_type", "name_key", "id")


def get_board(*, workspace_id: uuid.UUID, board_id: uuid.UUID) -> Board:
    """Recupere Board ativa ou arquivada sem atravessar Workspace."""
    try:
        return Board.objects.get(pk=board_id, workspace_id=workspace_id)
    except Board.DoesNotExist as error:
        raise OriginCatalogNotFoundError("Board não encontrada no Workspace.") from error


def get_exam(*, workspace_id: uuid.UUID, exam_id: uuid.UUID) -> Exam:
    """Recupere Exam validando também o Workspace de sua Board opcional."""
    try:
        return Exam.objects.select_related("board").get(
            Q(board__isnull=True) | Q(board__workspace_id=workspace_id),
            pk=exam_id,
            workspace_id=workspace_id,
        )
    except Exam.DoesNotExist as error:
        raise OriginCatalogNotFoundError("Exam não encontrado no Workspace.") from error


def get_source(*, workspace_id: uuid.UUID, source_id: uuid.UUID) -> Source:
    """Recupere Source ativa ou arquivada sem atravessar Workspace."""
    try:
        return Source.objects.get(pk=source_id, workspace_id=workspace_id)
    except Source.DoesNotExist as error:
        raise OriginCatalogNotFoundError("Source não encontrada no Workspace.") from error


def get_question(*, workspace_id: uuid.UUID, question_id: uuid.UUID) -> Question:
    """Carregue o agregado atual sem revelar questões de outro Workspace."""
    try:
        return (
            Question.objects.select_related(
                "discipline",
                "subject",
                "subsubject",
                "origin__source",
                "origin__exam__board",
                "origin__board",
            )
            .prefetch_related("revisions__alternatives")
            .get(pk=question_id, workspace_id=workspace_id)
        )
    except Question.DoesNotExist as error:
        raise QuestionCatalogNotFoundError("Questão não encontrada no Workspace.") from error


def get_current_revision(
    *, workspace_id: uuid.UUID, question_id: uuid.UUID
) -> QuestionRevision | None:
    """Retorne a única revisão corrente, quando o rascunho já possui conteúdo."""
    return (
        QuestionRevision.objects.filter(
            workspace_id=workspace_id,
            question_id=question_id,
            question__workspace_id=workspace_id,
            is_current=True,
        )
        .select_related("correct_alternative")
        .prefetch_related("alternatives")
        .first()
    )


def list_question_revisions(
    *, workspace_id: uuid.UUID, question_id: uuid.UUID
) -> QuerySet[QuestionRevision]:
    """Liste snapshots históricos de conteúdo em ordem de versão."""
    return (
        QuestionRevision.objects.filter(
            workspace_id=workspace_id,
            question_id=question_id,
            question__workspace_id=workspace_id,
        )
        .select_related("correct_alternative")
        .prefetch_related("alternatives")
        .order_by("version_number")
    )
