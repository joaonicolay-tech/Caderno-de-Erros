"""Integração da apresentação V0.4-S3 com a fachada analítica S2."""

from datetime import date
from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock, patch
from uuid import uuid4

import pytest
from django.test import Client
from django.urls import reverse

from modules.accounts.services import LOCAL_WORKSPACE_ID
from modules.analytics.read_models import (
    ActivitySummary,
    ErrorCategoryBreakdown,
    ErrorCategoryRow,
    PerformanceBreakdown,
    PerformanceRow,
    Ratio,
    ReviewSummary,
)
from shared.application.bootstrap import bootstrap_local_workspace


def _ratio(numerator: int, denominator: int) -> Ratio:
    return Ratio(
        numerator=numerator,
        denominator=denominator,
        percent=(Decimal(numerator) * 100 / Decimal(denominator)) if denominator else None,
    )


@pytest.mark.django_db
def test_dashboard_empty_state_distinguishes_unknown_accuracy_from_zero() -> None:
    bootstrap_local_workspace(timezone_id="America/Sao_Paulo")

    response = Client().get(reverse("accounts:home"))
    html = response.content.decode("utf-8")

    assert response.status_code == 200
    assert "Taxa de acerto" in html
    assert "Ainda sem tentativas válidas." in html
    assert "0.0%" not in html
    assert "Ainda não há erros válidos para classificar." in html


@pytest.mark.django_db
def test_dashboard_renders_s2_values_and_residue_without_reinterpretation() -> None:
    bootstrap_local_workspace(timezone_id="America/Sao_Paulo")
    analytics = Mock()
    analytics.activity.return_value = ActivitySummary(3, 2, 4, 2, 2, 2, 2, _ratio(2, 4))
    analytics.reviews.return_value = ReviewSummary(date(2026, 9, 10), 1, 2, 3, 4)
    math = PerformanceRow(uuid4(), "Matemática", None, 3, 2, 1, _ratio(2, 3))
    empty = PerformanceRow(uuid4(), "Sem amostra", None, 0, 0, 0, _ratio(0, 0))
    analytics.performance_pair.return_value = (
        PerformanceBreakdown((math, empty), 0, 3),
        PerformanceBreakdown((math,), 1, 4),
    )
    analytics.error_categories.return_value = ErrorCategoryBreakdown(
        rows=(ErrorCategoryRow(uuid4(), "ATTENTION", "Atenção", 1, _ratio(1, 1)),),
        classified_errors=1,
        unclassified_errors=1,
        eligible_errors=2,
    )

    with patch("modules.accounts.views.AnalyticsService", return_value=analytics) as service:
        response = Client().get(reverse("accounts:home"))

    html = response.content.decode("utf-8")
    assert response.status_code == 200
    service.assert_called_once_with(workspace_id=LOCAL_WORKSPACE_ID)
    assert "3 inicial(is)" not in html
    assert "2 inicial(is) e 2 de revisão" in html
    assert "50,0%" in html
    assert "Concluídas hoje" in html and "Devidas hoje" in html
    assert 'href="/reviews/?section=OVERDUE"' in html
    assert 'href="/reviews/?section=DUE"' in html
    assert 'href="/reviews/?section=FUTURE"' in html
    assert 'aria-label="2 revisões atrasadas"' in html
    assert 'href="/questions/?review_status=OVERDUE"' not in html
    assert "Matemática" in html and "66,7%" in html
    assert "Sem amostra" in html and "Sem dados" in html
    assert "Atenção:" in html
    assert "Erros válidos sem classificação:" in html
    assert "resíduo analítico, não uma categoria persistida" in html
    assert '<table aria-labelledby="discipline-title">' in html
    assert '<table aria-labelledby="subject-title">' in html
    analytics.performance_pair.assert_called_once_with()


def test_dashboard_view_delegates_analytics_to_s2() -> None:
    content = Path("src/modules/accounts/views.py").read_text(encoding="utf-8")

    assert "AnalyticsService(workspace_id=workspace.id)" in content
    assert "Question.objects" not in content
    assert "Attempt.objects" not in content
    assert "ReviewCycle.objects" not in content
