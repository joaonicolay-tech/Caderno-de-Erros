"""CTs da Etapa 5 para cadastro rápido e ativação de rascunho."""

import re
from pathlib import Path

import pytest
from django.test import Client
from django.urls import reverse

from modules.accounts.models import User, Workspace
from modules.questions.models import (
    Board,
    Question,
    QuestionDifficulty,
    QuestionOrigin,
    QuestionStatus,
    Source,
    SourceType,
)
from modules.questions.services import (
    QuestionOriginInput,
    archive_question,
    create_active,
    create_draft,
    create_or_reuse_source,
    set_question_origin,
    update_question_metadata,
)
from modules.taxonomy.models import Discipline, Subject, Subsubject
from modules.taxonomy.services import create_discipline, create_subject, create_subsubject
from shared.application.bootstrap import bootstrap_local_workspace

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _workspace() -> Workspace:
    return bootstrap_local_workspace(timezone_id="America/Sao_Paulo").workspace


def _taxonomy(workspace: Workspace) -> tuple[Discipline, Subject, Subsubject]:
    discipline = create_discipline(workspace_id=workspace.id, name="Matemática")
    subject = create_subject(workspace_id=workspace.id, discipline_id=discipline.id, name="Álgebra")
    subsubject = create_subsubject(
        workspace_id=workspace.id,
        subject_id=subject.id,
        name="Equações",
    )
    return discipline, subject, subsubject


def _payload(
    *, discipline_id: object | None = None, subject_id: object | None = None
) -> dict[str, str]:
    return {
        "draft_title": "Questão de teste",
        "discipline": str(discipline_id or ""),
        "subject": str(subject_id or ""),
        "subsubject": "",
        "difficulty": "MEDIUM",
        "stem": "Quanto é 2 + 2?",
        "alternative_1": "3",
        "alternative_2": "4",
        "alternative_3": "",
        "alternative_4": "",
        "correct_alternative": "2",
        "explanation": "A soma é quatro.",
        "trap_note": "Não confunda com multiplicação.",
        "notes": "Unicode: ação.",
        "source": "",
        "source_name": "",
        "source_type": "",
        "source_url": "",
        "source_notes": "",
        "exam": "",
        "exam_name": "",
        "exam_year": "",
        "board": "",
        "board_name": "",
        "board_website_url": "",
        "reference_year": "",
        "reference_text": "",
    }


@pytest.mark.django_db
def test_ct011_ct007_direct_active_creation_keeps_order_answer_and_feedback() -> None:
    workspace = _workspace()
    discipline, subject, _ = _taxonomy(workspace)
    payload = _payload(discipline_id=discipline.id, subject_id=subject.id)

    response = Client().post(
        reverse("questions:quick-entry"), {**payload, "action": "activate"}, follow=True
    )

    question = Question.objects.get(workspace=workspace)
    revision = question.revisions.get(is_current=True)
    alternatives = list(revision.alternatives.order_by("position"))
    assert response.redirect_chain == [
        (f"{reverse('questions:detail', args=[question.id])}?result=created", 302)
    ]
    assert "Questão ativa criada com sucesso" in response.content.decode("utf-8")
    assert question.status == QuestionStatus.ACTIVE
    assert [item.position for item in alternatives] == [1, 2]
    assert [item.label for item in alternatives] == ["A", "B"]
    assert revision.correct_alternative_id == alternatives[1].id


@pytest.mark.django_db
def test_ct005_ct006_draft_is_recoverable_and_only_activation_requires_minimums() -> None:
    workspace = _workspace()
    client = Client()

    saved = client.post(
        reverse("questions:quick-entry"),
        {**_payload(), "draft_title": "Rascunho recuperável", "action": "draft"},
    )
    question = Question.objects.get(workspace=workspace)
    activate_url = reverse("questions:draft-activate", args=[question.id])
    recovery = client.get(saved.headers["Location"])
    invalid = client.post(activate_url, {**_payload(), "lock_version": question.lock_version})

    assert question.status == QuestionStatus.DRAFT
    assert saved.status_code == 302
    assert saved.headers["Location"] == f"{activate_url}?result=draft"
    assert "Rascunho recuperável" in recovery.content.decode("utf-8")
    assert invalid.status_code == 200
    assert "Informe disciplina e assunto" in invalid.content.decode("utf-8")
    assert Question.objects.filter(workspace=workspace).count() == 1


