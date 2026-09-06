"""Validações dos catálogos de origem e questões."""

import unicodedata
from dataclasses import dataclass

from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import URLValidator

from modules.accounts.models import Workspace
from modules.taxonomy.exceptions import TaxonomyValidationError
from modules.taxonomy.validators import NormalizedTaxonomyName, normalize_taxonomy_name
from shared.domain.time import Calendar, Clock, SystemClock, TimeZoneId

from .exceptions import OriginCatalogValidationError, QuestionCatalogValidationError

ORIGIN_NAME_MAX_LENGTH = 120
ORIGIN_URL_MAX_LENGTH = 2048
MINIMUM_EXAM_YEAR = 1900
QUESTION_DRAFT_TITLE_MAX_LENGTH = 200
QUESTION_STEM_MAX_LENGTH = 20_000
ALTERNATIVE_TEXT_MAX_LENGTH = 4_000
ALTERNATIVE_LABEL_MAX_LENGTH = 10
QUESTION_EXPLANATION_MAX_LENGTH = 10_000
QUESTION_TRAP_NOTE_MAX_LENGTH = 5_000
QUESTION_NOTES_MAX_LENGTH = 10_000
QUESTION_REFERENCE_MAX_LENGTH = 1_000

_http_url_validator = URLValidator(schemes=("http", "https"))


def normalize_origin_name(value: str) -> NormalizedTaxonomyName:
    """Reutilize a política canônica já aprovada para nomes curtos."""
    try:
        return normalize_taxonomy_name(value)
    except TaxonomyValidationError as error:
        raise OriginCatalogValidationError(str(error)) from error


def normalize_optional_url(value: str | None, *, field_label: str) -> str | None:
    """Converta ausência em NULL e aceite somente URL HTTP(S) dentro do limite."""
    if value is None:
        return None
    if not isinstance(value, str):
        raise OriginCatalogValidationError(f"{field_label} deve ser uma URL ou nula.")
    normalized = value.strip()
    if not normalized:
        return None
    if len(normalized) > ORIGIN_URL_MAX_LENGTH:
        raise OriginCatalogValidationError(
            f"{field_label} deve ter no máximo {ORIGIN_URL_MAX_LENGTH} caracteres."
        )
    try:
        _http_url_validator(normalized)
    except DjangoValidationError as error:
        raise OriginCatalogValidationError(
            f"{field_label} deve ser uma URL HTTP(S) válida."
        ) from error
    return normalized


def normalize_optional_notes(value: str | None) -> str | None:
    """Preserve o texto informado e represente vazio como ausência."""
    if value is None:
        return None
    if not isinstance(value, str):
        raise OriginCatalogValidationError("As observações devem ser um texto ou nulas.")
    normalized = value.strip()
    return normalized or None


def validate_exam_year(
    year: int | None,
    *,
    workspace: Workspace,
    clock: Clock | None = None,
) -> None:
    """Valide 1900..ano civil corrente do Workspace + 2 via Clock/Calendar."""
    if year is None:
        return
    if isinstance(year, bool) or not isinstance(year, int):
        raise OriginCatalogValidationError("O ano da prova deve ser um inteiro ou nulo.")

    calendar = Calendar(clock or SystemClock())
    current_year = calendar.today(TimeZoneId(workspace.timezone_name)).value.year
    maximum_year = current_year + 2
    if year < MINIMUM_EXAM_YEAR or year > maximum_year:
        raise OriginCatalogValidationError(
            f"O ano da prova deve estar entre {MINIMUM_EXAM_YEAR} e {maximum_year}."
        )


def normalize_optional_question_text(
    value: str | None,
    *,
    field_label: str,
    max_length: int,
) -> str | None:
    """Normalize Unicode/bordas, preserve o conteúdo interno e use NULL para ausência."""
    if value is None:
        return None
    if not isinstance(value, str):
        raise QuestionCatalogValidationError(f"{field_label} deve ser um texto ou nulo.")
    normalized = unicodedata.normalize("NFC", value.strip())
    if not normalized:
        return None
    if len(normalized) > max_length:
        raise QuestionCatalogValidationError(
            f"{field_label} deve ter no máximo {max_length} caracteres."
        )
    return normalized


@dataclass(frozen=True, slots=True)
class NormalizedAlternative:
    """Texto preservado e chave usada para detectar alternativas indistinguíveis."""

    text: str
    text_key: str


def normalize_alternative_text(value: str) -> NormalizedAlternative:
    """Valide texto de alternativa e derive uma chave Unicode/casefold estável."""
    normalized = normalize_optional_question_text(
        value,
        field_label="A alternativa",
        max_length=ALTERNATIVE_TEXT_MAX_LENGTH,
    )
    if normalized is None:
        raise QuestionCatalogValidationError("A alternativa não pode ser vazia.")
    text_key = unicodedata.normalize("NFC", " ".join(normalized.split()).casefold())
    return NormalizedAlternative(text=normalized, text_key=text_key)


def normalize_alternative_label(value: str | None) -> str | None:
    """Normalize o rótulo curto opcional de uma alternativa."""
    return normalize_optional_question_text(
        value,
        field_label="O rótulo da alternativa",
        max_length=ALTERNATIVE_LABEL_MAX_LENGTH,
    )


def validate_reference_year(
    year: int | None,
    *,
    workspace: Workspace,
    clock: Clock | None = None,
) -> None:
    """Valide o ano de referência no calendário civil do Workspace."""
    if year is None:
        return
    if isinstance(year, bool) or not isinstance(year, int):
        raise QuestionCatalogValidationError("O ano de referência deve ser um inteiro ou nulo.")
    calendar = Calendar(clock or SystemClock())
    current_year = calendar.today(TimeZoneId(workspace.timezone_name)).value.year
    maximum_year = current_year + 2
    if year < MINIMUM_EXAM_YEAR or year > maximum_year:
        raise QuestionCatalogValidationError(
            f"O ano de referência deve estar entre {MINIMUM_EXAM_YEAR} e {maximum_year}."
        )
