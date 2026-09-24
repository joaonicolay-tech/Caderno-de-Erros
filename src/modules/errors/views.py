"""Gestão acessível de categorias pessoais pela fronteira S2A."""

from __future__ import annotations

import uuid

from django.core.exceptions import ValidationError
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from modules.accounts.exceptions import WorkspaceAccessDenied
from modules.accounts.models import Workspace
from modules.accounts.services import LOCAL_USER_ID, LOCAL_WORKSPACE_ID, get_workspace_for_owner

from .management_forms import (
    PersonalCategoryArchiveForm,
    PersonalCategoryCreateForm,
    PersonalCategoryMergeForm,
    PersonalCategoryRenameForm,
)
from .models import ErrorCategory, ErrorCategoryKind, ErrorCategoryState
from .services import PersonalCategoryConflictError, PersonalCategoryService


def _workspace() -> Workspace | None:
    try:
        return get_workspace_for_owner(
            actor_user_id=LOCAL_USER_ID,
            workspace_id=LOCAL_WORKSPACE_ID,
        )
    except WorkspaceAccessDenied:
        return None


def _personal_category_or_404(
    *, workspace: Workspace, category_id: uuid.UUID, active_only: bool = False
) -> ErrorCategory:
    categories = ErrorCategory.objects.filter(
        pk=category_id,
        workspace_id=workspace.id,
        category_kind=ErrorCategoryKind.PERSONAL,
    ).select_related("merged_into")
    if active_only:
        categories = categories.filter(state=ErrorCategoryState.ACTIVE)
    category = categories.first()
    if category is None or category.state == ErrorCategoryState.MERGED:
        raise Http404("Categoria pessoal não disponível neste Workspace.")
    return category


def category_list(request: HttpRequest) -> HttpResponse:
    workspace = _workspace()
    if workspace is None:
        return redirect("accounts:initial-setup")
    personal_categories = list(
        ErrorCategory.objects.filter(
            workspace_id=workspace.id,
            category_kind=ErrorCategoryKind.PERSONAL,
        )
        .select_related("merged_into")
        .order_by("state", "display_name", "id")
    )
    standard_categories = ErrorCategory.objects.filter(
        workspace_id=workspace.id,
        category_kind=ErrorCategoryKind.STANDARD,
    ).order_by("code", "id")
    feedback = {
        "created": "Categoria pessoal criada.",
        "renamed": "Categoria pessoal renomeada.",
        "archived": "Categoria pessoal arquivada; classificações históricas foram preservadas.",
        "merged": "Categoria pessoal consolidada; o histórico da origem foi preservado.",
    }.get(request.GET.get("result", ""), "")
    return render(
        request,
        "errors/category_list.html",
        {
            "workspace": workspace,
            "personal_categories": personal_categories,
            "standard_categories": standard_categories,
            "feedback": feedback,
            "breadcrumbs": [("Início", reverse("accounts:home")), ("Categorias", "")],
        },
    )


@never_cache
@require_http_methods(["GET", "POST"])
def create_category(request: HttpRequest) -> HttpResponse:
    workspace = _workspace()
    if workspace is None:
        return redirect("accounts:initial-setup")
    form = PersonalCategoryCreateForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            PersonalCategoryService(workspace_id=workspace.id).create(
                display_name=form.cleaned_data["display_name"]
            )
            return redirect(f"{reverse('categories:list')}?result=created")
        except (PersonalCategoryConflictError, ValidationError, ValueError) as error:
            form.add_error(None, str(error))
    return render(
        request,
        "errors/category_form.html",
        {
            "workspace": workspace,
            "form": form,
            "title": "Criar categoria pessoal",
            "category": None,
            "breadcrumbs": [
                ("Início", reverse("accounts:home")),
                ("Categorias", reverse("categories:list")),
                ("Criar", ""),
            ],
        },
        status=400 if request.method == "POST" and form.errors else 200,
    )


