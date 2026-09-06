"""Views finas dos fluxos web autorizados do catálogo de questões."""

import uuid
from typing import Any

from django.db import DatabaseError
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods

from modules.accounts.exceptions import WorkspaceAccessDenied
from modules.accounts.models import Workspace
from modules.accounts.services import LOCAL_USER_ID, LOCAL_WORKSPACE_ID, get_workspace_for_owner

from .exceptions import (
    OriginCatalogError,
    QuestionCatalogConcurrencyError,
    QuestionCatalogError,
    QuestionCatalogNotFoundError,
)
from .forms import (
    DraftActivationForm,
    QuestionArchiveForm,
    QuestionEditForm,
    QuestionQuickEntryForm,
)
from .models import Question, QuestionStatus
from .selectors import get_current_revision, get_question, list_question_revisions
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


def _detail_feedback(request: HttpRequest) -> str:
    return {
        "created": "Questão ativa criada com sucesso.",
        "activated": "Questão ativa criada com sucesso a partir do rascunho.",
        "edited": "Questão atualizada com sucesso.",
        "archived": "Questão arquivada. Seu conteúdo e suas revisões foram preservados.",
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
    if target is not None:
        form.fields[target].widget.attrs.update({"aria-invalid": "true", "autofocus": True})
    else:
        first_visible = next(field for field in form.fields.values() if not field.widget.is_hidden)
        first_visible.widget.attrs["autofocus"] = True


def _render_form(
    request: HttpRequest,
    *,
    workspace: Workspace,
    form: QuestionQuickEntryForm,
    title: str,
    eyebrow: str,
    draft: Question | None = None,
    cancel_url: str | None = None,
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
            "cancel_url": cancel_url or reverse("accounts:home"),
            "breadcrumbs": [("Início", reverse("accounts:home"))],
        },
    )


def _question_or_404(*, workspace: Workspace, question_id: uuid.UUID) -> Question:
    try:
        return get_question(workspace_id=workspace.id, question_id=question_id)
    except QuestionCatalogNotFoundError as error:
        raise Http404("Questão não encontrada.") from error


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
                question = QuestionCommandService.create_active(workspace_id=workspace.id, **values)
                return redirect(f"{reverse('questions:detail', args=[question.id])}?result=created")
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
            updated = QuestionCommandService.complete_draft(
                workspace_id=workspace.id,
                question_id=question.id,
                expected_lock_version=form.cleaned_data["lock_version"],
                **values,
            )
            return redirect(f"{reverse('questions:detail', args=[updated.id])}?result=activated")
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


@require_GET
def question_detail(request: HttpRequest, question_id: uuid.UUID) -> HttpResponse:
    """Exiba somente fatos persistidos do agregado e de suas revisões."""
    workspace = _local_workspace()
    if workspace is None:
        return redirect("accounts:initial-setup")
    question = _question_or_404(workspace=workspace, question_id=question_id)
    revisions = list(list_question_revisions(workspace_id=workspace.id, question_id=question.id))
    current_revision = next((item for item in revisions if item.is_current), None)
    return render(
        request,
        "questions/detail.html",
        {
            "workspace": workspace,
            "question": question,
            "current_revision": current_revision,
            "revisions": list(reversed(revisions)),
            "origin": getattr(question, "origin", None),
            "feedback": _detail_feedback(request),
            "breadcrumbs": [("Início", reverse("accounts:home"))],
        },
    )


@require_http_methods(["GET", "POST"])
def question_edit(request: HttpRequest, question_id: uuid.UUID) -> HttpResponse:
    """Edite o agregado por um único comando transacional e use PRG no sucesso."""
    workspace = _local_workspace()
    if workspace is None:
        return redirect("accounts:initial-setup")
    question = _question_or_404(workspace=workspace, question_id=question_id)
    if question.status == QuestionStatus.ARCHIVED:
        raise Http404("Questão arquivada não pode ser editada.")
    form = QuestionEditForm(
        request.POST if request.method == "POST" else None,
        initial=_initial_from_question(workspace=workspace, question=question),
        workspace_id=workspace.id,
    )
    if request.method == "POST" and form.is_valid():
        try:
            QuestionCommandService.edit(
                workspace_id=workspace.id,
                question_id=question.id,
                expected_lock_version=form.cleaned_data["lock_version"],
                **_command_values(form),
            )
            return redirect(f"{reverse('questions:detail', args=[question.id])}?result=edited")
        except QuestionCatalogConcurrencyError as error:
            question.refresh_from_db()
            data = request.POST.copy()
            data["lock_version"] = str(question.lock_version)
            form = QuestionEditForm(data, workspace_id=workspace.id)
            form.is_valid()
            _service_error(form, error)
        except (QuestionCatalogError, OriginCatalogError, DatabaseError, ValueError) as error:
            _service_error(form, error)
    return _render_form(
        request,
        workspace=workspace,
        form=form,
        title="Editar questão",
        eyebrow="Edição versionada",
        draft=question if question.status == QuestionStatus.DRAFT else None,
        cancel_url=reverse("questions:detail", args=[question.id]),
    )


@require_http_methods(["GET", "POST"])
def question_archive(request: HttpRequest, question_id: uuid.UUID) -> HttpResponse:
    """Confirme e arquive sem excluir qualquer parte do agregado."""
    workspace = _local_workspace()
    if workspace is None:
        return redirect("accounts:initial-setup")
    question = _question_or_404(workspace=workspace, question_id=question_id)
    if question.status == QuestionStatus.ARCHIVED:
        raise Http404("A questão já está arquivada.")
    form = QuestionArchiveForm(
        request.POST if request.method == "POST" else None,
        initial={"lock_version": question.lock_version},
    )
    if request.method == "POST" and form.is_valid():
        try:
            QuestionCommandService.archive(
                workspace_id=workspace.id,
                question_id=question.id,
                expected_lock_version=form.cleaned_data["lock_version"],
            )
            return redirect(f"{reverse('questions:detail', args=[question.id])}?result=archived")
        except QuestionCatalogConcurrencyError as error:
            question.refresh_from_db()
            if question.status == QuestionStatus.ARCHIVED:
                return redirect(reverse("questions:detail", args=[question.id]))
            data = request.POST.copy()
            data["lock_version"] = str(question.lock_version)
            form = QuestionArchiveForm(data)
            form.is_valid()
            form.add_error(None, str(error))
            form.fields["confirm"].widget.attrs["autofocus"] = True
        except (QuestionCatalogError, DatabaseError, ValueError) as error:
            form.add_error(None, str(error))
            form.fields["confirm"].widget.attrs["autofocus"] = True
    return render(
        request,
        "questions/archive_confirm.html",
        {
            "workspace": workspace,
            "question": question,
            "form": form,
            "breadcrumbs": [
                ("Início", reverse("accounts:home")),
                ("Detalhe da questão", reverse("questions:detail", args=[question.id])),
            ],
        },
    )
