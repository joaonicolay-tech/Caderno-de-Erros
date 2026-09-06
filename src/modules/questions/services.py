"""Serviços internos, transacionais e Workspace-scoped do catálogo de origem."""

import uuid
from collections.abc import Callable
from dataclasses import dataclass

from django.db import IntegrityError, models, transaction
from django.db.models import F, Max

from modules.accounts.models import Workspace
from modules.taxonomy.models import Discipline, Subject, Subsubject, TaxonomyStatus
from shared.domain.time import Clock, SystemClock

from .exceptions import (
    OriginCatalogConcurrencyError,
    OriginCatalogNotFoundError,
    OriginCatalogStateConflictError,
    OriginCatalogValidationError,
    QuestionCatalogConcurrencyError,
    QuestionCatalogNotFoundError,
    QuestionCatalogStateConflictError,
    QuestionCatalogValidationError,
)
from .models import (
    Alternative,
    Board,
    Exam,
    OriginCatalogItem,
    OriginStatus,
    Question,
    QuestionDifficulty,
    QuestionOrigin,
    QuestionRevision,
    QuestionStatus,
    RevisionChangeKind,
    Source,
    SourceType,
)
from .validators import (
    QUESTION_DRAFT_TITLE_MAX_LENGTH,
    QUESTION_EXPLANATION_MAX_LENGTH,
    QUESTION_NOTES_MAX_LENGTH,
    QUESTION_REFERENCE_MAX_LENGTH,
    QUESTION_STEM_MAX_LENGTH,
    QUESTION_TRAP_NOTE_MAX_LENGTH,
    normalize_alternative_label,
    normalize_alternative_text,
    normalize_optional_notes,
    normalize_optional_question_text,
    normalize_optional_url,
    normalize_origin_name,
    validate_exam_year,
    validate_reference_year,
)


@dataclass(frozen=True, slots=True)
class AlternativeInput:
    """Entrada textual ordenada para compor uma revisão."""

    text: str
    label: str | None = None


@dataclass(frozen=True, slots=True)
class QuestionOriginInput:
    """Snapshot opcional dos metadados de origem de uma questão."""

    source_id: uuid.UUID | None = None
    source_name: str | None = None
    source_type: str | None = None
    source_url: str | None = None
    source_notes: str | None = None
    exam_id: uuid.UUID | None = None
    exam_name: str | None = None
    exam_year: int | None = None
    board_id: uuid.UUID | None = None
    board_name: str | None = None
    board_website_url: str | None = None
    reference_year: int | None = None
    reference_text: str | None = None


def _get_workspace(workspace_id: uuid.UUID) -> Workspace:
    try:
        return Workspace.objects.get(pk=workspace_id)
    except Workspace.DoesNotExist as error:
        raise OriginCatalogNotFoundError("Workspace não encontrado.") from error


def _get_question_workspace(workspace_id: uuid.UUID) -> Workspace:
    try:
        return Workspace.objects.get(pk=workspace_id)
    except Workspace.DoesNotExist as error:
        raise QuestionCatalogNotFoundError("Workspace não encontrado.") from error


def _create_or_reuse[OriginItemT: OriginCatalogItem](
    *,
    queryset: models.QuerySet[OriginItemT],
    creator: Callable[[], OriginItemT],
) -> OriginItemT:
    existing = queryset.first()
    if existing is not None:
        return existing
    try:
        with transaction.atomic():
            return creator()
    except IntegrityError:
        existing = queryset.first()
        if existing is None:
            raise
        return existing


@transaction.atomic
def create_or_reuse_board(
    *,
    workspace_id: uuid.UUID,
    name: str,
    website_url: str | None = None,
) -> Board:
    """Crie ou reutilize a Board ativa equivalente dentro do Workspace."""
    normalized = normalize_origin_name(name)
    normalized_url = normalize_optional_url(website_url, field_label="O site da banca")
    workspace = _get_workspace(workspace_id)
    scoped = Board.objects.filter(
        workspace_id=workspace_id,
        name_key=normalized.key,
        status=OriginStatus.ACTIVE,
    )
    return _create_or_reuse(
        queryset=scoped,
        creator=lambda: Board.objects.create(
            workspace=workspace,
            name=normalized.display,
            name_key=normalized.key,
            website_url=normalized_url,
        ),
    )


def _get_active_board(*, workspace_id: uuid.UUID, board_id: uuid.UUID) -> Board:
    try:
        board = Board.objects.get(pk=board_id, workspace_id=workspace_id)
    except Board.DoesNotExist as error:
        raise OriginCatalogNotFoundError("Board não encontrada no Workspace.") from error
    if board.status != OriginStatus.ACTIVE:
        raise OriginCatalogStateConflictError("A Board precisa estar ativa.")
    return board


@transaction.atomic
def create_or_reuse_exam(
    *,
    workspace_id: uuid.UUID,
    name: str,
    board_id: uuid.UUID | None = None,
    year: int | None = None,
    clock: Clock | None = None,
) -> Exam:
    """Crie ou reutilize Exam pela chave lógica completa e pelo Workspace."""
    normalized = normalize_origin_name(name)
    workspace = _get_workspace(workspace_id)
    validate_exam_year(year, workspace=workspace, clock=clock)
    board = (
        _get_active_board(workspace_id=workspace_id, board_id=board_id)
        if board_id is not None
        else None
    )
    scoped = Exam.objects.filter(
        workspace_id=workspace_id,
        name_key=normalized.key,
        year=year,
        status=OriginStatus.ACTIVE,
    )
    if board_id is None:
        scoped = scoped.filter(board__isnull=True)
    else:
        scoped = scoped.filter(board_id=board_id)
    return _create_or_reuse(
        queryset=scoped,
        creator=lambda: Exam.objects.create(
            workspace=workspace,
            board=board,
            name=normalized.display,
            name_key=normalized.key,
            year=year,
        ),
    )


