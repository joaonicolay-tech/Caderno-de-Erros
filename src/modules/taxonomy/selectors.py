"""Consultas de taxonomia sempre limitadas ao Workspace atual."""

import uuid

from django.db.models import QuerySet

from .exceptions import TaxonomyNotFoundError
from .models import Discipline, Subject, Subsubject, TaxonomyStatus


def list_disciplines(*, workspace_id: uuid.UUID) -> QuerySet[Discipline]:
    """Liste disciplinas efetivamente disponíveis para novos vínculos."""
    return Discipline.objects.filter(
        workspace_id=workspace_id,
        status=TaxonomyStatus.ACTIVE,
    ).order_by("sort_order", "name_key", "id")


def list_archived_disciplines(*, workspace_id: uuid.UUID) -> QuerySet[Discipline]:
    """Liste disciplinas arquivadas para consulta histórica."""
    return Discipline.objects.filter(
        workspace_id=workspace_id,
        status=TaxonomyStatus.ARCHIVED,
    ).order_by("sort_order", "name_key", "id")


def list_subjects(*, workspace_id: uuid.UUID, discipline_id: uuid.UUID) -> QuerySet[Subject]:
    """Liste Subjects ativos cujo pai também está ativo no Workspace."""
    return Subject.objects.filter(
        workspace_id=workspace_id,
        discipline_id=discipline_id,
        status=TaxonomyStatus.ACTIVE,
        discipline__workspace_id=workspace_id,
        discipline__status=TaxonomyStatus.ACTIVE,
    ).order_by("sort_order", "name_key", "id")


def list_archived_subjects(
    *, workspace_id: uuid.UUID, discipline_id: uuid.UUID
) -> QuerySet[Subject]:
    """Liste Subjects explicitamente arquivados sob uma Discipline."""
    return Subject.objects.filter(
        workspace_id=workspace_id,
        discipline_id=discipline_id,
        status=TaxonomyStatus.ARCHIVED,
    ).order_by("sort_order", "name_key", "id")


def list_managed_subjects(
    *, workspace_id: uuid.UUID, discipline_id: uuid.UUID, archived: bool = False
) -> QuerySet[Subject]:
    """Liste o estado próprio para gestão, mesmo com pai indisponível."""
    status = TaxonomyStatus.ARCHIVED if archived else TaxonomyStatus.ACTIVE
    return Subject.objects.filter(
        workspace_id=workspace_id,
        discipline_id=discipline_id,
        discipline__workspace_id=workspace_id,
        status=status,
    ).order_by("sort_order", "name_key", "id")


def list_subsubjects(*, workspace_id: uuid.UUID, subject_id: uuid.UUID) -> QuerySet[Subsubject]:
    """Liste Subsubjects cuja cadeia completa está ativa no Workspace."""
    return Subsubject.objects.filter(
        workspace_id=workspace_id,
        subject_id=subject_id,
        status=TaxonomyStatus.ACTIVE,
        subject__workspace_id=workspace_id,
        subject__status=TaxonomyStatus.ACTIVE,
        subject__discipline__workspace_id=workspace_id,
        subject__discipline__status=TaxonomyStatus.ACTIVE,
    ).order_by("sort_order", "name_key", "id")


def list_archived_subsubjects(
    *, workspace_id: uuid.UUID, subject_id: uuid.UUID
) -> QuerySet[Subsubject]:
    """Liste Subsubjects explicitamente arquivados sob um Subject."""
    return Subsubject.objects.filter(
        workspace_id=workspace_id,
        subject_id=subject_id,
        status=TaxonomyStatus.ARCHIVED,
    ).order_by("sort_order", "name_key", "id")


def list_managed_subsubjects(
    *, workspace_id: uuid.UUID, subject_id: uuid.UUID, archived: bool = False
) -> QuerySet[Subsubject]:
    """Liste o estado próprio sem confundir ancestral arquivado com item arquivado."""
    status = TaxonomyStatus.ARCHIVED if archived else TaxonomyStatus.ACTIVE
    return Subsubject.objects.filter(
        workspace_id=workspace_id,
        subject_id=subject_id,
        subject__workspace_id=workspace_id,
        subject__discipline__workspace_id=workspace_id,
        status=status,
    ).order_by("sort_order", "name_key", "id")


def count_subjects(*, workspace_id: uuid.UUID, discipline_id: uuid.UUID) -> int:
    """Conte descendentes existentes, ativos ou arquivados, para confirmação."""
    return Subject.objects.filter(
        workspace_id=workspace_id,
        discipline_id=discipline_id,
        discipline__workspace_id=workspace_id,
    ).count()


def count_subsubjects(*, workspace_id: uuid.UUID, subject_id: uuid.UUID) -> int:
    """Conte descendentes existentes sem consultar capacidades futuras."""
    return Subsubject.objects.filter(
        workspace_id=workspace_id,
        subject_id=subject_id,
        subject__workspace_id=workspace_id,
        subject__discipline__workspace_id=workspace_id,
    ).count()


def get_discipline(*, workspace_id: uuid.UUID, discipline_id: uuid.UUID) -> Discipline:
    """Recupere inclusive item arquivado, sem atravessar Workspace."""
    try:
        return Discipline.objects.get(pk=discipline_id, workspace_id=workspace_id)
    except Discipline.DoesNotExist as error:
        raise TaxonomyNotFoundError("Discipline não encontrada no Workspace.") from error


def get_subject(*, workspace_id: uuid.UUID, subject_id: uuid.UUID) -> Subject:
    """Recupere inclusive item arquivado, validando também o pai."""
    try:
        return Subject.objects.select_related("discipline").get(
            pk=subject_id,
            workspace_id=workspace_id,
            discipline__workspace_id=workspace_id,
        )
    except Subject.DoesNotExist as error:
        raise TaxonomyNotFoundError("Subject não encontrado no Workspace.") from error


def get_subsubject(*, workspace_id: uuid.UUID, subsubject_id: uuid.UUID) -> Subsubject:
    """Recupere inclusive item arquivado, validando toda a cadeia."""
    try:
        return Subsubject.objects.select_related("subject__discipline").get(
            pk=subsubject_id,
            workspace_id=workspace_id,
            subject__workspace_id=workspace_id,
            subject__discipline__workspace_id=workspace_id,
        )
    except Subsubject.DoesNotExist as error:
        raise TaxonomyNotFoundError("Subsubject não encontrado no Workspace.") from error