@pytest.mark.django_db
def test_ct005_draft_can_be_completed_and_activated_without_duplicate() -> None:
    workspace = _workspace()
    discipline, subject, _ = _taxonomy(workspace)
    client = Client()
    client.post(reverse("questions:quick-entry"), {**_payload(), "action": "draft"})
    question = Question.objects.get(workspace=workspace)
    activate_url = reverse("questions:draft-activate", args=[question.id])

    response = client.post(
        activate_url,
        {
            **_payload(discipline_id=discipline.id, subject_id=subject.id),
            "lock_version": question.lock_version,
            "action": "activate",
        },
        follow=True,
    )
    question.refresh_from_db()

    assert question.status == QuestionStatus.ACTIVE
    assert Question.objects.filter(workspace=workspace).count() == 1
    assert question.revisions.filter(is_current=True).count() == 1
    assert "Questão ativa criada com sucesso" in response.content.decode("utf-8")


@pytest.mark.django_db
def test_ct094_ct012_invalid_activation_preserves_unicode_input_without_creating() -> None:
    workspace = _workspace()
    discipline, subject, _ = _taxonomy(workspace)
    payload = _payload(discipline_id=discipline.id, subject_id=subject.id)
    payload.update(alternative_2="  três  ", correct_alternative="")

    response = Client().post(reverse("questions:quick-entry"), {**payload, "action": "activate"})
    html = response.content.decode("utf-8")

    assert response.status_code == 200
    assert "exatamente uma alternativa correta" in html
    assert 'value="  três  "' in html
    assert 'aria-invalid="true"' in html
    assert Question.objects.filter(workspace=workspace).count() == 0


@pytest.mark.django_db
def test_ct138_origin_is_optional_created_reused_and_rolled_back_with_question() -> None:
    workspace = _workspace()
    discipline, subject, _ = _taxonomy(workspace)
    client = Client()
    payload = _payload(discipline_id=discipline.id, subject_id=subject.id)
    payload.update(source_name="Manual de Álgebra", source_type="BOOK", board_name="Banca Única")

    first = client.post(reverse("questions:quick-entry"), {**payload, "action": "activate"})
    second = client.post(reverse("questions:quick-entry"), {**payload, "action": "activate"})
    invalid = client.post(
        reverse("questions:quick-entry"),
        {
            **payload,
            "source_name": "Será revertida",
            "exam_name": "Prova inválida",
            "exam_year": "1899",
            "action": "activate",
        },
    )

    assert first.status_code == 302
    assert second.status_code == 302
    assert Question.objects.filter(workspace=workspace).count() == 2
    assert Source.objects.filter(workspace=workspace, name="Manual de Álgebra").count() == 1
    assert Board.objects.filter(workspace=workspace, name="Banca Única").count() == 1
    assert QuestionOrigin.objects.filter(workspace=workspace).count() == 2
    assert invalid.status_code == 200
    assert not Source.objects.filter(workspace=workspace, name="Será revertida").exists()
    assert Question.objects.filter(workspace=workspace).count() == 2


@pytest.mark.django_db
def test_ct095_foreign_ids_are_rejected_without_exposing_or_writing() -> None:
    local = _workspace()
    discipline, subject, _ = _taxonomy(local)
    owner = User.objects.create_user(email="foreign-question@example.test")
    foreign = Workspace.objects.create(owner_user=owner, name="Estrangeiro", timezone_name="UTC")
    foreign_discipline, foreign_subject, _ = _taxonomy(foreign)
    payload = _payload(discipline_id=foreign_discipline.id, subject_id=foreign_subject.id)

    response = Client().post(reverse("questions:quick-entry"), {**payload, "action": "activate"})
    foreign_draft = Question.objects.create(workspace=foreign, draft_title="Sigiloso")
    read = Client().get(reverse("questions:draft-activate", args=[foreign_draft.id]))

    assert response.status_code == 200
    assert 'aria-invalid="true"' in response.content.decode("utf-8")
    assert read.status_code == 404
    assert "Sigiloso" not in read.content.decode("utf-8")
    assert not Question.objects.filter(workspace=local).exists()
    assert discipline.workspace_id == local.id and subject.workspace_id == local.id


@pytest.mark.django_db
def test_ct096_csrf_and_ct097_escaping_are_preserved() -> None:
    workspace = _workspace()
    payload = '<script>alert("x")</script>'
    client = Client()
    saved = client.post(
        reverse("questions:quick-entry"),
        {**_payload(), "draft_title": payload, "action": "draft"},
    )
    question = Question.objects.get(workspace=workspace)
    html = client.get(saved.headers["Location"]).content.decode("utf-8")
    protected = Client(enforce_csrf_checks=True)

    assert payload not in html
    assert "&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;" in html
    assert protected.post(reverse("questions:quick-entry"), {"action": "draft"}).status_code == 403
    assert Client().put(reverse("questions:draft-activate", args=[question.id])).status_code == 405