@transaction.atomic
def create_or_reuse_source(
    *,
    workspace_id: uuid.UUID,
    source_type: str,
    name: str,
    locator_url: str | None = None,
    notes: str | None = None,
) -> Source:
    """Crie ou reutilize Source ativa pela combinação tipo/nome normalizado."""
    normalized = normalize_origin_name(name)
    if source_type not in SourceType.values:
        raise OriginCatalogValidationError("O tipo da fonte é inválido.")
    normalized_url = normalize_optional_url(locator_url, field_label="O endereço da fonte")
    normalized_notes = normalize_optional_notes(notes)
    workspace = _get_workspace(workspace_id)
    scoped = Source.objects.filter(
        workspace_id=workspace_id,
        source_type=source_type,
        name_key=normalized.key,
        status=OriginStatus.ACTIVE,
    )
    return _create_or_reuse(
        queryset=scoped,
        creator=lambda: Source.objects.create(
            workspace=workspace,
            source_type=source_type,
            name=normalized.display,
            name_key=normalized.key,
            locator_url=normalized_url,
            notes=normalized_notes,
        ),
    )


@transaction.atomic
def _archive_item[OriginItemT: OriginCatalogItem](
    *,
    queryset: models.QuerySet[OriginItemT],
    item_id: uuid.UUID,
    expected_lock_version: int,
    clock: Clock | None,
) -> OriginItemT:
    try:
        item = queryset.get(pk=item_id)
    except queryset.model.DoesNotExist as error:
        raise OriginCatalogNotFoundError(
            "Referência de origem não encontrada no Workspace."
        ) from error
    if item.status == OriginStatus.ARCHIVED:
        raise OriginCatalogStateConflictError("A referência de origem já está arquivada.")
    if item.lock_version != expected_lock_version:
        raise OriginCatalogConcurrencyError("A referência mudou; recarregue a versão atual.")

    now = (clock or SystemClock()).now().value
    updated = queryset.filter(
        pk=item.id,
        status=OriginStatus.ACTIVE,
        lock_version=expected_lock_version,
    ).update(
        status=OriginStatus.ARCHIVED,
        archived_at=now,
        lock_version=F("lock_version") + 1,
        updated_at=now,
    )
    if updated != 1:
        raise OriginCatalogConcurrencyError("A referência mudou; recarregue a versão atual.")
    item.refresh_from_db()
    return item


def archive_board(
    *,
    workspace_id: uuid.UUID,
    board_id: uuid.UUID,
    expected_lock_version: int,
    clock: Clock | None = None,
) -> Board:
    """Arquive Board sem alterar automaticamente seus Exams."""
    return _archive_item(
        queryset=Board.objects.filter(workspace_id=workspace_id),
        item_id=board_id,
        expected_lock_version=expected_lock_version,
        clock=clock,
    )


def archive_exam(
    *,
    workspace_id: uuid.UUID,
    exam_id: uuid.UUID,
    expected_lock_version: int,
    clock: Clock | None = None,
) -> Exam:
    """Arquive Exam preservando os vínculos históricos futuros."""
    return _archive_item(
        queryset=Exam.objects.filter(workspace_id=workspace_id),
        item_id=exam_id,
        expected_lock_version=expected_lock_version,
        clock=clock,
    )


def archive_source(
    *,
    workspace_id: uuid.UUID,
    source_id: uuid.UUID,
    expected_lock_version: int,
    clock: Clock | None = None,
) -> Source:
    """Arquive Source preservando os vínculos históricos futuros."""
    return _archive_item(
        queryset=Source.objects.filter(workspace_id=workspace_id),
        item_id=source_id,
        expected_lock_version=expected_lock_version,
        clock=clock,
    )


def _normalize_draft_title(value: str | None) -> str | None:
    return normalize_optional_question_text(
        value,
        field_label="O título provisório",
        max_length=QUESTION_DRAFT_TITLE_MAX_LENGTH,
    )


def _validate_difficulty(value: str | None) -> None:
    if value is not None and value not in QuestionDifficulty.values:
        raise QuestionCatalogValidationError("A dificuldade da questão é inválida.")


