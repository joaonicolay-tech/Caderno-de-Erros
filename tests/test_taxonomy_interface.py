"""Gestão web acessível da taxonomia: CT-003/004/094-097/137."""

import re
import uuid
from pathlib import Path

import pytest
from django.test import Client
from django.urls import reverse

from modules.accounts.models import User, Workspace
from modules.taxonomy.models import Discipline, Subject, Subsubject, TaxonomyStatus
from modules.taxonomy.services import (
    create_discipline,
    create_subject,
    create_subsubject,
    rename_discipline,
)
from shared.application.bootstrap import bootstrap_local_workspace

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _local_workspace() -> Workspace:
    return bootstrap_local_workspace(timezone_id="America/Sao_Paulo").workspace


def _foreign_workspace() -> Workspace:
    owner = User.objects.create_user(email="foreign@example.test")
    return Workspace.objects.create(
        owner_user=owner,
        name="Espaço estrangeiro",
        timezone_name="UTC",
    )


@pytest.mark.django_db
def test_taxonomy_redirects_to_first_access_without_local_workspace() -> None:
    response = Client().get(reverse("taxonomy:index"))

    assert response.status_code == 302
    assert response.headers["Location"] == reverse("accounts:initial-setup")


@pytest.mark.django_db
def test_empty_taxonomy_and_home_expose_only_the_implemented_capability() -> None:
    _local_workspace()
    client = Client()

    response = client.get(reverse("taxonomy:index"))
    html = response.content.decode("utf-8")
    home = client.get(reverse("accounts:home")).content.decode("utf-8")

    assert response.status_code == 200
    assert "Nenhuma disciplina ativa" in html
    assert reverse("taxonomy:discipline-create") in html
    assert 'aria-label="Filtrar por estado"' in html
    assert 'aria-current="page"' in html
    assert "Painel de estudo" in home
    assert "Tentativas" in home
    assert reverse("taxonomy:index") in home
    assert reverse("questions:quick-entry") in home
    for forbidden in ("Métricas", "Busca"):
        assert f">{forbidden}<" not in home


@pytest.mark.django_db
def test_ct003_and_ct094_duplicate_form_preserves_input_and_associates_error() -> None:
    workspace = _local_workspace()
    client = Client()
    create_url = reverse("taxonomy:discipline-create")

    created = client.post(create_url, {"name": "Álgebra"}, follow=True)
    duplicate = client.post(create_url, {"name": "  áLGEBRA  "})
    html = duplicate.content.decode("utf-8")

    assert created.redirect_chain == [(f"{reverse('taxonomy:index')}?result=created", 302)]
    assert "Disciplina criada com sucesso" in created.content.decode("utf-8")
    assert duplicate.status_code == 200
    assert "Já existe um item ativo com esse nome" in html
    assert 'value="  áLGEBRA  "' in html
    assert 'aria-invalid="true"' in html
    assert 'aria-describedby="name-help name-errors"' in html
    assert "autofocus" in html
    assert Discipline.objects.filter(workspace=workspace).count() == 1


