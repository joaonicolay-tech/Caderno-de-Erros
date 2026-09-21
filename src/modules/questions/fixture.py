"""Fixture sintética, determinística e restrita ao banco descartável de testes."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid5

from django.conf import settings
from django.db import models, transaction

from modules.accounts.services import LOCAL_WORKSPACE_ID
from modules.taxonomy.models import Discipline, Subject, Subsubject
from shared.application.bootstrap import bootstrap_local_workspace

from .models import (
    Alternative,
    Board,
    Exam,
    Question,
    QuestionDifficulty,
    QuestionOrigin,
    QuestionRevision,
    QuestionStatus,
    RevisionChangeKind,
    Source,
    SourceType,
)

FIXTURE_SEED = "v02-catalog-demo-001"
_NAMESPACE = UUID("51f3f570-3907-50c2-8993-2298da89241d")
_INSTANT = datetime(2026, 9, 6, 12, 0, tzinfo=UTC)
_DRAFT_TITLE = "Fixture sintética V0.2 — rascunho"


class FixtureSafetyError(ValueError):
    """Indique uma tentativa de carregar a fixture fora de ambiente descartável."""


@dataclass(frozen=True, slots=True)
class FixtureLoadResult:
    """Contagens sanitizadas da fixture carregada ou já existente."""

    discipline_count: int
    subject_count: int
    subsubject_count: int
    board_count: int
    exam_count: int
    source_count: int
    question_count: int
    revision_count: int
    alternative_count: int
    origin_count: int


def _id(name: str) -> UUID:
    return uuid5(_NAMESPACE, name)


def _ensure_disposable_test_database() -> None:
    if getattr(settings, "CEI_PROFILE", None) != "test":
        raise FixtureSafetyError(
            "A fixture V0.2 só pode ser carregada no perfil de teste descartável."
        )


def _result() -> FixtureLoadResult:
    workspace_id = LOCAL_WORKSPACE_ID
    return FixtureLoadResult(
        discipline_count=Discipline.objects.filter(workspace_id=workspace_id).count(),
        subject_count=Subject.objects.filter(workspace_id=workspace_id).count(),
        subsubject_count=Subsubject.objects.filter(workspace_id=workspace_id).count(),
        board_count=Board.objects.filter(workspace_id=workspace_id).count(),
        exam_count=Exam.objects.filter(workspace_id=workspace_id).count(),
        source_count=Source.objects.filter(workspace_id=workspace_id).count(),
        question_count=Question.objects.filter(workspace_id=workspace_id).count(),
        revision_count=QuestionRevision.objects.filter(workspace_id=workspace_id).count(),
        alternative_count=Alternative.objects.filter(workspace_id=workspace_id).count(),
        origin_count=QuestionOrigin.objects.filter(workspace_id=workspace_id).count(),
    )


def _revision(
    *, question: Question, name: str, version: int, stem: str, current: bool, change_kind: str
) -> QuestionRevision:
    revision = QuestionRevision.objects.create(
        id=_id(f"revision:{name}"),
        workspace_id=LOCAL_WORKSPACE_ID,
        question=question,
        version_number=version,
        is_current=False,
        stem=stem,
        explanation="Conteúdo sintético para validar a apresentação do catálogo.",
        change_kind=change_kind,
    )
    alternatives = tuple(
        Alternative(
            id=_id(f"alternative:{name}:{position}"),
            workspace_id=LOCAL_WORKSPACE_ID,
            question_revision=revision,
            position=position,
            label=label,
            text=f"Opção sintética {label} da revisão {version}",
            text_key=f"opção sintética {label.lower()} da revisão {version}",
        )
        for position, label in enumerate(("A", "B", "C", "D"), start=1)
    )
    Alternative.objects.bulk_create(alternatives)
    models.QuerySet.update(
        QuestionRevision.objects.filter(pk=revision.id),
        correct_alternative_id=alternatives[1].id,
        is_current=current,
        created_at=_INSTANT,
    )
    revision.refresh_from_db()
    return revision


@transaction.atomic
def load_v02_fixture(*, seed: str = FIXTURE_SEED) -> FixtureLoadResult:
    """Carregue uma única amostra segura; repetir a mesma semente não duplica dados."""
    _ensure_disposable_test_database()
    if seed != FIXTURE_SEED:
        raise FixtureSafetyError("A fixture V0.2 aceita somente a semente documentada.")

    bootstrap_local_workspace(timezone_id="America/Sao_Paulo")
    if Question.objects.filter(pk=_id("question:draft")).exists():
        expected = _result()
        if expected.question_count < 3 or expected.revision_count < 3 or expected.origin_count < 1:
            raise FixtureSafetyError(
                "A fixture existente está incompleta; use um banco descartável novo."
            )
        return expected

    discipline = Discipline.objects.create(
        id=_id("taxonomy:discipline"),
        workspace_id=LOCAL_WORKSPACE_ID,
        name="Catálogo sintético",
        sort_order=1,
    )
    subject = Subject.objects.create(
        id=_id("taxonomy:subject"),
        workspace_id=LOCAL_WORKSPACE_ID,
        discipline=discipline,
        name="Validação operacional",
        sort_order=1,
    )
    subsubject = Subsubject.objects.create(
        id=_id("taxonomy:subsubject"),
        workspace_id=LOCAL_WORKSPACE_ID,
        subject=subject,
        name="Dados reproduzíveis",
        sort_order=1,
    )
    board = Board.objects.create(
        id=_id("board"), workspace_id=LOCAL_WORKSPACE_ID, name="Banca sintética"
    )
    exam = Exam.objects.create(
        id=_id("exam"),
        workspace_id=LOCAL_WORKSPACE_ID,
        board=board,
        name="Prova sintética",
        year=2026,
    )
    source = Source.objects.create(
        id=_id("source"),
        workspace_id=LOCAL_WORKSPACE_ID,
        source_type=SourceType.OTHER,
        name="Fonte sintética de validação",
        notes="Não contém material de estudo ou dados pessoais.",
    )

    Question.objects.create(
        id=_id("question:draft"),
        workspace_id=LOCAL_WORKSPACE_ID,
        draft_title=_DRAFT_TITLE,
    )
    active = Question.objects.create(
        id=_id("question:active"),
        workspace_id=LOCAL_WORKSPACE_ID,
        discipline=discipline,
        subject=subject,
        subsubject=subsubject,
        question_type="OBJECTIVE_SINGLE",
        status=QuestionStatus.ACTIVE,
        difficulty=QuestionDifficulty.EASY,
        draft_title="Fixture sintética V0.2 — ativa",
        activated_at=_INSTANT,
    )
    first = _revision(
        question=active,
        name="active:one",
        version=1,
        stem="Item sintético: selecione uma alternativa para validar o catálogo.",
        current=True,
        change_kind=RevisionChangeKind.INITIAL,
    )
    models.QuerySet.update(QuestionRevision.objects.filter(pk=first.id), is_current=False)
    _revision(
        question=active,
        name="active:two",
        version=2,
        stem="Item sintético revisado: selecione uma alternativa para validar o catálogo.",
        current=True,
        change_kind=RevisionChangeKind.NON_CRITICAL_EDIT,
    )
    QuestionOrigin.objects.create(
        id=_id("origin:active"),
        workspace_id=LOCAL_WORKSPACE_ID,
        question=active,
        source=source,
        exam=exam,
        reference_text="Referência sintética para teste de relações.",
    )

    archived = Question.objects.create(
        id=_id("question:archived"),
        workspace_id=LOCAL_WORKSPACE_ID,
        discipline=discipline,
        subject=subject,
        question_type="OBJECTIVE_SINGLE",
        status=QuestionStatus.ARCHIVED,
        difficulty=QuestionDifficulty.MEDIUM,
        draft_title="Fixture sintética V0.2 — arquivada",
        activated_at=_INSTANT,
        archived_at=_INSTANT,
    )
    _revision(
        question=archived,
        name="archived:one",
        version=1,
        stem="Item sintético arquivado para validar preservação histórica.",
        current=True,
        change_kind=RevisionChangeKind.INITIAL,
    )
    for model in (Discipline, Subject, Subsubject, Board, Exam, Source, Question, QuestionOrigin):
        model.objects.filter(workspace_id=LOCAL_WORKSPACE_ID).update(
            created_at=_INSTANT, updated_at=_INSTANT
        )
    return _result()