def _get_taxonomy(
    *,
    workspace_id: uuid.UUID,
    discipline_id: uuid.UUID | None,
    subject_id: uuid.UUID | None,
    subsubject_id: uuid.UUID | None,
    required: bool,
) -> tuple[Discipline | None, Subject | None, Subsubject | None]:
    if subject_id is not None and discipline_id is None:
        raise QuestionCatalogValidationError("Informe a Discipline do Subject.")
    if subsubject_id is not None and subject_id is None:
        raise QuestionCatalogValidationError("Informe o Subject do Subsubject.")
    if required and (discipline_id is None or subject_id is None):
        raise QuestionCatalogValidationError("Uma questão ativa exige Discipline e Subject ativos.")

    discipline = None
    if discipline_id is not None:
        discipline = Discipline.objects.filter(
            pk=discipline_id,
            workspace_id=workspace_id,
        ).first()
        if discipline is None:
            raise QuestionCatalogNotFoundError("Discipline não encontrada no Workspace.")
        if discipline.status != TaxonomyStatus.ACTIVE:
            raise QuestionCatalogStateConflictError("A Discipline precisa estar ativa.")

    subject = None
    if subject_id is not None:
        if discipline_id is None:
            raise QuestionCatalogValidationError("Informe a Discipline do Subject.")
        subject = Subject.objects.filter(
            pk=subject_id,
            workspace_id=workspace_id,
            discipline_id=discipline_id,
        ).first()
        if subject is None:
            raise QuestionCatalogValidationError(
                "O Subject deve pertencer à Discipline e ao Workspace informados."
            )
        if subject.status != TaxonomyStatus.ACTIVE:
            raise QuestionCatalogStateConflictError("O Subject precisa estar ativo.")

    subsubject = None
    if subsubject_id is not None:
        if subject_id is None:
            raise QuestionCatalogValidationError("Informe o Subject do Subsubject.")
        subsubject = Subsubject.objects.filter(
            pk=subsubject_id,
            workspace_id=workspace_id,
            subject_id=subject_id,
        ).first()
        if subsubject is None:
            raise QuestionCatalogValidationError(
                "O Subsubject deve pertencer ao Subject e ao Workspace informados."
            )
        if subsubject.status != TaxonomyStatus.ACTIVE:
            raise QuestionCatalogStateConflictError("O Subsubject precisa estar ativo.")
    return discipline, subject, subsubject


def _normalize_alternatives(
    alternatives: list[AlternativeInput | str] | tuple[AlternativeInput | str, ...],
) -> list[tuple[str, str | None, str]]:
    normalized: list[tuple[str, str | None, str]] = []
    seen_keys: set[str] = set()
    for value in alternatives:
        item = AlternativeInput(text=value) if isinstance(value, str) else value
        if not isinstance(item, AlternativeInput):
            raise QuestionCatalogValidationError(
                "Cada alternativa deve ser texto ou AlternativeInput."
            )
        text_value = normalize_alternative_text(item.text)
        if text_value.text_key in seen_keys:
            raise QuestionCatalogValidationError(
                "As alternativas devem ser textualmente distintas."
            )
        seen_keys.add(text_value.text_key)
        normalized.append(
            (
                text_value.text,
                normalize_alternative_label(item.label),
                text_value.text_key,
            )
        )
    return normalized


def _normalize_revision_content(
    *,
    stem: str | None,
    alternatives: list[AlternativeInput | str] | tuple[AlternativeInput | str, ...],
    correct_alternative_position: int | None,
    explanation: str | None,
    trap_note: str | None,
    notes: str | None,
    change_kind: str,
    change_reason: str | None,
) -> tuple[
    str | None,
    list[tuple[str, str | None, str]],
    int | None,
    str | None,
    str | None,
    str | None,
    str | None,
]:
    if change_kind not in RevisionChangeKind.values:
        raise QuestionCatalogValidationError("O tipo de alteração da revisão é inválido.")
    normalized_stem = normalize_optional_question_text(
        stem,
        field_label="O enunciado",
        max_length=QUESTION_STEM_MAX_LENGTH,
    )
    normalized_explanation = normalize_optional_question_text(
        explanation,
        field_label="A explicação",
        max_length=QUESTION_EXPLANATION_MAX_LENGTH,
    )
    normalized_trap = normalize_optional_question_text(
        trap_note,
        field_label="A pegadinha",
        max_length=QUESTION_TRAP_NOTE_MAX_LENGTH,
    )
    normalized_notes = normalize_optional_question_text(
        notes,
        field_label="As observações",
        max_length=QUESTION_NOTES_MAX_LENGTH,
    )
    normalized_reason = normalize_optional_question_text(
        change_reason,
        field_label="O motivo da alteração",
        max_length=QUESTION_REFERENCE_MAX_LENGTH,
    )
    if change_kind == RevisionChangeKind.CRITICAL_CORRECTION and normalized_reason is None:
        raise QuestionCatalogValidationError("A correção crítica exige um motivo.")
    normalized_alternatives = _normalize_alternatives(alternatives)
    if correct_alternative_position is not None:
        if (
            isinstance(correct_alternative_position, bool)
            or not isinstance(correct_alternative_position, int)
            or not 1 <= correct_alternative_position <= len(normalized_alternatives)
        ):
            raise QuestionCatalogValidationError(
                "A posição do gabarito deve identificar uma alternativa da própria revisão."
            )
    return (
        normalized_stem,
        normalized_alternatives,
        correct_alternative_position,
        normalized_explanation,
        normalized_trap,
        normalized_notes,
        normalized_reason,
    )


def _has_versioned_content(
    *,
    stem: str | None,
    alternatives: list[tuple[str, str | None, str]],
    explanation: str | None,
    trap_note: str | None,
    notes: str | None,
) -> bool:
    return any((stem, alternatives, explanation, trap_note, notes))


def _validate_active_revision(
    *,
    stem: str | None,
    alternatives: list[tuple[str, str | None, str]],
    correct_alternative_position: int | None,
) -> None:
    if stem is None:
        raise QuestionCatalogValidationError("Uma questão ativa exige enunciado.")
    if len(alternatives) < 2:
        raise QuestionCatalogValidationError(
            "Uma questão ativa exige pelo menos duas alternativas distintas."
        )
    if correct_alternative_position is None:
        raise QuestionCatalogValidationError(
            "Uma questão ativa exige exatamente uma alternativa correta."
        )


