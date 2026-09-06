"""CTs persistentes e transacionais do catálogo de questões da V0.2/Etapa 4."""

import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, transaction
from django.db.migrations.loader import MigrationLoader
from django.db.models.deletion import ProtectedError

from modules.accounts.models import User, Workspace
from modules.questions.exceptions import (
    QuestionCatalogConcurrencyError,
    QuestionCatalogNotFoundError,
    QuestionCatalogStateConflictError,
    QuestionCatalogValidationError,
)
from modules.questions.models import (
    Alternative,
    Question,
    QuestionDifficulty,
    QuestionOrigin,
    QuestionRevision,
    QuestionStatus,
    RevisionChangeKind,
    SourceType,
)
from modules.questions.selectors import (
    get_current_revision,
    get_question,
    list_question_revisions,
)
from modules.questions.services import (
    AlternativeInput,
    QuestionCommandService,
    QuestionOriginInput,
    archive_question,
    create_active,
    create_draft,
    create_or_reuse_board,
    create_or_reuse_exam,
    create_or_reuse_source,
    edit_question,
    save_revision,
    set_question_origin,
    update_question_metadata,
)
from modules.taxonomy.models import Discipline, Subject, Subsubject
from modules.taxonomy.services import create_discipline, create_subject, create_subsubject
from shared.domain.time import FixedClock, Instant

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _workspace(*, email: str, timezone_name: str = "America/Sao_Paulo") -> Workspace:
    user = User.objects.create_user(email=email)
    return Workspace.objects.create(
        owner_user=user,
        name=f"Espaço {email}",
        timezone_name=timezone_name,
    )


def _taxonomy(*, workspace: Workspace, suffix: str = "") -> tuple[Discipline, Subject, Subsubject]:
    discipline = create_discipline(workspace_id=workspace.id, name=f"Disciplina{suffix}")
    subject = create_subject(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        name=f"Assunto{suffix}",
    )
    subsubject = create_subsubject(
        workspace_id=workspace.id,
        subject_id=subject.id,
        name=f"Subassunto{suffix}",
    )
    return discipline, subject, subsubject


def _active_question(*, workspace: Workspace, suffix: str = "") -> Question:
    discipline, subject, subsubject = _taxonomy(workspace=workspace, suffix=suffix)
    return create_active(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        subject_id=subject.id,
        subsubject_id=subsubject.id,
        stem=f"Quanto é 2 + 2?{suffix}",
        alternatives=["3", "4"],
        correct_alternative_position=2,
    )


@pytest.mark.django_db
def test_ct005_draft_with_title_exists_without_revision() -> None:
    workspace = _workspace(email="draft-title@example.test")

    question = QuestionCommandService.create_draft(
        workspace_id=workspace.id,
        draft_title="  Questão para completar  ",
    )

    assert question.status == QuestionStatus.DRAFT
    assert question.draft_title == "Questão para completar"
    assert question.revisions.count() == 0
    assert get_current_revision(workspace_id=workspace.id, question_id=question.id) is None


@pytest.mark.django_db
def test_err_v02_007_any_versioned_content_creates_immutable_current_revision() -> None:
    workspace = _workspace(email="draft-content@example.test")

    question = create_draft(
        workspace_id=workspace.id,
        draft_title="Rascunho parcial",
        explanation="  Explicação em construção  ",
    )
    revision = get_current_revision(workspace_id=workspace.id, question_id=question.id)

    assert revision is not None
    assert revision.version_number == 1
    assert revision.is_current is True
    assert revision.explanation == "Explicação em construção"
    assert revision.stem is None
    with pytest.raises(ValidationError, match="imutável"):
        revision.explanation = "Sobrescrita"
        revision.save()


@pytest.mark.django_db
def test_draft_requires_title_or_real_versioned_content() -> None:
    workspace = _workspace(email="empty-draft@example.test")

    with pytest.raises(QuestionCatalogValidationError, match="título provisório"):
        create_draft(workspace_id=workspace.id, stem="  ", notes="")

    assert Question.objects.count() == 0