@pytest.mark.django_db
def test_concurrent_draft_activation_preserves_input_and_current_state() -> None:
    workspace = _workspace()
    discipline, subject, _ = _taxonomy(workspace)
    question = Question.objects.create(workspace=workspace, draft_title="Concorrente")
    stale = question.lock_version
    update_question_metadata(
        workspace_id=workspace.id,
        question_id=question.id,
        expected_lock_version=stale,
        discipline_id=None,
        subject_id=None,
        draft_title="Atualizado em outra aba",
    )

    response = Client().post(
        reverse("questions:draft-activate", args=[question.id]),
        {
            **_payload(discipline_id=discipline.id, subject_id=subject.id),
            "lock_version": stale,
            "action": "activate",
        },
    )
    html = response.content.decode("utf-8")
    question.refresh_from_db()

    assert response.status_code == 200
    assert "A questão mudou" in html
    assert 'value="Quanto é 2 + 2?"' not in html  # textarea preserves content, not value attr
    assert "Quanto é 2 + 2?" in html
    assert 'name="lock_version" value="2"' in html
    assert question.status == QuestionStatus.DRAFT
    assert question.revisions.count() == 0


@pytest.mark.django_db
def test_ct139_detail_is_faithful_for_draft_active_and_archived_without_future_data() -> None:
    workspace = _workspace()
    discipline, subject, subsubject = _taxonomy(workspace)
    draft = create_draft(
        workspace_id=workspace.id,
        draft_title='<script>alert("rascunho")</script>',
    )
    active = create_active(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        subject_id=subject.id,
        subsubject_id=subsubject.id,
        difficulty=QuestionDifficulty.HARD,
        stem="Enunciado ativo",
        alternatives=["Errada", "Correta"],
        correct_alternative_position=2,
        explanation="Explicação persistida",
    )
    archived = create_active(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        subject_id=subject.id,
        stem="Enunciado arquivado",
        alternatives=["A", "B"],
        correct_alternative_position=1,
    )
    archive_question(
        workspace_id=workspace.id,
        question_id=archived.id,
        expected_lock_version=archived.lock_version,
    )
    client = Client()

    draft_html = client.get(reverse("questions:detail", args=[draft.id])).content.decode("utf-8")
    active_html = client.get(reverse("questions:detail", args=[active.id])).content.decode("utf-8")
    archived_html = client.get(reverse("questions:detail", args=[archived.id])).content.decode(
        "utf-8"
    )

    assert "Estado: Rascunho" in draft_html
    assert "Conteúdo ainda não informado" in draft_html
    assert '<script>alert("rascunho")</script>' not in draft_html
    assert "&lt;script&gt;alert(&quot;rascunho&quot;)&lt;/script&gt;" in draft_html
    assert "Estado: Ativa" in active_html
    assert "Enunciado ativo" in active_html
    assert "Explicação persistida" in active_html
    assert "Difícil" in active_html
    assert "Estado: Arquivada" in archived_html
    assert "Enunciado arquivado" in archived_html
    for html in (draft_html, active_html, archived_html):
        lowered = html.lower()
        assert "tentativa" not in lowered
        assert "ciclo" not in lowered
        assert "fila" not in lowered
        assert "métrica" not in lowered
        assert "aprendizagem" not in lowered


@pytest.mark.django_db
def test_ct095_detail_edit_and_archive_never_expose_foreign_workspace_question() -> None:
    _workspace()
    owner = User.objects.create_user(email="foreign-detail@example.test")
    foreign = Workspace.objects.create(owner_user=owner, name="Estrangeiro", timezone_name="UTC")
    discipline, subject, _ = _taxonomy(foreign)
    question = create_active(
        workspace_id=foreign.id,
        discipline_id=discipline.id,
        subject_id=subject.id,
        stem="Conteúdo sigiloso",
        alternatives=["A", "B"],
        correct_alternative_position=1,
    )

    for route in ("questions:detail", "questions:edit", "questions:archive"):
        response = Client().get(reverse(route, args=[question.id]))
        assert response.status_code == 404
        assert "Conteúdo sigiloso" not in response.content.decode("utf-8")


