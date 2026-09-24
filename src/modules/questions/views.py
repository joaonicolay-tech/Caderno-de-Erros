"""Views finas dos fluxos web autorizados do catálogo de questões."""

import json
import uuid
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, cast
from urllib.parse import urlencode, urlsplit

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import DatabaseError
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods

from modules.accounts.exceptions import WorkspaceAccessDenied
from modules.accounts.models import Workspace
from modules.accounts.services import LOCAL_USER_ID, LOCAL_WORKSPACE_ID, get_workspace_for_owner
from modules.data_management.exceptions import DataManagementError
from modules.search.forms import QuestionSearchForm
from modules.search.models import SavedFilter
from modules.search.saved_filter_services import (
    check_filter_compatibilities,
    payload_from_search_form,
)
from modules.search.selectors import list_questions, paginate_questions

from .corrections import AnswerKeyCorrectionConflictError, AnswerKeyCorrectionService
from .deletion import PermanentDeletionConflictError, PermanentQuestionDeletionService
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
from .management_forms import AnswerKeyCorrectionForm, PermanentQuestionDeleteForm
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
                *[form[f"alternative_{index}"] for index in range(1, form.alternative_count + 1)],
                form["correct_alternative"],
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
        "answer-key-corrected": "Gabarito corrigido para tentativas futuras; revisões e respostas históricas foram preservadas.",
    }.get(request.GET.get("result", ""), "")


def _list_feedback(request: HttpRequest) -> str:
    return {
        "deleted": "A questão elegível foi excluída permanentemente.",
        "deleted-cleanup-warning": (
            "A questão foi excluída. A remoção do diretório temporário de restore falhou; "
            "mantenha a pasta backups para inspeção manual antes da limpeza."
        ),
        "filter-saved": "Filtro salvo nesta lista.",
        "filter-renamed": "Filtro renomeado.",
        "filter-deleted": "Filtro salvo excluído.",
    }.get(request.GET.get("result", ""), "")


@require_GET
def question_list(request: HttpRequest) -> HttpResponse:
    """Liste o catálogo do Workspace local sem alterar qualquer registro."""
    workspace = _local_workspace()
    if workspace is None:
        return redirect("accounts:initial-setup")
    form_data = request.GET.copy()
    if "status" not in form_data:
        form_data["status"] = QuestionStatus.ACTIVE
    form = QuestionSearchForm(form_data, workspace_id=workspace.id)
    result = None
    page_notice = ""
    if form.is_valid():
        data = form.cleaned_data
        result = paginate_questions(
            questions=list_questions(
                workspace_id=workspace.id,
                status=data["status"],
                query=data["query"].strip(),
                discipline_id=data["discipline"].id if data["discipline"] else None,
                subject_id=data["subject"].id if data["subject"] else None,
                subsubject_id=data["subsubject"].id if data["subsubject"] else None,
                review_status=data["review_status"],
                initial_result=data["initial_result"],
                error_category_id=(
                    uuid.UUID(data["error_category"])
                    if data["error_category"] not in ("", "unclassified")
                    else None
                ),
                unclassified_error=data["error_category"] == "unclassified",
            ),
            requested_page=request.GET.get("page"),
        )
        if result.page_was_adjusted:
            page_notice = "A página solicitada não existe; mostramos uma página válida."
    parameters = request.GET.copy()
    for key in tuple(parameters):
        if key not in form.fields and key != "page":
            parameters.pop(key)
    return_parameters = parameters.copy()
    if result is not None and "page" in return_parameters:
        return_parameters["page"] = str(result.page.number)
    parameters.pop("page", None)
    return_query = urlencode(return_parameters, doseq=True)
    active_filters = [
        ("Estado", dict(QuestionStatus.choices)[form.cleaned_data["status"]])
        if form.is_valid()
        else None,
        ("Busca", form.cleaned_data["query"])
        if form.is_valid() and form.cleaned_data["query"]
        else None,
        ("Disciplina", form.cleaned_data["discipline"].name)
        if form.is_valid() and form.cleaned_data["discipline"]
        else None,
        ("Assunto", form.cleaned_data["subject"].name)
        if form.is_valid() and form.cleaned_data["subject"]
        else None,
        ("Subassunto", form.cleaned_data["subsubject"].name)
        if form.is_valid() and form.cleaned_data["subsubject"]
        else None,
        (
            "Situação de revisão",
            dict(cast(Any, form.fields["review_status"]).choices)[
                form.cleaned_data["review_status"]
            ],
        )
        if form.is_valid() and form.cleaned_data["review_status"]
        else None,
        (
            "Resultado inicial",
            dict(cast(Any, form.fields["initial_result"]).choices)[
                form.cleaned_data["initial_result"]
            ],
        )
        if form.is_valid() and form.cleaned_data["initial_result"]
        else None,
        (
            "Categoria de erro",
            dict(cast(Any, form.fields["error_category"]).choices)[
                form.cleaned_data["error_category"]
            ],
        )
        if form.is_valid() and form.cleaned_data["error_category"]
        else None,
    ]
    saved_filter_rows = list(
        SavedFilter.objects.filter(
            workspace_id=workspace.id,
            owner_user_id=LOCAL_USER_ID,
        ).order_by("name_key", "id")
    )
    compatibility_by_id = check_filter_compatibilities(
        saved_filter_rows,
        workspace_id=workspace.id,
    )
    saved_filters: list[tuple[SavedFilter, str]] = [
        (saved_filter, compatibility_by_id[saved_filter.id]) for saved_filter in saved_filter_rows
    ]
    return render(
        request,
        "questions/list.html",
        {
            "workspace": workspace,
            "form": form,
            "result": result,
            "page_notice": page_notice,
            "active_filters": [item for item in active_filters if item is not None],
            "query_without_page": urlencode(parameters, doseq=True),
            "current_query": urlencode(parameters, doseq=True),
            "feedback": _list_feedback(request),
            "saved_filters": saved_filters,
            "filter_payload_json": json.dumps(
                payload_from_search_form(form) if form.is_valid() else {},
                ensure_ascii=True,
                separators=(",", ":"),
            ),
            "return_to": (
                f"{reverse('questions:list')}?{return_query}"
                if return_query
                else reverse("questions:list")
            ),
            "breadcrumbs": [("Início", reverse("accounts:home"))],
        },
    )


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
        for alternative in alternatives:
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