def _create_revision(
    *,
    question: Question,
    stem: str | None,
    alternatives: list[tuple[str, str | None, str]],
    correct_alternative_position: int | None,
    explanation: str | None,
    trap_note: str | None,
    notes: str | None,
    change_kind: str,
    change_reason: str | None,
) -> QuestionRevision:
    latest = question.revisions.aggregate(maximum=Max("version_number"))["maximum"]
    version_number = 1 if latest is None else int(latest) + 1
    revision = QuestionRevision.objects.create(
        workspace_id=question.workspace_id,
        question=question,
        version_number=version_number,
        is_current=False,
        stem=stem,
        explanation=explanation,
        trap_note=trap_note,
        notes=notes,
        change_kind=change_kind,
        change_reason=change_reason,
    )
    rows = [
        Alternative(
            workspace_id=question.workspace_id,
            question_revision=revision,
            position=position,
            label=label,
            text=text_value,
            text_key=text_key,
        )
        for position, (text_value, label, text_key) in enumerate(alternatives, start=1)
    ]
    Alternative.objects.bulk_create(rows)
    if correct_alternative_position is not None:
        correct = rows[correct_alternative_position - 1]
        QuestionRevision.objects.filter(pk=revision.id).update(correct_alternative_id=correct.id)
        revision.correct_alternative_id = correct.id
    question.revisions.filter(is_current=True).update(is_current=False)
    QuestionRevision.objects.filter(pk=revision.id).update(is_current=True)
    revision.is_current = True
    return revision


def _origin_has_data(value: QuestionOriginInput) -> bool:
    return (
        value.source_id is not None
        or bool(value.source_name and value.source_name.strip())
        or value.exam_id is not None
        or bool(value.exam_name and value.exam_name.strip())
        or value.board_id is not None
        or bool(value.board_name and value.board_name.strip())
        or value.reference_year is not None
        or bool(value.reference_text and value.reference_text.strip())
    )


def _resolve_catalog_origin(
    *, workspace_id: uuid.UUID, value: QuestionOriginInput, clock: Clock | None
) -> QuestionOriginInput:
    """Crie/reuse referências informadas no cadastro dentro da transação da questão."""
    if value.source_id is not None and value.source_name:
        raise QuestionCatalogValidationError(
            "Escolha uma fonte existente ou informe uma nova fonte."
        )
    if value.exam_id is not None and value.exam_name:
        raise QuestionCatalogValidationError(
            "Escolha uma prova existente ou informe uma nova prova."
        )
    if value.board_id is not None and value.board_name:
        raise QuestionCatalogValidationError(
            "Escolha uma banca existente ou informe uma nova banca."
        )
    if value.exam_id is not None and (value.board_id is not None or value.board_name):
        raise QuestionCatalogValidationError(
            "Uma prova existente já define sua banca, quando houver."
        )
    if (value.exam_id is not None or value.exam_name) and value.reference_year is not None:
        raise QuestionCatalogValidationError(
            "Com prova, o ano de referência deriva da própria prova."
        )

    source_id = value.source_id
    if value.source_name and value.source_name.strip():
        if value.source_type is None:
            raise QuestionCatalogValidationError("Informe o tipo da nova fonte.")
        source_id = create_or_reuse_source(
            workspace_id=workspace_id,
            source_type=value.source_type,
            name=value.source_name,
            locator_url=value.source_url,
            notes=value.source_notes,
        ).id

    board_id = value.board_id
    if value.board_name and value.board_name.strip():
        board_id = create_or_reuse_board(
            workspace_id=workspace_id,
            name=value.board_name,
            website_url=value.board_website_url,
        ).id

    exam_id = value.exam_id
    if value.exam_name and value.exam_name.strip():
        exam_id = create_or_reuse_exam(
            workspace_id=workspace_id,
            name=value.exam_name,
            board_id=board_id,
            year=value.exam_year,
            clock=clock,
        ).id
        board_id = None
    elif exam_id is not None:
        board_id = None

    return QuestionOriginInput(
        source_id=source_id,
        exam_id=exam_id,
        board_id=board_id,
        reference_year=value.reference_year,
        reference_text=value.reference_text,
    )


def _validate_origin_input(
    *,
    workspace: Workspace,
    value: QuestionOriginInput,
    clock: Clock | None,
) -> tuple[Source | None, Exam | None, Board | None, str | None]:
    if value.exam_id is not None and value.board_id is not None:
        raise QuestionCatalogValidationError("Prova e banca direta não podem coexistir.")
    if value.exam_id is not None and value.reference_year is not None:
        raise QuestionCatalogValidationError(
            "Com prova, o ano de referência deriva da própria prova."
        )
    validate_reference_year(value.reference_year, workspace=workspace, clock=clock)
    reference_text = normalize_optional_question_text(
        value.reference_text,
        field_label="A referência textual",
        max_length=QUESTION_REFERENCE_MAX_LENGTH,
    )

    def active_reference[ReferenceT: OriginCatalogItem](
        queryset: models.QuerySet[ReferenceT], identifier: uuid.UUID | None, label: str
    ) -> ReferenceT | None:
        if identifier is None:
            return None
        item = queryset.filter(pk=identifier, workspace=workspace).first()
        if item is None:
            raise QuestionCatalogNotFoundError(f"{label} não encontrada no Workspace.")
        if item.status != OriginStatus.ACTIVE:
            raise QuestionCatalogStateConflictError(f"{label} precisa estar ativa.")
        return item

    source = active_reference(Source.objects.all(), value.source_id, "Source")
    exam = active_reference(Exam.objects.all(), value.exam_id, "Exam")
    board = active_reference(Board.objects.all(), value.board_id, "Board")
    if exam is not None and exam.board_id is not None:
        exam_board = Board.objects.filter(pk=exam.board_id, workspace=workspace).first()
        if exam_board is None or exam_board.status != OriginStatus.ACTIVE:
            raise QuestionCatalogValidationError(
                "A Board derivada do Exam deve estar ativa no mesmo Workspace."
            )
    return source, exam, board, reference_text


