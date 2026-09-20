"""Seed idempotente das categorias padrão."""

import logging
import uuid
from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import F, Max

from modules.accounts.models import Workspace
from modules.attempts.persistence import run_sqlite_critical_write
from modules.operations.correlation import correlation_scope
from modules.operations.events import EventCode, EventOutcome
from modules.operations.models import AuditEntityType, AuditEventCode
from modules.operations.services import record_audit_event
from modules.operations.structured_logging import emit_event
from modules.operations.validators import normalize_reason_code
from shared.domain.time import Clock, SystemClock

from .catalog import STANDARD_ERROR_CATEGORIES, normalize_name_key
from .models import (
    ErrorCategory,
    ErrorCategoryCode,
    ErrorCategoryKind,
    ErrorCategoryState,
    ErrorClassification,
    ErrorClassificationRevision,
)


@dataclass(frozen=True, slots=True)
class StandardCategorySeedResult:
    """Categorias resultantes e quantidade criada nesta execução."""

    categories: tuple[ErrorCategory, ...]
    created_count: int


class ErrorDiagnosisConflictError(RuntimeError):
    """A projeção de diagnóstico mudou desde a versão apresentada."""


class PersonalCategoryConflictError(RuntimeError):
    """A categoria pessoal não está elegível ou mudou concorrentemente."""


def _personal_name(value: str) -> tuple[str, str]:
    display_name = " ".join(value.split())
    if not display_name or len(display_name) > 120:
        raise ValidationError("O nome da categoria pessoal deve possuir de 1 a 120 caracteres.")
    return display_name, normalize_name_key(display_name)


