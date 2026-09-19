"""Acesso direto e protegido à conclusão de uma Review conhecida."""

import secrets
import uuid

from django.conf import settings
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from modules.accounts.exceptions import WorkspaceAccessDenied
from modules.accounts.models import Workspace
from modules.accounts.services import LOCAL_USER_ID, LOCAL_WORKSPACE_ID, get_workspace_for_owner
from modules.attempts.context import InitialAttemptError
from modules.attempts.forms import CancelForm, ReviewAnswerForm, ReviewConfirmationForm
from modules.errors.forms import ErrorClassificationCorrectionForm
from modules.errors.models import ErrorCategory, ErrorClassification
from modules.errors.services import ErrorDiagnosisConflictError, ErrorDiagnosisService

from .policies import ReviewTemporalStatus
from .selectors import ReviewQueueSection, get_learning_timeline, list_review_queue
from .services import CompleteReviewService

SESSION_COOKIE = "review_session"
COOKIE_SALT = "review-session-v1"


def _workspace() -> Workspace | None:
    try:
        return get_workspace_for_owner(actor_user_id=LOCAL_USER_ID, workspace_id=LOCAL_WORKSPACE_ID)
    except WorkspaceAccessDenied:
        return None


@never_cache
@require_http_methods(["GET"])
def queue(request: HttpRequest) -> HttpResponse:
    """Exiba as três seções derivadas; cada uma possui paginação independente."""
    workspace = _workspace()
    if workspace is None:
        return redirect("accounts:initial-setup")

    def page(name: str) -> int:
        try:
            return max(1, int(request.GET.get(name, "1")))
        except ValueError:
            return 1

    result = list_review_queue(
        workspace_id=workspace.id,
        overdue_page=page("overdue_page"),
        due_page=page("due_page"),
        future_page=page("future_page"),
    )
    requested_section = request.GET.get("section", "").upper()
    sections: dict[str, tuple[str, ReviewQueueSection]] = {
        ReviewTemporalStatus.OVERDUE: ("Atrasadas", result.overdue),
        ReviewTemporalStatus.DUE: ("Devidas hoje", result.due),
        ReviewTemporalStatus.FUTURE: ("Futuras", result.future),
    }
    return render(
        request,
        "reviews/queue.html",
        {
            "workspace": workspace,
            "queue": result,
            "selected_section": sections.get(requested_section),
            "actionable_review": (result.overdue.entries or result.due.entries or (None,))[0],
        },
    )


@never_cache
@require_http_methods(["GET"])
def timeline(request: HttpRequest, question_id: uuid.UUID) -> HttpResponse:
    workspace = _workspace()
    if workspace is None:
        return redirect("accounts:initial-setup")
    try:
        events = get_learning_timeline(workspace_id=workspace.id, question_id=question_id)
    except Exception as error:
        raise Http404("Histórico não encontrado.") from error
    return render(request, "reviews/timeline.html", {"workspace": workspace, "events": events})


@never_cache
@require_http_methods(["GET", "POST"])
def correct_diagnosis(request: HttpRequest, attempt_id: uuid.UUID) -> HttpResponse:
    workspace = _workspace()
    if workspace is None:
        return redirect("accounts:initial-setup")
    classification = (
        ErrorClassification.objects.filter(workspace_id=workspace.id, attempt_id=attempt_id)
        .select_related("attempt", "category")
        .first()
    )
    if classification is None:
        raise Http404("Diagnóstico não encontrado.")
    form = ErrorClassificationCorrectionForm(
        request.POST if request.method == "POST" else None,
        initial={
            "lock_version": classification.lock_version,
            "category": classification.category_id,
            "other_description": classification.other_description,
        },
        workspace_id=workspace.id,
    )
    if request.method == "POST" and form.is_valid():
        try:
            ErrorDiagnosisService(workspace_id=workspace.id).correct(
                attempt_id=attempt_id,
                category_id=form.cleaned_data["category"].id,
                other_description=form.cleaned_data["other_description"],
                change_reason=form.cleaned_data["change_reason"],
                expected_lock_version=form.cleaned_data["lock_version"],
            )
            return redirect("reviews:timeline", question_id=classification.attempt.question_id)
        except (ErrorDiagnosisConflictError, ValueError) as error:
            form.add_error(None, str(error))
    return render(
        request, "reviews/diagnosis_correct.html", {"form": form, "classification": classification}
    )


