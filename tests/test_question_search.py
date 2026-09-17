"""CTs da Etapa 7 para listagem, busca e filtros de questões."""

import re
import uuid
from datetime import UTC, date, datetime

import pytest
from django.test import Client
from django.urls import reverse

from modules.accounts.models import User, Workspace
from modules.attempts.models import Attempt, AttemptStatus, AttemptType
from modules.errors.models import ErrorCategory, ErrorClassification
from modules.questions.models import Question, QuestionStatus
from modules.questions.services import archive_question, create_active, create_draft
from modules.reviews.models import Review, ReviewCycleState, ReviewState
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


def _initial_attempt(*, workspace: Workspace, question: Question, correct: bool) -> Attempt:
    revision = question.revisions.get(is_current=True)
    return Attempt.objects.create(
        workspace=workspace,
        question=question,
        question_revision=revision,
        attempt_type=AttemptType.INITIAL,
        selected_alternative=revision.alternatives.get(position=1 if correct else 2),
        is_correct=correct,
        occurred_at=datetime(2026, 9, 15, 15, tzinfo=UTC),
        timezone_name=workspace.timezone_name,
        local_date=date(2026, 9, 15),
        status=AttemptStatus.VALID,
        idempotency_key=uuid.uuid4(),
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


@pytest.mark.django_db
def test_s4_learning_filters_combine_and_keep_workspace_isolation() -> None:
    workspace = _workspace()
    discipline, subject, _ = _taxonomy(workspace)
    correct_question = _active_question(
        workspace=workspace, discipline=discipline, subject=subject, stem="Correta"
    )
    incorrect_question = _active_question(
        workspace=workspace, discipline=discipline, subject=subject, stem="Incorreta"
    )
    correct_attempt = _initial_attempt(workspace=workspace, question=correct_question, correct=True)
    incorrect_attempt = _initial_attempt(
        workspace=workspace, question=incorrect_question, correct=False
    )
    category = ErrorCategory.objects.get(workspace=workspace, code="CONCEPTUAL")
    ErrorClassification.objects.create(
        workspace=workspace, attempt=incorrect_attempt, category=category
    )
    owner = User.objects.create_user(email="s4-foreign@example.test")
    foreign = Workspace.objects.create(owner_user=owner, name="Foreign", timezone_name="UTC")
    foreign_discipline, foreign_subject, _ = _taxonomy(foreign, " foreign")
    foreign_question = _active_question(
        workspace=foreign, discipline=foreign_discipline, subject=foreign_subject, stem="Foreign"
    )
    _initial_attempt(workspace=foreign, question=foreign_question, correct=False)

    client = Client()
    correct = client.get(reverse("questions:list"), {"initial_result": "correct"})
    combined = client.get(
        reverse("questions:list"),
        {"query": "Incorreta", "initial_result": "incorrect", "error_category": str(category.id)},
    )
    residue = client.get(reverse("questions:list"), {"error_category": "unclassified"})

    assert str(correct_question.id) in correct.content.decode("utf-8")
    assert str(incorrect_question.id) not in correct.content.decode("utf-8")
    assert str(incorrect_question.id) in combined.content.decode("utf-8")
    assert str(correct_attempt.question_id) not in combined.content.decode("utf-8")
    assert str(foreign_question.id) not in combined.content.decode("utf-8")
    assert "Nenhuma questão encontrada" in residue.content.decode("utf-8")


@pytest.mark.django_db
def test_s4_review_filter_drilldown_reconciles_pending_review_question() -> None:
    workspace = _workspace()
    discipline, subject, _ = _taxonomy(workspace)
    question = _active_question(
        workspace=workspace, discipline=discipline, subject=subject, stem="Devida"
    )
    review = Review.objects.get(
        workspace=workspace,
        question=question,
        state=ReviewState.PENDING,
        review_cycle__state=ReviewCycleState.ACTIVE,
    )
    Review.objects.filter(pk=review.id).update(current_due_date=date.today())

    response = Client().get(reverse("questions:list"), {"review_status": "DUE"})

    assert response.status_code == 200
    assert str(question.id) in response.content.decode("utf-8")
    assert response.context["result"].total == 1


@pytest.mark.django_db
def test_s4_detail_returns_to_consultation_and_links_existing_timeline() -> None:
    workspace = _workspace()
    discipline, subject, _ = _taxonomy(workspace)
    question = _active_question(workspace=workspace, discipline=discipline, subject=subject)

    response = Client().get(
        reverse("questions:detail", args=[question.id]),
        {"return_to": "/questions/?query=Enunciado&page=1"},
    )
    html = response.content.decode("utf-8")

    assert 'href="/questions/?query=Enunciado&amp;page=1"' in html
    assert reverse("reviews:timeline", args=[question.id]) in html


@pytest.mark.django_db
def test_s4_pagination_preserves_valid_search_and_filter_parameters() -> None:
    workspace = _workspace()
    discipline, subject, _ = _taxonomy(workspace)
    for position in range(11):
        question = _active_question(
            workspace=workspace,
            discipline=discipline,
            subject=subject,
            stem=f"Paginação {position}",
        )
        _initial_attempt(workspace=workspace, question=question, correct=True)

    response = Client().get(
        reverse("questions:list"),
        {"query": "Paginação", "initial_result": "correct", "page": "1", "ignored": "x"},
    )
    html = response.content.decode("utf-8")

    assert "page=2" in html
    assert "query=Pagina%C3%A7%C3%A3o" in html
    assert "initial_result=correct" in html
    assert "ignored" not in html
    assert response.context["return_to"] == (
        "/questions/?query=Pagina%C3%A7%C3%A3o&initial_result=correct&page=1"
    )


@pytest.mark.django_db
def test_s8_list_detail_link_preserves_safe_consultation_context() -> None:
    workspace = _workspace()
    discipline, subject, _ = _taxonomy(workspace)
    question = _active_question(
        workspace=workspace,
        discipline=discipline,
        subject=subject,
        stem="Retorno preservado",
    )

    response = Client().get(reverse("questions:list"), {"query": "Retorno", "page": "1"})
    html = response.content.decode("utf-8")

    assert response.context["return_to"] == "/questions/?query=Retorno&page=1"
    assert (
        f'href="/questions/{question.id}/?return_to=/questions/%3Fquery%3DRetorno%26page%3D1"'
        in html
    )


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
