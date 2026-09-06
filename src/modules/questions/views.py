"""Views finas do cadastro rápido e da ativação de rascunho."""

import uuid
from typing import Any

from django.db import DatabaseError
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from modules.accounts.exceptions import WorkspaceAccessDenied
from modules.accounts.models import Workspace
from modules.accounts.services import LOCAL_USER_ID, LOCAL_WORKSPACE_ID, get_workspace_for_owner

from .exceptions import (
    OriginCatalogError,
    QuestionCatalogConcurrencyError,
    QuestionCatalogError,
    QuestionCatalogNotFoundError,
)
from .forms import DraftActivationForm, QuestionQuickEntryForm
from .models import Question, QuestionStatus
from .selectors import get_current_revision, get_question
from .services import QuestionCommandService


def _local_workspace() -> Workspace | None:
    try:
        return get_workspace_for_owner(
            actor_user_id=LOCAL_USER_ID,
            workspace_id=LOCAL_WORKSPACE_ID,
        )
    except WorkspaceAccessDenied:
        return None


def _field_groups(form: QuestionQuickEntryForm) -> list[tuple[str, list[Any]]]:
    return [
        (
            "Dados essenciais",
            [
                form[name]
                for name in (
                    "draft_title",
                    "discipline",
                    "subject",
                    "subsubject",
                    "difficulty",
                    "stem",
                )
            ],
        ),
        (
            "Alternativas e gabarito",
            [
                form[name]
                for name in (
                    "alternative_1",
                    "alternative_2",
                    "alternative_3",
                    "alternative_4",
                    "correct_alternative",
                )
            ],
        ),
        ("Explicações opcionais", [form[name] for name in ("explanation", "trap_note", "notes")]),
        (
            "Origem opcional",
            [
                form[name]
                for name in (
                    "source",
                    "source_name",
                    "source_type",
                    "source_url",
                    "source_notes",
                    "exam",
                    "exam_name",
                    "exam_year",
                    "board",
                    "board_name",
                    "board_website_url",
                    "reference_year",
                    "reference_text",
                )
            ],
        ),
    ]


def _feedback(request: HttpRequest) -> str:
    return {
        "draft": "Rascunho salvo. Complete os campos abaixo quando quiser ativá-lo.",
        "active": "Questão ativa criada com sucesso.",
    }.get(request.GET.get("result", ""), "")


def _initial_from_question(*, workspace: Workspace, question: Question) -> dict[str, Any]:
    initial: dict[str, Any] = {
        "draft_title": question.draft_title,
        "discipline": question.discipline_id,
        "subject": question.subject_id,
        "subsubject": question.subsubject_id,
        "difficulty": question.difficulty or "",
        "lock_version": question.lock_version,
    }
    revision = get_current_revision(workspace_id=workspace.id, question_id=question.id)
    if revision is not None:
        initial.update(
            stem=revision.stem,
            explanation=revision.explanation,
            trap_note=revision.trap_note,
            notes=revision.notes,
        )
        alternatives = list(revision.alternatives.all().order_by("position"))
        for alternative in alternatives[:4]:
            initial[f"alternative_{alternative.position}"] = alternative.text
        if revision.correct_alternative_id:
            correct = next(
                item for item in alternatives if item.id == revision.correct_alternative_id
            )
            initial["correct_alternative"] = str(correct.position)
    origin = getattr(question, "origin", None)
    if origin is not None:
        initial.update(
            source=origin.source_id,
            exam=origin.exam_id,
            board=origin.board_id,
            reference_year=origin.reference_year,
            reference_text=origin.reference_text,
        )
    return initial


def _command_values(form: QuestionQuickEntryForm) -> dict[str, Any]:
    alternatives, correct_position = form.alternative_inputs()
    data = form.cleaned_data
    return {
        "draft_title": data["draft_title"],
        "discipline_id": data["discipline"].id if data["discipline"] else None,
        "subject_id": data["subject"].id if data["subject"] else None,
        "subsubject_id": data["subsubject"].id if data["subsubject"] else None,
        "difficulty": data["difficulty"] or None,
        "stem": data["stem"],
        "alternatives": alternatives,
        "correct_alternative_position": correct_position,
        "explanation": data["explanation"],
        "trap_note": data["trap_note"],
        "notes": data["notes"],
        "origin": form.origin_input(),
    }


