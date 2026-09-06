"""CT-073/074/081/082/138 e invariantes do catálogo de origem da V0.2."""

import json
import os
import subprocess
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, transaction
from django.db.migrations.loader import MigrationLoader
from django.db.models.deletion import ProtectedError

from modules.accounts.models import User, Workspace
from modules.questions.exceptions import (
    OriginCatalogConcurrencyError,
    OriginCatalogNotFoundError,
    OriginCatalogStateConflictError,
    OriginCatalogValidationError,
)
from modules.questions.models import Board, Exam, OriginStatus, Source, SourceType
from modules.questions.selectors import (
    get_board,
    get_exam,
    get_source,
    list_archived_boards,
    list_archived_exams,
    list_archived_sources,
    list_boards,
    list_exams,
    list_sources,
)
from modules.questions.services import (
    archive_board,
    archive_exam,
    archive_source,
    create_or_reuse_board,
    create_or_reuse_exam,
    create_or_reuse_source,
)
from modules.questions.validators import normalize_origin_name
from shared.domain.time import FixedClock, Instant

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _workspace(*, email: str, timezone_name: str = "America/Sao_Paulo") -> Workspace:
    user = User.objects.create_user(email=email)
    return Workspace.objects.create(
        owner_user=user,
        name=f"Espaço {email}",
        timezone_name=timezone_name,
    )


@pytest.mark.parametrize("invalid", ["", "   ", "x" * 121, 7])
def test_origin_normalizer_reuses_the_canonical_name_policy(invalid: object) -> None:
    normalized = normalize_origin_name("  a\u0301LGEBRA\t ")

    assert normalized.display == "áLGEBRA"
    assert normalized.key == "álgebra"
    with pytest.raises(OriginCatalogValidationError):
        normalize_origin_name(invalid)  # type: ignore[arg-type]


@pytest.mark.django_db
def test_ct138_create_reuses_equivalent_active_references_within_workspace() -> None:
    workspace = _workspace(email="reuse@example.test")
    board = create_or_reuse_board(
        workspace_id=workspace.id,
        name="  CESPE  ",
        website_url=" https://www.cebraspe.org.br ",
    )
    same_board = create_or_reuse_board(workspace_id=workspace.id, name="cespe")
    exam = create_or_reuse_exam(
        workspace_id=workspace.id,
        board_id=board.id,
        name="Concurso Nacional",
        year=2026,
    )
    same_exam = create_or_reuse_exam(
        workspace_id=workspace.id,
        board_id=board.id,
        name=" concurso   nacional ",
        year=2026,
    )
    source = create_or_reuse_source(
        workspace_id=workspace.id,
        source_type=SourceType.BOOK,
        name="Curso de Matemática",
        locator_url="https://example.test/livro",
        notes="  Capítulo 1  ",
    )
    same_source = create_or_reuse_source(
        workspace_id=workspace.id,
        source_type=SourceType.BOOK,
        name=" curso de matemática ",
    )

    assert same_board.id == board.id
    assert same_exam.id == exam.id
    assert same_source.id == source.id
    assert board.website_url == "https://www.cebraspe.org.br"
    assert source.notes == "Capítulo 1"
    assert Board.objects.count() == Exam.objects.count() == Source.objects.count() == 1


@pytest.mark.django_db
def test_equivalence_keys_preserve_meaningful_exam_and_source_differences() -> None:
    workspace = _workspace(email="keys@example.test")
    board_a = create_or_reuse_board(workspace_id=workspace.id, name="Banca A")
    board_b = create_or_reuse_board(workspace_id=workspace.id, name="Banca B")

    exams = {
        create_or_reuse_exam(workspace_id=workspace.id, name="Prova"),
        create_or_reuse_exam(workspace_id=workspace.id, name="Prova", year=2026),
        create_or_reuse_exam(workspace_id=workspace.id, name="Prova", board_id=board_a.id),
        create_or_reuse_exam(
            workspace_id=workspace.id,
            name="Prova",
            board_id=board_b.id,
            year=2026,
        ),
    }
    book = create_or_reuse_source(
        workspace_id=workspace.id,
        source_type=SourceType.BOOK,
        name="Referência",
    )
    website = create_or_reuse_source(
        workspace_id=workspace.id,
        source_type=SourceType.WEBSITE,
        name="Referência",
    )

    assert len(exams) == 4
    assert book.id != website.id


