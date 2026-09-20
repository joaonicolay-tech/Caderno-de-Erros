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


class AuditEntityType(models.TextChoices):
    REVIEW = "REVIEW", "Review"
    REVIEW_CYCLE = "REVIEW_CYCLE", "Ciclo de revisão"
    ERROR_CATEGORY = "ERROR_CATEGORY", "Categoria de erro"
    ATTEMPT = "ATTEMPT", "Tentativa"


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
    entity_id = models.UUIDField()
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
        ]

    def __str__(self) -> str:
        return f"{self.event_code}:{self.entity_type}:{self.entity_id}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self._state.adding:
            raise ValidationError("AuditEvent é append-only.")
        self.reason_code = normalize_reason_code(self.reason_code, required=False)
        self.full_clean()
        super().save(*args, **kwargs)

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        raise ValidationError("AuditEvent é append-only.")
