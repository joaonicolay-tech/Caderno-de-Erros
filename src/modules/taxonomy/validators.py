"""Política canônica de nomes da taxonomia."""

import unicodedata
from dataclasses import dataclass

from .exceptions import TaxonomyValidationError

TAXONOMY_NAME_MAX_LENGTH = 120


@dataclass(frozen=True, slots=True)
class NormalizedTaxonomyName:
    """Representação de exibição e chave exata de comparação."""

    display: str
    key: str


def normalize_taxonomy_name(value: str) -> NormalizedTaxonomyName:
    """Normalize espaços, Unicode e caixa sem remover acentos."""
    if not isinstance(value, str):
        raise TaxonomyValidationError("O nome deve ser um texto.")

    display = unicodedata.normalize("NFC", " ".join(value.split()))
    if not display:
        raise TaxonomyValidationError("O nome não pode ser vazio.")
    if len(display) > TAXONOMY_NAME_MAX_LENGTH:
        raise TaxonomyValidationError(
            f"O nome deve ter no máximo {TAXONOMY_NAME_MAX_LENGTH} caracteres."
        )

    key = unicodedata.normalize("NFC", display.casefold())
    if len(key) > TAXONOMY_NAME_MAX_LENGTH:
        raise TaxonomyValidationError(
            "A representação normalizada do nome deve ter no máximo "
            f"{TAXONOMY_NAME_MAX_LENGTH} caracteres."
        )
    return NormalizedTaxonomyName(display=display, key=key)