@pytest.mark.django_db
def test_ct138_year_boundaries_use_workspace_calendar_and_controlled_clock() -> None:
    workspace = _workspace(
        email="year@example.test",
        timezone_name="Pacific/Kiritimati",
    )
    clock = FixedClock(Instant(datetime(2026, 12, 31, 12, 30, tzinfo=UTC)))

    minimum = create_or_reuse_exam(
        workspace_id=workspace.id,
        name="Prova antiga",
        year=1900,
        clock=clock,
    )
    maximum = create_or_reuse_exam(
        workspace_id=workspace.id,
        name="Prova futura",
        year=2029,
        clock=clock,
    )

    assert minimum.year == 1900
    assert maximum.year == 2029
    with pytest.raises(OriginCatalogValidationError, match="1900 e 2029"):
        create_or_reuse_exam(
            workspace_id=workspace.id,
            name="Inválida antiga",
            year=1899,
            clock=clock,
        )
    with pytest.raises(OriginCatalogValidationError, match="1900 e 2029"):
        create_or_reuse_exam(
            workspace_id=workspace.id,
            name="Inválida futura",
            year=2030,
            clock=clock,
        )
    with pytest.raises(OriginCatalogValidationError, match="inteiro"):
        create_or_reuse_exam(
            workspace_id=workspace.id,
            name="Inválida booleana",
            year=True,
            clock=clock,
        )


@pytest.mark.django_db
def test_ct138_exam_board_year_and_catalog_details_are_optional() -> None:
    workspace = _workspace(email="optional@example.test")
    board = create_or_reuse_board(workspace_id=workspace.id, name="Sem site")
    exam = create_or_reuse_exam(workspace_id=workspace.id, name="Prova sem metadados")
    source = create_or_reuse_source(
        workspace_id=workspace.id,
        source_type=SourceType.OTHER,
        name="Sem detalhes",
        locator_url="   ",
        notes=" ",
    )

    assert board.website_url is None
    assert exam.board is None
    assert exam.year is None
    assert source.locator_url is None
    assert source.notes is None


@pytest.mark.django_db
def test_ct074_creation_and_queries_are_fully_workspace_scoped() -> None:
    workspace_a = _workspace(email="origin-a@example.test")
    workspace_b = _workspace(email="origin-b@example.test")
    board_a = create_or_reuse_board(workspace_id=workspace_a.id, name="Mesma banca")
    board_b = create_or_reuse_board(workspace_id=workspace_b.id, name=" mesma banca ")
    exam_a = create_or_reuse_exam(
        workspace_id=workspace_a.id,
        board_id=board_a.id,
        name="Prova A",
    )
    source_a = create_or_reuse_source(
        workspace_id=workspace_a.id,
        source_type=SourceType.PDF,
        name="Material A",
    )

    assert board_a.id != board_b.id
    assert list(list_boards(workspace_id=workspace_a.id)) == [board_a]
    assert list(list_boards(workspace_id=workspace_b.id)) == [board_b]
    assert list(list_exams(workspace_id=workspace_b.id)) == []
    assert list(list_sources(workspace_id=workspace_b.id)) == []
    for getter, identifier in (
        (get_board, board_a.id),
        (get_exam, exam_a.id),
        (get_source, source_a.id),
    ):
        with pytest.raises(OriginCatalogNotFoundError):
            getter(workspace_id=workspace_b.id, **{f"{getter.__name__[4:]}_id": identifier})

    with pytest.raises(OriginCatalogNotFoundError):
        create_or_reuse_exam(
            workspace_id=workspace_a.id,
            board_id=board_b.id,
            name="Mistura indevida",
        )
    assert Exam.objects.count() == 1