def _add_alternative_form(
    request: HttpRequest,
    *,
    form_class: type[QuestionQuickEntryForm],
    workspace: Workspace,
    initial: dict[str, Any] | None = None,
) -> QuestionQuickEntryForm:
    """Reexiba os valores enviados com uma posição adicional, sem gravar dados."""
    return form_class(
        request.POST,
        initial=initial,
        workspace_id=workspace.id,
        alternative_count=form_class(
            request.POST, initial=initial, workspace_id=workspace.id
        ).alternative_count
        + 1,
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
    if request.method == "POST" and request.POST.get("action") == "add-alternative":
        form = _add_alternative_form(
            request, form_class=QuestionQuickEntryForm, workspace=workspace
        )
    if (
        request.method == "POST"
        and request.POST.get("action") != "add-alternative"
        and form.is_valid()
    ):
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
    form: QuestionQuickEntryForm = DraftActivationForm(
        request.POST if request.method == "POST" else None,
        initial=_initial_from_question(workspace=workspace, question=question),
        workspace_id=workspace.id,
    )
    if request.method == "POST" and request.POST.get("action") == "add-alternative":
        form = _add_alternative_form(
            request,
            form_class=DraftActivationForm,
            workspace=workspace,
            initial=_initial_from_question(workspace=workspace, question=question),
        )
    if (
        request.method == "POST"
        and request.POST.get("action") != "add-alternative"
        and form.is_valid()
    ):
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
    return_to = request.GET.get("return_to", "")
    list_prefix = reverse("questions:list")
    parsed_return_to = urlsplit(return_to)
    if parsed_return_to.scheme or parsed_return_to.netloc or parsed_return_to.path != list_prefix:
        return_to = list_prefix
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
            "can_correct_answer_key": (
                question.status == QuestionStatus.ACTIVE and current_revision is not None
            ),
            "return_to": return_to,
            "breadcrumbs": [("Início", reverse("accounts:home")), ("Consulta", return_to)],
        },
    )