@never_cache
@require_http_methods(["GET", "POST"])
def complete(request: HttpRequest, review_id: uuid.UUID) -> HttpResponse:
    """Adapte a jornada E3 sem selector, fila ou histórico visual."""
    session = request.get_signed_cookie(SESSION_COOKIE, default="", salt=COOKIE_SALT)
    if not session and request.method == "POST":
        return HttpResponse("Sessão inválida. Reabra a revisão.", status=403)
    session = session or secrets.token_urlsafe(32)
    service = CompleteReviewService(
        actor_id=LOCAL_USER_ID, workspace_id=LOCAL_WORKSPACE_ID, session=session
    )
    cookie_name = f"review_context_{review_id.hex}"
    token = request.get_signed_cookie(cookie_name, default="", salt=COOKIE_SALT) or ""
    try:
        response = _journey(request, review_id, service, token, cookie_name)
    except InitialAttemptError as error:
        status = 503 if error.code == "PERSISTENCE_FAILURE" else 409
        if error.code == "ACCESS_DENIED":
            status = 403
        response = render(
            request,
            "reviews/complete.html",
            {
                "error": (
                    "Falha de persistência. Reenvie a confirmação com a mesma chave."
                    if status == 503
                    else "Review indisponível, futura ou contexto inválido. Reabra a revisão."
                ),
                "code": error.code,
                "review_id": review_id,
            },
            status=status,
        )
        if status == 409 and error.code not in {
            "INVALID_DIAGNOSIS",
            "INVALID_EASE",
            "INVALID_INPUT",
        }:
            response.delete_cookie(cookie_name)
    response.set_signed_cookie(
        SESSION_COOKIE,
        session,
        salt=COOKIE_SALT,
        httponly=True,
        samesite="Strict",
        secure=request.is_secure(),
    )
    response["Referrer-Policy"] = settings.FORM_POST_REFERRER_POLICY
    return response


def _journey(
    request: HttpRequest,
    review_id: uuid.UUID,
    service: CompleteReviewService,
    token: str,
    cookie_name: str,
) -> HttpResponse:
    action = request.POST.get("action", "") if request.method == "POST" else ""
    if action in {"confirm", "cancel"}:
        form = (
            ReviewConfirmationForm(request.POST)
            if action == "confirm"
            else CancelForm(request.POST)
        )
        if isinstance(form, ReviewConfirmationForm):
            form.fields["category_id"].queryset = ErrorCategory.objects.filter(  # type: ignore[attr-defined]
                workspace_id=service.attempts.workspace_id
            )
        if not form.is_valid() or form.cleaned_data["token"] != token:
            raise InitialAttemptError("INVALID_INPUT")
        context = service._review_context(token, allow_completed=action == "confirm")
        if context.review_id != review_id:
            raise InitialAttemptError("INVALID_CONTEXT")
        if action == "cancel":
            service.cancel(token)
            response = redirect("reviews:complete", review_id=review_id)
            response.delete_cookie(cookie_name)
            return response
        category = form.cleaned_data["category_id"]
        try:
            receipt = service.complete_review(
                token=token,
                key=form.cleaned_data["key"],
                perceived_ease=form.cleaned_data["perceived_ease"] or None,
                category_id=category.id if category else None,
                description=form.cleaned_data["other_description"],
            )
        except InitialAttemptError as error:
            if error.code not in {"INVALID_DIAGNOSIS", "INVALID_EASE", "PERSISTENCE_FAILURE"}:
                raise
            form.add_error(
                None,
                "Selecione uma categoria; Outra exige descrição."
                if error.code == "INVALID_DIAGNOSIS"
                else "Falha de persistência. Reenvie com os mesmos dados.",
            )
            return render(
                request,
                "reviews/complete.html",
                {
                    **service.feedback(token),
                    "confirmation": form,
                    "cancel": CancelForm(initial={"token": token}),
                },
                status=400 if error.code != "PERSISTENCE_FAILURE" else 503,
            )
        return render(request, "reviews/complete.html", {"receipt": receipt.id})
    if request.method == "POST" and action != "answer":
        raise InitialAttemptError("INVALID_INPUT")
    if action == "answer" or not token:
        data = service.presentation(review_id)
        answer = ReviewAnswerForm(request.POST if action else None, initial=data)
        answer.fields["alternative_id"].choices = data["alternatives"]  # type: ignore[attr-defined]
        if action and answer.is_valid():
            if token:
                service.cancel(token)
            values = answer.cleaned_data
            token = service.evaluate(
                review_id=review_id,
                revision_id=values["revision_id"],
                lock_version=values["lock_version"],
                review_lock_version=values["review_lock_version"],
                alternative_id=uuid.UUID(values["alternative_id"]),
            )
            response = redirect("reviews:complete", review_id=review_id)
            response.set_signed_cookie(
                cookie_name,
                token,
                salt=COOKIE_SALT,
                httponly=True,
                samesite="Strict",
                secure=request.is_secure(),
            )
            return response
        return render(
            request,
            "reviews/complete.html",
            {"stem": data["stem"], "answer": answer},
            status=400 if action else 200,
        )
    context = service._review_context(token)
    if context.review_id != review_id:
        raise InitialAttemptError("INVALID_CONTEXT")
    confirmation = ReviewConfirmationForm(
        initial={"token": token, "key": uuid.uuid5(uuid.NAMESPACE_OID, context.nonce)}
    )
    confirmation.fields["category_id"].queryset = ErrorCategory.objects.filter(  # type: ignore[attr-defined]
        workspace_id=service.attempts.workspace_id
    )
    if context.is_correct:
        del confirmation.fields["category_id"]
        del confirmation.fields["other_description"]
    return render(
        request,
        "reviews/complete.html",
        {
            **service.feedback(token),
            "confirmation": confirmation,
            "cancel": CancelForm(initial={"token": token}),
        },
    )