@pytest.mark.django_db
def test_ct074_model_guard_rejects_cross_workspace_exam_board() -> None:
    workspace_a = _workspace(email="guard-origin-a@example.test")
    workspace_b = _workspace(email="guard-origin-b@example.test")
    board_b = create_or_reuse_board(workspace_id=workspace_b.id, name="Banca B")

    with pytest.raises(ValidationError, match="mesmo Workspace"):
        Exam.objects.create(
            workspace=workspace_a,
            board=board_b,
            name="Prova inválida",
        )

    assert Exam.objects.count() == 0


@pytest.mark.django_db
def test_archiving_preserves_history_and_allows_new_active_equivalent() -> None:
    workspace = _workspace(email="archive-origin@example.test")
    board = create_or_reuse_board(workspace_id=workspace.id, name="Banca")
    exam = create_or_reuse_exam(
        workspace_id=workspace.id,
        board_id=board.id,
        name="Prova",
        year=2026,
    )
    source = create_or_reuse_source(
        workspace_id=workspace.id,
        source_type=SourceType.COURSE,
        name="Curso",
    )
    clock = FixedClock(Instant(datetime(2026, 9, 6, 10, 0, tzinfo=UTC)))

    archived_board = archive_board(
        workspace_id=workspace.id,
        board_id=board.id,
        expected_lock_version=1,
        clock=clock,
    )
    archived_exam = archive_exam(
        workspace_id=workspace.id,
        exam_id=exam.id,
        expected_lock_version=1,
        clock=clock,
    )
    archived_source = archive_source(
        workspace_id=workspace.id,
        source_id=source.id,
        expected_lock_version=1,
        clock=clock,
    )
    replacement_board = create_or_reuse_board(workspace_id=workspace.id, name=" banca ")
    replacement_source = create_or_reuse_source(
        workspace_id=workspace.id,
        source_type=SourceType.COURSE,
        name=" curso ",
    )

    for item in (archived_board, archived_exam, archived_source):
        assert item.status == OriginStatus.ARCHIVED
        assert item.archived_at == clock.now().value
        assert item.lock_version == 2
    assert replacement_board.id != board.id
    assert replacement_source.id != source.id
    assert list(list_archived_boards(workspace_id=workspace.id)) == [archived_board]
    assert list(list_archived_exams(workspace_id=workspace.id)) == [archived_exam]
    assert list(list_archived_sources(workspace_id=workspace.id)) == [archived_source]
    assert list(list_boards(workspace_id=workspace.id)) == [replacement_board]
    assert list(list_sources(workspace_id=workspace.id)) == [replacement_source]


@pytest.mark.django_db
def test_archiving_rejects_stale_cross_workspace_and_repeated_commands() -> None:
    workspace_a = _workspace(email="archive-command-a@example.test")
    workspace_b = _workspace(email="archive-command-b@example.test")
    board = create_or_reuse_board(workspace_id=workspace_a.id, name="Banca")

    with pytest.raises(OriginCatalogNotFoundError):
        archive_board(
            workspace_id=workspace_b.id,
            board_id=board.id,
            expected_lock_version=1,
        )
    with pytest.raises(OriginCatalogConcurrencyError):
        archive_board(
            workspace_id=workspace_a.id,
            board_id=board.id,
            expected_lock_version=2,
        )
    archived = archive_board(
        workspace_id=workspace_a.id,
        board_id=board.id,
        expected_lock_version=1,
    )
    with pytest.raises(OriginCatalogStateConflictError):
        archive_board(
            workspace_id=workspace_a.id,
            board_id=board.id,
            expected_lock_version=archived.lock_version,
        )


@pytest.mark.django_db
def test_exam_under_archived_board_is_historical_but_not_available() -> None:
    workspace = _workspace(email="availability@example.test")
    board = create_or_reuse_board(workspace_id=workspace.id, name="Banca")
    exam = create_or_reuse_exam(
        workspace_id=workspace.id,
        board_id=board.id,
        name="Prova",
    )
    archive_board(
        workspace_id=workspace.id,
        board_id=board.id,
        expected_lock_version=1,
    )

    exam.refresh_from_db()
    assert exam.status == OriginStatus.ACTIVE
    assert list(list_exams(workspace_id=workspace.id)) == []
    assert get_exam(workspace_id=workspace.id, exam_id=exam.id) == exam
    with pytest.raises(OriginCatalogStateConflictError):
        create_or_reuse_exam(
            workspace_id=workspace.id,
            board_id=board.id,
            name="Outra prova",
        )


