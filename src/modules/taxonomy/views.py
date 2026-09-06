"""Orquestração fina da gestão web da taxonomia."""

import uuid
from collections.abc import Callable

from django.db import DatabaseError
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods

from modules.accounts.exceptions import WorkspaceAccessDenied
from modules.accounts.models import Workspace
from modules.accounts.services import (
    LOCAL_USER_ID,
    LOCAL_WORKSPACE_ID,
    get_workspace_for_owner,
)

from .exceptions import (
    TaxonomyConcurrencyError,
    TaxonomyDuplicateNameError,
    TaxonomyNotFoundError,
    TaxonomyStateConflictError,
    TaxonomyValidationError,
)
from .forms import TaxonomyArchiveForm, TaxonomyEditForm, TaxonomyNameForm
from .models import TaxonomyStatus
from .selectors import (
    count_subjects,
    count_subsubjects,
    get_discipline,
    get_subject,
    get_subsubject,
    list_archived_disciplines,
    list_disciplines,
    list_managed_subjects,
    list_managed_subsubjects,
)
from .services import (
    archive_discipline,
    archive_subject,
    archive_subsubject,
    create_discipline,
    create_subject,
    create_subsubject,
    rename_discipline,
    rename_subject,
    rename_subsubject,
)


def _local_workspace() -> Workspace | None:
    try:
        return get_workspace_for_owner(
            actor_user_id=LOCAL_USER_ID,
            workspace_id=LOCAL_WORKSPACE_ID,
        )
    except WorkspaceAccessDenied:
        return None


def _feedback(request: HttpRequest, messages: dict[str, str]) -> str:
    return messages.get(request.GET.get("result", ""), "")


def _with_result(view_name: str, result: str, **kwargs: uuid.UUID) -> HttpResponse:
    return redirect(f"{reverse(view_name, kwargs=kwargs)}?result={result}")


def _as_404[ItemT](selector: Callable[[], ItemT]) -> ItemT:
    try:
        return selector()
    except TaxonomyNotFoundError as error:
        raise Http404("Item de taxonomia não encontrado.") from error


def _name_service_error(form: TaxonomyNameForm, error: Exception) -> None:
    if isinstance(error, TaxonomyDuplicateNameError):
        form.add_error("name", "Já existe um item ativo com esse nome neste contexto.")
    elif isinstance(error, TaxonomyConcurrencyError):
        form.add_error(
            None,
            "O item mudou em outra operação. Confira os dados atuais e envie novamente.",
        )
    elif isinstance(error, TaxonomyStateConflictError):
        form.add_error(None, "O contexto acadêmico não está mais disponível.")
    elif isinstance(error, TaxonomyValidationError):
        form.add_error("name", str(error))
    else:
        form.add_error(
            None,
            "Não foi possível salvar. Nenhuma alteração foi confirmada.",
        )
    form.focus_name_error()


def _archive_service_error(form: TaxonomyArchiveForm, error: Exception) -> None:
    if isinstance(error, TaxonomyConcurrencyError):
        message = "O item mudou em outra operação. Confira o estado atual e confirme novamente."
    elif isinstance(error, TaxonomyStateConflictError):
        message = "O item já está arquivado ou não está mais disponível."
    else:
        message = "Não foi possível arquivar. Nenhuma alteração foi confirmada."
    form.add_error(None, message)
    form.focus_confirmation_error()


def _unavailable(
    request: HttpRequest,
    *,
    workspace: Workspace,
    title: str,
    message: str,
    return_url: str,
) -> HttpResponse:
    return render(
        request,
        "taxonomy/unavailable.html",
        {
            "workspace": workspace,
            "title": title,
            "message": message,
            "return_url": return_url,
        },
        status=409,
    )


@require_GET
def taxonomy_index(request: HttpRequest) -> HttpResponse:
    """Liste disciplinas ativas ou arquivadas do Workspace local."""
    workspace = _local_workspace()
    if workspace is None:
        return redirect("accounts:initial-setup")
    archived = request.GET.get("state") == "archived"
    items = (
        list_archived_disciplines(workspace_id=workspace.id)
        if archived
        else list_disciplines(workspace_id=workspace.id)
    )
    return render(
        request,
        "taxonomy/index.html",
        {
            "workspace": workspace,
            "items": items,
            "show_archived": archived,
            "feedback": _feedback(
                request,
                {
                    "created": "Disciplina criada com sucesso.",
                    "updated": "Disciplina atualizada com sucesso.",
                    "archived": "Disciplina arquivada com sucesso.",
                    "cancelled": "Arquivamento cancelado. Nenhum dado foi alterado.",
                },
            ),
        },
    )