class PersonalCategoryService:
    """Gerencie categorias pessoais sem reescrever classificações históricas."""

    def __init__(self, *, workspace_id: uuid.UUID) -> None:
        self.workspace_id = workspace_id

    def create(self, *, display_name: str) -> ErrorCategory:
        name, name_key = _personal_name(display_name)

        def write() -> ErrorCategory:
            try:
                with transaction.atomic(durable=True):
                    if not Workspace.objects.filter(pk=self.workspace_id).exists():
                        raise PersonalCategoryConflictError("Workspace não disponível.")
                    if ErrorCategory.objects.filter(
                        workspace_id=self.workspace_id,
                        category_kind=ErrorCategoryKind.PERSONAL,
                        name_key=name_key,
                    ).exists():
                        raise PersonalCategoryConflictError(
                            "Já existe categoria pessoal com esse nome no Workspace."
                        )
                    return ErrorCategory.objects.create(
                        workspace_id=self.workspace_id,
                        code=f"PERSONAL_{uuid.uuid4().hex.upper()}",
                        display_name=name,
                        name_key=name_key,
                        description="",
                        category_kind=ErrorCategoryKind.PERSONAL,
                        state=ErrorCategoryState.ACTIVE,
                    )
            except IntegrityError as error:
                raise PersonalCategoryConflictError(
                    "Já existe categoria pessoal com esse nome no Workspace."
                ) from error

        return run_sqlite_critical_write(write)

    def rename(
        self,
        *,
        category_id: uuid.UUID,
        display_name: str,
        reason_code: str,
        expected_lock_version: int,
        correlation_id: str | None = None,
    ) -> ErrorCategory:
        name, name_key = _personal_name(display_name)
        reason = normalize_reason_code(reason_code, required=True)

        def write() -> ErrorCategory:
            try:
                with transaction.atomic(durable=True):
                    with correlation_scope(correlation_id) as correlation:
                        category = self._locked_active_or_archived(category_id)
                        if category.lock_version != expected_lock_version:
                            raise PersonalCategoryConflictError("A categoria mudou; recarregue.")
                        changed = (
                            ErrorCategory.objects.filter(
                                pk=category.id,
                                workspace_id=self.workspace_id,
                                category_kind=ErrorCategoryKind.PERSONAL,
                                lock_version=expected_lock_version,
                            )
                            .exclude(state=ErrorCategoryState.MERGED)
                            .update(
                                display_name=name,
                                name_key=name_key,
                                lock_version=F("lock_version") + 1,
                            )
                        )
                        if changed != 1:
                            raise PersonalCategoryConflictError("A categoria mudou; recarregue.")
                        record_audit_event(
                            workspace_id=self.workspace_id,
                            event_code=AuditEventCode.PERSONAL_CATEGORY_RENAMED,
                            entity_type=AuditEntityType.ERROR_CATEGORY,
                            entity_id=category.id,
                            correlation_id=correlation,
                            reason_code=reason,
                        )
                        category.refresh_from_db()
                        return category
            except IntegrityError as error:
                raise PersonalCategoryConflictError(
                    "Já existe categoria pessoal com esse nome no Workspace."
                ) from error

        return run_sqlite_critical_write(write)

    def archive(
        self,
        *,
        category_id: uuid.UUID,
        reason_code: str,
        expected_lock_version: int,
        correlation_id: str | None = None,
    ) -> ErrorCategory:
        reason = normalize_reason_code(reason_code, required=True)

        def write() -> ErrorCategory:
            with transaction.atomic(durable=True):
                with correlation_scope(correlation_id) as correlation:
                    category = self._locked_active(category_id)
                    changed = ErrorCategory.objects.filter(
                        pk=category.id,
                        workspace_id=self.workspace_id,
                        category_kind=ErrorCategoryKind.PERSONAL,
                        state=ErrorCategoryState.ACTIVE,
                        lock_version=expected_lock_version,
                    ).update(
                        state=ErrorCategoryState.ARCHIVED,
                        lock_version=F("lock_version") + 1,
                    )
                    if changed != 1:
                        raise PersonalCategoryConflictError("A categoria mudou; recarregue.")
                    record_audit_event(
                        workspace_id=self.workspace_id,
                        event_code=AuditEventCode.PERSONAL_CATEGORY_ARCHIVED,
                        entity_type=AuditEntityType.ERROR_CATEGORY,
                        entity_id=category.id,
                        correlation_id=correlation,
                        reason_code=reason,
                    )
                    category.refresh_from_db()
                    return category

        return run_sqlite_critical_write(write)

    def merge(
        self,
        *,
        source_id: uuid.UUID,
        target_id: uuid.UUID,
        reason_code: str,
        expected_lock_version: int,
        correlation_id: str | None = None,
    ) -> ErrorCategory:
        if source_id == target_id:
            raise PersonalCategoryConflictError("Uma categoria não pode ser consolidada em si.")
        reason = normalize_reason_code(reason_code, required=True)

        def write() -> ErrorCategory:
            with transaction.atomic(durable=True):
                with correlation_scope(correlation_id) as correlation:
                    categories = {
                        item.id: item
                        for item in ErrorCategory.objects.select_for_update().filter(
                            workspace_id=self.workspace_id,
                            category_kind=ErrorCategoryKind.PERSONAL,
                        )
                    }
                    source = categories.get(source_id)
                    target = categories.get(target_id)
                    if (
                        source is None
                        or target is None
                        or source.state != ErrorCategoryState.ACTIVE
                        or target.state != ErrorCategoryState.ACTIVE
                        or source.lock_version != expected_lock_version
                    ):
                        raise PersonalCategoryConflictError(
                            "Merge exige origem e alvo pessoais ativos do mesmo Workspace."
                        )
                    current = target
                    visited: set[uuid.UUID] = set()
                    while current.merged_into_id is not None:
                        if current.id == source.id or current.id in visited:
                            raise PersonalCategoryConflictError("Merge criaria um ciclo.")
                        visited.add(current.id)
                        next_category = categories.get(current.merged_into_id)
                        if next_category is None:
                            raise PersonalCategoryConflictError("Cadeia de merge inválida.")
                        current = next_category
                    changed = ErrorCategory.objects.filter(
                        pk=source.id,
                        workspace_id=self.workspace_id,
                        category_kind=ErrorCategoryKind.PERSONAL,
                        state=ErrorCategoryState.ACTIVE,
                        lock_version=expected_lock_version,
                    ).update(
                        state=ErrorCategoryState.MERGED,
                        merged_into=target,
                        lock_version=F("lock_version") + 1,
                    )
                    if changed != 1:
                        raise PersonalCategoryConflictError("A categoria mudou; recarregue.")
                    record_audit_event(
                        workspace_id=self.workspace_id,
                        event_code=AuditEventCode.PERSONAL_CATEGORY_MERGED,
                        entity_type=AuditEntityType.ERROR_CATEGORY,
                        entity_id=source.id,
                        related_entity_id=target.id,
                        correlation_id=correlation,
                        reason_code=reason,
                    )
                    source.refresh_from_db()
                    return source

        return run_sqlite_critical_write(write)

    def _locked_active(self, category_id: uuid.UUID) -> ErrorCategory:
        category = (
            ErrorCategory.objects.select_for_update()
            .filter(
                pk=category_id,
                workspace_id=self.workspace_id,
                category_kind=ErrorCategoryKind.PERSONAL,
                state=ErrorCategoryState.ACTIVE,
            )
            .first()
        )
        if category is None:
            raise PersonalCategoryConflictError("Categoria pessoal ativa não disponível.")
        return category

    def _locked_active_or_archived(self, category_id: uuid.UUID) -> ErrorCategory:
        category = (
            ErrorCategory.objects.select_for_update()
            .filter(
                pk=category_id,
                workspace_id=self.workspace_id,
                category_kind=ErrorCategoryKind.PERSONAL,
                state__in=[ErrorCategoryState.ACTIVE, ErrorCategoryState.ARCHIVED],
            )
            .first()
        )
        if category is None:
            raise PersonalCategoryConflictError("Categoria pessoal não disponível.")
        return category


