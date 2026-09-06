"""CTs da Etapa 7 para listagem, busca e filtros de questões."""

import re
from datetime import UTC, datetime

import pytest
from django.test import Client
from django.urls import reverse

from modules.accounts.models import User, Workspace
from modules.questions.models import Question, QuestionStatus
from modules.questions.services import archive_question, create_active, create_draft
from modules.search.selectors import list_questions, paginate_questions
from modules.taxonomy.models import Discipline, Subject, Subsubject
from modules.taxonomy.services import create_discipline, create_subject, create_subsubject
from shared.application.bootstrap import bootstrap_local_workspace

PROJECT_ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]


def _workspace() -> Workspace:
    return bootstrap_local_workspace(timezone_id="America/Sao_Paulo").workspace


def _taxonomy(workspace: Workspace, suffix: str = "") -> tuple[Discipline, Subject, Subsubject]:
    discipline = create_discipline(workspace_id=workspace.id, name=f"Matemática{suffix}")
    subject = create_subject(
        workspace_id=workspace.id, discipline_id=discipline.id, name=f"Álgebra{suffix}"
    )
    subsubject = create_subsubject(
        workspace_id=workspace.id,
        subject_id=subject.id,
        name=f"Equações{suffix}",
    )
    return discipline, subject, subsubject


def _active_question(
    *,
    workspace: Workspace,
    discipline: Discipline,
    subject: Subject,
    subsubject: Subsubject | None = None,
    stem: str = "Enunciado",
    explanation: str = "",
) -> Question:
    return create_active(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        subject_id=subject.id,
        subsubject_id=subsubject.id if subsubject else None,
        draft_title=f"Título {stem}",
        stem=stem,
        alternatives=["A", "B"],
        correct_alternative_position=1,
        explanation=explanation,
    )


@pytest.mark.django_db
def test_ct005_ct085_list_defaults_to_active_and_searches_text_only_in_workspace() -> None:
    workspace = _workspace()
    discipline, subject, subsubject = _taxonomy(workspace)
    active = _active_question(
        workspace=workspace,
        discipline=discipline,
        subject=subject,
        subsubject=subsubject,
        stem="Equação com acentuação",
        explanation="Explicação de raízes.",
    )
    draft = create_draft(workspace_id=workspace.id, draft_title="Rascunho recuperável")
    archived = _active_question(
        workspace=workspace,
        discipline=discipline,
        subject=subject,
        stem="Arquivada",
    )
    archive_question(
        workspace_id=workspace.id,
        question_id=archived.id,
        expected_lock_version=archived.lock_version,
    )
    owner = User.objects.create_user(email="search-foreign@example.test")
    foreign = Workspace.objects.create(owner_user=owner, name="Estrangeiro", timezone_name="UTC")
    foreign_discipline, foreign_subject, _ = _taxonomy(foreign, " estrangeira")
    _active_question(
        workspace=foreign,
        discipline=foreign_discipline,
        subject=foreign_subject,
        stem="Equação confidencial",
    )

    assert list(list_questions(workspace_id=workspace.id).values_list("id", flat=True)) == [
        active.id
    ]
    assert list(
        list_questions(workspace_id=workspace.id, status=QuestionStatus.DRAFT).values_list(
            "id", flat=True
        )
    ) == [draft.id]
    assert list(
        list_questions(
            workspace_id=workspace.id,
            query="explicação de raízes",
        ).values_list("id", flat=True)
    ) == [active.id]
    default_list = Client().get(reverse("questions:list"))
    draft_list = Client().get(reverse("questions:list"), {"status": QuestionStatus.DRAFT})

    assert 'option value="ACTIVE" selected' in default_list.content.decode("utf-8")
    assert str(active.id) in default_list.content.decode("utf-8")
    assert str(draft.id) in draft_list.content.decode("utf-8")