def _service_error(form: QuestionQuickEntryForm, error: Exception) -> None:
    message = str(error)
    fields = {
        "enunciado": "stem",
        "alternativa": "correct_alternative",
        "gabarito": "correct_alternative",
        "Discipline": "discipline",
        "Subject": "subject",
        "Subsubject": "subsubject",
        "dificuldade": "difficulty",
        "fonte": "source",
        "prova": "exam",
        "banca": "board",
        "referência": "reference_text",
        "rascunho": "draft_title",
    }
    target = next((field for fragment, field in fields.items() if fragment in message), None)
    form.add_error(target, message)


def _render_form(
    request: HttpRequest,
    *,
    workspace: Workspace,
    form: QuestionQuickEntryForm,
    title: str,
    eyebrow: str,
    draft: Question | None = None,
) -> HttpResponse:
    return render(
        request,
        "questions/quick_entry.html",
        {
            "workspace": workspace,
            "form": form,
            "field_groups": _field_groups(form),
            "title": title,
            "eyebrow": eyebrow,
            "feedback": _feedback(request),
            "draft": draft,
            "breadcrumbs": [("Início", reverse("accounts:home"))],
        },
    )


@require_http_methods(["GET", "POST"])
def quick_entry(request: HttpRequest) -> HttpResponse:
    """Crie um rascunho ou uma questão ativa por PRG."""
    workspace = _local_workspace()
    if workspace is None:
        return redirect("accounts:initial-setup")
    form = QuestionQuickEntryForm(
        request.POST if request.method == "POST" else None, workspace_id=workspace.id
    )
    if request.method == "POST" and form.is_valid():
        try:
            values = _command_values(form)
            if request.POST.get("action") == "draft":
                question = QuestionCommandService.create_draft(workspace_id=workspace.id, **values)
                return redirect(
                    f"{reverse('questions:draft-activate', args=[question.id])}?result=draft"
                )
            if request.POST.get("action") == "activate":
                if values["discipline_id"] is None or values["subject_id"] is None:
                    raise ValueError("Informe disciplina e assunto para ativar a questão.")
                QuestionCommandService.create_active(workspace_id=workspace.id, **values)
                return redirect(f"{reverse('questions:quick-entry')}?result=active")
            form.add_error(None, "Escolha salvar rascunho ou ativar a questão.")
        except (QuestionCatalogError, OriginCatalogError, DatabaseError, ValueError) as error:
            _service_error(form, error)
    return _render_form(
        request,
        workspace=workspace,
        form=form,
        title="Nova questão",
        eyebrow="Cadastro rápido",
    )


@require_http_methods(["GET", "POST"])
def draft_activate(request: HttpRequest, question_id: uuid.UUID) -> HttpResponse:
    """Retome exclusivamente o rascunho indicado e o ative de modo atômico."""
    workspace = _local_workspace()
    if workspace is None:
        return redirect("accounts:initial-setup")
    try:
        question = get_question(workspace_id=workspace.id, question_id=question_id)
    except QuestionCatalogNotFoundError as error:
        raise Http404("Rascunho não encontrado.") from error
    if question.status != QuestionStatus.DRAFT:
        raise Http404("Rascunho não encontrado.")
    form = DraftActivationForm(
        request.POST if request.method == "POST" else None,
        initial=_initial_from_question(workspace=workspace, question=question),
        workspace_id=workspace.id,
    )
    if request.method == "POST" and form.is_valid():
        try:
            values = _command_values(form)
            if values["discipline_id"] is None or values["subject_id"] is None:
                raise ValueError("Informe disciplina e assunto para ativar a questão.")
            QuestionCommandService.complete_draft(
                workspace_id=workspace.id,
                question_id=question.id,
                expected_lock_version=form.cleaned_data["lock_version"],
                **values,
            )
            return redirect(f"{reverse('questions:quick-entry')}?result=active")
        except QuestionCatalogConcurrencyError as error:
            question.refresh_from_db()
            data = request.POST.copy()
            data["lock_version"] = str(question.lock_version)
            form = DraftActivationForm(data, workspace_id=workspace.id)
            form.is_valid()
            _service_error(form, error)
        except (QuestionCatalogError, OriginCatalogError, DatabaseError, ValueError) as error:
            _service_error(form, error)
    return _render_form(
        request,
        workspace=workspace,
        form=form,
        title="Completar rascunho",
        eyebrow="Rascunho recuperável",
        draft=question,
    )