def _replace_origin(
    *,
    question: Question,
    workspace: Workspace,
    value: QuestionOriginInput | None,
    clock: Clock | None,
) -> QuestionOrigin | None:
    existing = QuestionOrigin.objects.filter(question=question).first()
    if value is None or not _origin_has_data(value):
        if existing is not None:
            existing.delete()
        return None
    resolved = _resolve_catalog_origin(workspace_id=workspace.id, value=value, clock=clock)
    source, exam, board, reference_text = _validate_origin_input(
        workspace=workspace,
        value=resolved,
        clock=clock,
    )
    if existing is None:
        return QuestionOrigin.objects.create(
            workspace=workspace,
            question=question,
            source=source,
            exam=exam,
            board=board,
            reference_year=resolved.reference_year,
            reference_text=reference_text,
        )
    existing.source = source
    existing.exam = exam
    existing.board = board
    existing.reference_year = resolved.reference_year
    existing.reference_text = reference_text
    existing.lock_version += 1
    existing.save()
    return existing


def _locked_question(*, workspace_id: uuid.UUID, question_id: uuid.UUID) -> Question:
    try:
        return Question.objects.select_for_update().get(
            pk=question_id,
            workspace_id=workspace_id,
        )
    except Question.DoesNotExist as error:
        raise QuestionCatalogNotFoundError("Questão não encontrada no Workspace.") from error


def _check_question_lock(question: Question, expected_lock_version: int) -> None:
    if question.lock_version != expected_lock_version:
        raise QuestionCatalogConcurrencyError("A questão mudou; recarregue a versão atual.")


@transaction.atomic
def create_draft(
    *,
    workspace_id: uuid.UUID,
    draft_title: str | None = None,
    discipline_id: uuid.UUID | None = None,
    subject_id: uuid.UUID | None = None,
    subsubject_id: uuid.UUID | None = None,
    difficulty: str | None = None,
    stem: str | None = None,
    alternatives: list[AlternativeInput | str] | tuple[AlternativeInput | str, ...] = (),
    correct_alternative_position: int | None = None,
    explanation: str | None = None,
    trap_note: str | None = None,
    notes: str | None = None,
    origin: QuestionOriginInput | None = None,
    clock: Clock | None = None,
) -> Question:
    """Crie rascunho mínimo ou com uma primeira revisão parcial imutável."""
    workspace = _get_question_workspace(workspace_id)
    normalized_title = _normalize_draft_title(draft_title)
    _validate_difficulty(difficulty)
    discipline, subject, subsubject = _get_taxonomy(
        workspace_id=workspace_id,
        discipline_id=discipline_id,
        subject_id=subject_id,
        subsubject_id=subsubject_id,
        required=False,
    )
    content = _normalize_revision_content(
        stem=stem,
        alternatives=alternatives,
        correct_alternative_position=correct_alternative_position,
        explanation=explanation,
        trap_note=trap_note,
        notes=notes,
        change_kind=RevisionChangeKind.INITIAL,
        change_reason=None,
    )
    if normalized_title is None and not _has_versioned_content(
        stem=content[0],
        alternatives=content[1],
        explanation=content[3],
        trap_note=content[4],
        notes=content[5],
    ):
        raise QuestionCatalogValidationError(
            "O rascunho exige título provisório ou algum conteúdo versionável."
        )
    question = Question.objects.create(
        workspace=workspace,
        discipline=discipline,
        subject=subject,
        subsubject=subsubject,
        difficulty=difficulty,
        draft_title=normalized_title,
    )
    if _has_versioned_content(
        stem=content[0],
        alternatives=content[1],
        explanation=content[3],
        trap_note=content[4],
        notes=content[5],
    ):
        _create_revision(
            question=question,
            stem=content[0],
            alternatives=content[1],
            correct_alternative_position=content[2],
            explanation=content[3],
            trap_note=content[4],
            notes=content[5],
            change_kind=RevisionChangeKind.INITIAL,
            change_reason=content[6],
        )
    _replace_origin(question=question, workspace=workspace, value=origin, clock=clock)
    return question


@transaction.atomic
def create_active(
    *,
    workspace_id: uuid.UUID,
    discipline_id: uuid.UUID,
    subject_id: uuid.UUID,
    stem: str,
    alternatives: list[AlternativeInput | str] | tuple[AlternativeInput | str, ...],
    correct_alternative_position: int,
    subsubject_id: uuid.UUID | None = None,
    difficulty: str | None = None,
    draft_title: str | None = None,
    explanation: str | None = None,
    trap_note: str | None = None,
    notes: str | None = None,
    origin: QuestionOriginInput | None = None,
    clock: Clock | None = None,
) -> Question:
    """Crie atomicamente questão, revisão, alternativas, gabarito e origem opcionais."""
    workspace = _get_question_workspace(workspace_id)
    _validate_difficulty(difficulty)
    discipline, subject, subsubject = _get_taxonomy(
        workspace_id=workspace_id,
        discipline_id=discipline_id,
        subject_id=subject_id,
        subsubject_id=subsubject_id,
        required=True,
    )
    content = _normalize_revision_content(
        stem=stem,
        alternatives=alternatives,
        correct_alternative_position=correct_alternative_position,
        explanation=explanation,
        trap_note=trap_note,
        notes=notes,
        change_kind=RevisionChangeKind.INITIAL,
        change_reason=None,
    )
    _validate_active_revision(
        stem=content[0],
        alternatives=content[1],
        correct_alternative_position=content[2],
    )
    question = Question.objects.create(
        workspace=workspace,
        discipline=discipline,
        subject=subject,
        subsubject=subsubject,
        difficulty=difficulty,
        draft_title=_normalize_draft_title(draft_title),
    )
    _create_revision(
        question=question,
        stem=content[0],
        alternatives=content[1],
        correct_alternative_position=content[2],
        explanation=content[3],
        trap_note=content[4],
        notes=content[5],
        change_kind=RevisionChangeKind.INITIAL,
        change_reason=content[6],
    )
    now = (clock or SystemClock()).now().value
    Question.objects.filter(pk=question.id).update(
        status=QuestionStatus.ACTIVE,
        activated_at=now,
        updated_at=now,
    )
    _replace_origin(question=question, workspace=workspace, value=origin, clock=clock)
    question.refresh_from_db()
    return question


