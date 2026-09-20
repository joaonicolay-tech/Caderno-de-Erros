"""Registro explícito de auditoria funcional, sem payload livre."""

import uuid
from datetime import date

from .models import AuditEvent


def record_audit_event(
    *,
    workspace_id: uuid.UUID,
    event_code: str,
    entity_type: str,
    entity_id: uuid.UUID,
    correlation_id: str,
    related_entity_id: uuid.UUID | None = None,
    reason_code: str | None = None,
    previous_date: date | None = None,
    new_date: date | None = None,
    timezone_name: str | None = None,
) -> AuditEvent:
    """Persista somente o conjunto fechado de metadados permitido."""
    return AuditEvent.objects.create(
        workspace_id=workspace_id,
        event_code=event_code,
        entity_type=entity_type,
        entity_id=entity_id,
        related_entity_id=related_entity_id,
        correlation_id=correlation_id,
        reason_code=reason_code,
        previous_date=previous_date,
        new_date=new_date,
        timezone_name=timezone_name,
    )
