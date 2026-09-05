"""Casos de uso transacionais e Workspace-scoped da taxonomia."""

import uuid
from collections.abc import Callable

from django.db import IntegrityError, models, transaction
from django.db.models import F

from modules.accounts.models import Workspace
from shared.domain.time import Clock, SystemClock

from .exceptions import (
    TaxonomyConcurrencyError,
    TaxonomyDuplicateNameError,
    TaxonomyNotFoundError,
    TaxonomyStateConflictError,
    TaxonomyValidationError,
)
from .models import Discipline, Subject, Subsubject, TaxonomyItem, TaxonomyStatus
from .validators import NormalizedTaxonomyName, normalize_taxonomy_name


def _validate_sort_order(sort_order: int | None) -> None:
    if sort_order is not None and (isinstance(sort_order, bool) or not isinstance(sort_order, int)):
        raise TaxonomyValidationError("A ordem deve ser um número inteiro ou nula.")


def _require_workspace(workspace_id: uuid.UUID) -> None:
    if not Workspace.objects.filter(pk=workspace_id).exists():
        raise TaxonomyNotFoundError("Workspace não encontrado.")


def _raise_duplicate() -> None:
    raise TaxonomyDuplicateNameError(
        "Já existe um item ativo com esse nome normalizado no mesmo escopo."
    )


def _create_item[TaxonomyItemT: TaxonomyItem](
    *,
    creator: Callable[[NormalizedTaxonomyName], TaxonomyItemT],
    normalized: NormalizedTaxonomyName,
) -> TaxonomyItemT:
    try:
        with transaction.atomic():
            return creator(normalized)
    except IntegrityError as error:
        raise TaxonomyDuplicateNameError(
            "Já existe um item ativo com esse nome normalizado no mesmo escopo."
        ) from error


@transaction.atomic
def create_discipline(
    *, workspace_id: uuid.UUID, name: str, sort_order: int | None = None
) -> Discipline:
    """Crie uma Discipline ativa no Workspace informado."""
    normalized = normalize_taxonomy_name(name)
    _validate_sort_order(sort_order)
    _require_workspace(workspace_id)
    if Discipline.objects.filter(
        workspace_id=workspace_id,
        name_key=normalized.key,
        status=TaxonomyStatus.ACTIVE,
    ).exists():
        _raise_duplicate()
    return _create_item(
        normalized=normalized,
        creator=lambda value: Discipline.objects.create(
            workspace_id=workspace_id,
            name=value.display,
            name_key=value.key,
            sort_order=sort_order,
        ),
    )


@transaction.atomic
def create_subject(
    *,
    workspace_id: uuid.UUID,
    discipline_id: uuid.UUID,
    name: str,
    sort_order: int | None = None,
) -> Subject:
    """Crie um Subject somente sob Discipline ativa do mesmo Workspace."""
    normalized = normalize_taxonomy_name(name)
    _validate_sort_order(sort_order)
    _require_workspace(workspace_id)
    try:
        discipline = Discipline.objects.get(pk=discipline_id, workspace_id=workspace_id)
    except Discipline.DoesNotExist as error:
        raise TaxonomyNotFoundError("Discipline não encontrada no Workspace.") from error
    if discipline.status != TaxonomyStatus.ACTIVE:
        raise TaxonomyStateConflictError("A Discipline precisa estar ativa.")
    if Subject.objects.filter(
        workspace_id=workspace_id,
        discipline_id=discipline_id,
        name_key=normalized.key,
        status=TaxonomyStatus.ACTIVE,
    ).exists():
        _raise_duplicate()
    return _create_item(
        normalized=normalized,
        creator=lambda value: Subject.objects.create(
            workspace_id=workspace_id,
            discipline=discipline,
            name=value.display,
            name_key=value.key,
            sort_order=sort_order,
        ),
    )