@require_http_methods(["GET", "POST"])
def discipline_create(request: HttpRequest) -> HttpResponse:
    """Crie Discipline pelo serviço de domínio."""
    workspace = _local_workspace()
    if workspace is None:
        return redirect("accounts:initial-setup")
    form = TaxonomyNameForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            create_discipline(workspace_id=workspace.id, name=form.cleaned_data["name"])
        except TaxonomyNotFoundError as error:
            raise Http404("Workspace não encontrado.") from error
        except (TaxonomyValidationError, TaxonomyStateConflictError, DatabaseError) as error:
            _name_service_error(form, error)
        else:
            return _with_result("taxonomy:index", "created")
    return render(
        request,
        "taxonomy/item_form.html",
        {
            "workspace": workspace,
            "form": form,
            "title": "Nova disciplina",
            "eyebrow": "Taxonomia · Disciplina",
            "submit_label": "Criar disciplina",
            "return_url": reverse("taxonomy:index"),
            "breadcrumbs": [("Taxonomia", reverse("taxonomy:index"))],
        },
    )


@require_http_methods(["GET", "POST"])
def discipline_edit(request: HttpRequest, discipline_id: uuid.UUID) -> HttpResponse:
    """Edite Discipline usando a versão apresentada."""
    workspace = _local_workspace()
    if workspace is None:
        return redirect("accounts:initial-setup")
    discipline = _as_404(
        lambda: get_discipline(workspace_id=workspace.id, discipline_id=discipline_id)
    )
    form = TaxonomyEditForm(
        request.POST if request.method == "POST" else None,
        initial={"name": discipline.name, "lock_version": discipline.lock_version},
    )
    if request.method == "POST" and form.is_valid():
        try:
            rename_discipline(
                workspace_id=workspace.id,
                discipline_id=discipline.id,
                name=form.cleaned_data["name"],
                expected_lock_version=form.cleaned_data["lock_version"],
            )
        except TaxonomyNotFoundError as error:
            raise Http404("Disciplina não encontrada.") from error
        except (TaxonomyValidationError, TaxonomyConcurrencyError, DatabaseError) as error:
            discipline.refresh_from_db()
            data = request.POST.copy()
            data["lock_version"] = str(discipline.lock_version)
            form = TaxonomyEditForm(data=data)
            form.is_valid()
            _name_service_error(form, error)
        else:
            return _with_result("taxonomy:index", "updated")
    return render(
        request,
        "taxonomy/item_form.html",
        {
            "workspace": workspace,
            "form": form,
            "title": "Editar disciplina",
            "eyebrow": "Taxonomia · Disciplina",
            "submit_label": "Salvar disciplina",
            "return_url": reverse("taxonomy:index"),
            "breadcrumbs": [("Taxonomia", reverse("taxonomy:index"))],
        },
    )


@require_http_methods(["GET", "POST"])
def discipline_archive(request: HttpRequest, discipline_id: uuid.UUID) -> HttpResponse:
    """Confirme o arquivamento não destrutivo de Discipline."""
    workspace = _local_workspace()
    if workspace is None:
        return redirect("accounts:initial-setup")
    discipline = _as_404(
        lambda: get_discipline(workspace_id=workspace.id, discipline_id=discipline_id)
    )
    if request.method == "POST" and request.POST.get("action") == "cancel":
        return _with_result("taxonomy:index", "cancelled")
    form = TaxonomyArchiveForm(
        request.POST if request.method == "POST" else None,
        initial={"lock_version": discipline.lock_version},
    )
    if request.method == "POST" and form.is_valid():
        try:
            archive_discipline(
                workspace_id=workspace.id,
                discipline_id=discipline.id,
                expected_lock_version=form.cleaned_data["lock_version"],
            )
        except TaxonomyNotFoundError as error:
            raise Http404("Disciplina não encontrada.") from error
        except (TaxonomyConcurrencyError, TaxonomyStateConflictError, DatabaseError) as error:
            discipline.refresh_from_db()
            data = request.POST.copy()
            data["lock_version"] = str(discipline.lock_version)
            data.pop("confirmed", None)
            form = TaxonomyArchiveForm(data=data)
            form.is_valid()
            _archive_service_error(form, error)
        else:
            return redirect(f"{reverse('taxonomy:index')}?state=archived&result=archived")
    subject_total = count_subjects(workspace_id=workspace.id, discipline_id=discipline.id)
    return render(
        request,
        "taxonomy/archive_confirm.html",
        {
            "workspace": workspace,
            "form": form,
            "title": "Arquivar disciplina",
            "item": discipline,
            "item_label": "Disciplina",
            "impact_summary": f"{subject_total} assunto(s) existente(s) permanecerão preservados.",
            "descendant_notice": (
                "Assuntos e subassuntos descendentes deixarão de estar disponíveis para "
                "novos vínculos, sem terem seus estados alterados automaticamente."
            ),
            "return_url": reverse("taxonomy:index"),
            "breadcrumbs": [("Taxonomia", reverse("taxonomy:index"))],
        },
    )