@pytest.mark.django_db
def test_ct008_edit_view_versions_content_preserves_previous_and_updates_origin() -> None:
    workspace = _workspace()
    discipline, subject, _ = _taxonomy(workspace)
    question = create_active(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        subject_id=subject.id,
        stem="Versão inicial",
        alternatives=["Um", "Dois"],
        correct_alternative_position=1,
    )
    first = question.revisions.get(is_current=True)
    payload = _payload(discipline_id=discipline.id, subject_id=subject.id)
    payload.update(
        lock_version=str(question.lock_version),
        stem="Versão enriquecida",
        alternative_1="Três",
        alternative_2="Quatro",
        correct_alternative="2",
        source_name="Livro <seguro>",
        source_type=SourceType.BOOK,
    )

    response = Client().post(reverse("questions:edit", args=[question.id]), payload, follow=True)
    question.refresh_from_db()
    first.refresh_from_db()
    current = question.revisions.get(is_current=True)
    html = response.content.decode("utf-8")

    assert response.redirect_chain == [
        (f"{reverse('questions:detail', args=[question.id])}?result=edited", 302)
    ]
    assert question.lock_version == 2
    assert question.revisions.count() == 2
    assert question.revisions.filter(is_current=True).count() == 1
    assert first.is_current is False and first.stem == "Versão inicial"
    assert list(first.alternatives.order_by("position").values_list("text", flat=True)) == [
        "Um",
        "Dois",
    ]
    assert current.stem == "Versão enriquecida"
    assert current.correct_alternative is not None
    assert current.correct_alternative.text == "Quatro"
    assert question.origin.source is not None
    assert question.origin.source.name == "Livro <seguro>"
    assert "Versão inicial" in html and "Versão enriquecida" in html
    assert "Livro &lt;seguro&gt;" in html


@pytest.mark.django_db
def test_edit_view_validation_and_service_failure_preserve_input_and_rollback() -> None:
    workspace = _workspace()
    discipline, subject, _ = _taxonomy(workspace)
    question = create_active(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        subject_id=subject.id,
        stem="Original",
        alternatives=["A", "B"],
        correct_alternative_position=1,
    )
    payload = _payload(discipline_id=discipline.id, subject_id=subject.id)
    payload.update(
        lock_version=str(question.lock_version),
        stem="Entrada preservada ç",
        source_name="Fonte revertida",
        source_type=SourceType.BOOK,
        exam_name="Prova futura",
        exam_year="9999",
    )

    response = Client().post(reverse("questions:edit", args=[question.id]), payload)
    html = response.content.decode("utf-8")
    question.refresh_from_db()

    assert response.status_code == 200
    assert "Entrada preservada ç" in html
    assert 'aria-invalid="true"' in html
    assert "autofocus" in html
    assert question.lock_version == 1
    assert question.revisions.count() == 1
    assert question.revisions.get().stem == "Original"
    assert not Source.objects.filter(workspace=workspace, name="Fonte revertida").exists()
    assert not QuestionOrigin.objects.filter(question=question).exists()


@pytest.mark.django_db
def test_edit_view_stale_lock_preserves_input_and_returns_current_lock() -> None:
    workspace = _workspace()
    discipline, subject, _ = _taxonomy(workspace)
    question = create_active(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        subject_id=subject.id,
        stem="Original concorrente",
        alternatives=["A", "B"],
        correct_alternative_position=1,
    )
    stale = question.lock_version
    update_question_metadata(
        workspace_id=workspace.id,
        question_id=question.id,
        expected_lock_version=stale,
        discipline_id=discipline.id,
        subject_id=subject.id,
        difficulty=QuestionDifficulty.EASY,
    )
    payload = _payload(discipline_id=discipline.id, subject_id=subject.id)
    payload.update(lock_version=str(stale), stem="Minha edição concorrente")

    response = Client().post(reverse("questions:edit", args=[question.id]), payload)
    html = response.content.decode("utf-8")
    question.refresh_from_db()

    assert response.status_code == 200
    assert "A questão mudou" in html
    assert "Minha edição concorrente" in html
    assert 'name="lock_version" value="2"' in html
    assert question.revisions.count() == 1
    assert question.revisions.get().stem == "Original concorrente"


