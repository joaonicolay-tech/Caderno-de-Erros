"""Projeções paginadas de leitura do catálogo de questões."""

import uuid
from dataclasses import dataclass
from typing import Any, cast

from django.core.paginator import EmptyPage, Page, Paginator
from django.db.models import Prefetch, Q, QuerySet

from modules.analytics.selectors import eligible_reviews
from modules.attempts.models import AttemptStatus, AttemptType
from modules.questions.models import Question, QuestionRevision, QuestionStatus
from modules.reviews.policies import ReviewTemporalStatus

PAGE_SIZE = 10


@dataclass(frozen=True)
class QuestionListItem:
    """Dados exclusivamente necessários para uma linha de catálogo."""

    question: Question
    stem: str
    explanation: str


@dataclass(frozen=True)
class QuestionListPage:
    """Página de resultados e informação de recuperação da paginação."""

    page: Page[QuestionListItem]
    total: int
    page_was_adjusted: bool


def list_questions(
    *,
    workspace_id: uuid.UUID,
    status: str = QuestionStatus.ACTIVE,
    query: str = "",
    discipline_id: uuid.UUID | None = None,
    subject_id: uuid.UUID | None = None,
    subsubject_id: uuid.UUID | None = None,
    review_status: str = "",
    initial_result: str = "",
    error_category_id: uuid.UUID | None = None,
    unclassified_error: bool = False,
) -> QuerySet[Question]:
    """Liste somente questões do Workspace com ordenação total estável."""

    questions = Question.objects.filter(workspace_id=workspace_id, status=status)
    if query:
        questions = questions.filter(
            Q(revisions__is_current=True)
            & (Q(revisions__stem__icontains=query) | Q(revisions__explanation__icontains=query))
        )
    if discipline_id is not None:
        questions = questions.filter(discipline_id=discipline_id)
    if subject_id is not None:
        questions = questions.filter(subject_id=subject_id)
    if subsubject_id is not None:
        questions = questions.filter(subsubject_id=subsubject_id)
    if review_status:
        questions = questions.filter(
            id__in=eligible_reviews(
                workspace_id=workspace_id,
                status=ReviewTemporalStatus(review_status),
            ).values("question_id")
        )
    if initial_result:
        questions = questions.filter(
            attempts__workspace_id=workspace_id,
            attempts__attempt_type=AttemptType.INITIAL,
            attempts__status=AttemptStatus.VALID,
            attempts__is_correct=initial_result == "correct",
        )
    if error_category_id is not None or unclassified_error:
        questions = questions.filter(
            attempts__workspace_id=workspace_id,
            attempts__status=AttemptStatus.VALID,
            attempts__is_correct=False,
        )
        if unclassified_error:
            questions = questions.filter(attempts__error_classification__isnull=True)
        else:
            questions = questions.filter(
                attempts__error_classification__workspace_id=workspace_id,
                attempts__error_classification__category_id=error_category_id,
            )
    return (
        questions.select_related("discipline", "subject", "subsubject")
        .prefetch_related(
            Prefetch(
                "revisions",
                queryset=QuestionRevision.objects.filter(is_current=True).only(
                    "id", "question_id", "stem", "explanation"
                ),
                to_attr="current_revisions",
            )
        )
        .order_by("-updated_at", "id")
        .distinct()
    )


def paginate_questions(
    *, questions: QuerySet[Question], requested_page: str | None
) -> QuestionListPage:
    """Paginar resultados, recuperando páginas inválidas sem expor dados extras."""

    paginator = Paginator(questions, PAGE_SIZE)
    page_was_adjusted = False
    try:
        page_number = int(requested_page) if requested_page else 1
        if page_number < 1:
            raise ValueError
    except ValueError:
        page_number = 1
        page_was_adjusted = requested_page is not None
    try:
        question_page = paginator.page(page_number)
    except EmptyPage:
        question_page = paginator.page(paginator.num_pages)
        page_was_adjusted = True
    items = []
    for question in question_page.object_list:
        revisions = cast(list[QuestionRevision], getattr(question, "current_revisions", []))
        revision = revisions[0] if revisions else None
        items.append(
            QuestionListItem(
                question=question,
                stem=revision.stem or "" if revision else "",
                explanation=revision.explanation or "" if revision else "",
            )
        )
    return QuestionListPage(
        page=Page(items, question_page.number, cast(Any, paginator)),
        total=paginator.count,
        page_was_adjusted=page_was_adjusted,
    )
