"""Thin local UI for functional export and operational backup/restore preparation."""

import os
import tempfile
from dataclasses import asdict
from datetime import UTC, datetime
from typing import Any, BinaryIO, cast

from django.core import signing
from django.http import FileResponse, HttpRequest, HttpResponse
from django.http.response import HttpResponseBase
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from modules.accounts.exceptions import WorkspaceAccessDenied
from modules.accounts.services import LOCAL_USER_ID, LOCAL_WORKSPACE_ID, get_workspace_for_owner
from modules.attempts.models import Attempt
from modules.questions.models import Question
from modules.reviews.models import Review, ReviewCycle

from .portability import ExportValidationError, export_workspace
from .services import ReconciliationResult
from .ui_services import (
    RestorePreview,
    UIRecoveryError,
    cancel_prepared_restore,
    create_backup_download,
    prepare_restore,
    preview_restore,
)

_SALT = "cei-s7-restore-preview"


def _workspace() -> Any:
    try:
        return get_workspace_for_owner(actor_user_id=LOCAL_USER_ID, workspace_id=LOCAL_WORKSPACE_ID)
    except WorkspaceAccessDenied:
        return None


def _page(request: HttpRequest, **context: object) -> HttpResponse:
    return render(
        request,
        "data_management/portability.html",
        {
            "workspace": _workspace(),
            "settings_module": os.environ.get("DJANGO_SETTINGS_MODULE", ""),
            **context,
        },
    )


def _current_counts() -> dict[str, int]:
    return {
        "questions": Question.objects.filter(workspace_id=LOCAL_WORKSPACE_ID).count(),
        "attempts": Attempt.objects.filter(workspace_id=LOCAL_WORKSPACE_ID).count(),
        "cycles": ReviewCycle.objects.filter(workspace_id=LOCAL_WORKSPACE_ID).count(),
        "reviews": Review.objects.filter(workspace_id=LOCAL_WORKSPACE_ID).count(),
    }


@require_http_methods(["GET", "POST"])
def portability(request: HttpRequest) -> HttpResponseBase:
    workspace = _workspace()
    if workspace is None:
        return redirect("accounts:initial-setup")
    if request.method == "GET":
        return _page(request)
    action = request.POST.get("action", "")
    if action in {"export", "backup"}:
        artifact = cast(BinaryIO, tempfile.TemporaryFile(mode="w+b"))
        try:
            if action == "export":
                export_workspace(workspace_id=workspace.id, destination=artifact)
            else:
                create_backup_download(artifact)
            artifact.seek(0)
            name = f"cei-{action}-{datetime.now(UTC):%Y-%m-%d}.zip"
            return FileResponse(
                artifact, as_attachment=True, filename=name, content_type="application/zip"
            )
        except (OSError, ExportValidationError, UIRecoveryError):
            artifact.close()
            return _page(request, error="Não foi possível gerar o arquivo solicitado.")
    if action == "cancel":
        return _page(request, feedback="Restauração cancelada; nenhum dado foi alterado.")
    if action == "cancel_prepared":
        try:
            cancel_prepared_restore(request.POST.get("ticket", ""))
        except UIRecoveryError as error:
            return _page(request, error=str(error))
        return _page(request, feedback="Restore pendente descartado; banco ativo preservado.")
    if action not in {"preview", "confirm"}:
        return _page(request, error="Ação desconhecida.")
    backup = request.FILES.get("backup")
    manifest = request.FILES.get("manifest")
    if backup is None or manifest is None:
        return _page(request, error="Selecione o SQLite e o manifesto correspondente.")
    try:
        preview = preview_restore(cast(BinaryIO, backup), cast(BinaryIO, manifest))
        if action == "preview":
            return _page(
                request,
                preview=preview,
                current_counts=_current_counts(),
                token=signing.dumps(asdict(preview), salt=_SALT),
                feedback="Backup validado em cópia isolada. Confira o impacto antes de confirmar.",
            )
        if request.POST.get("confirmed") != "on" or request.POST.get("confirmation") != "RESTAURAR":
            return _page(request, error="Marque a confirmação e digite RESTAURAR.")
        try:
            signed = signing.loads(request.POST.get("token", ""), salt=_SALT)
            expected = RestorePreview(
                upload_sha256=signed["upload_sha256"],
                manifest_sha256=signed["manifest_sha256"],
                active_fingerprint=signed["active_fingerprint"],
                candidate=ReconciliationResult(**signed["candidate"]),
            )
        except (signing.BadSignature, KeyError, TypeError, ValueError):
            return _page(request, error="Preview inválido; valide o backup novamente.")
        if preview != expected:
            return _page(request, error="O preview mudou; valide o backup novamente.")
        backup.seek(0)
        manifest.seek(0)
        ticket = prepare_restore(
            cast(BinaryIO, backup), cast(BinaryIO, manifest), expected=expected
        )
        return _page(request, ticket=ticket, candidate=preview.candidate)
    except UIRecoveryError as error:
        return _page(request, error=str(error))
