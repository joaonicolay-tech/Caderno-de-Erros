"""Expurgo explícito e seletivo da auditoria sanitizada de exclusão S2D."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from django.db import connection, transaction

from .models import AuditEvent, AuditEventCode

RETENTION = timedelta(days=90)


def purge_expired_question_deletion_events(*, now: datetime | None = None) -> int:
    """Remova somente eventos finais sanitizados cujo prazo UTC terminou."""
    instant = now or datetime.now(UTC)
    if instant.tzinfo is None or instant.utcoffset() is None:
        raise ValueError("O instante de expurgo precisa ter fuso.")
    cutoff = instant.astimezone(UTC) - RETENTION
    with transaction.atomic(durable=True):
        eligible = AuditEvent.objects.filter(
            event_code=AuditEventCode.QUESTION_PERMANENTLY_DELETED,
            created_at__lte=cutoff,
            entity_type="QUESTION",
            entity_id__isnull=True,
            previous_entity_id__isnull=True,
            related_entity_id__isnull=True,
            previous_date__isnull=True,
            new_date__isnull=True,
            timezone_name__isnull=True,
            reason_code__isnull=False,
        ).values_list("id", flat=True)
        ids = list(eligible)
        deleted = 0
        with connection.cursor() as cursor:
            for offset in range(0, len(ids), 400):
                batch = ids[offset : offset + 400]
                placeholders = ",".join(["%s"] * len(batch))
                cursor.execute(
                    "DELETE FROM operations_auditevent "  # noqa: S608
                    f"WHERE event_code = %s AND created_at <= %s AND id IN ({placeholders})",
                    [
                        AuditEventCode.QUESTION_PERMANENTLY_DELETED,
                        cutoff,
                        *(item.hex for item in batch),
                    ],
                )
                deleted += cursor.rowcount
        return deleted