@pytest.mark.django_db
def test_ct010_archive_requires_confirmation_preserves_data_and_disables_mutations() -> None:
    workspace = _workspace()
    discipline, subject, _ = _taxonomy(workspace)
    question = create_active(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        subject_id=subject.id,
        stem="Questão para arquivar",
        alternatives=["A", "B"],
        correct_alternative_position=1,
    )
    source = create_or_reuse_source(
        workspace_id=workspace.id,
        source_type=SourceType.WEBSITE,
        name="Portal",
    )
    set_question_origin(
        workspace_id=workspace.id,
        question_id=question.id,
        expected_lock_version=1,
        origin=QuestionOriginInput(source_id=source.id),
    )
    question.refresh_from_db()
    archive_url = reverse("questions:archive", args=[question.id])
    client = Client()

    confirmation = client.get(archive_url)
    missing = client.post(archive_url, {"lock_version": question.lock_version})
    protected = Client(enforce_csrf_checks=True).post(
        archive_url,
        {"lock_version": question.lock_version, "confirm": "on"},
    )
    question.refresh_from_db()

    assert confirmation.status_code == 200
    assert "Esta versão não oferece reativação" in confirmation.content.decode("utf-8")
    assert "Confirme o arquivamento" in missing.content.decode("utf-8")
    assert "autofocus" in missing.content.decode("utf-8")
    assert protected.status_code == 403
    assert question.status == QuestionStatus.ACTIVE
    assert client.put(archive_url).status_code == 405
    assert client.put(reverse("questions:edit", args=[question.id])).status_code == 405
    assert client.post(reverse("questions:detail", args=[question.id])).status_code == 405

    stale = question.lock_version
    update_question_metadata(
        workspace_id=workspace.id,
        question_id=question.id,
        expected_lock_version=stale,
        discipline_id=discipline.id,
        subject_id=subject.id,
        difficulty=QuestionDifficulty.MEDIUM,
    )
    conflict = client.post(
        archive_url,
        {"lock_version": stale, "confirm": "on"},
    )
    question.refresh_from_db()
    conflict_html = conflict.content.decode("utf-8")
    assert "A questão mudou" in conflict_html
    assert f'name="lock_version" value="{question.lock_version}"' in conflict_html
    assert question.status == QuestionStatus.ACTIVE

    archived = client.post(
        archive_url,
        {"lock_version": question.lock_version, "confirm": "on"},
        follow=True,
    )
    question.refresh_from_db()
    html = archived.content.decode("utf-8")

    assert question.status == QuestionStatus.ARCHIVED
    assert question.archived_at is not None
    assert question.revisions.count() == 1
    assert QuestionOrigin.objects.filter(question=question, source=source).exists()
    assert "Questão arquivada" in html
    assert "Editar questão" not in html and "Arquivar questão" not in html
    assert client.get(reverse("questions:edit", args=[question.id])).status_code == 404
    assert client.get(archive_url).status_code == 404


@pytest.mark.django_db
def test_draft_detail_and_edit_support_partial_versioned_content() -> None:
    workspace = _workspace()
    question = create_draft(workspace_id=workspace.id, draft_title="Rascunho parcial")
    payload = _payload()
    payload.update(
        lock_version=str(question.lock_version),
        draft_title="Rascunho parcial",
        stem="Somente um enunciado por enquanto",
        alternative_1="",
        alternative_2="",
        correct_alternative="",
    )

    response = Client().post(reverse("questions:edit", args=[question.id]), payload, follow=True)
    question.refresh_from_db()

    assert response.status_code == 200
    assert question.status == QuestionStatus.DRAFT
    assert question.revisions.count() == 1
    assert question.revisions.get(is_current=True).stem == "Somente um enunciado por enquanto"
    assert "Conteúdo atual" in response.content.decode("utf-8")


def test_ct142_templates_remain_semantic_keyboard_accessible_and_responsive() -> None:
    template = (PROJECT_ROOT / "src" / "templates" / "questions" / "quick_entry.html").read_text(
        encoding="utf-8"
    )
    detail = (PROJECT_ROOT / "src" / "templates" / "questions" / "detail.html").read_text(
        encoding="utf-8"
    )
    archive = (PROJECT_ROOT / "src" / "templates" / "questions" / "archive_confirm.html").read_text(
        encoding="utf-8"
    )
    css = (PROJECT_ROOT / "src" / "static" / "css" / "app.css").read_text(encoding="utf-8")

    assert "{% csrf_token %}" in template
    assert "<fieldset" in template and "<legend>" in template
    assert 'role="alert"' in template
    assert not re.search(r'tabindex="[1-9]', template)
    assert 'name="action" value="draft"' in template
    assert 'name="action" value="activate"' in template
    assert "textarea" in css
    assert "flex-wrap: wrap" in css
    assert "<article" in detail and "<section" in detail and "<dl" in detail
    assert 'aria-label="Ações da questão"' in detail
    assert "{% csrf_token %}" in archive
    assert '<label for="{{ form.confirm.id_for_label }}">' in archive
    assert 'role="alert"' in archive
    assert not re.search(r'tabindex="[1-9]', detail + archive)
    assert "overflow-wrap: anywhere" in css
    assert 'class="visually-hidden"' in template
    assert "obrigat" in template