@pytest.mark.django_db
def test_ct137_complete_create_edit_and_hierarchical_navigation() -> None:
    workspace = _local_workspace()
    client = Client()

    client.post(reverse("taxonomy:discipline-create"), {"name": "Matemática"})
    discipline = Discipline.objects.get(workspace=workspace)
    subjects_url = reverse("taxonomy:subject-list", args=[discipline.id])
    subject_create_url = reverse("taxonomy:subject-create", args=[discipline.id])
    subject_created = client.post(subject_create_url, {"name": "Álgebra"}, follow=True)
    subject = Subject.objects.get(workspace=workspace)
    subsubjects_url = reverse("taxonomy:subsubject-list", args=[subject.id])
    subsubject_created = client.post(
        reverse("taxonomy:subsubject-create", args=[subject.id]),
        {"name": "Equações"},
        follow=True,
    )
    subsubject = Subsubject.objects.get(workspace=workspace)

    discipline_edit = client.post(
        reverse("taxonomy:discipline-edit", args=[discipline.id]),
        {"name": "Matemática aplicada", "lock_version": discipline.lock_version},
        follow=True,
    )
    subject_edit = client.post(
        reverse("taxonomy:subject-edit", args=[subject.id]),
        {"name": "Álgebra linear", "lock_version": subject.lock_version},
        follow=True,
    )
    subsubject_edit = client.post(
        reverse("taxonomy:subsubject-edit", args=[subsubject.id]),
        {"name": "Sistemas lineares", "lock_version": subsubject.lock_version},
        follow=True,
    )

    assert subject_created.redirect_chain == [(f"{subjects_url}?result=created", 302)]
    assert subsubject_created.redirect_chain == [(f"{subsubjects_url}?result=created", 302)]
    assert "Assunto atualizado com sucesso" in subject_edit.content.decode("utf-8")
    assert "Subassunto atualizado com sucesso" in subsubject_edit.content.decode("utf-8")
    assert "Disciplina atualizada com sucesso" in discipline_edit.content.decode("utf-8")
    discipline.refresh_from_db()
    subject.refresh_from_db()
    subsubject.refresh_from_db()
    assert discipline.name == "Matemática aplicada"
    assert subject.name == "Álgebra linear"
    assert subsubject.name == "Sistemas lineares"
    hierarchy = client.get(subsubjects_url).content.decode("utf-8")
    assert "Matemática aplicada" in hierarchy
    assert "Álgebra linear" in hierarchy
    assert "Sistemas lineares" in hierarchy
    assert "Trilha de navegação" in hierarchy


@pytest.mark.django_db
def test_ct004_and_ct095_foreign_or_unknown_ids_return_safe_404() -> None:
    local = _local_workspace()
    foreign = _foreign_workspace()
    foreign_discipline = create_discipline(workspace_id=foreign.id, name="Nome sigiloso")
    foreign_subject = create_subject(
        workspace_id=foreign.id,
        discipline_id=foreign_discipline.id,
        name="Assunto sigiloso",
    )
    foreign_subsubject = create_subsubject(
        workspace_id=foreign.id,
        subject_id=foreign_subject.id,
        name="Subassunto sigiloso",
    )
    client = Client()
    urls = [
        reverse("taxonomy:discipline-edit", args=[foreign_discipline.id]),
        reverse("taxonomy:discipline-archive", args=[foreign_discipline.id]),
        reverse("taxonomy:subject-list", args=[foreign_discipline.id]),
        reverse("taxonomy:subject-create", args=[foreign_discipline.id]),
        reverse("taxonomy:subject-edit", args=[foreign_subject.id]),
        reverse("taxonomy:subject-archive", args=[foreign_subject.id]),
        reverse("taxonomy:subsubject-list", args=[foreign_subject.id]),
        reverse("taxonomy:subsubject-create", args=[foreign_subject.id]),
        reverse("taxonomy:subsubject-edit", args=[foreign_subsubject.id]),
        reverse("taxonomy:subsubject-archive", args=[foreign_subsubject.id]),
        reverse("taxonomy:discipline-edit", args=[uuid.uuid4()]),
    ]

    for url in urls:
        get_response = client.get(url)
        post_response = client.post(url, {"name": "Ataque", "lock_version": 1})
        assert get_response.status_code == 404
        assert post_response.status_code in {404, 405}
        assert "sigiloso" not in get_response.content.decode("utf-8").lower()

    assert not Discipline.objects.filter(workspace=local).exists()
    foreign_discipline.refresh_from_db()
    assert foreign_discipline.name == "Nome sigiloso"


@pytest.mark.django_db
def test_stale_edit_preserves_input_and_never_overwrites_first_tab() -> None:
    workspace = _local_workspace()
    discipline = create_discipline(workspace_id=workspace.id, name="Original")
    stale_version = discipline.lock_version
    rename_discipline(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        name="Salva na primeira aba",
        expected_lock_version=stale_version,
    )

    response = Client().post(
        reverse("taxonomy:discipline-edit", args=[discipline.id]),
        {"name": "Entrada preservada da segunda aba", "lock_version": stale_version},
    )
    html = response.content.decode("utf-8")

    assert response.status_code == 200
    assert "O item mudou em outra operação" in html
    assert 'value="Entrada preservada da segunda aba"' in html
    assert 'name="lock_version" value="2"' in html
    assert 'role="alert"' in html
    assert "autofocus" in html
    discipline.refresh_from_db()
    assert discipline.name == "Salva na primeira aba"
    assert discipline.lock_version == 2


