"""Adaptador HTTP local da jornada inicial protegida."""

import secrets
import uuid

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from modules.accounts.services import LOCAL_USER_ID, LOCAL_WORKSPACE_ID
from modules.errors.models import ErrorCategory

from .context import InitialAttemptError
from .forms import AnswerForm, CancelForm, ConfirmationForm
from .services import AttemptService

SESSION_COOKIE = "initial_session"
COOKIE_SALT = "initial-session-v1"


@never_cache
@require_http_methods(["GET", "POST"])
def initial(request: HttpRequest, question_id: uuid.UUID) -> HttpResponse:
    """Cookie contém só identificador aleatório assinado; dados ficam no servidor."""
    session = request.get_signed_cookie(SESSION_COOKIE, default="", salt=COOKIE_SALT)
    if not session and request.method == "POST":
        return HttpResponse("Sessão inválida. Reabra a questão.", status=403)
    session = session or secrets.token_urlsafe(32)
    service = AttemptService(
        actor_id=LOCAL_USER_ID, workspace_id=LOCAL_WORKSPACE_ID, session=session
    )
    cookie_name = f"initial_context_{question_id.hex}"
    token = request.get_signed_cookie(cookie_name, default="", salt=COOKIE_SALT) or ""
    try:
        response = _journey(request, question_id, service, token, cookie_name)
    except InitialAttemptError as error:
        status = 503 if error.code == "PERSISTENCE_FAILURE" else 409
        if error.code == "ACCESS_DENIED":
            status = 403
        response = render(
            request,
            "attempts/initial.html",
            {
                "error": (
                    "Falha de persistência. Reenvie a confirmação com a mesma chave."
                    if status == 503
                    else "Contexto inválido ou estado atualizado. Reabra a questão para responder."
                ),
                "code": error.code,
                "question_id": question_id,
            },
            status=status,
        )
        if status == 409 and error.code != "INVALID_DIAGNOSIS":
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
    question_id: uuid.UUID,
    service: AttemptService,
    token: str,
    cookie_name: str,
) -> HttpResponse:
    action = request.POST.get("action", "") if request.method == "POST" else ""
    if action in {"confirm", "cancel"}:
        form = ConfirmationForm(request.POST) if action == "confirm" else CancelForm(request.POST)
        if isinstance(form, ConfirmationForm):
            form.fields["category_id"].queryset = ErrorCategory.objects.filter(  # type: ignore[attr-defined]
                workspace_id=service.workspace().id
            )
        if not form.is_valid() or form.cleaned_data["token"] != token:
            raise InitialAttemptError("INVALID_INPUT")
        context = service.context(token, allow_completed=action == "confirm")
        if context.question_id != question_id:
            raise InitialAttemptError("INVALID_CONTEXT")
        if action == "cancel":
            service.cancel(token)
            response = redirect("attempts:initial", question_id=question_id)
            response.delete_cookie(cookie_name)
            return response
        category = form.cleaned_data["category_id"]
        try:
            receipt = service.confirm(
                token=token,
                key=form.cleaned_data["key"],
                category_id=category.id if category else None,
                other_description=form.cleaned_data["other_description"],
            )
        except InitialAttemptError as error:
            if error.code not in {"INVALID_DIAGNOSIS", "PERSISTENCE_FAILURE"}:
                raise
            form.add_error(
                None,
                (
                    "Selecione uma categoria. Outra exige uma descrição."
                    if error.code == "INVALID_DIAGNOSIS"
                    else "Falha de persistência. Reenvie esta confirmação com os mesmos dados."
                ),
            )
            return render(
                request,
                "attempts/initial.html",
                {
                    **service.feedback(token),
                    "confirmation": form,
                    "cancel": CancelForm(initial={"token": token}),
                },
                status=400 if error.code == "INVALID_DIAGNOSIS" else 503,
            )
        return render(request, "attempts/initial.html", {"receipt": receipt.id})
    if request.method == "POST" and action != "answer":
        raise InitialAttemptError("INVALID_INPUT")
    if action == "answer" or not token:
        data = service.presentation(question_id)
        answer = AnswerForm(request.POST if action else None, initial=data)
        answer.fields["alternative_id"].choices = data["alternatives"]  # type: ignore[attr-defined]
        if action and answer.is_valid():
            if token:
                service.cancel(token)
            values = answer.cleaned_data
            token = service.evaluate(
                question_id=question_id,
                revision_id=values["revision_id"],
                lock_version=values["lock_version"],
                alternative_id=uuid.UUID(values["alternative_id"]),
            )
            response = redirect("attempts:initial", question_id=question_id)
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
            "attempts/initial.html",
            {"stem": data["stem"], "answer": answer},
            status=400 if action else 200,
        )
    context = service.context(token)
    if context.question_id != question_id:
        raise InitialAttemptError("INVALID_CONTEXT")
    feedback = service.feedback(token)
    confirmation = ConfirmationForm(
        initial={"token": token, "key": uuid.uuid5(uuid.NAMESPACE_OID, context.nonce)}
    )
    confirmation.fields["category_id"].queryset = ErrorCategory.objects.filter(  # type: ignore[attr-defined]
        workspace_id=service.workspace_id
    )
    if context.is_correct:
        del confirmation.fields["category_id"]
        del confirmation.fields["other_description"]
    return render(
        request,
        "attempts/initial.html",
        {
            **feedback,
            "confirmation": confirmation,
            "cancel": CancelForm(initial={"token": token}),
        },
    )
