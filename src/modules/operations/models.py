"""Auditoria funcional mínima, distinta de logs e recibos técnicos."""

import uuid
from typing import Any, ClassVar

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from modules.accounts.models import Workspace

from .validators import normalize_reason_code


class AuditEventCode(models.TextChoices):
    REVIEW_RESCHEDULED = "REVIEW_RESCHEDULED", "Review reagendada"
    MANUAL_REVIEW_INCLUDED = "MANUAL_REVIEW_INCLUDED", "Review incluída manualmente"
    PERSONAL_CATEGORY_RENAMED = "PERSONAL_CATEGORY_RENAMED", "Categoria pessoal renomeada"
    PERSONAL_CATEGORY_ARCHIVED = "PERSONAL_CATEGORY_ARCHIVED", "Categoria pessoal arquivada"
    PERSONAL_CATEGORY_MERGED = "PERSONAL_CATEGORY_MERGED", "Categoria pessoal consolidada"
    ATTEMPT_VOIDED = "ATTEMPT_VOIDED", "Tentativa anulada"
    ATTEMPT_REPLACED = "ATTEMPT_REPLACED", "Tentativa substituída"
    ANSWER_KEY_CORRECTED = "ANSWER_KEY_CORRECTED", "Gabarito corrigido"
    QUESTION_PERMANENTLY_DELETED = (
        "QUESTION_PERMANENTLY_DELETED",
        "Questão excluída permanentemente",
    )


class AuditEntityType(models.TextChoices):
    REVIEW = "REVIEW", "Review"
    REVIEW_CYCLE = "REVIEW_CYCLE", "Ciclo de revisão"
    ERROR_CATEGORY = "ERROR_CATEGORY", "Categoria de erro"
    ATTEMPT = "ATTEMPT", "Tentativa"
    QUESTION = "QUESTION", "Questão"


class AuditEventQuerySet(models.QuerySet["AuditEvent"]):
    def update(self, **kwargs: Any) -> int:
        raise ValidationError("AuditEvent é append-only.")

    def delete(self) -> tuple[int, dict[str, int]]:
        raise ValidationError("AuditEvent é append-only.")


class AuditEvent(models.Model):
    """Metadados fechados que explicam uma mutação funcional confirmada."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.PROTECT,
        related_name="audit_events",
    )
    event_code = models.CharField(max_length=40, choices=AuditEventCode.choices)
    entity_type = models.CharField(max_length=32, choices=AuditEntityType.choices)
    entity_id = models.UUIDField(null=True, blank=True)
    previous_entity_id = models.UUIDField(null=True, blank=True)
    related_entity_id = models.UUIDField(null=True, blank=True)
    correlation_id = models.UUIDField()
    reason_code = models.CharField(max_length=64, null=True, blank=True)  # noqa: DJ001
    previous_date = models.DateField(null=True, blank=True)
    new_date = models.DateField(null=True, blank=True)
    timezone_name = models.CharField(max_length=64, null=True, blank=True)  # noqa: DJ001
    created_at = models.DateTimeField(auto_now_add=True)

    objects = AuditEventQuerySet.as_manager()

    class Meta:
        db_table = "operations_auditevent"
        indexes: ClassVar[list[models.Index]] = [
            models.Index(
                fields=["workspace", "event_code", "created_at"],
                name="audit_ws_code_time_idx",
            ),
            models.Index(
                fields=["workspace", "entity_type", "entity_id"],
                name="audit_ws_entity_idx",
            ),
        ]
        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=["workspace", "event_code", "correlation_id"],
                condition=Q(event_code=AuditEventCode.QUESTION_PERMANENTLY_DELETED),
                name="audit_delete_correlation_uq",
            ),
            models.CheckConstraint(
                condition=Q(event_code__in=AuditEventCode.values),
                name="audit_event_code_valid",
            ),
            models.CheckConstraint(
                condition=Q(entity_type__in=AuditEntityType.values),
                name="audit_entity_type_valid",
            ),
            models.CheckConstraint(
                condition=Q(reason_code__isnull=True) | ~Q(reason_code=""),
                name="audit_reason_not_empty",
            ),
            models.CheckConstraint(
                condition=(
                    Q(
                        event_code=AuditEventCode.REVIEW_RESCHEDULED,
                        entity_type=AuditEntityType.REVIEW,
                        previous_date__isnull=False,
                        new_date__isnull=False,
                        timezone_name__isnull=False,
                        reason_code__isnull=False,
                    )
                    | ~Q(event_code=AuditEventCode.REVIEW_RESCHEDULED)
                ),
                name="audit_reschedule_metadata_valid",
            ),
            models.CheckConstraint(
                condition=(
                    Q(
                        event_code__in=(
                            AuditEventCode.ATTEMPT_VOIDED,
                            AuditEventCode.ATTEMPT_REPLACED,
                        ),
                        entity_type=AuditEntityType.ATTEMPT,
                        reason_code__isnull=False,
                        previous_date__isnull=True,
                        new_date__isnull=True,
                        timezone_name__isnull=True,
                    )
                    | ~Q(
                        event_code__in=(
                            AuditEventCode.ATTEMPT_VOIDED,
                            AuditEventCode.ATTEMPT_REPLACED,
                        )
                    )
                ),
                name="audit_attempt_metadata_valid",
            ),
            models.CheckConstraint(
                condition=(
                    Q(
                        event_code=AuditEventCode.ANSWER_KEY_CORRECTED,
                        entity_type=AuditEntityType.QUESTION,
                        previous_entity_id__isnull=False,
                        related_entity_id__isnull=False,
                        reason_code__isnull=False,
                        previous_date__isnull=True,
                        new_date__isnull=True,
                        timezone_name__isnull=True,
                    )
                    | (
                        ~Q(event_code=AuditEventCode.ANSWER_KEY_CORRECTED)
                        & Q(previous_entity_id__isnull=True)
                    )
                ),
                name="audit_answer_key_metadata_valid",
            ),
            models.CheckConstraint(
                condition=(
                    Q(
                        event_code=AuditEventCode.QUESTION_PERMANENTLY_DELETED,
                        entity_type=AuditEntityType.QUESTION,
                        entity_id__isnull=True,
                        previous_entity_id__isnull=True,
                        related_entity_id__isnull=True,
                        previous_date__isnull=True,
                        new_date__isnull=True,
                        timezone_name__isnull=True,
                        reason_code__isnull=False,
                    )
                    | (
                        ~Q(event_code=AuditEventCode.QUESTION_PERMANENTLY_DELETED)
                        & Q(entity_id__isnull=False)
                    )
                ),
                name="audit_delete_metadata_valid",
            ),
        ]

    def __str__(self) -> str:
        technical_id = self.id if self.entity_id is None else self.entity_id
        return f"{self.event_code}:{self.entity_type}:{technical_id}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self._state.adding:
            raise ValidationError("AuditEvent é append-only.")
        self.reason_code = normalize_reason_code(self.reason_code, required=False)
        self.full_clean()
        super().save(*args, **kwargs)

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        raise ValidationError("AuditEvent é append-only.")
