"""Apresentação fina do espaço e da configuração local."""

from decimal import Decimal, localcontext
from fractions import Fraction
from typing import Any

from django.db import DatabaseError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from modules.analytics import AnalyticsService
from modules.priority.services import list_subject_priorities
from shared.application.bootstrap import bootstrap_local_workspace

from .exceptions import LocalBootstrapConflict, WorkspaceAccessDenied, WorkspaceConcurrencyError
from .forms import InitialSetupForm, TimezoneChangeForm
from .models import Workspace
from .services import (
    LOCAL_USER_ID,
    LOCAL_WORKSPACE_ID,
    TIMEZONE_CHANGE_NOTICE,
    change_workspace_timezone,
    get_workspace_for_owner,
)


def _local_workspace() -> Workspace | None:
    try:
        return get_workspace_for_owner(
            actor_user_id=LOCAL_USER_ID,
            workspace_id=LOCAL_WORKSPACE_ID,
        )
    except WorkspaceAccessDenied:
        return None


def _status_message(request: HttpRequest, messages: dict[str, str]) -> str:
    return messages.get(request.GET.get("status", ""), "")


def home(request: HttpRequest) -> HttpResponse:
    """Apresente o dashboard V0.4 a partir da fachada analítica read-only."""
    workspace = _local_workspace()
    if workspace is None:
        return redirect("accounts:initial-setup")
    analytics = AnalyticsService(workspace_id=workspace.id)
    activity = analytics.activity()
    reviews = analytics.reviews()
    disciplines, subjects = analytics.performance_pair()
    error_categories = analytics.error_categories()
    return render(
        request,
        "accounts/home.html",
        {
            "workspace": workspace,
            "activity": activity,
            "reviews": reviews,
            "disciplines": disciplines,
            "subjects": subjects,
            "error_categories": error_categories,
            "observed_error_categories": tuple(row for row in error_categories.rows if row.errors),
            "feedback": _status_message(
                request,
                {"configured": "Configuração inicial concluída com sucesso."},
            ),
        },
    )


def _display_factor(value: Fraction | None) -> str:
    if value is None:
        return "Indisponível"
    with localcontext() as context:
        context.prec = 20
        return f"{Decimal(value.numerator) / Decimal(value.denominator):.2f}"


def priority(request: HttpRequest) -> HttpResponse:
    """Show optional advice; reading it has no operational side effects."""
    workspace = _local_workspace()
    if workspace is None:
        return redirect("accounts:initial-setup")
    recommendation = list_subject_priorities(workspace_id=workspace.id)
    explanations = {
        "LOW_DOMAIN": "Domínio baixo",
        "OVERDUE_REVIEWS": "Revisões atrasadas",
        "RECURRING_ERRORS": "Erros de revisão recorrentes",
        "RECENT_DECLINE": "Queda recente no desempenho",
        "NO_CONTRIBUTING_RISK": "Nenhum fator elevou a prioridade",
    }
    insufficiency = {
        "MISSING_CONFIDENCE": "Confiança de domínio indisponível",
        "LOW_CONFIDENCE": "Confiança de domínio abaixo de 40",
        "MISSING_DOMAIN_EVIDENCE": "Domínio sem evidência",
        "NO_ACTIVE_QUESTIONS": "Nenhuma questão ativa",
        "MISSING_RECURRENCE_EVIDENCE": "Menos de três questões com duas revisões válidas nos últimos 90 dias",
        "MISSING_RECENT_DECLINE_BASELINE": "Menos de três questões com revisões válidas nas duas janelas de 30 dias",
    }

    def display(row: Any) -> dict[str, Any]:
        result = row.result
        return {
            "subject": row.subject,
            "score": _display_factor(result.score),
            "confidence": result.confidence,
            "w": _display_factor(result.w),
            "o": _display_factor(result.o),
            "r": _display_factor(result.r),
            "d": _display_factor(result.d),
            "active": result.active_question_count,
            "overdue": result.overdue_question_count,
            "recurrence_eligible": result.recurrence_eligible_count,
            "recurring": result.recurring_question_count,
            "comparable": result.comparable_question_count,
            "explanations": tuple(explanations[code] for code in result.explanation_codes),
            "reasons": tuple(insufficiency[code] for code in result.reason_codes),
        }

    return render(
        request,
        "accounts/priority.html",
        {
            "workspace": workspace,
            "evaluated_on": recommendation.evaluated_on,
            "ranked": tuple(display(row) for row in recommendation.ranked),
            "collecting": tuple(display(row) for row in recommendation.collect_more_evidence),
        },
    )