@transaction.atomic
def complete_draft(
    *,
    workspace_id: uuid.UUID,
    question_id: uuid.UUID,
    expected_lock_version: int,
    discipline_id: uuid.UUID,
    subject_id: uuid.UUID,
    stem: str,
    alternatives: list[AlternativeInput | str] | tuple[AlternativeInput | str, ...],
    correct_alternative_position: int,
    subsubject_id: uuid.UUID | None = None,
    difficulty: str | None = None,
    draft_title: str | None = None,
    explanation: str | None = None,
    trap_note: str | None = None,
    notes: str | None = None,
    origin: QuestionOriginInput | None = None,
    clock: Clock | None = None,
) -> Question:
    """Complete e ative um rascunho em uma única transação do agregado."""
    question = _locked_question(workspace_id=workspace_id, question_id=question_id)
    _check_question_lock(question, expected_lock_version)
    if question.status != QuestionStatus.DRAFT:
        raise QuestionCatalogStateConflictError("Somente um rascunho pode ser ativado neste fluxo.")
    workspace = _get_question_workspace(workspace_id)
    _validate_difficulty(difficulty)
    discipline, subject, subsubject = _get_taxonomy(
        workspace_id=workspace_id,
        discipline_id=discipline_id,
        subject_id=subject_id,
        subsubject_id=subsubject_id,
        required=True,
    )
    content = _normalize_revision_content(
        stem=stem,
        alternatives=alternatives,
        correct_alternative_position=correct_alternative_position,
        explanation=explanation,
        trap_note=trap_note,
        notes=notes,
        change_kind=RevisionChangeKind.INITIAL,
        change_reason=None,
    )
    _validate_active_revision(
        stem=content[0],
        alternatives=content[1],
        correct_alternative_position=content[2],
    )
    _create_revision(
        question=question,
        stem=content[0],
        alternatives=content[1],
        correct_alternative_position=content[2],
        explanation=content[3],
        trap_note=content[4],
        notes=content[5],
        change_kind=RevisionChangeKind.INITIAL,
        change_reason=content[6],
    )
    _replace_origin(question=question, workspace=workspace, value=origin, clock=clock)
    now = (clock or SystemClock()).now().value
    updated = Question.objects.filter(
        pk=question.id,
        workspace_id=workspace_id,
        lock_version=expected_lock_version,
    ).update(
        discipline=discipline,
        subject=subject,
        subsubject=subsubject,
        difficulty=difficulty,
        draft_title=_normalize_draft_title(draft_title),
        status=QuestionStatus.ACTIVE,
        activated_at=now,
        archived_at=None,
        lock_version=F("lock_version") + 1,
        updated_at=now,
    )
    if updated != 1:
        raise QuestionCatalogConcurrencyError("A questão mudou; recarregue a versão atual.")
    question.refresh_from_db()
    return question


@transaction.atomic
def save_revision(
    *,
    workspace_id: uuid.UUID,
    question_id: uuid.UUID,
    expected_lock_version: int,
    stem: str | None,
    alternatives: list[AlternativeInput | str] | tuple[AlternativeInput | str, ...],
    correct_alternative_position: int | None,
    explanation: str | None = None,
    trap_note: str | None = None,
    notes: str | None = None,
    change_kind: str = RevisionChangeKind.NON_CRITICAL_EDIT,
    change_reason: str | None = None,
    activate: bool = False,
    clock: Clock | None = None,
) -> QuestionRevision:
    """Publique novo snapshot e troque a revisão corrente atomicamente."""
    question = _locked_question(workspace_id=workspace_id, question_id=question_id)
    _check_question_lock(question, expected_lock_version)
    if question.status == QuestionStatus.ARCHIVED:
        raise QuestionCatalogStateConflictError("Questão arquivada não pode receber revisão.")
    content = _normalize_revision_content(
        stem=stem,
        alternatives=alternatives,
        correct_alternative_position=correct_alternative_position,
        explanation=explanation,
        trap_note=trap_note,
        notes=notes,
        change_kind=change_kind,
        change_reason=change_reason,
    )
    if not _has_versioned_content(
        stem=content[0],
        alternatives=content[1],
        explanation=content[3],
        trap_note=content[4],
        notes=content[5],
    ):
        raise QuestionCatalogValidationError("Uma revisão exige algum conteúdo versionável.")
    becoming_active = activate or question.status == QuestionStatus.ACTIVE
    if becoming_active:
        _get_taxonomy(
            workspace_id=workspace_id,
            discipline_id=question.discipline_id,
            subject_id=question.subject_id,
            subsubject_id=question.subsubject_id,
            required=True,
        )
        _validate_active_revision(
            stem=content[0],
            alternatives=content[1],
            correct_alternative_position=content[2],
        )
    revision = _create_revision(
        question=question,
        stem=content[0],
        alternatives=content[1],
        correct_alternative_position=content[2],
        explanation=content[3],
        trap_note=content[4],
        notes=content[5],
        change_kind=change_kind,
        change_reason=content[6],
    )
    now = (clock or SystemClock()).now().value
    update_values: dict[str, object] = {
        "lock_version": F("lock_version") + 1,
        "updated_at": now,
    }
    if activate:
        update_values.update(status=QuestionStatus.ACTIVE, activated_at=now, archived_at=None)
    updated = Question.objects.filter(
        pk=question.id,
        workspace_id=workspace_id,
        lock_version=expected_lock_version,
    ).update(**update_values)
    if updated != 1:
        raise QuestionCatalogConcurrencyError("A questão mudou; recarregue a versão atual.")
    return revision