@require_http_methods(["GET", "POST"])
def answer_key_correction(request: HttpRequest, question_id: uuid.UUID) -> HttpResponse:
    """Adapte a UI ao service S2C sem criar ou editar revisions diretamente."""
    workspace = _local_workspace()
    if workspace is None:
        return redirect("accounts:initial-setup")
    question = _question_or_404(workspace=workspace, question_id=question_id)
    revision = get_current_revision(workspace_id=workspace.id, question_id=question.id)
    if revision is None:
        raise Http404("A questão não possui revisão corrente para corrigir.")
    alternatives = list(revision.alternatives.order_by("position", "id"))
    current_position = next(
        (item.position for item in alternatives if item.id == revision.correct_alternative_id),
        None,
    )
    form = AnswerKeyCorrectionForm(
        request.POST if request.method == "POST" else None,
        initial={
            "expected_revision_id": revision.id,
            "correct_alternative_position": str(current_position or ""),
        },
        alternatives=alternatives,
    )
    stale_conflict = False
    if request.method == "POST" and form.is_valid():
        try:
            AnswerKeyCorrectionService(workspace_id=workspace.id).correct(
                question_id=question.id,
                expected_revision_id=form.cleaned_data["expected_revision_id"],
                correct_alternative_position=int(form.cleaned_data["correct_alternative_position"]),
                reason_code=form.cleaned_data["reason_code"],
            )
            return redirect(
                f"{reverse('questions:detail', args=[question.id])}?result=answer-key-corrected"
            )
        except AnswerKeyCorrectionConflictError as error:
            stale_conflict = True
            form.add_error(None, str(error))
        except (ValidationError, DatabaseError, ValueError) as error:
            form.add_error(None, str(error))
    return render(
        request,
        "questions/answer_key_correction.html",
        {
            "workspace": workspace,
            "question": question,
            "revision": revision,
            "alternatives": alternatives,
            "current_position": current_position,
            "form": form,
            "stale_conflict": stale_conflict,
            "breadcrumbs": [
                ("Início", reverse("accounts:home")),
                ("Detalhe da questão", reverse("questions:detail", args=[question.id])),
                ("Corrigir gabarito", ""),
            ],
        },
        status=409 if stale_conflict else 400 if request.method == "POST" and form.errors else 200,
    )


_DELETION_BLOCKER_LABELS = {
    "CROSS_WORKSPACE_REFERENCE": "Foi encontrada uma referência de outro Workspace.",
    "REVISION_EXTERNAL_REFERENCE": "Uma revisão possui referência externa ao agregado.",
    "SHARED_CROSS_WORKSPACE_REFERENCE": "Uma dependência compartilhada pertence a outro Workspace.",
    "ATTEMPT_EXTERNAL_REFERENCE": "Uma Attempt possui referência externa ao agregado.",
    "CYCLE_EXTERNAL_REFERENCE": "Um ciclo de Review possui referência externa ao agregado.",
    "REVIEW_EXTERNAL_REFERENCE": "Uma Review possui referência externa ao agregado.",
    "EXTERNAL_DEPENDENCY": "Existe dependência fora do agregado autorizado.",
    "RECEIPT_RETENTION": "Um recibo ainda está no período mínimo de retenção.",
    "TRANSIENT_CONTEXT": "Há contexto de resposta temporário ainda válido.",
}

_DELETION_IMPACT_LABELS = {
    "questions": "Questions",
    "revisions": "Revisões de conteúdo",
    "alternatives": "Alternativas históricas",
    "attempts": "Attempts históricas",
    "reviews": "Reviews",
    "cycles": "Ciclos de Review",
    "schedule_changes": "Reagendamentos",
    "classifications": "Classificações",
    "classification_revisions": "Revisões de classificação",
    "origins": "Origens",
}