@pytest.mark.django_db(transaction=True)
def test_ct073_database_constraints_cover_uniqueness_states_types_year_and_lock() -> None:
    workspace = _workspace(email="origin-constraints@example.test")
    board = create_or_reuse_board(workspace_id=workspace.id, name="Banca")
    exam = create_or_reuse_exam(workspace_id=workspace.id, name="Prova")
    source = create_or_reuse_source(
        workspace_id=workspace.id,
        source_type=SourceType.BOOK,
        name="Fonte",
    )

    invalid_operations = (
        lambda: Board.objects.bulk_create(
            [Board(workspace=workspace, name="Banca", name_key=board.name_key)]
        ),
        lambda: Exam.objects.bulk_create(
            [Exam(workspace=workspace, name="Prova", name_key=exam.name_key)]
        ),
        lambda: Source.objects.bulk_create(
            [
                Source(
                    workspace=workspace,
                    source_type=SourceType.BOOK,
                    name="Fonte",
                    name_key=source.name_key,
                )
            ]
        ),
        lambda: Exam.objects.filter(pk=exam.id).update(year=1899),
        lambda: Source.objects.filter(pk=source.id).update(source_type="INVALID"),
        lambda: Board.objects.filter(pk=board.id).update(status="INVALID"),
        lambda: Board.objects.filter(pk=board.id).update(
            status=OriginStatus.ARCHIVED,
            archived_at=None,
        ),
        lambda: Board.objects.filter(pk=board.id).update(lock_version=0),
    )
    for operation in invalid_operations:
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                operation()

    assert Board.objects.count() == Exam.objects.count() == Source.objects.count() == 1


@pytest.mark.django_db(transaction=True)
def test_ct073_foreign_keys_reject_orphans_and_use_protect() -> None:
    workspace = _workspace(email="origin-fk@example.test")
    board = create_or_reuse_board(workspace_id=workspace.id, name="Banca")
    create_or_reuse_exam(
        workspace_id=workspace.id,
        board_id=board.id,
        name="Prova",
    )
    create_or_reuse_source(
        workspace_id=workspace.id,
        source_type=SourceType.PDF,
        name="Fonte",
    )

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Exam.objects.bulk_create(
                [
                    Exam(
                        workspace=workspace,
                        board_id=uuid.uuid4(),
                        name="Órfã",
                        name_key="órfã",
                    )
                ]
            )
    with pytest.raises(ProtectedError):
        board.delete()
    with pytest.raises(ProtectedError):
        workspace.delete()

    assert Board.objects.filter(pk=board.id).exists()
    assert Exam.objects.count() == 1
    assert Source.objects.count() == 1


@pytest.mark.django_db
def test_invalid_urls_source_type_and_workspace_are_rejected_without_partial_data() -> None:
    workspace = _workspace(email="validation-origin@example.test")

    with pytest.raises(OriginCatalogValidationError, match="HTTP"):
        create_or_reuse_board(
            workspace_id=workspace.id,
            name="Banca",
            website_url="ftp://example.test",
        )
    with pytest.raises(OriginCatalogValidationError, match="tipo"):
        create_or_reuse_source(
            workspace_id=workspace.id,
            source_type="INVALID",
            name="Fonte",
        )
    with pytest.raises(OriginCatalogNotFoundError):
        create_or_reuse_board(workspace_id=uuid.uuid4(), name="Banca")

    assert Board.objects.count() == Source.objects.count() == 0


@pytest.mark.django_db
def test_ct081_origin_migration_remains_frozen_as_questions_root() -> None:
    loader = MigrationLoader(connection)
    migration = loader.get_migration("questions", "0001_origin_catalog")

    assert loader.graph.root_nodes("questions") == [("questions", "0001_origin_catalog")]
    assert migration.dependencies == [("accounts", "0001_initial")]
    assert {
        "questions_board",
        "questions_exam",
        "questions_source",
    }.issubset(connection.introspection.table_names())
    assert [getattr(operation, "name", None) for operation in migration.operations[:3]] == [
        "Board",
        "Exam",
        "Source",
    ]