@require_GET
def subject_list(request: HttpRequest, discipline_id: uuid.UUID) -> HttpResponse:
    """Liste Subjects no contexto inequívoco da Discipline."""
    workspace = _local_workspace()
    if workspace is None:
        return redirect("accounts:initial-setup")
    discipline = _as_404(
        lambda: get_discipline(workspace_id=workspace.id, discipline_id=discipline_id)
    )
    archived = request.GET.get("state") == "archived"
    items = list_managed_subjects(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        archived=archived,
    )
    parent_available = discipline.status == TaxonomyStatus.ACTIVE
    return render(
        request,
        "taxonomy/children.html",
        {
            "workspace": workspace,
            "items": items,
            "parent": discipline,
            "parent_available": parent_available,
            "show_archived": archived,
            "level": "subject",
            "title": "Assuntos",
            "item_singular": "assunto",
            "item_plural": "assuntos",
            "new_url": reverse("taxonomy:subject-create", args=[discipline.id]),
            "active_url": reverse("taxonomy:subject-list", args=[discipline.id]),
            "archived_url": f"{reverse('taxonomy:subject-list', args=[discipline.id])}?state=archived",
            "return_url": reverse("taxonomy:index"),
            "feedback": _feedback(
                request,
                {
                    "created": "Assunto criado com sucesso.",
                    "updated": "Assunto atualizado com sucesso.",
                    "archived": "Assunto arquivado com sucesso.",
                    "cancelled": "Arquivamento cancelado. Nenhum dado foi alterado.",
                },
            ),
            "breadcrumbs": [("Taxonomia", reverse("taxonomy:index"))],
        },
    )


@require_http_methods(["GET", "POST"])
def subject_create(request: HttpRequest, discipline_id: uuid.UUID) -> HttpResponse:
    """Crie Subject somente sob Discipline ativa e Workspace-scoped."""
    workspace = _local_workspace()
    if workspace is None:
        return redirect("accounts:initial-setup")
    discipline = _as_404(
        lambda: get_discipline(workspace_id=workspace.id, discipline_id=discipline_id)
    )
    return_url = reverse("taxonomy:subject-list", args=[discipline.id])
    if discipline.status != TaxonomyStatus.ACTIVE:
        return _unavailable(
            request,
            workspace=workspace,
            title="Novo assunto indisponível",
            message="A disciplina está arquivada e não aceita novos assuntos.",
            return_url=return_url,
        )
    form = TaxonomyNameForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            create_subject(
                workspace_id=workspace.id,
                discipline_id=discipline.id,
                name=form.cleaned_data["name"],
            )
        except TaxonomyNotFoundError as error:
            raise Http404("Disciplina não encontrada.") from error
        except (TaxonomyValidationError, TaxonomyStateConflictError, DatabaseError) as error:
            _name_service_error(form, error)
        else:
            return _with_result("taxonomy:subject-list", "created", discipline_id=discipline.id)
    return render(
        request,
        "taxonomy/item_form.html",
        {
            "workspace": workspace,
            "form": form,
            "title": "Novo assunto",
            "eyebrow": f"{discipline.name} · Assunto",
            "context_notice": f"Disciplina: {discipline.name}",
            "submit_label": "Criar assunto",
            "return_url": return_url,
            "breadcrumbs": [
                ("Taxonomia", reverse("taxonomy:index")),
                ("Assuntos", return_url),
            ],
        },
    )