@require_http_methods(["GET", "POST"])
def permanent_delete_preview(request: HttpRequest, question_id: uuid.UUID) -> HttpResponse:
    """Mostre e confirme somente pelo preview/delete oficiais de S2D."""
    workspace = _local_workspace()
    if workspace is None:
        return redirect("accounts:initial-setup")
    question = _question_or_404(workspace=workspace, question_id=question_id)
    service = PermanentQuestionDeletionService(workspace_id=workspace.id)
    try:
        preview = service.preview(question_id=question.id)
    except Question.DoesNotExist as error:
        raise Http404("Questão não encontrada neste Workspace.") from error

    form = PermanentQuestionDeleteForm(
        request.POST if request.method == "POST" else None,
        initial={
            "expected_fingerprint": preview.fingerprint,
            "confirmation_token": preview.confirmation_token,
            "correlation_id": uuid.uuid4(),
        },
        required_token=preview.confirmation_token,
        backup_required=preview.backup_required,
    )
    stale_conflict = False
    backup_failure = False
    if request.method == "POST" and form.is_valid():
        if not preview.eligible:
            stale_conflict = True
            form.add_error(None, "O preview atual está bloqueado; nenhuma exclusão foi aplicada.")
        else:
            backup_path = None
            restore_path = None
            deletion_completed = False
            backup_directory = Path(settings.BASE_DIR) / "backups"
            try:
                if preview.backup_required:
                    backup_path = backup_directory / (
                        f"pre-delete-{form.cleaned_data['correlation_id'].hex}.sqlite3"
                    )
                    with TemporaryDirectory(
                        prefix=".s3-delete-restore-",
                        dir=backup_directory,
                    ) as restore_directory:
                        restore_path = Path(restore_directory) / "isolated-restore.sqlite3"
                        service.delete(
                            question_id=question.id,
                            expected_fingerprint=form.cleaned_data["expected_fingerprint"],
                            confirmation_token=form.cleaned_data["confirmation_token"],
                            reason_code="USER_CONFIRMED_PERMANENT_DELETE",
                            correlation_id=form.cleaned_data["correlation_id"],
                            backup_path=backup_path,
                            isolated_restore_path=restore_path,
                        )
                        deletion_completed = True
                else:
                    service.delete(
                        question_id=question.id,
                        expected_fingerprint=form.cleaned_data["expected_fingerprint"],
                        confirmation_token=form.cleaned_data["confirmation_token"],
                        reason_code="USER_CONFIRMED_PERMANENT_DELETE",
                        correlation_id=form.cleaned_data["correlation_id"],
                    )
                    deletion_completed = True
                return redirect(f"{reverse('questions:list')}?result=deleted")
            except PermanentDeletionConflictError:
                stale_conflict = True
                form.add_error(
                    None,
                    "O estado mudou ou a confirmação não é mais válida. A exclusão não ocorreu; abra um novo preview.",
                )
            except (DataManagementError, OSError, ValueError, DatabaseError):
                if deletion_completed:
                    return redirect(f"{reverse('questions:list')}?result=deleted-cleanup-warning")
                backup_failure = preview.backup_required
                form.add_error(
                    None,
                    (
                        "O backup ou restore isolado não foi validado. A exclusão não ocorreu; preserve eventuais artefatos e tente novamente."
                        if backup_failure
                        else "A exclusão não foi concluída. O agregado permanece disponível; abra um novo preview."
                    ),
                )

    blockers = [
        _DELETION_BLOCKER_LABELS.get(code, "Uma dependência impede a exclusão permanente.")
        for code in preview.blockers
    ]
    impact = [
        (_DELETION_IMPACT_LABELS.get(name, "Dependência do agregado"), count)
        for name, count in preview.impact
    ]
    return render(
        request,
        "questions/permanent_delete_preview.html",
        {
            "workspace": workspace,
            "question": question,
            "preview": preview,
            "blockers": blockers,
            "impact": impact,
            "archive_is_default": "ARCHIVE_IS_DEFAULT" in preview.warnings,
            "form": form,
            "stale_conflict": stale_conflict,
            "backup_failure": backup_failure,
            "breadcrumbs": [
                ("Início", reverse("accounts:home")),
                ("Detalhe da questão", reverse("questions:detail", args=[question.id])),
                ("Preview de exclusão permanente", ""),
            ],
        },
        status=409 if stale_conflict else 400 if request.method == "POST" and form.errors else 200,
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
    form: QuestionQuickEntryForm = QuestionEditForm(
        request.POST if request.method == "POST" else None,
        initial=_initial_from_question(workspace=workspace, question=question),
        workspace_id=workspace.id,
    )
    if request.method == "POST" and request.POST.get("action") == "add-alternative":
        form = _add_alternative_form(
            request,
            form_class=QuestionEditForm,
            workspace=workspace,
            initial=_initial_from_question(workspace=workspace, question=question),
        )
    if (
        request.method == "POST"
        and request.POST.get("action") != "add-alternative"
        and form.is_valid()
    ):
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
