"""Fluxos e inspeções acessíveis da interface mínima da V0.1."""

import base64
import hashlib
import re
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch

import pytest
from django.test import Client
from django.urls import reverse

from modules.accounts.models import User, Workspace
from modules.accounts.services import LOCAL_WORKSPACE_ID
from modules.errors.models import ErrorCategory
from modules.operations.correlation import current_correlation_id
from shared.application.bootstrap import bootstrap_local_workspace

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_HTMX_SRI = "sha384-H5SrcfygHmAuTDZphMHqBJLc3FhssKjG7w/CeCpFReSfwBWDTKpkzPP8c+cLsK+V"  # pragma: allowlist secret -- SRI público


class SemanticAuditParser(HTMLParser):
    """Colete a estrutura relevante sem adicionar parser externo."""

    def __init__(self) -> None:
        super().__init__()
        self.tags: list[str] = []
        self.links: list[dict[str, str | None]] = []
        self.labels: list[dict[str, str | None]] = []
        self.elements: list[tuple[str, dict[str, str | None]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        self.tags.append(tag)
        self.elements.append((tag, attributes))
        if tag == "a":
            self.links.append(attributes)
        if tag == "label":
            self.labels.append(attributes)


def parsed_html(response_content: bytes) -> SemanticAuditParser:
    parser = SemanticAuditParser()
    parser.feed(response_content.decode("utf-8"))
    return parser


def initialized_workspace(timezone_name: str = "America/Sao_Paulo") -> Workspace:
    return bootstrap_local_workspace(timezone_id=timezone_name).workspace


@pytest.mark.django_db
def test_home_redirects_uninitialized_user_to_first_access() -> None:
    response = Client().get(reverse("accounts:home"))
    assert response.status_code == 302
    assert response.headers["Location"] == reverse("accounts:initial-setup")


@pytest.mark.django_db
def test_first_access_is_semantic_labeled_and_does_not_assume_timezone() -> None:
    response = Client().get(reverse("accounts:initial-setup"))
    html = response.content.decode("utf-8")
    parsed = parsed_html(response.content)

    assert response.status_code == 200
    assert '<html lang="pt-BR">' in html
    assert "Configure seu espaço local" in html
    assert "America/Sao_Paulo" in html
    assert '<option value="" selected>Selecione um fuso horário</option>' in html
    assert {"header", "nav", "main", "section", "footer", "h1", "form"} <= set(parsed.tags)
    assert any(label.get("for") == "id_timezone_name" for label in parsed.labels)
    assert 'aria-describedby="timezone-help timezone-errors"' in html
    assert 'name="timezone_name"' in html
    assert 'name="csrfmiddlewaretoken"' in html


@pytest.mark.django_db
def test_invalid_timezone_is_rejected_and_associated_with_field() -> None:
    response = Client().post(
        reverse("accounts:initial-setup"),
        {"timezone_name": "Invalid/Timezone"},
    )
    html = response.content.decode("utf-8")

    assert response.status_code == 200
    assert "Escolha um identificador de fuso IANA válido." in html
    assert 'aria-invalid="true"' in html
    assert 'id="timezone-errors"' in html
    assert "autofocus" in html
    assert User.objects.count() == 0
    assert Workspace.objects.count() == 0
    assert ErrorCategory.objects.count() == 0


@pytest.mark.django_db
def test_valid_first_access_persists_timezone_and_shows_success() -> None:
    response = Client().post(
        reverse("accounts:initial-setup"),
        {"timezone_name": "America/Sao_Paulo"},
        follow=True,
    )

    assert response.status_code == 200
    assert response.redirect_chain == [("/?status=configured", 302)]
    assert "Configuração inicial concluída com sucesso." in response.content.decode("utf-8")
    workspace = Workspace.objects.get(pk=LOCAL_WORKSPACE_ID)
    assert workspace.timezone_name == "America/Sao_Paulo"
    assert workspace.locale == "pt-BR"
    assert User.objects.count() == 1
    assert ErrorCategory.objects.count() == 10


@pytest.mark.django_db
def test_initialized_home_only_links_existing_capabilities_and_preserves_unicode() -> None:
    initialized_workspace()
    response = Client().get(reverse("accounts:home"))
    html = response.content.decode("utf-8")
    links = {link.get("href") for link in parsed_html(response.content).links}

    assert response.status_code == 200
    assert "Visão do seu estudo" in html
    assert "Sem dados" in html
    assert "Painel de estudo" in html
    assert links == {
        "/",
        "/configuracoes/",
        "/questions/",
        "/questions/new/",
        "/reviews/",
        "/taxonomy/",
        "#conteudo-principal",
    }
    for forbidden_path in (
        "/questoes/",
        "/revisoes/",
        "/dashboard/",
        "/busca/",
        "/metricas/",
        "/categorias/",
    ):
        assert forbidden_path not in html


@pytest.mark.django_db
def test_existing_workspace_redirects_first_access_to_settings() -> None:
    initialized_workspace()
    response = Client().get(reverse("accounts:initial-setup"))
    assert response.status_code == 302
    assert response.headers["Location"] == reverse("accounts:settings")


@pytest.mark.django_db
def test_timezone_change_requires_confirmation_and_then_persists() -> None:
    workspace = initialized_workspace()
    missing_confirmation = Client().post(
        reverse("accounts:settings"),
        {
            "timezone_name": "Asia/Tokyo",
            "lock_version": workspace.lock_version,
            "action": "save",
        },
    )
    missing_html = missing_confirmation.content.decode("utf-8")
    assert missing_confirmation.status_code == 200
    assert "Confirme a alteração antes de salvar." in missing_html
    assert 'aria-describedby="timezone-impact confirmed-errors"' in missing_html
    workspace.refresh_from_db()
    assert workspace.timezone_name == "America/Sao_Paulo"

    changed = Client().post(
        reverse("accounts:settings"),
        {
            "timezone_name": "Asia/Tokyo",
            "lock_version": workspace.lock_version,
            "confirmed": "on",
            "action": "save",
        },
        follow=True,
    )
    assert changed.status_code == 200
    assert "Fuso horário alterado com sucesso." in changed.content.decode("utf-8")
    workspace.refresh_from_db()
    assert workspace.timezone_name == "Asia/Tokyo"
    assert workspace.lock_version == 2


@pytest.mark.django_db
def test_timezone_change_can_be_cancelled_without_validation_or_write() -> None:
    workspace = initialized_workspace()
    response = Client().post(
        reverse("accounts:settings"),
        {
            "timezone_name": "Asia/Tokyo",
            "lock_version": workspace.lock_version,
            "action": "cancel",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert "Alteração cancelada" in response.content.decode("utf-8")
    workspace.refresh_from_db()
    assert workspace.timezone_name == "America/Sao_Paulo"
    assert workspace.lock_version == 1


@pytest.mark.django_db
def test_stale_lock_version_requires_conscious_reconfirmation() -> None:
    workspace = initialized_workspace()
    stale_version = workspace.lock_version
    Workspace.objects.filter(pk=workspace.id).update(lock_version=stale_version + 1)

    response = Client().post(
        reverse("accounts:settings"),
        {
            "timezone_name": "Asia/Tokyo",
            "lock_version": stale_version,
            "confirmed": "on",
            "action": "save",
        },
    )
    html = response.content.decode("utf-8")

    assert response.status_code == 200
    assert "A configuração mudou em outra operação." in html
    assert 'role="alert"' in html
    assert "autofocus" in html
    assert f'value="{stale_version + 1}"' in html
    assert 'name="confirmed"' in html
    assert 'name="confirmed"' in html and 'name="confirmed" checked' not in html
    workspace.refresh_from_db()
    assert workspace.timezone_name == "America/Sao_Paulo"


@pytest.mark.django_db
def test_settings_explains_impact_and_http_correlation_survives() -> None:
    initialized_workspace()
    correlation_id = "12345678-1234-4234-8234-123456789abc"
    response = Client().get(
        reverse("accounts:settings"),
        HTTP_X_CORRELATION_ID=correlation_id,
    )
    html = response.content.decode("utf-8")
    assert response.headers["X-Correlation-ID"] == correlation_id
    assert "muda o cálculo de hoje e os novos cálculos" in html
    assert "Não existem filas ou revisões nesta versão." in html


@pytest.mark.django_db
def test_timezone_change_reuses_http_correlation_without_logging_form_payload() -> None:
    workspace = initialized_workspace()
    correlation_id = "12345678-1234-4234-8234-123456789abc"
    observed: list[tuple[str | None, dict[str, object]]] = []

    def observe_event(*args: object, **kwargs: object) -> None:
        del args
        context = kwargs.get("context", {})
        assert isinstance(context, dict)
        observed.append((current_correlation_id(), context))

    with patch("modules.accounts.services.emit_event", side_effect=observe_event):
        response = Client().post(
            reverse("accounts:settings"),
            {
                "timezone_name": "Asia/Tokyo",
                "lock_version": workspace.lock_version,
                "confirmed": "on",
                "action": "save",
            },
            HTTP_X_CORRELATION_ID=correlation_id,
        )

    assert response.status_code == 302
    assert response.headers["X-Correlation-ID"] == correlation_id
    assert observed
    assert {item[0] for item in observed} == {correlation_id}
    assert all("timezone_name" not in context for _, context in observed)


@pytest.mark.django_db
def test_configuration_write_keeps_csrf_protection() -> None:
    initialized_workspace()
    response = Client(enforce_csrf_checks=True).post(
        reverse("accounts:settings"),
        {
            "timezone_name": "Asia/Tokyo",
            "lock_version": 1,
            "confirmed": "on",
            "action": "save",
        },
    )
    assert response.status_code == 403


def test_templates_use_native_keyboard_semantics_and_visible_focus() -> None:
    template_root = PROJECT_ROOT / "src" / "templates"
    templates = "\n".join(
        path.read_text(encoding="utf-8") for path in template_root.rglob("*.html")
    )
    css = (PROJECT_ROOT / "src" / "static" / "css" / "app.css").read_text(encoding="utf-8")

    assert 'tabindex="1"' not in templates
    assert 'tabindex="2"' not in templates
    assert '<a class="skip-link" href="#conteudo-principal">' in templates
    assert '<button type="submit">' in templates
    assert 'type="submit" name="action" value="cancel"' in templates
    assert ":focus-visible" in css
    assert "outline:" in css
    assert "cursor: pointer" in css


def test_layout_has_responsive_boundaries_without_horizontal_dependency() -> None:
    css = (PROJECT_ROOT / "src" / "static" / "css" / "app.css").read_text(encoding="utf-8")
    base = (PROJECT_ROOT / "src" / "templates" / "base.html").read_text(encoding="utf-8")

    assert 'name="viewport" content="width=device-width, initial-scale=1"' in base
    assert "width: 100%" in css
    assert "max-width: 72rem" in css
    assert "@media (min-width: 48rem)" in css
    assert "flex-wrap: wrap" in css
    assert "overflow-wrap: anywhere" in css
    assert "min-width: 20rem" in css


def test_vendored_htmx_matches_frozen_version_and_integrity() -> None:
    asset = PROJECT_ROOT / "src" / "static" / "vendor" / "htmx-2.0.10.min.js"
    content = asset.read_bytes()
    digest = base64.b64encode(hashlib.sha384(content).digest()).decode("ascii")

    assert b'version:"2.0.10"' in content
    assert f"sha384-{digest}" == EXPECTED_HTMX_SRI
    templates = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (PROJECT_ROOT / "src" / "templates").rglob("*.html")
    )
    assert "hx-" not in templates
    assert "htmx-2.0.10.min.js" not in templates


def test_documented_primary_colors_meet_text_contrast_target() -> None:
    def luminance(hex_color: str) -> float:
        channels = [int(hex_color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
        linear = [
            value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
            for value in channels
        ]
        return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

    def contrast(first: str, second: str) -> float:
        lighter, darker = sorted((luminance(first), luminance(second)), reverse=True)
        return (lighter + 0.05) / (darker + 0.05)

    css = (PROJECT_ROOT / "src" / "static" / "css" / "app.css").read_text(encoding="utf-8")
    colors = dict(re.findall(r"--([a-z-]+):\s*(#[0-9a-fA-F]{6})", css))
    assert contrast(colors["text"], colors["background"]) >= 4.5
    assert contrast(colors["primary"], "#ffffff") >= 4.5
    assert contrast(colors["error"], colors["error-bg"]) >= 4.5
    assert contrast(colors["success"], colors["success-bg"]) >= 4.5