@require_http_methods(["GET", "POST"])
def subject_edit(request: HttpRequest, subject_id: uuid.UUID) -> HttpResponse:
    """Edite Subject sem aceitar identificador de outro Workspace."""
    workspace = _local_workspace()
    if workspace is None:
        return redirect("accounts:initial-setup")
    subject = _as_404(lambda: get_subject(workspace_id=workspace.id, subject_id=subject_id))
    return_url = reverse("taxonomy:subject-list", args=[subject.discipline_id])
    form = TaxonomyEditForm(
        request.POST if request.method == "POST" else None,
        initial={"name": subject.name, "lock_version": subject.lock_version},
    )
    if request.method == "POST" and form.is_valid():
        try:
            rename_subject(
                workspace_id=workspace.id,
                subject_id=subject.id,
                name=form.cleaned_data["name"],
                expected_lock_version=form.cleaned_data["lock_version"],
            )
        except TaxonomyNotFoundError as error:
            raise Http404("Assunto não encontrado.") from error
        except (TaxonomyValidationError, TaxonomyConcurrencyError, DatabaseError) as error:
            subject.refresh_from_db()
            data = request.POST.copy()
            data["lock_version"] = str(subject.lock_version)
            form = TaxonomyEditForm(data=data)
            form.is_valid()
            _name_service_error(form, error)
        else:
            return _with_result(
                "taxonomy:subject-list", "updated", discipline_id=subject.discipline_id
            )
    return render(
        request,
        "taxonomy/item_form.html",
        {
            "workspace": workspace,
            "form": form,
            "title": "Editar assunto",
            "eyebrow": f"{subject.discipline.name} · Assunto",
            "context_notice": f"Disciplina: {subject.discipline.name}",
            "submit_label": "Salvar assunto",
            "return_url": return_url,
            "breadcrumbs": [
                ("Taxonomia", reverse("taxonomy:index")),
                ("Assuntos", return_url),
            ],
        },
    )


@require_http_methods(["GET", "POST"])
def subject_archive(request: HttpRequest, subject_id: uuid.UUID) -> HttpResponse:
    """Confirme o arquivamento não destrutivo de Subject."""
    workspace = _local_workspace()
    if workspace is None:
        return redirect("accounts:initial-setup")
    subject = _as_404(lambda: get_subject(workspace_id=workspace.id, subject_id=subject_id))
    return_url = reverse("taxonomy:subject-list", args=[subject.discipline_id])
    if request.method == "POST" and request.POST.get("action") == "cancel":
        return _with_result(
            "taxonomy:subject-list", "cancelled", discipline_id=subject.discipline_id
        )
    form = TaxonomyArchiveForm(
        request.POST if request.method == "POST" else None,
        initial={"lock_version": subject.lock_version},
    )
    if request.method == "POST" and form.is_valid():
        try:
            archive_subject(
                workspace_id=workspace.id,
                subject_id=subject.id,
                expected_lock_version=form.cleaned_data["lock_version"],
            )
        except TaxonomyNotFoundError as error:
            raise Http404("Assunto não encontrado.") from error
        except (TaxonomyConcurrencyError, TaxonomyStateConflictError, DatabaseError) as error:
            subject.refresh_from_db()
            data = request.POST.copy()
            data["lock_version"] = str(subject.lock_version)
            data.pop("confirmed", None)
            form = TaxonomyArchiveForm(data=data)
            form.is_valid()
            _archive_service_error(form, error)
        else:
            target = reverse("taxonomy:subject-list", args=[subject.discipline_id])
            return redirect(f"{target}?state=archived&result=archived")
    total = count_subsubjects(workspace_id=workspace.id, subject_id=subject.id)
    return render(
        request,
        "taxonomy/archive_confirm.html",
        {
            "workspace": workspace,
            "form": form,
            "title": "Arquivar assunto",
            "item": subject,
            "item_label": "Assunto",
            "impact_summary": f"{total} subassunto(s) existente(s) permanecerão preservados.",
            "descendant_notice": (
                "Subassuntos descendentes deixarão de estar disponíveis para novos vínculos, "
                "sem terem seus estados alterados automaticamente."
            ),
            "return_url": return_url,
            "breadcrumbs": [
                ("Taxonomia", reverse("taxonomy:index")),
                ("Assuntos", return_url),
            ],
        },
    )