@never_cache
@require_http_methods(["GET", "POST"])
def rename_category(request: HttpRequest, category_id: uuid.UUID) -> HttpResponse:
    workspace = _workspace()
    if workspace is None:
        return redirect("accounts:initial-setup")
    category = _personal_category_or_404(workspace=workspace, category_id=category_id)
    form = PersonalCategoryRenameForm(
        request.POST if request.method == "POST" else None,
        initial={
            "display_name": category.display_name,
            "expected_lock_version": category.lock_version,
        },
    )
    stale_conflict = False
    if request.method == "POST" and form.is_valid():
        try:
            PersonalCategoryService(workspace_id=workspace.id).rename(
                category_id=category.id,
                display_name=form.cleaned_data["display_name"],
                reason_code=form.cleaned_data["reason_code"],
                expected_lock_version=form.cleaned_data["expected_lock_version"],
            )
            return redirect(f"{reverse('categories:list')}?result=renamed")
        except PersonalCategoryConflictError as error:
            stale_conflict = True
            form.add_error(None, str(error))
        except (ValidationError, ValueError) as error:
            form.add_error(None, str(error))
    return render(
        request,
        "errors/category_form.html",
        {
            "workspace": workspace,
            "category": category,
            "form": form,
            "title": "Renomear categoria pessoal",
            "stale_conflict": stale_conflict,
            "breadcrumbs": [
                ("Início", reverse("accounts:home")),
                ("Categorias", reverse("categories:list")),
                ("Renomear", ""),
            ],
        },
        status=409 if stale_conflict else 400 if request.method == "POST" and form.errors else 200,
    )


@never_cache
@require_http_methods(["GET", "POST"])
def archive_category(request: HttpRequest, category_id: uuid.UUID) -> HttpResponse:
    workspace = _workspace()
    if workspace is None:
        return redirect("accounts:initial-setup")
    category = _personal_category_or_404(
        workspace=workspace,
        category_id=category_id,
        active_only=True,
    )
    form = PersonalCategoryArchiveForm(
        request.POST if request.method == "POST" else None,
        initial={"expected_lock_version": category.lock_version},
    )
    stale_conflict = False
    if request.method == "POST" and form.is_valid():
        try:
            PersonalCategoryService(workspace_id=workspace.id).archive(
                category_id=category.id,
                reason_code=form.cleaned_data["reason_code"],
                expected_lock_version=form.cleaned_data["expected_lock_version"],
            )
            return redirect(f"{reverse('categories:list')}?result=archived")
        except PersonalCategoryConflictError as error:
            stale_conflict = True
            form.add_error(None, str(error))
        except (ValidationError, ValueError) as error:
            form.add_error(None, str(error))
    return render(
        request,
        "errors/category_confirm.html",
        {
            "workspace": workspace,
            "category": category,
            "form": form,
            "title": "Arquivar categoria pessoal",
            "effect": "A categoria deixa de ser usada em novas classificações; classificações históricas permanecem consultáveis.",
            "stale_conflict": stale_conflict,
            "breadcrumbs": [
                ("Início", reverse("accounts:home")),
                ("Categorias", reverse("categories:list")),
                ("Arquivar", ""),
            ],
        },
        status=409 if stale_conflict else 400 if request.method == "POST" and form.errors else 200,
    )


@never_cache
@require_http_methods(["GET", "POST"])
def merge_category(request: HttpRequest, category_id: uuid.UUID) -> HttpResponse:
    workspace = _workspace()
    if workspace is None:
        return redirect("accounts:initial-setup")
    category = _personal_category_or_404(
        workspace=workspace,
        category_id=category_id,
        active_only=True,
    )
    form = PersonalCategoryMergeForm(
        request.POST if request.method == "POST" else None,
        initial={"expected_lock_version": category.lock_version},
        workspace_id=workspace.id,
        source_id=category.id,
    )
    stale_conflict = False
    target = None
    if request.method == "POST" and form.is_valid():
        target = form.cleaned_data["target"]
        try:
            PersonalCategoryService(workspace_id=workspace.id).merge(
                source_id=category.id,
                target_id=target.id,
                reason_code=form.cleaned_data["reason_code"],
                expected_lock_version=form.cleaned_data["expected_lock_version"],
            )
            return redirect(f"{reverse('categories:list')}?result=merged")
        except PersonalCategoryConflictError as error:
            stale_conflict = True
            form.add_error(None, str(error))
        except (ValidationError, ValueError) as error:
            form.add_error(None, str(error))
    return render(
        request,
        "errors/category_merge.html",
        {
            "workspace": workspace,
            "category": category,
            "target": target,
            "form": form,
            "stale_conflict": stale_conflict,
            "breadcrumbs": [
                ("Início", reverse("accounts:home")),
                ("Categorias", reverse("categories:list")),
                ("Consolidar", ""),
            ],
        },
        status=409 if stale_conflict else 400 if request.method == "POST" and form.errors else 200,
    )