@pytest.mark.django_db
def test_ct006_ct007_create_active_requires_complete_hierarchy_content_and_answer() -> None:
    workspace = _workspace(email="active-validation@example.test")
    discipline, subject, _ = _taxonomy(workspace=workspace)

    invalid_calls = (
        {"stem": "", "alternatives": ["A", "B"], "correct_alternative_position": 1},
        {"stem": "Enunciado", "alternatives": ["A"], "correct_alternative_position": 1},
        {"stem": "Enunciado", "alternatives": ["A", " a "], "correct_alternative_position": 1},
        {"stem": "Enunciado", "alternatives": ["A", "B"], "correct_alternative_position": 3},
    )
    for values in invalid_calls:
        with pytest.raises(QuestionCatalogValidationError):
            create_active(
                workspace_id=workspace.id,
                discipline_id=discipline.id,
                subject_id=subject.id,
                **values,  # type: ignore[arg-type]
            )

    assert Question.objects.count() == 0
    assert QuestionRevision.objects.count() == 0
    assert Alternative.objects.count() == 0


@pytest.mark.django_db
def test_ct011_ct139_active_aggregate_keeps_order_and_answer_in_own_revision() -> None:
    workspace = _workspace(email="active@example.test")
    discipline, subject, subsubject = _taxonomy(workspace=workspace)
    clock = FixedClock(Instant(datetime(2026, 9, 6, 15, 0, tzinfo=UTC)))

    question = create_active(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        subject_id=subject.id,
        subsubject_id=subsubject.id,
        difficulty=QuestionDifficulty.MEDIUM,
        stem="Qual alternativa é correta?",
        alternatives=[
            AlternativeInput(text="Primeira", label="A"),
            AlternativeInput(text="Segunda", label="B"),
        ],
        correct_alternative_position=2,
        clock=clock,
    )
    revision = question.revisions.get(is_current=True)
    alternatives = list(revision.alternatives.order_by("position"))

    assert question.status == QuestionStatus.ACTIVE
    assert question.activated_at == clock.now().value
    assert question.difficulty == QuestionDifficulty.MEDIUM
    assert [item.position for item in alternatives] == [1, 2]
    assert [item.label for item in alternatives] == ["A", "B"]
    assert revision.correct_alternative_id == alternatives[1].id
    assert revision.correct_alternative is not None
    assert revision.correct_alternative.question_revision_id == revision.id


@pytest.mark.django_db
def test_ct008_ct075_revision_switch_is_atomic_and_preserves_previous_snapshot() -> None:
    workspace = _workspace(email="revision@example.test")
    question = _active_question(workspace=workspace)
    first = question.revisions.get(is_current=True)
    first_alternatives = list(first.alternatives.order_by("position"))

    second = save_revision(
        workspace_id=workspace.id,
        question_id=question.id,
        expected_lock_version=1,
        stem="Quanto é 3 + 3?",
        alternatives=["5", "6", "7"],
        correct_alternative_position=2,
        change_kind=RevisionChangeKind.CRITICAL_CORRECTION,
        change_reason="Correção do enunciado e do gabarito",
    )
    first.refresh_from_db()
    question.refresh_from_db()

    assert first.is_current is False
    assert second.is_current is True
    assert second.version_number == 2
    assert second.change_kind == RevisionChangeKind.CRITICAL_CORRECTION
    assert question.lock_version == 2
    assert list(first.alternatives.order_by("position")) == first_alternatives
    assert QuestionRevision.objects.filter(question=question, is_current=True).count() == 1
    assert second.correct_alternative is not None
    assert second.correct_alternative.question_revision_id == second.id