@require_GET
def subsubject_list(request: HttpRequest, subject_id: uuid.UUID) -> HttpResponse:
    """Liste Subsubjects mostrando toda a cadeia acadêmica."""
    workspace = _local_workspace()
    if workspace is None:
        return redirect("accounts:initial-setup")
    subject = _as_404(lambda: get_subject(workspace_id=workspace.id, subject_id=subject_id))
    archived = request.GET.get("state") == "archived"
    items = list_managed_subsubjects(
        workspace_id=workspace.id,
        subject_id=subject.id,
        archived=archived,
    )
    parent_available = (
        subject.status == TaxonomyStatus.ACTIVE
        and subject.discipline.status == TaxonomyStatus.ACTIVE
    )
    subject_url = reverse("taxonomy:subject-list", args=[subject.discipline_id])
    active_url = reverse("taxonomy:subsubject-list", args=[subject.id])
    return render(
        request,
        "taxonomy/children.html",
        {
            "workspace": workspace,
            "items": items,
            "parent": subject,
            "discipline": subject.discipline,
            "parent_available": parent_available,
            "show_archived": archived,
            "level": "subsubject",
            "title": "Subassuntos",
            "item_singular": "subassunto",
            "item_plural": "subassuntos",
            "new_url": reverse("taxonomy:subsubject-create", args=[subject.id]),
            "active_url": active_url,
            "archived_url": f"{active_url}?state=archived",
            "return_url": subject_url,
            "feedback": _feedback(
                request,
                {
                    "created": "Subassunto criado com sucesso.",
                    "updated": "Subassunto atualizado com sucesso.",
                    "archived": "Subassunto arquivado com sucesso.",
                    "cancelled": "Arquivamento cancelado. Nenhum dado foi alterado.",
                },
            ),
            "breadcrumbs": [
                ("Taxonomia", reverse("taxonomy:index")),
                ("Assuntos", subject_url),
            ],
        },
    )


@require_http_methods(["GET", "POST"])
def subsubject_create(request: HttpRequest, subject_id: uuid.UUID) -> HttpResponse:
    """Crie Subsubject somente quando toda a cadeia está disponível."""
    workspace = _local_workspace()
    if workspace is None:
        return redirect("accounts:initial-setup")
    subject = _as_404(lambda: get_subject(workspace_id=workspace.id, subject_id=subject_id))
    return_url = reverse("taxonomy:subsubject-list", args=[subject.id])
    if (
        subject.status != TaxonomyStatus.ACTIVE
        or subject.discipline.status != TaxonomyStatus.ACTIVE
    ):
        return _unavailable(
            request,
            workspace=workspace,
            title="Novo subassunto indisponível",
            message="O assunto ou sua disciplina está arquivado e não aceita novos subassuntos.",
            return_url=return_url,
        )
    form = TaxonomyNameForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            create_subsubject(
                workspace_id=workspace.id,
                subject_id=subject.id,
                name=form.cleaned_data["name"],
            )
        except TaxonomyNotFoundError as error:
            raise Http404("Assunto não encontrado.") from error
        except (TaxonomyValidationError, TaxonomyStateConflictError, DatabaseError) as error:
            _name_service_error(form, error)
        else:
            return _with_result("taxonomy:subsubject-list", "created", subject_id=subject.id)
    return render(
        request,
        "taxonomy/item_form.html",
        {
            "workspace": workspace,
            "form": form,
            "title": "Novo subassunto",
            "eyebrow": f"{subject.discipline.name} · {subject.name} · Subassunto",
            "context_notice": (f"Disciplina: {subject.discipline.name} → Assunto: {subject.name}"),
            "submit_label": "Criar subassunto",
            "return_url": return_url,
            "breadcrumbs": [
                ("Taxonomia", reverse("taxonomy:index")),
                ("Assuntos", reverse("taxonomy:subject-list", args=[subject.discipline_id])),
                ("Subassuntos", return_url),
            ],
        },
    )


