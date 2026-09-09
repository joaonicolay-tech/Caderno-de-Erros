"""Acesso direto e protegido à conclusão de uma Review conhecida."""

import secrets
import uuid

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from modules.accounts.services import LOCAL_USER_ID, LOCAL_WORKSPACE_ID
from modules.attempts.context import InitialAttemptError
from modules.attempts.forms import CancelForm, ReviewAnswerForm, ReviewConfirmationForm
from modules.errors.models import ErrorCategory

from .services import CompleteReviewService

SESSION_COOKIE = "review_session"
COOKIE_SALT = "review-session-v1"


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
    response["Referrer-Policy"] = "no-referrer"
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
