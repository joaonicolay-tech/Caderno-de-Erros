"""Validadores persistentes do módulo Accounts/Workspace."""

from django.core.exceptions import ValidationError

from shared.domain.time import TimeZoneId


def validate_iana_timezone(value: str) -> None:
    """Rejeite valores que não identifiquem um fuso IANA disponível."""
    try:
        TimeZoneId(value)
    except (TypeError, ValueError) as error:
        raise ValidationError(
            "Informe um identificador de fuso IANA válido.",
            code="invalid_timezone",
        ) from error
