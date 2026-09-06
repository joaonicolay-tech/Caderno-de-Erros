"""Serviços internos, transacionais e Workspace-scoped do catálogo de origem."""

import uuid
from collections.abc import Callable

from django.db import IntegrityError, models, transaction
from django.db.models import F

from modules.accounts.models import Workspace
from shared.domain.time import Clock, SystemClock

from .exceptions import (
    OriginCatalogConcurrencyError,
    OriginCatalogNotFoundError,
    OriginCatalogStateConflictError,
    OriginCatalogValidationError,
)
from .models import Board, Exam, OriginCatalogItem, OriginStatus, Source, SourceType
from .validators import (
    normalize_optional_notes,
    normalize_optional_url,
    normalize_origin_name,
    validate_exam_year,
)


def _get_workspace(workspace_id: uuid.UUID) -> Workspace:
    try:
        return Workspace.objects.get(pk=workspace_id)
    except Workspace.DoesNotExist as error:
        raise OriginCatalogNotFoundError("Workspace não encontrado.") from error


def _create_or_reuse[OriginItemT: OriginCatalogItem](
    *,
    queryset: models.QuerySet[OriginItemT],
    creator: Callable[[], OriginItemT],
) -> OriginItemT:
    existing = queryset.first()
    if existing is not None:
        return existing
    try:
        with transaction.atomic():
            return creator()
    except IntegrityError:
        existing = queryset.first()
        if existing is None:
            raise
        return existing


@transaction.atomic
def create_or_reuse_board(
    *,
    workspace_id: uuid.UUID,
    name: str,
    website_url: str | None = None,
) -> Board:
    """Crie ou reutilize a Board ativa equivalente dentro do Workspace."""
    normalized = normalize_origin_name(name)
    normalized_url = normalize_optional_url(website_url, field_label="O site da banca")
    workspace = _get_workspace(workspace_id)
    scoped = Board.objects.filter(
        workspace_id=workspace_id,
        name_key=normalized.key,
        status=OriginStatus.ACTIVE,
    )
    return _create_or_reuse(
        queryset=scoped,
        creator=lambda: Board.objects.create(
            workspace=workspace,
            name=normalized.display,
            name_key=normalized.key,
            website_url=normalized_url,
        ),
    )


def _get_active_board(*, workspace_id: uuid.UUID, board_id: uuid.UUID) -> Board:
    try:
        board = Board.objects.get(pk=board_id, workspace_id=workspace_id)
    except Board.DoesNotExist as error:
        raise OriginCatalogNotFoundError("Board não encontrada no Workspace.") from error
    if board.status != OriginStatus.ACTIVE:
        raise OriginCatalogStateConflictError("A Board precisa estar ativa.")
    return board


@transaction.atomic
def create_or_reuse_exam(
    *,
    workspace_id: uuid.UUID,
    name: str,
    board_id: uuid.UUID | None = None,
    year: int | None = None,
    clock: Clock | None = None,
) -> Exam:
    """Crie ou reutilize Exam pela chave lógica completa e pelo Workspace."""
    normalized = normalize_origin_name(name)
    workspace = _get_workspace(workspace_id)
    validate_exam_year(year, workspace=workspace, clock=clock)
    board = (
        _get_active_board(workspace_id=workspace_id, board_id=board_id)
        if board_id is not None
        else None
    )
    scoped = Exam.objects.filter(
        workspace_id=workspace_id,
        name_key=normalized.key,
        year=year,
        status=OriginStatus.ACTIVE,
    )
    if board_id is None:
        scoped = scoped.filter(board__isnull=True)
    else:
        scoped = scoped.filter(board_id=board_id)
    return _create_or_reuse(
        queryset=scoped,
        creator=lambda: Exam.objects.create(
            workspace=workspace,
            board=board,
            name=normalized.display,
            name_key=normalized.key,
            year=year,
        ),
    )


@transaction.atomic
def create_or_reuse_source(
    *,
    workspace_id: uuid.UUID,
    source_type: str,
    name: str,
    locator_url: str | None = None,
    notes: str | None = None,
) -> Source:
    """Crie ou reutilize Source ativa pela combinação tipo/nome normalizado."""
    normalized = normalize_origin_name(name)
    if source_type not in SourceType.values:
        raise OriginCatalogValidationError("O tipo da fonte é inválido.")
    normalized_url = normalize_optional_url(locator_url, field_label="O endereço da fonte")
    normalized_notes = normalize_optional_notes(notes)
    workspace = _get_workspace(workspace_id)
    scoped = Source.objects.filter(
        workspace_id=workspace_id,
        source_type=source_type,
        name_key=normalized.key,
        status=OriginStatus.ACTIVE,
    )
    return _create_or_reuse(
        queryset=scoped,
        creator=lambda: Source.objects.create(
            workspace=workspace,
            source_type=source_type,
            name=normalized.display,
            name_key=normalized.key,
            locator_url=normalized_url,
            notes=normalized_notes,
        ),
    )


@transaction.atomic
def _archive_item[OriginItemT: OriginCatalogItem](
    *,
    queryset: models.QuerySet[OriginItemT],
    item_id: uuid.UUID,
    expected_lock_version: int,
    clock: Clock | None,
) -> OriginItemT:
    try:
        item = queryset.get(pk=item_id)
    except queryset.model.DoesNotExist as error:
        raise OriginCatalogNotFoundError(
            "Referência de origem não encontrada no Workspace."
        ) from error
    if item.status == OriginStatus.ARCHIVED:
        raise OriginCatalogStateConflictError("A referência de origem já está arquivada.")
    if item.lock_version != expected_lock_version:
        raise OriginCatalogConcurrencyError("A referência mudou; recarregue a versão atual.")

    now = (clock or SystemClock()).now().value
    updated = queryset.filter(
        pk=item.id,
        status=OriginStatus.ACTIVE,
        lock_version=expected_lock_version,
    ).update(
        status=OriginStatus.ARCHIVED,
        archived_at=now,
        lock_version=F("lock_version") + 1,
        updated_at=now,
    )
    if updated != 1:
        raise OriginCatalogConcurrencyError("A referência mudou; recarregue a versão atual.")
    item.refresh_from_db()
    return item


def archive_board(
    *,
    workspace_id: uuid.UUID,
    board_id: uuid.UUID,
    expected_lock_version: int,
    clock: Clock | None = None,
) -> Board:
    """Arquive Board sem alterar automaticamente seus Exams."""
    return _archive_item(
        queryset=Board.objects.filter(workspace_id=workspace_id),
        item_id=board_id,
        expected_lock_version=expected_lock_version,
        clock=clock,
    )


def archive_exam(
    *,
    workspace_id: uuid.UUID,
    exam_id: uuid.UUID,
    expected_lock_version: int,
    clock: Clock | None = None,
) -> Exam:
    """Arquive Exam preservando os vínculos históricos futuros."""
    return _archive_item(
        queryset=Exam.objects.filter(workspace_id=workspace_id),
        item_id=exam_id,
        expected_lock_version=expected_lock_version,
        clock=clock,
    )


def archive_source(
    *,
    workspace_id: uuid.UUID,
    source_id: uuid.UUID,
    expected_lock_version: int,
    clock: Clock | None = None,
) -> Source:
    """Arquive Source preservando os vínculos históricos futuros."""
    return _archive_item(
        queryset=Source.objects.filter(workspace_id=workspace_id),
        item_id=source_id,
        expected_lock_version=expected_lock_version,
        clock=clock,
    )