@pytest.mark.django_db
def test_archive_requires_confirmation_can_cancel_and_preserves_descendants() -> None:
    workspace = _local_workspace()
    discipline = create_discipline(workspace_id=workspace.id, name="Física")
    subject = create_subject(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        name="Mecânica",
    )
    subsubject = create_subsubject(
        workspace_id=workspace.id,
        subject_id=subject.id,
        name="Cinemática",
    )
    client = Client()
    archive_url = reverse("taxonomy:discipline-archive", args=[discipline.id])

    confirmation = client.get(archive_url).content.decode("utf-8")
    missing_confirmation = client.post(
        archive_url,
        {"action": "archive", "lock_version": discipline.lock_version},
    )
    cancelled = client.post(
        archive_url,
        {"action": "cancel", "lock_version": discipline.lock_version},
        follow=True,
    )
    discipline.refresh_from_db()

    assert "1 assunto(s) existente(s) permanecerão preservados" in confirmation
    assert "deixará de estar disponível para novos vínculos" in confirmation
    assert "Confirme o arquivamento" in missing_confirmation.content.decode("utf-8")
    assert "Arquivamento cancelado" in cancelled.content.decode("utf-8")
    assert discipline.status == TaxonomyStatus.ACTIVE

    archived = client.post(
        archive_url,
        {
            "action": "archive",
            "lock_version": discipline.lock_version,
            "confirmed": "on",
        },
        follow=True,
    )
    discipline.refresh_from_db()
    subject.refresh_from_db()
    subsubject.refresh_from_db()

    assert "Disciplina arquivada com sucesso" in archived.content.decode("utf-8")
    assert discipline.status == TaxonomyStatus.ARCHIVED
    assert discipline.archived_at is not None
    assert subject.status == TaxonomyStatus.ACTIVE
    assert subsubject.status == TaxonomyStatus.ACTIVE

    subjects_url = reverse("taxonomy:subject-list", args=[discipline.id])
    historical = client.get(subjects_url).content.decode("utf-8")
    assert subject.name in historical
    assert "indisponível devido ao ancestral arquivado" in historical
    assert reverse("taxonomy:subject-create", args=[discipline.id]) not in historical
    blocked = client.get(reverse("taxonomy:subject-create", args=[discipline.id]))
    assert blocked.status_code == 409
    assert "disciplina está arquivada" in blocked.content.decode("utf-8")


@pytest.mark.django_db
def test_subject_and_subsubject_archive_flows_remain_historical() -> None:
    workspace = _local_workspace()
    discipline = create_discipline(workspace_id=workspace.id, name="História")
    subject = create_subject(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        name="Antiguidade",
    )
    subsubject = create_subsubject(
        workspace_id=workspace.id,
        subject_id=subject.id,
        name="Roma",
    )
    client = Client()

    subsubject_response = client.post(
        reverse("taxonomy:subsubject-archive", args=[subsubject.id]),
        {"action": "archive", "lock_version": 1, "confirmed": "on"},
        follow=True,
    )
    subject_response = client.post(
        reverse("taxonomy:subject-archive", args=[subject.id]),
        {"action": "archive", "lock_version": 1, "confirmed": "on"},
        follow=True,
    )
    subject.refresh_from_db()
    subsubject.refresh_from_db()

    assert "Subassunto arquivado com sucesso" in subsubject_response.content.decode("utf-8")
    assert "Assunto arquivado com sucesso" in subject_response.content.decode("utf-8")
    assert subject.status == TaxonomyStatus.ARCHIVED
    assert subsubject.status == TaxonomyStatus.ARCHIVED
    subject_history = client.get(
        f"{reverse('taxonomy:subject-list', args=[discipline.id])}?state=archived"
    ).content.decode("utf-8")
    subsubject_history = client.get(
        f"{reverse('taxonomy:subsubject-list', args=[subject.id])}?state=archived"
    ).content.decode("utf-8")
    assert subject.name in subject_history
    assert subsubject.name in subsubject_history
    assert client.get(reverse("taxonomy:subsubject-create", args=[subject.id])).status_code == 409


