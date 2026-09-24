"""Persistência e validação fechada de filtros salvos da lista de Questions."""

from __future__ import annotations

import unicodedata
import uuid
from typing import Any

from django.db import IntegrityError, transaction
from django.http import QueryDict

from modules.accounts.models import Workspace
from modules.errors.models import ErrorCategory, ErrorCategoryState
from modules.questions.models import QuestionStatus
from modules.reviews.policies import ReviewTemporalStatus
from modules.taxonomy.models import Discipline, Subject, Subsubject

from .forms import QuestionSearchForm
from .models import SavedFilter, SavedFilterContext

QUESTIONS_LIST_SCHEMA_VERSION = 1
QUESTIONS_LIST_FIELDS = frozenset(
    {
        "query",
        "status",
        "discipline",
        "subject",
        "subsubject",
        "review_status",
        "initial_result",
        "error_category",
    }
)


class SavedFilterError(ValueError):
    """Entrada, compatibilidade ou identidade de filtro recusada."""


class SavedFilterConflictError(SavedFilterError):
    """Nome já usado pelo mesmo owner e contexto."""


def normalize_saved_filter_name(value: str) -> tuple[str, str]:
    display = " ".join(unicodedata.normalize("NFKC", value).split())
    if not display or len(display) > 80:
        raise SavedFilterError("O nome deve ter de 1 a 80 caracteres.")
    key = unicodedata.normalize("NFKC", display).casefold()
    if len(key) > 160:
        raise SavedFilterError("O nome normalizado é longo demais.")
    return display, key


def validate_questions_list_payload(payload: object, *, workspace_id: uuid.UUID) -> dict[str, str]:
    """Valide somente as chaves atuais e delegue valores ao form de busca vigente."""
    if not isinstance(payload, dict):
        raise SavedFilterError("O conteúdo do filtro precisa ser um objeto JSON.")
    unknown = set(payload) - QUESTIONS_LIST_FIELDS
    if unknown:
        raise SavedFilterError("O filtro contém campos que esta lista não reconhece.")

    query_data = QueryDict("", mutable=True)
    for field in QUESTIONS_LIST_FIELDS:
        value = payload.get(field, "")
        if value is None:
            value = ""
        if not isinstance(value, str):
            raise SavedFilterError("O filtro contém um valor com tipo inválido.")
        query_data[field] = value

    form = QuestionSearchForm(query_data, workspace_id=workspace_id)
    if not form.is_valid():
        raise SavedFilterError("Um ou mais valores do filtro não são válidos neste Workspace.")

    category_value = form.cleaned_data["error_category"]
    if category_value not in ("", "unclassified"):
        category = (
            ErrorCategory.objects.filter(
                pk=category_value,
                workspace_id=workspace_id,
            )
            .only("state")
            .first()
        )
        if category is None:
            raise SavedFilterError("A categoria salva não pertence a este Workspace.")
        if category.state != ErrorCategoryState.ACTIVE:
            raise SavedFilterError("A categoria foi arquivada ou consolidada; ajuste o filtro.")

    cleaned = form.cleaned_data
    return {
        "query": cleaned["query"],
        "status": cleaned["status"],
        "discipline": str(cleaned["discipline"].id) if cleaned["discipline"] else "",
        "subject": str(cleaned["subject"].id) if cleaned["subject"] else "",
        "subsubject": str(cleaned["subsubject"].id) if cleaned["subsubject"] else "",
        "review_status": cleaned["review_status"],
        "initial_result": cleaned["initial_result"],
        "error_category": category_value,
    }


def payload_from_search_form(form: QuestionSearchForm) -> dict[str, str]:
    """Converta dados já limpos em um payload estável e fechado."""
    if not form.is_valid():
        raise SavedFilterError("Corrija os filtros antes de salvá-los.")
    data: dict[str, Any] = {
        "query": form.cleaned_data["query"],
        "status": form.cleaned_data["status"],
        "discipline": str(form.cleaned_data["discipline"].id)
        if form.cleaned_data["discipline"]
        else "",
        "subject": str(form.cleaned_data["subject"].id) if form.cleaned_data["subject"] else "",
        "subsubject": str(form.cleaned_data["subsubject"].id)
        if form.cleaned_data["subsubject"]
        else "",
        "review_status": form.cleaned_data["review_status"],
        "initial_result": form.cleaned_data["initial_result"],
        "error_category": form.cleaned_data["error_category"],
    }
    return {key: str(value or "") for key, value in data.items()}


