"""Validações fechadas para metadados funcionais auditáveis."""

import re

from django.core.exceptions import ValidationError

_REASON_CODE_PATTERN = re.compile(r"[A-Z][A-Z0-9_]{0,63}\Z")


def normalize_reason_code(value: str | None, *, required: bool) -> str | None:
    """Aceite somente códigos opacos; texto livre não pertence à auditoria."""
    normalized = value.strip().upper() if isinstance(value, str) else ""
    if not normalized:
        if required:
            raise ValidationError("Um código de motivo é obrigatório.")
        return None
    if not _REASON_CODE_PATTERN.fullmatch(normalized):
        raise ValidationError("O motivo deve ser um código de até 64 caracteres (A-Z, 0-9 e _).")
    return normalized