@pytest.mark.django_db
def test_subject_and_subsubject_archive_can_be_cancelled_without_changes() -> None:
    workspace = _local_workspace()
    discipline = create_discipline(workspace_id=workspace.id, name="Química")
    subject = create_subject(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        name="Química orgânica",
    )
    subsubject = create_subsubject(
        workspace_id=workspace.id,
        subject_id=subject.id,
        name="Hidrocarbonetos",
    )
    client = Client()

    subject_response = client.post(
        reverse("taxonomy:subject-archive", args=[subject.id]),
        {"action": "cancel", "lock_version": subject.lock_version},
        follow=True,
    )
    subsubject_response = client.post(
        reverse("taxonomy:subsubject-archive", args=[subsubject.id]),
        {"action": "cancel", "lock_version": subsubject.lock_version},
        follow=True,
    )
    subject.refresh_from_db()
    subsubject.refresh_from_db()

    assert "Arquivamento cancelado" in subject_response.content.decode("utf-8")
    assert "Arquivamento cancelado" in subsubject_response.content.decode("utf-8")
    assert subject.status == TaxonomyStatus.ACTIVE
    assert subsubject.status == TaxonomyStatus.ACTIVE


@pytest.mark.django_db
def test_stale_archive_requires_new_confirmation_and_preserves_state() -> None:
    workspace = _local_workspace()
    discipline = create_discipline(workspace_id=workspace.id, name="Geografia")
    stale_version = discipline.lock_version
    rename_discipline(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        name="Geografia humana",
        expected_lock_version=stale_version,
    )

    response = Client().post(
        reverse("taxonomy:discipline-archive", args=[discipline.id]),
        {"action": "archive", "lock_version": stale_version, "confirmed": "on"},
    )
    html = response.content.decode("utf-8")

    assert response.status_code == 200
    assert "O item mudou em outra operação" in html
    assert 'name="lock_version" value="2"' in html
    assert 'name="confirmed"' in html
    assert 'name="confirmed" checked' not in html
    discipline.refresh_from_db()
    assert discipline.status == TaxonomyStatus.ACTIVE


@pytest.mark.django_db
def test_ct097_user_html_is_escaped_in_lists_context_and_attributes() -> None:
    workspace = _local_workspace()
    payload = '<script>alert("x")</script>'
    discipline = create_discipline(workspace_id=workspace.id, name=payload)

    html = Client().get(reverse("taxonomy:index")).content.decode("utf-8")

    assert payload not in html
    assert "&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;" in html
    assert Discipline.objects.get(pk=discipline.id).name == payload


@pytest.mark.django_db
def test_ct096_mutations_keep_csrf_and_http_method_protection() -> None:
    workspace = _local_workspace()
    discipline = create_discipline(workspace_id=workspace.id, name="Biologia")
    protected_client = Client(enforce_csrf_checks=True)
    urls = [
        reverse("taxonomy:discipline-create"),
        reverse("taxonomy:discipline-edit", args=[discipline.id]),
        reverse("taxonomy:discipline-archive", args=[discipline.id]),
    ]

    for url in urls:
        get_response = Client().get(url)
        assert 'name="csrfmiddlewaretoken"' in get_response.content.decode("utf-8")
        assert protected_client.post(url, {"name": "Ataque", "lock_version": 1}).status_code == 403
        assert Client().put(url, data={"name": "Ataque"}).status_code == 405

    discipline.refresh_from_db()
    assert discipline.name == "Biologia"
    assert discipline.status == TaxonomyStatus.ACTIVE


def test_taxonomy_templates_are_keyboard_semantic_and_responsive() -> None:
    templates = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (PROJECT_ROOT / "src" / "templates" / "taxonomy").glob("*.html")
    )
    css = (PROJECT_ROOT / "src" / "static" / "css" / "app.css").read_text(encoding="utf-8")

    assert not re.search(r'tabindex="[1-9]', templates)
    assert "{% csrf_token %}" in templates
    assert '<button type="submit"' in templates
    assert 'type="submit" name="action" value="cancel"' in templates
    assert 'role="alert"' in templates
    assert 'aria-describedby="archive-impact confirmed-errors"' not in templates
    assert "flex-wrap: wrap" in css
    assert "overflow-wrap: anywhere" in css
    assert "width: min(100%, 32rem)" in css
    assert "@media (min-width: 48rem)" in css
