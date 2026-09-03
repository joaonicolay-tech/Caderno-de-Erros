"""Testes de logging, correlação e health local da Etapa 5."""

import json
import logging
from collections.abc import Iterator
from contextlib import contextmanager
from io import StringIO
from typing import Any, cast
from unittest.mock import patch

import pytest
from django.apps import apps
from django.conf import settings
from django.core.management import get_commands
from django.core.management.commands.migrate import Command as DjangoMigrateCommand
from django.db import OperationalError
from django.test import Client

from modules.accounts.models import User, Workspace
from modules.errors.models import ErrorCategory
from modules.operations.apps import OperationsConfig
from modules.operations.correlation import (
    correlation_scope,
    current_correlation_id,
    normalized_correlation_id,
)
from modules.operations.events import EventCode, EventOutcome
from modules.operations.management.commands.migrate import Command as InstrumentedMigrateCommand
from modules.operations.structured_logging import REDACTED, StructuredJsonFormatter, emit_event
from shared.application.bootstrap import bootstrap_local_workspace

FIXED_CORRELATION_ID = "12345678-1234-4234-8234-123456789abc"
PRIVATE_SENTINEL = "PRIVATE-SENTINEL-DO-NOT-LOG-42"


@contextmanager
def captured_logger(name: str = "cei") -> Iterator[StringIO]:
    """Capture o logger indicado usando o formatter efetivo da aplicação."""
    logger = logging.getLogger(name)
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(StructuredJsonFormatter())
    previous_level = logger.level
    previous_propagate = logger.propagate
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    logger.addHandler(handler)
    try:
        yield stream
    finally:
        logger.removeHandler(handler)
        logger.setLevel(previous_level)
        logger.propagate = previous_propagate


def parsed_events(stream: StringIO) -> list[dict[str, Any]]:
    """Converta as linhas capturadas em documentos JSON."""
    return [cast(dict[str, Any], json.loads(line)) for line in stream.getvalue().splitlines()]


def test_structured_log_has_required_fields_and_correlation() -> None:
    with captured_logger("cei.test.format") as stream, correlation_scope(FIXED_CORRELATION_ID):
        emit_event(
            EventCode.BACKUP_FAILED,
            operation="backup.create",
            outcome=EventOutcome.FAILED,
            level=logging.ERROR,
            context={"error_code": "BACKUP_FAILURE", "record_count": 0},
            logger=logging.getLogger("cei.test.format"),
        )

    event = parsed_events(stream)[0]
    assert set(event) == {
        "timestamp",
        "level",
        "event_code",
        "correlation_id",
        "operation",
        "outcome",
        "context",
    }
    assert event["timestamp"].endswith("+00:00")
    assert event["level"] == "ERROR"
    assert event["event_code"] == "BACKUP_FAILED"
    assert event["correlation_id"] == FIXED_CORRELATION_ID
    assert event["operation"] == "backup.create"
    assert event["outcome"] == "failed"


def test_central_sanitization_removes_secret_and_private_payloads() -> None:
    private_context = {
        "password": PRIVATE_SENTINEL,
        "secret_key": settings.SECRET_KEY,
        "token": PRIVATE_SENTINEL,
        "authorization": f"Bearer {PRIVATE_SENTINEL}",
        "cookie": PRIVATE_SENTINEL,
        "session": PRIVATE_SENTINEL,
        "body": {"question": PRIVATE_SENTINEL, "answer": PRIVATE_SENTINEL},
        "payload": PRIVATE_SENTINEL,
        "safe_id": "entity-123",
        "diagnostic": f"Authorization: Bearer {PRIVATE_SENTINEL}",
    }
    with captured_logger("cei.test.sanitize") as stream:
        emit_event(
            EventCode.BACKUP_FAILED,
            operation="backup.create",
            outcome=EventOutcome.FAILED,
            context=private_context,
            logger=logging.getLogger("cei.test.sanitize"),
        )

    raw_log = stream.getvalue()
    event = parsed_events(stream)[0]
    assert PRIVATE_SENTINEL not in raw_log
    assert settings.SECRET_KEY not in raw_log
    assert event["context"]["safe_id"] == "entity-123"
    assert event["context"]["password"] == REDACTED
    assert event["context"]["body"] == REDACTED
    assert event["context"]["diagnostic"] == f"Authorization={REDACTED}"


def test_formatter_omits_traceback_and_sanitizes_unclassified_message() -> None:
    logger = logging.getLogger("cei.test.unclassified")
    with captured_logger(logger.name) as stream:
        try:
            raise RuntimeError(f"token={PRIVATE_SENTINEL}")
        except RuntimeError:
            logger.exception("Authorization=Bearer %s", PRIVATE_SENTINEL)

    raw_log = stream.getvalue()
    event = parsed_events(stream)[0]
    assert event["event_code"] == "UNCLASSIFIED_LOG"
    assert PRIVATE_SENTINEL not in raw_log
    assert "Traceback" not in raw_log


def test_correlation_scope_propagates_and_does_not_persist() -> None:
    assert current_correlation_id() is None
    with correlation_scope(FIXED_CORRELATION_ID) as outer:
        with correlation_scope() as inner:
            assert outer == inner == FIXED_CORRELATION_ID
            assert current_correlation_id() == FIXED_CORRELATION_ID
    assert current_correlation_id() is None


