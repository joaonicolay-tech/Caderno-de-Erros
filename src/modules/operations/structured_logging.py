"""Emissão JSON e sanitização central dos logs operacionais."""

import json
import logging
import re
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime

from django.conf import settings

from .correlation import current_correlation_id, new_correlation_id
from .events import EventCode, EventOutcome

LOGGER = logging.getLogger("cei")
REDACTED = "[REDACTED]"

_SENSITIVE_KEYS = frozenset(
    {
        "authorization",
        "alternative",
        "alternatives",
        "answer",
        "body",
        "content",
        "cookie",
        "cookies",
        "credential",
        "credentials",
        "database_name",
        "dsn",
        "enunciado",
        "explanation",
        "headers",
        "password",
        "passwd",
        "path",
        "payload",
        "question",
        "query_string",
        "request",
        "request_body",
        "response_body",
        "resposta",
        "secret",
        "secret_key",
        "session",
        "sessionid",
        "set_cookie",
        "token",
    }
)
_SENSITIVE_SUFFIXES = ("_password", "_secret", "_token", "_cookie", "_session")
_CREDENTIAL_PATTERN = re.compile(
    r"(?i)\b(authorization|password|passwd|secret(?:_key)?|token|cookie|session(?:id)?)"
    r"\b\s*[:=]\s*(?:bearer\s+|basic\s+)?(?:\"[^\"]*\"|'[^']*'|[^,;\s]+)"
)
_AUTH_SCHEME_PATTERN = re.compile(r"(?i)\b(?:bearer|basic)\s+[a-z0-9._~+/=-]+")


def _is_sensitive_key(key: object) -> bool:
    normalized = str(key).strip().lower().replace("-", "_")
    return normalized in _SENSITIVE_KEYS or normalized.endswith(_SENSITIVE_SUFFIXES)


def _configured_secret_values() -> tuple[str, ...]:
    try:
        secret = str(settings.SECRET_KEY)
    except Exception:  # pragma: no cover - proteção antes da configuração Django
        return ()
    return (secret,) if secret else ()


def _sanitize_text(value: str, secret_values: Sequence[str]) -> str:
    sanitized = value
    for secret in secret_values:
        if secret:
            sanitized = sanitized.replace(secret, REDACTED)
    sanitized = _CREDENTIAL_PATTERN.sub(lambda match: f"{match.group(1)}={REDACTED}", sanitized)
    return _AUTH_SCHEME_PATTERN.sub(REDACTED, sanitized)


def sanitize_log_value(
    value: object,
    *,
    secret_values: Sequence[str] | None = None,
) -> object:
    """Sanitize recursivamente chaves e valores antes da serialização."""
    secrets = tuple(secret_values) if secret_values is not None else _configured_secret_values()
    if isinstance(value, Mapping):
        sanitized_mapping: dict[str, object] = {}
        for key, item in value.items():
            normalized_key = str(key)
            sanitized_mapping[normalized_key] = (
                REDACTED
                if _is_sensitive_key(key)
                else sanitize_log_value(item, secret_values=secrets)
            )
        return sanitized_mapping
    if isinstance(value, str):
        return _sanitize_text(value, secrets)
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return [sanitize_log_value(item, secret_values=secrets) for item in value]
    return f"<{type(value).__name__}>"


class StructuredJsonFormatter(logging.Formatter):
    """Produza uma linha JSON segura, sem traceback nem payload arbitrário."""

    def format(self, record: logging.LogRecord) -> str:
        event_code = getattr(record, "event_code", "UNCLASSIFIED_LOG")
        operation = getattr(record, "operation", record.name)
        outcome = getattr(record, "outcome", record.levelname.lower())
        context = getattr(record, "technical_context", {})
        if event_code == "UNCLASSIFIED_LOG":
            context = {"message": record.getMessage(), "details": context}

        document = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(
                timespec="milliseconds"
            ),
            "level": record.levelname,
            "event_code": event_code,
            "correlation_id": getattr(
                record,
                "correlation_id",
                current_correlation_id() or new_correlation_id(),
            ),
            "operation": operation,
            "outcome": outcome,
            "context": context,
        }
        return json.dumps(
            sanitize_log_value(document),
            ensure_ascii=False,
            separators=(",", ":"),
        )


def emit_event(
    event_code: EventCode,
    *,
    operation: str,
    outcome: EventOutcome,
    level: int = logging.INFO,
    context: Mapping[str, object] | None = None,
    logger: logging.Logger = LOGGER,
) -> None:
    """Emita somente campos estruturados; o formatter aplica a sanitização final."""
    logger.log(
        level,
        event_code.value,
        extra={
            "event_code": event_code.value,
            "correlation_id": current_correlation_id() or new_correlation_id(),
            "operation": operation,
            "outcome": outcome.value,
            "technical_context": dict(context or {}),
        },
    )