@transaction.atomic
def update_question_metadata(
    *,
    workspace_id: uuid.UUID,
    question_id: uuid.UUID,
    expected_lock_version: int,
    discipline_id: uuid.UUID | None,
    subject_id: uuid.UUID | None,
    subsubject_id: uuid.UUID | None = None,
    difficulty: str | None = None,
    draft_title: str | None = None,
    clock: Clock | None = None,
) -> Question:
    """Atualize apenas metadados atuais, sem criar revisão de conteúdo."""
    question = _locked_question(workspace_id=workspace_id, question_id=question_id)
    _check_question_lock(question, expected_lock_version)
    if question.status == QuestionStatus.ARCHIVED:
        raise QuestionCatalogStateConflictError("Questão arquivada não pode ser editada.")
    _validate_difficulty(difficulty)
    discipline, subject, subsubject = _get_taxonomy(
        workspace_id=workspace_id,
        discipline_id=discipline_id,
        subject_id=subject_id,
        subsubject_id=subsubject_id,
        required=question.status == QuestionStatus.ACTIVE,
    )
    now = (clock or SystemClock()).now().value
    updated = Question.objects.filter(
        pk=question.id,
        workspace_id=workspace_id,
        lock_version=expected_lock_version,
    ).update(
        discipline=discipline,
        subject=subject,
        subsubject=subsubject,
        difficulty=difficulty,
        draft_title=_normalize_draft_title(draft_title),
        lock_version=F("lock_version") + 1,
        updated_at=now,
    )
    if updated != 1:
        raise QuestionCatalogConcurrencyError("A questão mudou; recarregue a versão atual.")
    question.refresh_from_db()
    return question


@transaction.atomic
def set_question_origin(
    *,
    workspace_id: uuid.UUID,
    question_id: uuid.UUID,
    expected_lock_version: int,
    origin: QuestionOriginInput | None,
    clock: Clock | None = None,
) -> QuestionOrigin | None:
    """Crie, substitua ou remova a origem 0..1 dentro do agregado."""
    question = _locked_question(workspace_id=workspace_id, question_id=question_id)
    _check_question_lock(question, expected_lock_version)
    if question.status == QuestionStatus.ARCHIVED:
        raise QuestionCatalogStateConflictError("Questão arquivada não pode ser editada.")
    workspace = _get_question_workspace(workspace_id)
    result = _replace_origin(question=question, workspace=workspace, value=origin, clock=clock)
    now = (clock or SystemClock()).now().value
    updated = Question.objects.filter(
        pk=question.id,
        workspace_id=workspace_id,
        lock_version=expected_lock_version,
    ).update(lock_version=F("lock_version") + 1, updated_at=now)
    if updated != 1:
        raise QuestionCatalogConcurrencyError("A questão mudou; recarregue a versão atual.")
    return result


@transaction.atomic
def archive_question(
    *,
    workspace_id: uuid.UUID,
    question_id: uuid.UUID,
    expected_lock_version: int,
    clock: Clock | None = None,
) -> Question:
    """Arquive a identidade sem apagar suas revisões ou origem."""
    question = _locked_question(workspace_id=workspace_id, question_id=question_id)
    _check_question_lock(question, expected_lock_version)
    if question.status == QuestionStatus.ARCHIVED:
        raise QuestionCatalogStateConflictError("A questão já está arquivada.")
    now = (clock or SystemClock()).now().value
    updated = Question.objects.filter(
        pk=question.id,
        workspace_id=workspace_id,
        lock_version=expected_lock_version,
    ).update(
        status=QuestionStatus.ARCHIVED,
        archived_at=now,
        lock_version=F("lock_version") + 1,
        updated_at=now,
    )
    if updated != 1:
        raise QuestionCatalogConcurrencyError("A questão mudou; recarregue a versão atual.")
    question.refresh_from_db()
    return question


def _revision_matches(
    *,
    revision: QuestionRevision | None,
    stem: str | None,
    alternatives: list[tuple[str, str | None, str]],
    correct_alternative_position: int | None,
    explanation: str | None,
    trap_note: str | None,
    notes: str | None,
) -> bool:
    """Compare a entrada normalizada com o snapshot corrente, sem o alterar."""
    if revision is None:
        return not _has_versioned_content(
            stem=stem,
            alternatives=alternatives,
            explanation=explanation,
            trap_note=trap_note,
            notes=notes,
        )
    current_alternatives = list(revision.alternatives.order_by("position"))
    current_answer = _revision_answer_position(
        revision=revision,
        alternatives=current_alternatives,
    )
    return (
        revision.stem == stem
        and revision.explanation == explanation
        and revision.trap_note == trap_note
        and revision.notes == notes
        and [(item.text, item.label) for item in current_alternatives]
        == [(text, label) for text, label, _text_key in alternatives]
        and current_answer == correct_alternative_position
    )