@pytest.mark.django_db
def test_ct085_list_view_has_visible_filters_hierarchical_validation_and_empty_state() -> None:
    workspace = _workspace()
    discipline, subject, subsubject = _taxonomy(workspace)
    other_discipline, other_subject, _ = _taxonomy(workspace, " complementar")
    matched = _active_question(
        workspace=workspace,
        discipline=discipline,
        subject=subject,
        subsubject=subsubject,
        stem="Busca filtrada",
    )
    _active_question(
        workspace=workspace,
        discipline=other_discipline,
        subject=other_subject,
        stem="Outra questão",
    )
    client = Client()

    response = client.get(
        reverse("questions:list"),
        {
            "query": "Busca",
            "discipline": str(discipline.id),
            "subject": str(subject.id),
            "subsubject": str(subsubject.id),
        },
    )
    html = response.content.decode("utf-8")
    invalid = client.get(
        reverse("questions:list"),
        {"discipline": str(discipline.id), "subject": str(other_subject.id)},
    )
    empty = client.get(reverse("questions:list"), {"query": "inexistente"})

    assert response.status_code == 200
    assert str(matched.id) in html
    assert "Filtros ativos" in html
    assert "Total: 1 questão encontrada." in html
    assert invalid.status_code == 200
    assert "subject" in invalid.context["form"].errors
    assert "Nenhuma questão encontrada" in empty.content.decode("utf-8")


@pytest.mark.django_db
def test_ct086_pagination_has_stable_tiebreaker_without_omission_and_recovers_invalid_page() -> (
    None
):
    workspace = _workspace()
    discipline, subject, _ = _taxonomy(workspace)
    questions = [
        _active_question(
            workspace=workspace,
            discipline=discipline,
            subject=subject,
            stem=f"Questão {position}",
        )
        for position in range(12)
    ]
    timestamp = datetime(2026, 9, 6, 12, 0, tzinfo=UTC)
    Question.objects.filter(id__in=[question.id for question in questions]).update(
        updated_at=timestamp
    )
    queryset = list_questions(workspace_id=workspace.id)
    first = paginate_questions(questions=queryset, requested_page="1")
    second = paginate_questions(questions=queryset, requested_page="2")
    expected_ids = list(queryset.values_list("id", flat=True))
    actual_ids = [
        item.question.id for item in list(first.page.object_list) + list(second.page.object_list)
    ]
    invalid = Client().get(reverse("questions:list"), {"page": "99"})

    assert actual_ids == expected_ids
    assert len(set(actual_ids)) == 12
    assert first.page.number == 1 and second.page.number == 2
    assert "página solicitada não existe" in invalid.content.decode("utf-8")


@pytest.mark.django_db
def test_ct095_list_rejects_foreign_filters_without_revealing_foreign_content() -> None:
    _workspace()
    owner = User.objects.create_user(email="foreign-filter@example.test")
    foreign = Workspace.objects.create(owner_user=owner, name="Estrangeiro", timezone_name="UTC")
    discipline, subject, _ = _taxonomy(foreign)
    question = _active_question(
        workspace=foreign,
        discipline=discipline,
        subject=subject,
        stem="Conteúdo sigiloso",
    )

    response = Client().get(reverse("questions:list"), {"discipline": str(discipline.id)})
    html = response.content.decode("utf-8")

    assert response.status_code == 200
    assert str(question.id) not in html
    assert "Conteúdo sigiloso" not in html
    assert "discipline" in response.context["form"].errors


@pytest.mark.django_db
def test_ct097_list_escapes_rendered_content() -> None:
    workspace = _workspace()
    discipline, subject, _ = _taxonomy(workspace)
    payload = '<script>alert("x")</script>'
    _active_question(
        workspace=workspace,
        discipline=discipline,
        subject=subject,
        stem=payload,
    )

    html = Client().get(reverse("questions:list")).content.decode("utf-8")

    assert payload not in html
    assert "&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;" in html


def test_ct142_list_template_is_semantic_keyboard_accessible_and_responsive() -> None:
    template = (PROJECT_ROOT / "src" / "templates" / "questions" / "list.html").read_text(
        encoding="utf-8"
    )
    css = (PROJECT_ROOT / "src" / "static" / "css" / "app.css").read_text(encoding="utf-8")

    assert '<form method="get" aria-label="Buscar e filtrar questões">' in template
    assert "<fieldset" in template and "<legend>" in template
    assert 'role="status"' in template
    assert 'aria-label="Paginas de questões"' in template
    assert not re.search(r'tabindex="[1-9]', template)
    assert ".filter-grid" in css and "flex-wrap: wrap" in css