@transaction.atomic
def create_subsubject(
    *,
    workspace_id: uuid.UUID,
    subject_id: uuid.UUID,
    name: str,
    sort_order: int | None = None,
) -> Subsubject:
    """Crie Subsubject apenas quando Subject e Discipline estão ativos."""
    normalized = normalize_taxonomy_name(name)
    _validate_sort_order(sort_order)
    _require_workspace(workspace_id)
    try:
        subject = Subject.objects.select_related("discipline").get(
            pk=subject_id,
            workspace_id=workspace_id,
            discipline__workspace_id=workspace_id,
        )
    except Subject.DoesNotExist as error:
        raise TaxonomyNotFoundError("Subject não encontrado no Workspace.") from error
    if (
        subject.status != TaxonomyStatus.ACTIVE
        or subject.discipline.status != TaxonomyStatus.ACTIVE
    ):
        raise TaxonomyStateConflictError("O Subject e sua Discipline precisam estar ativos.")
    if Subsubject.objects.filter(
        workspace_id=workspace_id,
        subject_id=subject_id,
        name_key=normalized.key,
        status=TaxonomyStatus.ACTIVE,
    ).exists():
        _raise_duplicate()
    return _create_item(
        normalized=normalized,
        creator=lambda value: Subsubject.objects.create(
            workspace_id=workspace_id,
            subject=subject,
            name=value.display,
            name_key=value.key,
            sort_order=sort_order,
        ),
    )


@transaction.atomic
def _rename_item[TaxonomyItemT: TaxonomyItem](
    *,
    queryset: models.QuerySet[TaxonomyItemT],
    duplicate_queryset: models.QuerySet[TaxonomyItemT],
    item_id: uuid.UUID,
    name: str,
    expected_lock_version: int,
    clock: Clock | None,
) -> TaxonomyItemT:
    normalized = normalize_taxonomy_name(name)
    try:
        item = queryset.get(pk=item_id)
    except queryset.model.DoesNotExist as error:
        raise TaxonomyNotFoundError("Item de taxonomia não encontrado no Workspace.") from error
    if item.lock_version != expected_lock_version:
        raise TaxonomyConcurrencyError("O item mudou; recarregue a versão atual.")
    if (
        item.status == TaxonomyStatus.ACTIVE
        and duplicate_queryset.filter(
            name_key=normalized.key,
            status=TaxonomyStatus.ACTIVE,
        )
        .exclude(pk=item.id)
        .exists()
    ):
        _raise_duplicate()

    current_clock = clock or SystemClock()
    try:
        with transaction.atomic():
            updated = queryset.filter(
                pk=item.id,
                lock_version=expected_lock_version,
            ).update(
                name=normalized.display,
                name_key=normalized.key,
                lock_version=F("lock_version") + 1,
                updated_at=current_clock.now().value,
            )
    except IntegrityError as error:
        raise TaxonomyDuplicateNameError(
            "Já existe um item ativo com esse nome normalizado no mesmo escopo."
        ) from error
    if updated != 1:
        raise TaxonomyConcurrencyError("O item mudou; recarregue a versão atual.")
    item.refresh_from_db()
    return item


def rename_discipline(
    *,
    workspace_id: uuid.UUID,
    discipline_id: uuid.UUID,
    name: str,
    expected_lock_version: int,
    clock: Clock | None = None,
) -> Discipline:
    """Renomeie por compare-and-swap sem recriar os vínculos."""
    scoped = Discipline.objects.filter(workspace_id=workspace_id)
    return _rename_item(
        queryset=scoped,
        duplicate_queryset=scoped,
        item_id=discipline_id,
        name=name,
        expected_lock_version=expected_lock_version,
        clock=clock,
    )