def _revision_answer_position(
    *, revision: QuestionRevision, alternatives: list[Alternative]
) -> int | None:
    return next(
        (
            alternative.position
            for alternative in alternatives
            if alternative.id == revision.correct_alternative_id
        ),
        None,
    )


def _classify_revision_change(
    *,
    revision: QuestionRevision | None,
    alternatives: list[tuple[str, str | None, str]],
    correct_alternative_position: int | None,
    stem: str | None,
) -> tuple[str, str | None]:
    """Classifique de modo determinístico a mudança que será persistida."""
    if revision is None:
        return RevisionChangeKind.INITIAL, None
    current_alternatives = list(revision.alternatives.order_by("position"))
    current_answer = _revision_answer_position(
        revision=revision,
        alternatives=current_alternatives,
    )
    alternatives_changed = [(item.text, item.label) for item in current_alternatives] != [
        (text, label) for text, label, _text_key in alternatives
    ]
    if alternatives_changed or current_answer != correct_alternative_position:
        return (
            RevisionChangeKind.CRITICAL_CORRECTION,
            "Alternativas ou gabarito alterados antes de tentativas.",
        )
    if revision.stem == stem:
        return RevisionChangeKind.ENRICHMENT, None
    return RevisionChangeKind.NON_CRITICAL_EDIT, None


@transaction.atomic
def edit_question(
    *,
    workspace_id: uuid.UUID,
    question_id: uuid.UUID,
    expected_lock_version: int,
    discipline_id: uuid.UUID | None,
    subject_id: uuid.UUID | None,
    subsubject_id: uuid.UUID | None = None,
    difficulty: str | None = None,
    draft_title: str | None = None,
    stem: str | None = None,
    alternatives: list[AlternativeInput | str] | tuple[AlternativeInput | str, ...] = (),
    correct_alternative_position: int | None = None,
    explanation: str | None = None,
    trap_note: str | None = None,
    notes: str | None = None,
    origin: QuestionOriginInput | None = None,
    clock: Clock | None = None,
) -> Question:
    """Edite metadados, origem e conteúdo como um único comando do agregado."""
    question = _locked_question(workspace_id=workspace_id, question_id=question_id)
    _check_question_lock(question, expected_lock_version)
    if question.status == QuestionStatus.ARCHIVED:
        raise QuestionCatalogStateConflictError("Questão arquivada não pode ser editada.")

    workspace = _get_question_workspace(workspace_id)
    _validate_difficulty(difficulty)
    discipline, subject, subsubject = _get_taxonomy(
        workspace_id=workspace_id,
        discipline_id=discipline_id,
        subject_id=subject_id,
        subsubject_id=subsubject_id,
        required=question.status == QuestionStatus.ACTIVE,
    )
    content = _normalize_revision_content(
        stem=stem,
        alternatives=alternatives,
        correct_alternative_position=correct_alternative_position,
        explanation=explanation,
        trap_note=trap_note,
        notes=notes,
        change_kind=RevisionChangeKind.NON_CRITICAL_EDIT,
        change_reason=None,
    )
    if question.status == QuestionStatus.ACTIVE:
        _validate_active_revision(
            stem=content[0],
            alternatives=content[1],
            correct_alternative_position=content[2],
        )

    current_revision = question.revisions.filter(is_current=True).first()
    if not _revision_matches(
        revision=current_revision,
        stem=content[0],
        alternatives=content[1],
        correct_alternative_position=content[2],
        explanation=content[3],
        trap_note=content[4],
        notes=content[5],
    ):
        if not _has_versioned_content(
            stem=content[0],
            alternatives=content[1],
            explanation=content[3],
            trap_note=content[4],
            notes=content[5],
        ):
            raise QuestionCatalogValidationError("Uma revisão exige algum conteúdo versionável.")
        change_kind, change_reason = _classify_revision_change(
            revision=current_revision,
            alternatives=content[1],
            correct_alternative_position=content[2],
            stem=content[0],
        )
        _create_revision(
            question=question,
            stem=content[0],
            alternatives=content[1],
            correct_alternative_position=content[2],
            explanation=content[3],
            trap_note=content[4],
            notes=content[5],
            change_kind=change_kind,
            change_reason=change_reason,
        )

    _replace_origin(question=question, workspace=workspace, value=origin, clock=clock)
    now = (clock or SystemClock()).now().value
    updated = Question.objects.filter(
        pk=question.id,
        workspace_id=workspace_id,
        lock_version=expected_lock_version,
    ).update(
        discipline=discipline,
        subject=subject,
        subsubject=subsubject,
        difficulty=difficulty,
        draft_title=_normalize_draft_title(draft_title),
        lock_version=F("lock_version") + 1,
        updated_at=now,
    )
    if updated != 1:
        raise QuestionCatalogConcurrencyError("A questão mudou; recarregue a versão atual.")
    question.refresh_from_db()
    return question


class QuestionCommandService:
    """Fronteira explícita de escrita do agregado Question."""

    create_draft = staticmethod(create_draft)
    create_active = staticmethod(create_active)
    complete_draft = staticmethod(complete_draft)
    edit = staticmethod(edit_question)
    save_revision = staticmethod(save_revision)
    update_metadata = staticmethod(update_question_metadata)
    set_origin = staticmethod(set_question_origin)
    archive = staticmethod(archive_question)