def check_filter_compatibility(saved_filter: SavedFilter, *, workspace_id: uuid.UUID) -> str:
    """Retorne explicação legível sem reinterpretar contexto/schema antigos."""
    if saved_filter.context_code != SavedFilterContext.QUESTIONS_LIST:
        return "Este filtro pertence a outro contexto e precisa ser recriado."
    if saved_filter.schema_version != QUESTIONS_LIST_SCHEMA_VERSION:
        return "A versão deste filtro não é compatível; recrie-o com os filtros atuais."
    try:
        validate_questions_list_payload(saved_filter.payload, workspace_id=workspace_id)
    except SavedFilterError as error:
        return str(error)
    return ""


def check_filter_compatibilities(
    saved_filters: list[SavedFilter], *, workspace_id: uuid.UUID
) -> dict[uuid.UUID, str]:
    """Calcule estados para a lista com no máximo uma consulta de categorias."""
    result: dict[uuid.UUID, str] = {}
    pending_categories: dict[uuid.UUID, list[SavedFilter]] = {}
    category_ids: set[uuid.UUID] = set()
    for saved_filter in saved_filters:
        if saved_filter.context_code != SavedFilterContext.QUESTIONS_LIST:
            result[saved_filter.id] = (
                "Este filtro pertence a outro contexto e precisa ser recriado."
            )
            continue
        if saved_filter.schema_version != QUESTIONS_LIST_SCHEMA_VERSION:
            result[saved_filter.id] = (
                "A versão deste filtro não é compatível; recrie-o com os filtros atuais."
            )
            continue
        if (
            not isinstance(saved_filter.payload, dict)
            or set(saved_filter.payload) - QUESTIONS_LIST_FIELDS
        ):
            result[saved_filter.id] = "O conteúdo do filtro não corresponde ao schema atual."
            continue
        category_value = saved_filter.payload.get("error_category", "")
        if category_value in ("", "unclassified"):
            result[saved_filter.id] = ""
            continue
        try:
            category_id = uuid.UUID(category_value) if isinstance(category_value, str) else None
        except ValueError:
            category_id = None
        if category_id is None:
            result[saved_filter.id] = "A categoria salva é inválida; recrie o filtro."
            continue
        category_ids.add(category_id)
        pending_categories.setdefault(category_id, []).append(saved_filter)

    category_states = (
        dict(
            ErrorCategory.objects.filter(
                workspace_id=workspace_id, pk__in=category_ids
            ).values_list("id", "state")
        )
        if category_ids
        else {}
    )
    for category_id, filters in pending_categories.items():
        state = category_states.get(category_id)
        message = (
            "A categoria foi arquivada ou consolidada; ajuste o filtro."
            if state is not None and state != ErrorCategoryState.ACTIVE
            else "A categoria salva não pertence a este Workspace."
            if state is None
            else ""
        )
        for saved_filter in filters:
            result[saved_filter.id] = message
    _add_payload_compatibility_details(saved_filters, workspace_id=workspace_id, result=result)
    return result