def test_invalid_correlation_id_is_replaced() -> None:
    generated = normalized_correlation_id("not-a-valid-uuid")
    assert generated != "not-a-valid-uuid"
    assert normalized_correlation_id(generated) == generated


def test_native_migrate_command_is_instrumented() -> None:
    assert get_commands()["migrate"] == "modules.operations"


def test_application_initialization_emits_minimal_structured_event() -> None:
    config = cast(OperationsConfig, apps.get_app_config("operations"))
    config._initialization_logged = False
    try:
        with captured_logger() as stream:
            config.ready()
    finally:
        config._initialization_logged = True

    event = parsed_events(stream)[0]
    assert event["event_code"] == "APPLICATION_INITIALIZED"
    assert event["operation"] == "application.initialize"
    assert event["context"] == {"profile": "test", "version": "0.1.0"}


@pytest.mark.django_db
def test_health_is_ready_only_with_available_database() -> None:
    response = Client().get(
        "/health/",
        REMOTE_ADDR="127.0.0.1",
        HTTP_X_CORRELATION_ID=FIXED_CORRELATION_ID,
    )
    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "checks": {"application": "ok", "database": "ok"},
    }
    assert response.headers["X-Correlation-ID"] == FIXED_CORRELATION_ID


@pytest.mark.django_db
def test_health_is_unhealthy_and_safe_when_database_is_unavailable() -> None:
    private_error = f"database path and SECRET_KEY={PRIVATE_SENTINEL}"
    with captured_logger() as stream:
        with patch(
            "modules.operations.health.connection.cursor",
            side_effect=OperationalError(private_error),
        ):
            response = Client().get("/health/", REMOTE_ADDR="::1")

    raw_response = response.content.decode()
    raw_log = stream.getvalue()
    assert response.status_code == 503
    assert response.json() == {
        "status": "unhealthy",
        "checks": {"application": "ok", "database": "unavailable"},
    }
    assert PRIVATE_SENTINEL not in raw_response
    assert PRIVATE_SENTINEL not in raw_log
    assert settings.SECRET_KEY not in raw_response
    assert "Traceback" not in raw_response
    assert parsed_events(stream)[0]["event_code"] == "HEALTH_CHECK_FAILED"


def test_http_boundary_rejects_non_local_client_without_details() -> None:
    response = Client().get(
        "/health/",
        REMOTE_ADDR="192.0.2.10",
        HTTP_X_CORRELATION_ID="invalid-value",
    )
    assert response.status_code == 403
    assert response.json() == {"status": "forbidden"}
    assert response.headers["X-Correlation-ID"] != "invalid-value"


@pytest.mark.django_db
def test_bootstrap_and_seed_share_correlation_without_behavior_change() -> None:
    with captured_logger() as stream:
        result = bootstrap_local_workspace(
            timezone_id="America/Sao_Paulo",
            correlation_id=FIXED_CORRELATION_ID,
        )

    events = parsed_events(stream)
    event_codes = [event["event_code"] for event in events]
    assert event_codes == [
        "BOOTSTRAP_STARTED",
        "CATEGORY_SEED_STARTED",
        "CATEGORY_SEED_SUCCEEDED",
        "BOOTSTRAP_SUCCEEDED",
    ]
    assert {event["correlation_id"] for event in events} == {FIXED_CORRELATION_ID}
    assert User.objects.count() == 1
    assert Workspace.objects.count() == 1
    assert ErrorCategory.objects.count() == 10
    assert len(result.categories) == 10


@pytest.mark.django_db
def test_bootstrap_validation_failure_is_safe_and_rolls_back() -> None:
    with captured_logger() as stream:
        with pytest.raises(ValueError):
            bootstrap_local_workspace(
                timezone_id="Invalid/Timezone",
                workspace_name=PRIVATE_SENTINEL,
                correlation_id=FIXED_CORRELATION_ID,
            )

    events = parsed_events(stream)
    assert [event["event_code"] for event in events] == [
        "BOOTSTRAP_STARTED",
        "BOOTSTRAP_FAILED",
    ]
    assert {event["correlation_id"] for event in events} == {FIXED_CORRELATION_ID}
    assert PRIVATE_SENTINEL not in stream.getvalue()
    assert User.objects.count() == 0
    assert Workspace.objects.count() == 0
    assert ErrorCategory.objects.count() == 0


def test_migration_failure_is_correlated_without_exception_details() -> None:
    with captured_logger() as stream:
        with patch.object(
            DjangoMigrateCommand,
            "handle",
            side_effect=OperationalError(f"path={PRIVATE_SENTINEL}"),
        ):
            with pytest.raises(OperationalError):
                InstrumentedMigrateCommand().handle(correlation_id=FIXED_CORRELATION_ID)

    events = parsed_events(stream)
    assert [event["event_code"] for event in events] == [
        "MIGRATION_STARTED",
        "MIGRATION_FAILED",
    ]
    assert {event["correlation_id"] for event in events} == {FIXED_CORRELATION_ID}
    assert PRIVATE_SENTINEL not in stream.getvalue()
    assert "Traceback" not in stream.getvalue()