def rename_subject(
    *,
    workspace_id: uuid.UUID,
    subject_id: uuid.UUID,
    name: str,
    expected_lock_version: int,
    clock: Clock | None = None,
) -> Subject:
    """Renomeie Subject dentro de seu pai atual."""
    scoped = Subject.objects.filter(workspace_id=workspace_id)
    try:
        current = scoped.get(pk=subject_id)
    except Subject.DoesNotExist as error:
        raise TaxonomyNotFoundError("Subject não encontrado no Workspace.") from error
    return _rename_item(
        queryset=scoped,
        duplicate_queryset=scoped.filter(discipline_id=current.discipline_id),
        item_id=subject_id,
        name=name,
        expected_lock_version=expected_lock_version,
        clock=clock,
    )


def rename_subsubject(
    *,
    workspace_id: uuid.UUID,
    subsubject_id: uuid.UUID,
    name: str,
    expected_lock_version: int,
    clock: Clock | None = None,
) -> Subsubject:
    """Renomeie Subsubject dentro de seu pai atual."""
    scoped = Subsubject.objects.filter(workspace_id=workspace_id)
    try:
        current = scoped.get(pk=subsubject_id)
    except Subsubject.DoesNotExist as error:
        raise TaxonomyNotFoundError("Subsubject não encontrado no Workspace.") from error
    return _rename_item(
        queryset=scoped,
        duplicate_queryset=scoped.filter(subject_id=current.subject_id),
        item_id=subsubject_id,
        name=name,
        expected_lock_version=expected_lock_version,
        clock=clock,
    )


@transaction.atomic
def _archive_item[TaxonomyItemT: TaxonomyItem](
    *,
    queryset: models.QuerySet[TaxonomyItemT],
    item_id: uuid.UUID,
    expected_lock_version: int,
    clock: Clock | None,
) -> TaxonomyItemT:
    try:
        item = queryset.get(pk=item_id)
    except queryset.model.DoesNotExist as error:
        raise TaxonomyNotFoundError("Item de taxonomia não encontrado no Workspace.") from error
    if item.status == TaxonomyStatus.ARCHIVED:
        raise TaxonomyStateConflictError("O item já está arquivado.")
    if item.lock_version != expected_lock_version:
        raise TaxonomyConcurrencyError("O item mudou; recarregue a versão atual.")

    current_clock = clock or SystemClock()
    now = current_clock.now().value
    with transaction.atomic():
        updated = queryset.filter(
            pk=item.id,
            status=TaxonomyStatus.ACTIVE,
            lock_version=expected_lock_version,
        ).update(
            status=TaxonomyStatus.ARCHIVED,
            archived_at=now,
            lock_version=F("lock_version") + 1,
            updated_at=now,
        )
    if updated != 1:
        raise TaxonomyConcurrencyError("O item mudou; recarregue a versão atual.")
    item.refresh_from_db()
    return item


def archive_discipline(
    *,
    workspace_id: uuid.UUID,
    discipline_id: uuid.UUID,
    expected_lock_version: int,
    clock: Clock | None = None,
) -> Discipline:
    """Arquive Discipline sem alterar o estado dos descendentes."""
    return _archive_item(
        queryset=Discipline.objects.filter(workspace_id=workspace_id),
        item_id=discipline_id,
        expected_lock_version=expected_lock_version,
        clock=clock,
    )


def archive_subject(
    *,
    workspace_id: uuid.UUID,
    subject_id: uuid.UUID,
    expected_lock_version: int,
    clock: Clock | None = None,
) -> Subject:
    """Arquive Subject sem alterar seus Subsubjects."""
    return _archive_item(
        queryset=Subject.objects.filter(workspace_id=workspace_id),
        item_id=subject_id,
        expected_lock_version=expected_lock_version,
        clock=clock,
    )


def archive_subsubject(
    *,
    workspace_id: uuid.UUID,
    subsubject_id: uuid.UUID,
    expected_lock_version: int,
    clock: Clock | None = None,
) -> Subsubject:
    """Arquive Subsubject preservando seus vínculos históricos futuros."""
    return _archive_item(
        queryset=Subsubject.objects.filter(workspace_id=workspace_id),
        item_id=subsubject_id,
        expected_lock_version=expected_lock_version,
        clock=clock,
    )
