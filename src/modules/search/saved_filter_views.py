"""Views de filtros salvos: todas limitadas ao owner e Workspace local."""

from __future__ import annotations

import uuid
from urllib.parse import urlencode

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from modules.accounts.exceptions import WorkspaceAccessDenied
from modules.accounts.models import Workspace
from modules.accounts.services import LOCAL_USER_ID, LOCAL_WORKSPACE_ID, get_workspace_for_owner

from .models import SavedFilter
from .saved_filter_forms import SavedFilterCreateForm, SavedFilterDeleteForm, SavedFilterRenameForm
from .saved_filter_services import (
    SavedFilterError,
    check_filter_compatibility,
    create_saved_filter,
    delete_saved_filter,
    rename_saved_filter,
    validate_questions_list_payload,
)


def _workspace() -> Workspace | None:
    try:
        return get_workspace_for_owner(
            actor_user_id=LOCAL_USER_ID,
            workspace_id=LOCAL_WORKSPACE_ID,
        )
    except WorkspaceAccessDenied:
        return None


def _saved_filter_or_404(*, workspace: Workspace, saved_filter_id: uuid.UUID) -> SavedFilter:
    try:
        return SavedFilter.objects.get(
            pk=saved_filter_id,
            workspace_id=workspace.id,
            owner_user_id=LOCAL_USER_ID,
        )
    except SavedFilter.DoesNotExist as error:
        raise Http404("Filtro salvo não encontrado neste Workspace.") from error


def _management_context(
    *, workspace: Workspace, form: object, title: str, return_url: str
) -> dict[str, object]:
    return {
        "workspace": workspace,
        "form": form,
        "title": title,
        "return_url": return_url,
        "breadcrumbs": [
            ("Início", reverse("accounts:home")),
            ("Questões", reverse("questions:list")),
            (title, ""),
        ],
    }


@never_cache
@require_http_methods(["POST"])
def create_filter(request: HttpRequest) -> HttpResponse:
    workspace = _workspace()
    if workspace is None:
        return redirect("accounts:initial-setup")
    form = SavedFilterCreateForm(request.POST)
    if form.is_valid():
        try:
            create_saved_filter(
                workspace_id=workspace.id,
                owner_user_id=LOCAL_USER_ID,
                name=form.cleaned_data["name"],
                payload=form.cleaned_data["payload"],
            )
            return redirect(f"{reverse('questions:list')}?result=filter-saved")
        except SavedFilterError as error:
            form.add_error(None, str(error))
    context = _management_context(
        workspace=workspace,
        form=form,
        title="Salvar filtro",
        return_url=reverse("questions:list"),
    )
    return render(request, "search/saved_filter_form.html", context, status=400)


@never_cache
@require_http_methods(["GET"])
def apply_filter(request: HttpRequest, saved_filter_id: uuid.UUID) -> HttpResponse:
    workspace = _workspace()
    if workspace is None:
        return redirect("accounts:initial-setup")
    saved_filter = _saved_filter_or_404(workspace=workspace, saved_filter_id=saved_filter_id)
    problem = check_filter_compatibility(saved_filter, workspace_id=workspace.id)
    if problem:
        return render(
            request,
            "search/saved_filter_incompatible.html",
            {
                "workspace": workspace,
                "saved_filter": saved_filter,
                "problem": problem,
                "breadcrumbs": [
                    ("Início", reverse("accounts:home")),
                    ("Questões", reverse("questions:list")),
                    (saved_filter.name, ""),
                ],
            },
            status=409,
        )
    payload = validate_questions_list_payload(saved_filter.payload, workspace_id=workspace.id)
    query = urlencode(payload)
    return redirect(f"{reverse('questions:list')}?{query}")


@never_cache
@require_http_methods(["GET", "POST"])
def rename_filter(request: HttpRequest, saved_filter_id: uuid.UUID) -> HttpResponse:
    workspace = _workspace()
    if workspace is None:
        return redirect("accounts:initial-setup")
    saved_filter = _saved_filter_or_404(workspace=workspace, saved_filter_id=saved_filter_id)
    form = SavedFilterRenameForm(
        request.POST if request.method == "POST" else None,
        initial={"name": saved_filter.name},
    )
    if request.method == "POST" and form.is_valid():
        try:
            rename_saved_filter(saved_filter=saved_filter, name=form.cleaned_data["name"])
            return redirect(f"{reverse('questions:list')}?result=filter-renamed")
        except SavedFilterError as error:
            form.add_error(None, str(error))
    context = _management_context(
        workspace=workspace,
        form=form,
        title="Renomear filtro",
        return_url=reverse("questions:list"),
    )
    context["saved_filter"] = saved_filter
    return render(
        request,
        "search/saved_filter_form.html",
        context,
        status=400 if request.method == "POST" and form.errors else 200,
    )


@never_cache
@require_http_methods(["GET", "POST"])
def delete_filter(request: HttpRequest, saved_filter_id: uuid.UUID) -> HttpResponse:
    workspace = _workspace()
    if workspace is None:
        return redirect("accounts:initial-setup")
    saved_filter = _saved_filter_or_404(workspace=workspace, saved_filter_id=saved_filter_id)
    form = SavedFilterDeleteForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        delete_saved_filter(saved_filter=saved_filter)
        return redirect(f"{reverse('questions:list')}?result=filter-deleted")
    return render(
        request,
        "search/saved_filter_delete.html",
        {
            "workspace": workspace,
            "saved_filter": saved_filter,
            "form": form,
            "breadcrumbs": [
                ("Início", reverse("accounts:home")),
                ("Questões", reverse("questions:list")),
                ("Excluir filtro", ""),
            ],
        },
        status=400 if request.method == "POST" and form.errors else 200,
    )
