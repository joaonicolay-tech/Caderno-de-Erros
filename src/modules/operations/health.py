"""Diagnóstico local mínimo da aplicação e da persistência."""

import logging

from django.db import DatabaseError, connection
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_GET

from .events import EventCode, EventOutcome
from .structured_logging import emit_event


@require_GET
def health(request: HttpRequest) -> JsonResponse:
    """Informe prontidão sem expor configuração, caminhos ou exceções."""
    del request
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            database_ready = cursor.fetchone() == (1,)
    except DatabaseError:
        database_ready = False

    if database_ready:
        emit_event(
            EventCode.HEALTH_CHECK_SUCCEEDED,
            operation="health.check",
            outcome=EventOutcome.SUCCEEDED,
            context={"application": "ready", "database": "ready"},
        )
        return JsonResponse(
            {"status": "healthy", "checks": {"application": "ok", "database": "ok"}}
        )

    emit_event(
        EventCode.HEALTH_CHECK_FAILED,
        operation="health.check",
        outcome=EventOutcome.FAILED,
        level=logging.ERROR,
        context={"application": "ready", "database": "unavailable"},
    )
    return JsonResponse(
        {
            "status": "unhealthy",
            "checks": {"application": "ok", "database": "unavailable"},
        },
        status=503,
    )