@require_http_methods(["GET", "POST"])
def subsubject_edit(request: HttpRequest, subsubject_id: uuid.UUID) -> HttpResponse:
    """Edite Subsubject preservando o pai e usando lock otimista."""
    workspace = _local_workspace()
    if workspace is None:
        return redirect("accounts:initial-setup")
    subsubject = _as_404(
        lambda: get_subsubject(workspace_id=workspace.id, subsubject_id=subsubject_id)
    )
    return_url = reverse("taxonomy:subsubject-list", args=[subsubject.subject_id])
    form = TaxonomyEditForm(
        request.POST if request.method == "POST" else None,
        initial={"name": subsubject.name, "lock_version": subsubject.lock_version},
    )
    if request.method == "POST" and form.is_valid():
        try:
            rename_subsubject(
                workspace_id=workspace.id,
                subsubject_id=subsubject.id,
                name=form.cleaned_data["name"],
                expected_lock_version=form.cleaned_data["lock_version"],
            )
        except TaxonomyNotFoundError as error:
            raise Http404("Subassunto não encontrado.") from error
        except (TaxonomyValidationError, TaxonomyConcurrencyError, DatabaseError) as error:
            subsubject.refresh_from_db()
            data = request.POST.copy()
            data["lock_version"] = str(subsubject.lock_version)
            form = TaxonomyEditForm(data=data)
            form.is_valid()
            _name_service_error(form, error)
        else:
            return _with_result(
                "taxonomy:subsubject-list", "updated", subject_id=subsubject.subject_id
            )
    return render(
        request,
        "taxonomy/item_form.html",
        {
            "workspace": workspace,
            "form": form,
            "title": "Editar subassunto",
            "eyebrow": (
                f"{subsubject.subject.discipline.name} · {subsubject.subject.name} · Subassunto"
            ),
            "context_notice": (
                f"Disciplina: {subsubject.subject.discipline.name} → "
                f"Assunto: {subsubject.subject.name}"
            ),
            "submit_label": "Salvar subassunto",
            "return_url": return_url,
            "breadcrumbs": [
                ("Taxonomia", reverse("taxonomy:index")),
                (
                    "Assuntos",
                    reverse("taxonomy:subject-list", args=[subsubject.subject.discipline_id]),
                ),
                ("Subassuntos", return_url),
            ],
        },
    )


@require_http_methods(["GET", "POST"])
def subsubject_archive(request: HttpRequest, subsubject_id: uuid.UUID) -> HttpResponse:
    """Confirme o arquivamento não destrutivo de Subsubject."""
    workspace = _local_workspace()
    if workspace is None:
        return redirect("accounts:initial-setup")
    subsubject = _as_404(
        lambda: get_subsubject(workspace_id=workspace.id, subsubject_id=subsubject_id)
    )
    return_url = reverse("taxonomy:subsubject-list", args=[subsubject.subject_id])
    if request.method == "POST" and request.POST.get("action") == "cancel":
        return _with_result(
            "taxonomy:subsubject-list", "cancelled", subject_id=subsubject.subject_id
        )
    form = TaxonomyArchiveForm(
        request.POST if request.method == "POST" else None,
        initial={"lock_version": subsubject.lock_version},
    )
    if request.method == "POST" and form.is_valid():
        try:
            archive_subsubject(
                workspace_id=workspace.id,
                subsubject_id=subsubject.id,
                expected_lock_version=form.cleaned_data["lock_version"],
            )
        except TaxonomyNotFoundError as error:
            raise Http404("Subassunto não encontrado.") from error
        except (TaxonomyConcurrencyError, TaxonomyStateConflictError, DatabaseError) as error:
            subsubject.refresh_from_db()
            data = request.POST.copy()
            data["lock_version"] = str(subsubject.lock_version)
            data.pop("confirmed", None)
            form = TaxonomyArchiveForm(data=data)
            form.is_valid()
            _archive_service_error(form, error)
        else:
            target = reverse("taxonomy:subsubject-list", args=[subsubject.subject_id])
            return redirect(f"{target}?state=archived&result=archived")
    return render(
        request,
        "taxonomy/archive_confirm.html",
        {
            "workspace": workspace,
            "form": form,
            "title": "Arquivar subassunto",
            "item": subsubject,
            "item_label": "Subassunto",
            "impact_summary": "O item permanecerá consultável no histórico.",
            "descendant_notice": "Nenhum registro existente será apagado.",
            "return_url": return_url,
            "breadcrumbs": [
                ("Taxonomia", reverse("taxonomy:index")),
                (
                    "Assuntos",
                    reverse("taxonomy:subject-list", args=[subsubject.subject.discipline_id]),
                ),
                ("Subassuntos", return_url),
            ],
        },
    )