@require_http_methods(["GET", "POST"])
def initial_setup(request: HttpRequest) -> HttpResponse:
    """Execute FL-023 sem presumir fuso do servidor ou navegador."""
    if _local_workspace() is not None:
        return redirect("accounts:settings")

    form = InitialSetupForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            bootstrap_local_workspace(timezone_id=form.cleaned_data["timezone_name"])
        except (ValueError, LocalBootstrapConflict, DatabaseError):
            form.add_error(
                None,
                "Não foi possível concluir a configuração. Verifique os dados e tente novamente.",
            )
        else:
            return redirect(f"{reverse('accounts:home')}?status=configured")

    return render(request, "accounts/initial_setup.html", {"form": form})


def _change_form_initial(workspace: Workspace) -> dict[str, Any]:
    return {
        "timezone_name": workspace.timezone_name,
        "lock_version": workspace.lock_version,
    }


@require_http_methods(["GET", "POST"])
def settings_view(request: HttpRequest) -> HttpResponse:
    """Altere o fuso com confirmação, cancelamento e compare-and-swap."""
    workspace = _local_workspace()
    if workspace is None:
        return redirect("accounts:initial-setup")

    if request.method == "POST" and request.POST.get("action") == "cancel":
        change_workspace_timezone(
            actor_user_id=LOCAL_USER_ID,
            workspace_id=LOCAL_WORKSPACE_ID,
            timezone_id=workspace.timezone_name,
            expected_lock_version=workspace.lock_version,
            confirmed=False,
        )
        return redirect(f"{reverse('accounts:settings')}?status=cancelled")

    form = TimezoneChangeForm(
        request.POST if request.method == "POST" else None,
        initial=_change_form_initial(workspace),
    )
    if request.method == "POST" and form.is_valid():
        requested_timezone = form.cleaned_data["timezone_name"]
        try:
            result = change_workspace_timezone(
                actor_user_id=LOCAL_USER_ID,
                workspace_id=LOCAL_WORKSPACE_ID,
                timezone_id=requested_timezone,
                expected_lock_version=form.cleaned_data["lock_version"],
                confirmed=form.cleaned_data["confirmed"],
            )
        except WorkspaceConcurrencyError:
            workspace.refresh_from_db()
            form = TimezoneChangeForm(
                data={
                    "timezone_name": requested_timezone,
                    "lock_version": workspace.lock_version,
                }
            )
            form.is_valid()
            form.add_error(
                None,
                "A configuração mudou em outra operação. Confira o valor atual e confirme novamente.",
            )
        except (WorkspaceAccessDenied, DatabaseError):
            form.add_error(
                None,
                "Não foi possível salvar a configuração. O fuso anterior foi preservado.",
            )
        else:
            status = "updated" if result.changed else "unchanged"
            return redirect(f"{reverse('accounts:settings')}?status={status}")

    return render(
        request,
        "accounts/settings.html",
        {
            "form": form,
            "workspace": workspace,
            "impact_notice": TIMEZONE_CHANGE_NOTICE,
            "feedback": _status_message(
                request,
                {
                    "updated": "Fuso horário alterado com sucesso.",
                    "unchanged": "O fuso horário já estava configurado com esse valor.",
                    "cancelled": "Alteração cancelada. O fuso anterior foi preservado.",
                },
            ),
        },
    )