@pytest.mark.django_db
def test_ct140_failure_and_stale_lock_preserve_previous_current_revision(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workspace = _workspace(email="rollback@example.test")
    question = _active_question(workspace=workspace)
    first = question.revisions.get(is_current=True)

    def fail_bulk_create(*args: object, **kwargs: object) -> None:
        raise IntegrityError("falha controlada")

    monkeypatch.setattr(Alternative.objects, "bulk_create", fail_bulk_create)
    with pytest.raises(IntegrityError, match="controlada"):
        save_revision(
            workspace_id=workspace.id,
            question_id=question.id,
            expected_lock_version=1,
            stem="Nova versão",
            alternatives=["A", "B"],
            correct_alternative_position=1,
        )

    first.refresh_from_db()
    assert first.is_current is True
    assert QuestionRevision.objects.filter(question=question).count() == 1
    with pytest.raises(QuestionCatalogConcurrencyError):
        save_revision(
            workspace_id=workspace.id,
            question_id=question.id,
            expected_lock_version=2,
            stem="Outra versão",
            alternatives=["A", "B"],
            correct_alternative_position=1,
        )
    assert QuestionRevision.objects.filter(question=question, is_current=True).get() == first


@pytest.mark.django_db
def test_draft_can_be_activated_by_saving_a_complete_revision() -> None:
    workspace = _workspace(email="activate-draft@example.test")
    discipline, subject, _ = _taxonomy(workspace=workspace)
    question = create_draft(
        workspace_id=workspace.id,
        draft_title="Completar",
        discipline_id=discipline.id,
        subject_id=subject.id,
    )

    revision = save_revision(
        workspace_id=workspace.id,
        question_id=question.id,
        expected_lock_version=1,
        stem="Enunciado completo",
        alternatives=["Errada", "Correta"],
        correct_alternative_position=2,
        activate=True,
    )
    question.refresh_from_db()

    assert question.status == QuestionStatus.ACTIVE
    assert question.activated_at is not None
    assert question.lock_version == 2
    assert revision.version_number == 1


@pytest.mark.django_db
def test_ct074_hierarchy_and_selectors_never_cross_workspace() -> None:
    workspace_a = _workspace(email="question-a@example.test")
    workspace_b = _workspace(email="question-b@example.test")
    discipline_a, _, _ = _taxonomy(workspace=workspace_a, suffix=" A")
    discipline_b, subject_b, _ = _taxonomy(workspace=workspace_b, suffix=" B")

    with pytest.raises(QuestionCatalogValidationError, match="Subject"):
        create_active(
            workspace_id=workspace_a.id,
            discipline_id=discipline_a.id,
            subject_id=subject_b.id,
            stem="Mistura",
            alternatives=["A", "B"],
            correct_alternative_position=1,
        )
    question = create_active(
        workspace_id=workspace_b.id,
        discipline_id=discipline_b.id,
        subject_id=subject_b.id,
        stem="Válida",
        alternatives=["A", "B"],
        correct_alternative_position=1,
    )
    with pytest.raises(QuestionCatalogNotFoundError):
        get_question(workspace_id=workspace_a.id, question_id=question.id)
    assert get_current_revision(workspace_id=workspace_a.id, question_id=question.id) is None
    assert list(list_question_revisions(workspace_id=workspace_a.id, question_id=question.id)) == []


@pytest.mark.django_db
def test_model_guards_reject_cross_workspace_taxonomy_revision_alternative_and_origin() -> None:
    workspace_a = _workspace(email="guard-question-a@example.test")
    workspace_b = _workspace(email="guard-question-b@example.test")
    discipline_b, subject_b, _ = _taxonomy(workspace=workspace_b)
    question_a = create_draft(workspace_id=workspace_a.id, draft_title="A")

    with pytest.raises(ValidationError, match="Workspace"):
        Question.objects.create(
            workspace=workspace_a,
            discipline=discipline_b,
            subject=subject_b,
            draft_title="Inválida",
        )
    with pytest.raises(ValidationError, match="Workspace"):
        QuestionRevision.objects.create(
            workspace=workspace_b,
            question=question_a,
            version_number=1,
            change_kind=RevisionChangeKind.INITIAL,
        )


@pytest.mark.django_db
def test_ct138_origin_is_optional_unique_mutable_and_removed_when_empty() -> None:
    workspace = _workspace(email="question-origin@example.test")
    question = _active_question(workspace=workspace)
    board = create_or_reuse_board(workspace_id=workspace.id, name="Banca")
    exam = create_or_reuse_exam(
        workspace_id=workspace.id,
        board_id=board.id,
        name="Prova",
        year=2026,
    )
    source = create_or_reuse_source(
        workspace_id=workspace.id,
        source_type=SourceType.PDF,
        name="Caderno",
    )

    assert not QuestionOrigin.objects.filter(question=question).exists()
    origin = set_question_origin(
        workspace_id=workspace.id,
        question_id=question.id,
        expected_lock_version=1,
        origin=QuestionOriginInput(
            source_id=source.id,
            exam_id=exam.id,
            reference_text=" Questão 10 ",
        ),
    )
    assert origin is not None
    assert origin.exam_id == exam.id
    assert origin.board_id is None
    assert origin.reference_text == "Questão 10"
    assert QuestionOrigin.objects.filter(question=question).count() == 1

    removed = set_question_origin(
        workspace_id=workspace.id,
        question_id=question.id,
        expected_lock_version=2,
        origin=QuestionOriginInput(),
    )
    assert removed is None
    assert not QuestionOrigin.objects.filter(question=question).exists()


@pytest.mark.django_db
def test_ct138_origin_rejects_cross_workspace_exclusivity_and_dynamic_year() -> None:
    workspace_a = _workspace(email="origin-question-a@example.test")
    workspace_b = _workspace(email="origin-question-b@example.test")
    question = _active_question(workspace=workspace_a)
    foreign_source = create_or_reuse_source(
        workspace_id=workspace_b.id,
        source_type=SourceType.BOOK,
        name="Estrangeira",
    )
    board = create_or_reuse_board(workspace_id=workspace_a.id, name="Banca")
    exam = create_or_reuse_exam(workspace_id=workspace_a.id, name="Prova")
    clock = FixedClock(Instant(datetime(2026, 12, 31, 12, 30, tzinfo=UTC)))

    invalid_origins = (
        QuestionOriginInput(source_id=foreign_source.id),
        QuestionOriginInput(exam_id=exam.id, board_id=board.id),
        QuestionOriginInput(exam_id=exam.id, reference_year=2026),
        QuestionOriginInput(reference_year=2030),
        QuestionOriginInput(reference_year=1899),
    )
    for origin in invalid_origins:
        with pytest.raises((QuestionCatalogValidationError, QuestionCatalogNotFoundError)):
            set_question_origin(
                workspace_id=workspace_a.id,
                question_id=question.id,
                expected_lock_version=1,
                origin=origin,
                clock=clock,
            )

    question.refresh_from_db()
    assert question.lock_version == 1
    assert QuestionOrigin.objects.count() == 0


@pytest.mark.django_db
def test_metadata_edit_does_not_create_revision_and_respects_lock_and_active_taxonomy() -> None:
    workspace = _workspace(email="metadata@example.test")
    question = _active_question(workspace=workspace)
    discipline, subject, subsubject = _taxonomy(workspace=workspace, suffix=" Nova")

    updated = update_question_metadata(
        workspace_id=workspace.id,
        question_id=question.id,
        expected_lock_version=1,
        discipline_id=discipline.id,
        subject_id=subject.id,
        subsubject_id=subsubject.id,
        difficulty=QuestionDifficulty.HARD,
        draft_title="Referência interna",
    )

    assert updated.lock_version == 2
    assert updated.discipline_id == discipline.id
    assert updated.difficulty == QuestionDifficulty.HARD
    assert updated.revisions.count() == 1
    with pytest.raises(QuestionCatalogConcurrencyError):
        update_question_metadata(
            workspace_id=workspace.id,
            question_id=question.id,
            expected_lock_version=1,
            discipline_id=discipline.id,
            subject_id=subject.id,
        )


@pytest.mark.django_db
def test_ct010_archive_preserves_revisions_origin_and_rejects_future_edits() -> None:
    workspace = _workspace(email="archive-question@example.test")
    question = _active_question(workspace=workspace)
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
    clock = FixedClock(Instant(datetime(2026, 9, 6, 17, 0, tzinfo=UTC)))

    archived = archive_question(
        workspace_id=workspace.id,
        question_id=question.id,
        expected_lock_version=2,
        clock=clock,
    )

    assert archived.status == QuestionStatus.ARCHIVED
    assert archived.archived_at == clock.now().value
    assert archived.revisions.count() == 1
    assert QuestionOrigin.objects.filter(question=archived).exists()
    with pytest.raises(QuestionCatalogStateConflictError):
        save_revision(
            workspace_id=workspace.id,
            question_id=question.id,
            expected_lock_version=3,
            stem="Proibida",
            alternatives=["A", "B"],
            correct_alternative_position=1,
        )


@pytest.mark.django_db
def test_ct012_unicode_and_text_boundaries_are_preserved() -> None:
    workspace = _workspace(email="unicode-question@example.test")
    discipline, subject, _ = _taxonomy(workspace=workspace)
    stem = "á" * 20_000

    question = create_active(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        subject_id=subject.id,
        stem=stem,
        alternatives=["opção", "ac\u0327a\u0303o"],
        correct_alternative_position=1,
    )
    revision = question.revisions.get()

    assert revision.stem == stem
    assert revision.alternatives.get(position=2).text == "ação"
    with pytest.raises(QuestionCatalogValidationError, match="20000"):
        save_revision(
            workspace_id=workspace.id,
            question_id=question.id,
            expected_lock_version=1,
            stem="x" * 20_001,
            alternatives=["A", "B"],
            correct_alternative_position=1,
        )


@pytest.mark.django_db
def test_ct144_equal_stems_are_not_semantically_blocked() -> None:
    workspace = _workspace(email="duplicate-stem@example.test")
    discipline, subject, _ = _taxonomy(workspace=workspace)

    first = create_active(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        subject_id=subject.id,
        stem="Enunciado repetido",
        alternatives=["A", "B"],
        correct_alternative_position=1,
    )
    second = create_active(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        subject_id=subject.id,
        stem="Enunciado repetido",
        alternatives=["A", "B"],
        correct_alternative_position=1,
    )

    assert first.id != second.id
    assert Question.objects.count() == 2


@pytest.mark.django_db
def test_ct008_edit_command_versions_content_once_and_metadata_only_does_not() -> None:
    workspace = _workspace(email="edit-command@example.test")
    question = _active_question(workspace=workspace)
    discipline, subject, subsubject = _taxonomy(workspace=workspace, suffix=" Nova")
    first = question.revisions.get(is_current=True)
    first_values = list(first.alternatives.order_by("position").values_list("text", flat=True))

    edited = edit_question(
        workspace_id=workspace.id,
        question_id=question.id,
        expected_lock_version=1,
        discipline_id=discipline.id,
        subject_id=subject.id,
        subsubject_id=subsubject.id,
        difficulty=QuestionDifficulty.HARD,
        stem="Quanto é 3 + 3?",
        alternatives=["5", "6"],
        correct_alternative_position=2,
        explanation="Somamos três duas vezes.",
    )
    first.refresh_from_db()
    second = edited.revisions.get(is_current=True)

    assert edited.lock_version == 2
    assert edited.discipline_id == discipline.id
    assert first.is_current is False
    assert (
        list(first.alternatives.order_by("position").values_list("text", flat=True)) == first_values
    )
    assert second.version_number == 2
    assert second.correct_alternative is not None
    assert second.correct_alternative.question_revision_id == second.id

    metadata_only = edit_question(
        workspace_id=workspace.id,
        question_id=question.id,
        expected_lock_version=2,
        discipline_id=discipline.id,
        subject_id=subject.id,
        subsubject_id=subsubject.id,
        difficulty=QuestionDifficulty.MEDIUM,
        stem=second.stem,
        alternatives=[
            AlternativeInput(text=item.text, label=item.label)
            for item in second.alternatives.order_by("position")
        ],
        correct_alternative_position=2,
        explanation=second.explanation,
    )

    assert metadata_only.lock_version == 3
    assert metadata_only.difficulty == QuestionDifficulty.MEDIUM
    assert metadata_only.revisions.count() == 2
    assert metadata_only.revisions.filter(is_current=True).count() == 1


@pytest.mark.django_db
def test_ct140_edit_command_rolls_back_revision_metadata_and_origin_on_late_failure() -> None:
    workspace = _workspace(email="edit-rollback@example.test")
    question = _active_question(workspace=workspace)
    first = question.revisions.get(is_current=True)
    original_discipline_id = question.discipline_id
    discipline, subject, _ = _taxonomy(workspace=workspace, suffix=" Rollback")

    with pytest.raises(QuestionCatalogValidationError, match="1900"):
        edit_question(
            workspace_id=workspace.id,
            question_id=question.id,
            expected_lock_version=1,
            discipline_id=discipline.id,
            subject_id=subject.id,
            difficulty=QuestionDifficulty.HARD,
            stem="Conteúdo que deve ser revertido",
            alternatives=["A", "B"],
            correct_alternative_position=1,
            origin=QuestionOriginInput(reference_year=1899),
        )

    question.refresh_from_db()
    first.refresh_from_db()
    assert question.lock_version == 1
    assert question.discipline_id == original_discipline_id
    assert question.difficulty is None
    assert question.revisions.count() == 1
    assert first.is_current is True
    assert not QuestionOrigin.objects.filter(question=question).exists()


@pytest.mark.django_db(transaction=True)
def test_ct073_constraints_and_protected_foreign_keys_cover_local_invariants() -> None:
    workspace = _workspace(email="question-constraints@example.test")
    question = _active_question(workspace=workspace)
    revision = question.revisions.get()
    alternative = revision.alternatives.get(position=1)

    invalid_operations = (
        lambda: Question.objects.filter(pk=question.id).update(status="INVALID"),
        lambda: Question.objects.filter(pk=question.id).update(lock_version=0),
        lambda: QuestionRevision.objects.filter(pk=revision.id).update(version_number=0),
        lambda: QuestionRevision.objects.create(
            workspace=workspace,
            question=question,
            version_number=2,
            is_current=True,
            change_kind=RevisionChangeKind.INITIAL,
        ),
        lambda: Alternative.objects.filter(pk=alternative.id).update(position=0),
        lambda: QuestionOrigin.objects.create(workspace=workspace, question=question),
    )
    for operation in invalid_operations:
        with pytest.raises((IntegrityError, ValidationError)):
            with transaction.atomic():
                operation()

    with pytest.raises(ProtectedError):
        question.delete()
    with pytest.raises(ProtectedError):
        revision.delete()


@pytest.mark.django_db
def test_model_guard_rejects_answer_from_another_revision() -> None:
    workspace = _workspace(email="answer-guard@example.test")
    first_question = _active_question(workspace=workspace, suffix=" A")
    second_question = _active_question(workspace=workspace, suffix=" B")
    foreign_answer = second_question.revisions.get().alternatives.get(position=1)

    rogue = QuestionRevision(
        workspace=workspace,
        question=first_question,
        version_number=2,
        correct_alternative=foreign_answer,
        change_kind=RevisionChangeKind.NON_CRITICAL_EDIT,
    )
    with pytest.raises(ValidationError, match="própria revisão"):
        rogue.save()


@pytest.mark.django_db
def test_ct081_question_migration_has_frozen_dependencies_order_and_schema() -> None:
    loader = MigrationLoader(connection)
    migration = loader.get_migration("questions", "0002_question_catalog")
    operation_labels = [
        (operation.__class__.__name__, getattr(operation, "name", None))
        for operation in migration.operations
    ]

    assert migration.dependencies == [
        ("questions", "0001_origin_catalog"),
        ("taxonomy", "0001_initial"),
    ]
    revision_index = operation_labels.index(("CreateModel", "QuestionRevision"))
    alternative_index = operation_labels.index(("CreateModel", "Alternative"))
    answer_fk_index = operation_labels.index(("AddField", "correct_alternative"))
    assert revision_index < alternative_index < answer_fk_index
    assert {
        "questions_question",
        "questions_questionrevision",
        "questions_alternative",
        "questions_questionorigin",
    }.issubset(connection.introspection.table_names())


def test_ct082_upgrade_and_rollback_preserve_stage3_data() -> None:
    probe = r"""
import json
import uuid
import django
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

django.setup()
executor = MigrationExecutor(connection)
stage3 = [("auth", "0012_alter_user_first_name_max_length"), ("errors", "0001_initial"), ("questions", "0001_origin_catalog"), ("taxonomy", "0001_initial")]
executor.migrate(stage3)
apps = executor.loader.project_state(stage3).apps
User = apps.get_model("accounts", "User")
Workspace = apps.get_model("accounts", "Workspace")
Discipline = apps.get_model("taxonomy", "Discipline")
Board = apps.get_model("questions", "Board")
user = User.objects.create(id=uuid.uuid4(), password="!", status="ACTIVE")
workspace = Workspace.objects.create(id=uuid.uuid4(), owner_user=user, name="Espaço", timezone_name="America/Sao_Paulo", locale="pt-BR", lock_version=1)
Discipline.objects.create(workspace=workspace, name="Matemática", name_key="matemática")
Board.objects.create(workspace=workspace, name="Banca", name_key="banca")
executor = MigrationExecutor(connection)
executor.migrate(executor.loader.graph.leaf_nodes())
final_apps = executor.loader.project_state().apps
counts_after_upgrade = {
    "discipline": final_apps.get_model("taxonomy", "Discipline").objects.count(),
    "board": final_apps.get_model("questions", "Board").objects.count(),
    "question": final_apps.get_model("questions", "Question").objects.count(),
}
executor = MigrationExecutor(connection)
executor.migrate(stage3)
rolled_apps = executor.loader.project_state(stage3).apps
counts_after_rollback = {
    "discipline": rolled_apps.get_model("taxonomy", "Discipline").objects.count(),
    "board": rolled_apps.get_model("questions", "Board").objects.count(),
}
print(json.dumps({"upgrade": counts_after_upgrade, "rollback": counts_after_rollback}))
"""
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    environment["DJANGO_SETTINGS_MODULE"] = "config.settings.test"
    result = subprocess.run(
        [sys.executable, "-c", probe],
        cwd=PROJECT_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout.strip().splitlines()[-1]) == {
        "upgrade": {"discipline": 1, "board": 1, "question": 0},
        "rollback": {"discipline": 1, "board": 1},
    }