def _add_payload_compatibility_details(
    saved_filters: list[SavedFilter], *, workspace_id: uuid.UUID, result: dict[uuid.UUID, str]
) -> None:
    """Valide valores e hierarquia com consultas em lote, sem N+1 por filtro."""
    discipline_refs: dict[uuid.UUID, list[SavedFilter]] = {}
    subject_refs: dict[uuid.UUID, list[SavedFilter]] = {}
    subsubject_refs: dict[uuid.UUID, list[SavedFilter]] = {}
    for saved_filter in saved_filters:
        if result.get(saved_filter.id):
            continue
        payload = saved_filter.payload
        if not isinstance(payload, dict) or any(
            not isinstance(value, str) for value in payload.values()
        ):
            result[saved_filter.id] = (
                "O conte\u00fado do filtro n\u00e3o corresponde ao schema atual."
            )
            continue
        if len(payload.get("query", "")) > 200:
            result[saved_filter.id] = "O texto salvo excede o limite atual de busca."
        elif payload.get("status", "") not in {"", *QuestionStatus.values}:
            result[saved_filter.id] = "O estado salvo n\u00e3o existe no schema atual."
        elif payload.get("review_status", "") not in {
            "",
            ReviewTemporalStatus.OVERDUE.value,
            ReviewTemporalStatus.DUE.value,
            ReviewTemporalStatus.FUTURE.value,
        }:
            result[saved_filter.id] = (
                "A situa\u00e7\u00e3o de revis\u00e3o salva n\u00e3o existe no schema atual."
            )
        elif payload.get("initial_result", "") not in {"", "correct", "incorrect"}:
            result[saved_filter.id] = "O resultado inicial salvo n\u00e3o existe no schema atual."
        if result.get(saved_filter.id):
            continue
        for field, references in (
            ("discipline", discipline_refs),
            ("subject", subject_refs),
            ("subsubject", subsubject_refs),
        ):
            value = payload.get(field, "")
            if not value:
                continue
            try:
                identifier = uuid.UUID(value)
            except (TypeError, ValueError):
                result[saved_filter.id] = (
                    "Uma refer\u00eancia da taxonomia salva est\u00e1 inv\u00e1lida."
                )
                break
            references.setdefault(identifier, []).append(saved_filter)

    disciplines = set(
        Discipline.objects.filter(workspace_id=workspace_id, pk__in=discipline_refs).values_list(
            "id", flat=True
        )
    )
    subjects = dict(
        Subject.objects.filter(workspace_id=workspace_id, pk__in=subject_refs).values_list(
            "id", "discipline_id"
        )
    )
    subsubjects = dict(
        Subsubject.objects.filter(workspace_id=workspace_id, pk__in=subsubject_refs).values_list(
            "id", "subject_id"
        )
    )
    for identifier, filters in discipline_refs.items():
        if identifier not in disciplines:
            for saved_filter in filters:
                result[saved_filter.id] = result.get(saved_filter.id) or (
                    "A disciplina salva n\u00e3o pertence a este Workspace."
                )
    for identifier, filters in subject_refs.items():
        if identifier not in subjects:
            for saved_filter in filters:
                result[saved_filter.id] = result.get(saved_filter.id) or (
                    "O assunto salvo n\u00e3o pertence a este Workspace."
                )
    for identifier, filters in subsubject_refs.items():
        if identifier not in subsubjects:
            for saved_filter in filters:
                result[saved_filter.id] = result.get(saved_filter.id) or (
                    "O subassunto salvo n\u00e3o pertence a este Workspace."
                )
    for saved_filter in saved_filters:
        if result.get(saved_filter.id):
            continue
        payload = saved_filter.payload
        discipline_id = uuid.UUID(payload["discipline"]) if payload.get("discipline") else None
        subject_id = uuid.UUID(payload["subject"]) if payload.get("subject") else None
        subsubject_id = uuid.UUID(payload["subsubject"]) if payload.get("subsubject") else None
        subject_discipline = subjects.get(subject_id) if subject_id else None
        subsubject_subject = subsubjects.get(subsubject_id) if subsubject_id else None
        subsubject_discipline = subjects.get(subsubject_subject) if subsubject_subject else None
        if (
            (discipline_id and subject_discipline and subject_discipline != discipline_id)
            or (subject_id and subsubject_subject and subsubject_subject != subject_id)
            or (discipline_id and subsubject_discipline and subsubject_discipline != discipline_id)
        ):
            result[saved_filter.id] = "A hierarquia taxon\u00f4mica salva mudou; ajuste o filtro."


def create_saved_filter(
    *,
    workspace_id: uuid.UUID,
    owner_user_id: uuid.UUID,
    name: str,
    payload: object,
) -> SavedFilter:
    display, key = normalize_saved_filter_name(name)
    validated = validate_questions_list_payload(payload, workspace_id=workspace_id)
    if not Workspace.objects.filter(pk=workspace_id, owner_user_id=owner_user_id).exists():
        raise SavedFilterError("Workspace não disponível para esta identidade.")
    try:
        with transaction.atomic():
            return SavedFilter.objects.create(
                workspace_id=workspace_id,
                owner_user_id=owner_user_id,
                name=display,
                name_key=key,
                context_code=SavedFilterContext.QUESTIONS_LIST,
                schema_version=QUESTIONS_LIST_SCHEMA_VERSION,
                payload=validated,
            )
    except IntegrityError as error:
        raise SavedFilterConflictError(
            "Já existe um filtro com esse nome neste contexto."
        ) from error


def rename_saved_filter(
    *,
    saved_filter: SavedFilter,
    name: str,
) -> SavedFilter:
    display, key = normalize_saved_filter_name(name)
    saved_filter.name = display
    saved_filter.name_key = key
    try:
        with transaction.atomic():
            saved_filter.save(update_fields=["name", "name_key", "updated_at"])
    except IntegrityError as error:
        raise SavedFilterConflictError(
            "Já existe um filtro com esse nome neste contexto."
        ) from error
    return saved_filter


def delete_saved_filter(*, saved_filter: SavedFilter) -> None:
    with transaction.atomic():
        saved_filter.delete()