class ErrorDiagnosisService:
    """Corrija a projeção e acrescente revisões, sem tocar na Attempt."""

    def __init__(self, *, workspace_id: uuid.UUID, clock: Clock | None = None) -> None:
        self.workspace_id = workspace_id
        self.clock = clock or SystemClock()

    def correct(
        self,
        *,
        attempt_id: uuid.UUID,
        category_id: uuid.UUID,
        other_description: str = "",
        change_reason: str = "",
        expected_lock_version: int,
    ) -> ErrorClassification:
        """Faça a semeadura r1 e a correção rN em um commit curto e atômico."""
        description = " ".join(other_description.split()) or None
        reason = " ".join(change_reason.split()) or None
        if description is not None and len(description) > 500:
            raise ValueError("Descrição de diagnóstico excede o limite.")
        if reason is not None and len(reason) > 1000:
            raise ValueError("Razão de correção excede o limite.")

        def write() -> ErrorClassification:
            with transaction.atomic(durable=True):
                classification = (
                    ErrorClassification.objects.select_for_update()
                    .filter(workspace_id=self.workspace_id, attempt_id=attempt_id)
                    .select_related("attempt")
                    .first()
                )
                category = ErrorCategory.objects.filter(
                    pk=category_id, workspace_id=self.workspace_id
                ).first()
                if classification is None or category is None:
                    raise ErrorDiagnosisConflictError("Diagnóstico não disponível neste Workspace.")
                if classification.attempt.is_correct:
                    raise ErrorDiagnosisConflictError(
                        "Somente tentativa incorreta possui diagnóstico."
                    )
                if (
                    category.category_kind == ErrorCategoryKind.PERSONAL
                    and category.state != ErrorCategoryState.ACTIVE
                ):
                    raise ErrorDiagnosisConflictError(
                        "Somente categoria pessoal ativa aceita nova classificação."
                    )
                if category.code == ErrorCategoryCode.OTHER and description is None:
                    raise ValueError("A categoria OTHER exige descrição.")
                if classification.lock_version != expected_lock_version:
                    raise ErrorDiagnosisConflictError(
                        "O diagnóstico mudou; recarregue a versão atual."
                    )

                maximum = ErrorClassificationRevision.objects.filter(
                    error_classification=classification
                ).aggregate(maximum=Max("revision_number"))["maximum"]
                next_number = 1 if maximum is None else maximum + 1
                if maximum is None:
                    ErrorClassificationRevision.objects.create(
                        workspace_id=self.workspace_id,
                        error_classification=classification,
                        revision_number=1,
                        category_id=classification.category_id,
                        other_description=classification.other_description,
                        change_reason="Diagnóstico inicial preservado.",
                    )
                    next_number = 2
                ErrorClassificationRevision.objects.create(
                    workspace_id=self.workspace_id,
                    error_classification=classification,
                    revision_number=next_number,
                    category=category,
                    other_description=description,
                    change_reason=reason,
                )
                changed = ErrorClassification.objects.filter(
                    pk=classification.id,
                    workspace_id=self.workspace_id,
                    lock_version=expected_lock_version,
                ).update(
                    category=category,
                    other_description=description,
                    lock_version=F("lock_version") + 1,
                    updated_at=self.clock.now().value,
                )
                if changed != 1:
                    raise ErrorDiagnosisConflictError(
                        "O diagnóstico mudou; recarregue a versão atual."
                    )
                classification.refresh_from_db()
                return classification

        return run_sqlite_critical_write(write)


@transaction.atomic
def seed_standard_error_categories(
    workspace: Workspace,
    *,
    correlation_id: str | None = None,
) -> StandardCategorySeedResult:
    """Crie ou atualize textos canônicos, usando código como identidade estável."""
    with correlation_scope(correlation_id):
        emit_event(
            EventCode.CATEGORY_SEED_STARTED,
            operation="error_category.seed",
            outcome=EventOutcome.STARTED,
            context={"workspace_id": str(workspace.id)},
        )
        categories: list[ErrorCategory] = []
        created_count = 0
        try:
            for definition in STANDARD_ERROR_CATEGORIES:
                category, created = ErrorCategory.objects.update_or_create(
                    workspace=workspace,
                    code=definition.code,
                    defaults={
                        "display_name": definition.display_name,
                        "name_key": normalize_name_key(definition.display_name),
                        "description": definition.description,
                    },
                )
                categories.append(category)
                created_count += int(created)
        except Exception as error:
            emit_event(
                EventCode.CATEGORY_SEED_FAILED,
                operation="error_category.seed",
                outcome=EventOutcome.FAILED,
                level=logging.ERROR,
                context={
                    "workspace_id": str(workspace.id),
                    "error_code": "CATEGORY_SEED_FAILURE",
                    "error_type": type(error).__name__,
                },
            )
            raise

        emit_event(
            EventCode.CATEGORY_SEED_SUCCEEDED,
            operation="error_category.seed",
            outcome=EventOutcome.SUCCEEDED,
            context={
                "workspace_id": str(workspace.id),
                "category_count": len(categories),
                "created_count": created_count,
            },
        )
        return StandardCategorySeedResult(tuple(categories), created_count)