def _run_upgrade_probe(*, from_taxonomy: bool) -> dict[str, object]:
    start_targets = (
        '[("auth", "0012_alter_user_first_name_max_length"), '
        '("errors", "0001_initial"), ("taxonomy", "0001_initial")]'
        if from_taxonomy
        else '[("auth", "0012_alter_user_first_name_max_length"), ("errors", "0001_initial")]'
    )
    probe = f"""
import json
import uuid
import django
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

django.setup()
executor = MigrationExecutor(connection)
start_targets = {start_targets}
executor.migrate(start_targets)
old_apps = executor.loader.project_state(start_targets).apps
User = old_apps.get_model("accounts", "User")
Workspace = old_apps.get_model("accounts", "Workspace")
Category = old_apps.get_model("errors", "ErrorCategory")
user_id = uuid.UUID("31111111-1111-4111-8111-111111111111")
workspace_id = uuid.UUID("32222222-2222-4222-8222-222222222222")
user = User.objects.create(id=user_id, password="!", display_name="João", status="ACTIVE")
workspace = Workspace.objects.create(
    id=workspace_id,
    owner_user=user,
    name="Meu espaço",
    timezone_name="America/Sao_Paulo",
    locale="pt-BR",
    lock_version=1,
)
Category.objects.create(
    workspace=workspace,
    code="CONCEPTUAL",
    display_name="Conceitual",
    name_key="conceitual",
    description="Categoria preservada",
)
taxonomy_count = 0
if {from_taxonomy!r}:
    Discipline = old_apps.get_model("taxonomy", "Discipline")
    Discipline.objects.create(
        workspace=workspace,
        name="Matemática",
        name_key="matemática",
    )
    taxonomy_count = Discipline.objects.count()
executor = MigrationExecutor(connection)
executor.migrate(executor.loader.graph.leaf_nodes())
final_apps = executor.loader.project_state().apps
FinalWorkspace = final_apps.get_model("accounts", "Workspace")
FinalCategory = final_apps.get_model("errors", "ErrorCategory")
FinalDiscipline = final_apps.get_model("taxonomy", "Discipline")
Board = final_apps.get_model("questions", "Board")
Exam = final_apps.get_model("questions", "Exam")
Source = final_apps.get_model("questions", "Source")
current_workspace = FinalWorkspace.objects.get(pk=workspace_id)
print(json.dumps({{
    "workspace": str(current_workspace.id),
    "timezone": current_workspace.timezone_name,
    "categories": FinalCategory.objects.filter(workspace_id=workspace_id).count(),
    "disciplines": FinalDiscipline.objects.filter(workspace_id=workspace_id).count(),
    "taxonomy_before": taxonomy_count,
    "boards": Board.objects.count(),
    "exams": Exam.objects.count(),
    "sources": Source.objects.count(),
}}))
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
    return json.loads(result.stdout.strip().splitlines()[-1])  # type: ignore[no-any-return]


def test_ct082_upgrade_from_v01_preserves_existing_data() -> None:
    snapshot = _run_upgrade_probe(from_taxonomy=False)

    assert snapshot == {
        "workspace": "32222222-2222-4222-8222-222222222222",
        "timezone": "America/Sao_Paulo",
        "categories": 1,
        "disciplines": 0,
        "taxonomy_before": 0,
        "boards": 0,
        "exams": 0,
        "sources": 0,
    }


def test_ct082_upgrade_from_stage2_preserves_taxonomy_data() -> None:
    snapshot = _run_upgrade_probe(from_taxonomy=True)

    assert snapshot == {
        "workspace": "32222222-2222-4222-8222-222222222222",
        "timezone": "America/Sao_Paulo",
        "categories": 1,
        "disciplines": 1,
        "taxonomy_before": 1,
        "boards": 0,
        "exams": 0,
        "sources": 0,
    }
