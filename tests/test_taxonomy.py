"""CT-003/004/073/074/137 e invariantes da taxonomia da V0.2."""

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
from modules.taxonomy.exceptions import (
    TaxonomyConcurrencyError,
    TaxonomyDuplicateNameError,
    TaxonomyNotFoundError,
    TaxonomyStateConflictError,
    TaxonomyValidationError,
)
from modules.taxonomy.models import Discipline, Subject, Subsubject, TaxonomyStatus
from modules.taxonomy.selectors import (
    get_discipline,
    get_subject,
    get_subsubject,
    list_archived_disciplines,
    list_archived_subjects,
    list_archived_subsubjects,
    list_disciplines,
    list_subjects,
    list_subsubjects,
)
from modules.taxonomy.services import (
    archive_discipline,
    archive_subject,
    archive_subsubject,
    create_discipline,
    create_subject,
    create_subsubject,
    rename_discipline,
    rename_subject,
    rename_subsubject,
)
from modules.taxonomy.validators import normalize_taxonomy_name
from shared.domain.time import FixedClock, Instant

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _workspace(*, email: str) -> Workspace:
    user = User.objects.create_user(email=email)
    return Workspace.objects.create(
        owner_user=user,
        name=f"Espaço {email}",
        timezone_name="America/Sao_Paulo",
    )


@pytest.mark.parametrize("invalid", ["", "   ", "x" * 121, 7])
def test_normalizer_rejects_invalid_names(invalid: object) -> None:
    with pytest.raises(TaxonomyValidationError):
        normalize_taxonomy_name(invalid)  # type: ignore[arg-type]


def test_ct003_normalizer_collapses_space_case_and_unicode_but_preserves_accents() -> None:
    algebra = normalize_taxonomy_name("Álgebra")
    equivalent = normalize_taxonomy_name("  a\u0301LGEBRA\t ")
    accented = normalize_taxonomy_name("Matemática")
    unaccented = normalize_taxonomy_name("Matematica")

    assert algebra.display == "Álgebra"
    assert equivalent.display == "áLGEBRA"
    assert algebra.key == equivalent.key == "álgebra"
    assert accented.key != unaccented.key


@pytest.mark.django_db
def test_ct003_active_uniqueness_uses_normalized_name_and_allows_archived_reuse() -> None:
    workspace = _workspace(email="normalization@example.test")
    original = create_discipline(workspace_id=workspace.id, name="Álgebra", sort_order=2)

    with pytest.raises(TaxonomyDuplicateNameError):
        create_discipline(workspace_id=workspace.id, name="  áLGEBRA  ")

    distinct = create_discipline(workspace_id=workspace.id, name="Algebra")
    archived = archive_discipline(
        workspace_id=workspace.id,
        discipline_id=original.id,
        expected_lock_version=original.lock_version,
    )
    reused = create_discipline(workspace_id=workspace.id, name=" álgebra ")

    assert original.name == "Álgebra"
    assert original.sort_order == 2
    assert distinct.name_key == "algebra"
    assert archived.status == TaxonomyStatus.ARCHIVED
    assert reused.status == TaxonomyStatus.ACTIVE
    assert Discipline.objects.count() == 3


@pytest.mark.django_db
def test_ct003_same_child_name_is_allowed_under_different_parents_only() -> None:
    workspace = _workspace(email="parents@example.test")
    discipline_a = create_discipline(workspace_id=workspace.id, name="Matemática")
    discipline_b = create_discipline(workspace_id=workspace.id, name="Física")
    subject_a = create_subject(
        workspace_id=workspace.id,
        discipline_id=discipline_a.id,
        name="Vetores",
    )
    subject_b = create_subject(
        workspace_id=workspace.id,
        discipline_id=discipline_b.id,
        name=" vetores ",
    )

    with pytest.raises(TaxonomyDuplicateNameError):
        create_subject(
            workspace_id=workspace.id,
            discipline_id=discipline_a.id,
            name="VETORES",
        )

    create_subsubject(workspace_id=workspace.id, subject_id=subject_a.id, name="Produto")
    create_subsubject(workspace_id=workspace.id, subject_id=subject_b.id, name=" produto ")
    with pytest.raises(TaxonomyDuplicateNameError):
        create_subsubject(
            workspace_id=workspace.id,
            subject_id=subject_a.id,
            name="PRODUTO",
        )

    assert Subject.objects.count() == 2
    assert Subsubject.objects.count() == 2


@pytest.mark.django_db(transaction=True)
def test_database_constraints_enforce_active_uniqueness_state_and_lock() -> None:
    workspace = _workspace(email="constraints@example.test")
    discipline = create_discipline(workspace_id=workspace.id, name="Química")

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Discipline.objects.bulk_create(
                [
                    Discipline(
                        workspace=workspace,
                        name="química",
                        name_key=discipline.name_key,
                    )
                ]
            )
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Discipline.objects.filter(pk=discipline.id).update(
                status=TaxonomyStatus.ARCHIVED,
                archived_at=None,
            )
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Discipline.objects.filter(pk=discipline.id).update(lock_version=0)

    discipline.refresh_from_db()
    assert discipline.status == TaxonomyStatus.ACTIVE
    assert discipline.lock_version == 1


@pytest.mark.django_db
def test_initial_state_uuid_timestamps_and_optional_sort_order_are_persisted() -> None:
    workspace = _workspace(email="fields@example.test")
    discipline = create_discipline(workspace_id=workspace.id, name="História")
    subject = create_subject(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        name="Brasil",
    )
    subsubject = create_subsubject(
        workspace_id=workspace.id,
        subject_id=subject.id,
        name="República",
    )

    for item in (discipline, subject, subsubject):
        assert isinstance(item.id, uuid.UUID)
        assert item.status == TaxonomyStatus.ACTIVE
        assert item.sort_order is None
        assert item.archived_at is None
        assert item.lock_version == 1
        assert item.created_at.tzinfo is not None
        assert item.updated_at.tzinfo is not None
    assert subsubject.subject.discipline_id == discipline.id
    assert not hasattr(subsubject, "discipline_id")

    with pytest.raises(TaxonomyValidationError, match="ordem"):
        create_discipline(workspace_id=workspace.id, name="Inválida", sort_order=True)


@pytest.mark.django_db
def test_ct004_and_ct074_services_reject_cross_workspace_without_partial_data() -> None:
    workspace_a = _workspace(email="space-a@example.test")
    workspace_b = _workspace(email="space-b@example.test")
    discipline_b = create_discipline(workspace_id=workspace_b.id, name="Biologia")

    with pytest.raises(TaxonomyNotFoundError):
        create_subject(
            workspace_id=workspace_a.id,
            discipline_id=discipline_b.id,
            name="Genética",
        )
    assert Subject.objects.count() == 0

    subject_b = create_subject(
        workspace_id=workspace_b.id,
        discipline_id=discipline_b.id,
        name="Genética",
    )
    with pytest.raises(TaxonomyNotFoundError):
        create_subsubject(
            workspace_id=workspace_a.id,
            subject_id=subject_b.id,
            name="DNA",
        )
    assert Subsubject.objects.count() == 0


@pytest.mark.django_db
def test_mutations_cannot_reveal_or_change_another_workspace() -> None:
    workspace_a = _workspace(email="mutation-a@example.test")
    workspace_b = _workspace(email="mutation-b@example.test")
    discipline_a = create_discipline(workspace_id=workspace_a.id, name="Sociologia")

    with pytest.raises(TaxonomyNotFoundError):
        rename_discipline(
            workspace_id=workspace_b.id,
            discipline_id=discipline_a.id,
            name="Alteração indevida",
            expected_lock_version=1,
        )
    with pytest.raises(TaxonomyNotFoundError):
        archive_discipline(
            workspace_id=workspace_b.id,
            discipline_id=discipline_a.id,
            expected_lock_version=1,
        )

    discipline_a.refresh_from_db()
    assert discipline_a.name == "Sociologia"
    assert discipline_a.status == TaxonomyStatus.ACTIVE
    assert discipline_a.lock_version == 1


@pytest.mark.django_db
def test_ct074_model_guard_rejects_cross_workspace_outside_services() -> None:
    workspace_a = _workspace(email="guard-a@example.test")
    workspace_b = _workspace(email="guard-b@example.test")
    discipline_b = create_discipline(workspace_id=workspace_b.id, name="Geografia")

    with pytest.raises(ValidationError, match="mesmo Workspace"):
        Subject.objects.create(
            workspace=workspace_a,
            discipline=discipline_b,
            name="Cartografia",
        )

    subject_b = create_subject(
        workspace_id=workspace_b.id,
        discipline_id=discipline_b.id,
        name="Cartografia",
    )
    with pytest.raises(ValidationError, match="mesmo Workspace"):
        Subsubject.objects.create(
            workspace=workspace_a,
            subject=subject_b,
            name="Escalas",
        )

    assert Subject.objects.count() == 1
    assert Subsubject.objects.count() == 0


@pytest.mark.django_db(transaction=True)
def test_ct073_foreign_keys_reject_orphans_and_protect_hierarchy() -> None:
    workspace = _workspace(email="fk@example.test")
    discipline = create_discipline(workspace_id=workspace.id, name="Português")
    subject = create_subject(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        name="Gramática",
    )
    create_subsubject(workspace_id=workspace.id, subject_id=subject.id, name="Sintaxe")

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Subject.objects.bulk_create(
                [
                    Subject(
                        workspace=workspace,
                        discipline_id=uuid.uuid4(),
                        name="Órfão",
                        name_key="órfão",
                    )
                ]
            )
    with pytest.raises(ProtectedError):
        discipline.delete()
    with pytest.raises(ProtectedError):
        subject.delete()
    with pytest.raises(ProtectedError):
        workspace.delete()

    assert Discipline.objects.filter(pk=discipline.id).exists()
    assert Subject.objects.filter(pk=subject.id).exists()
    assert Subsubject.objects.count() == 1


@pytest.mark.django_db
def test_composed_transaction_rolls_back_when_hierarchy_creation_fails() -> None:
    workspace_a = _workspace(email="rollback-a@example.test")
    workspace_b = _workspace(email="rollback-b@example.test")
    parent_b = create_discipline(workspace_id=workspace_b.id, name="Artes")

    with pytest.raises(TaxonomyNotFoundError):
        with transaction.atomic():
            create_discipline(workspace_id=workspace_a.id, name="Temporária")
            create_subject(
                workspace_id=workspace_a.id,
                discipline_id=parent_b.id,
                name="Inválido",
            )

    assert not Discipline.objects.filter(workspace=workspace_a).exists()
    assert not Subject.objects.filter(workspace=workspace_a).exists()


@pytest.mark.django_db
def test_ct137_rename_uses_lock_and_preserves_identity_and_timestamp() -> None:
    workspace = _workspace(email="rename@example.test")
    discipline = create_discipline(workspace_id=workspace.id, name="Ciências")
    subject = create_subject(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        name="Natureza",
    )
    subsubject = create_subsubject(
        workspace_id=workspace.id,
        subject_id=subject.id,
        name="Ecologia",
    )
    clock = FixedClock(Instant(datetime(2026, 9, 5, 12, 0, tzinfo=UTC)))

    renamed_discipline = rename_discipline(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        name=" Ciências Naturais ",
        expected_lock_version=1,
        clock=clock,
    )
    renamed_subject = rename_subject(
        workspace_id=workspace.id,
        subject_id=subject.id,
        name="Meio Ambiente",
        expected_lock_version=1,
        clock=clock,
    )
    renamed_subsubject = rename_subsubject(
        workspace_id=workspace.id,
        subsubject_id=subsubject.id,
        name="Ecossistemas",
        expected_lock_version=1,
        clock=clock,
    )

    assert renamed_discipline.id == discipline.id
    assert renamed_discipline.name == "Ciências Naturais"
    assert renamed_subject.discipline_id == discipline.id
    assert renamed_subsubject.subject_id == subject.id
    for item in (renamed_discipline, renamed_subject, renamed_subsubject):
        assert item.lock_version == 2
        assert item.updated_at == clock.now().value

    with pytest.raises(TaxonomyConcurrencyError):
        rename_discipline(
            workspace_id=workspace.id,
            discipline_id=discipline.id,
            name="Sobrescrita",
            expected_lock_version=1,
        )


@pytest.mark.django_db
def test_rename_rejects_duplicate_in_same_parent_but_not_other_parent() -> None:
    workspace = _workspace(email="rename-duplicate@example.test")
    discipline_a = create_discipline(workspace_id=workspace.id, name="A")
    discipline_b = create_discipline(workspace_id=workspace.id, name="B")
    subject_a1 = create_subject(
        workspace_id=workspace.id,
        discipline_id=discipline_a.id,
        name="Primeiro",
    )
    subject_a2 = create_subject(
        workspace_id=workspace.id,
        discipline_id=discipline_a.id,
        name="Segundo",
    )
    subject_b = create_subject(
        workspace_id=workspace.id,
        discipline_id=discipline_b.id,
        name="Primeiro",
    )

    with pytest.raises(TaxonomyDuplicateNameError):
        rename_subject(
            workspace_id=workspace.id,
            subject_id=subject_a2.id,
            name=" primeiro ",
            expected_lock_version=1,
        )
    renamed = rename_subject(
        workspace_id=workspace.id,
        subject_id=subject_b.id,
        name="Segundo",
        expected_lock_version=1,
    )

    subject_a2.refresh_from_db()
    assert subject_a1.name == "Primeiro"
    assert subject_a2.name == "Segundo"
    assert renamed.name == "Segundo"


@pytest.mark.django_db
def test_ct137_archive_preserves_descendant_states_and_effective_availability() -> None:
    workspace = _workspace(email="archive@example.test")
    discipline = create_discipline(workspace_id=workspace.id, name="Filosofia")
    subject = create_subject(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        name="Ética",
    )
    subsubject = create_subsubject(
        workspace_id=workspace.id,
        subject_id=subject.id,
        name="Virtudes",
    )
    clock = FixedClock(Instant(datetime(2026, 9, 5, 13, 30, tzinfo=UTC)))

    archived = archive_discipline(
        workspace_id=workspace.id,
        discipline_id=discipline.id,
        expected_lock_version=1,
        clock=clock,
    )
    subject.refresh_from_db()
    subsubject.refresh_from_db()

    assert archived.archived_at == clock.now().value
    assert archived.lock_version == 2
    assert subject.status == TaxonomyStatus.ACTIVE
    assert subsubject.status == TaxonomyStatus.ACTIVE
    assert list(list_disciplines(workspace_id=workspace.id)) == []
    assert list(list_subjects(workspace_id=workspace.id, discipline_id=discipline.id)) == []
    assert list(list_subsubjects(workspace_id=workspace.id, subject_id=subject.id)) == []
    assert list(list_archived_disciplines(workspace_id=workspace.id)) == [archived]
    assert get_discipline(workspace_id=workspace.id, discipline_id=discipline.id) == archived

    with pytest.raises(TaxonomyStateConflictError):
        create_subject(
            workspace_id=workspace.id,
            discipline_id=discipline.id,
            name="Lógica",
        )
    with pytest.raises(TaxonomyStateConflictError):
        create_subsubject(
            workspace_id=workspace.id,
            subject_id=subject.id,
            name="Dever",
        )
    with pytest.raises(TaxonomyStateConflictError):
        archive_discipline(
            workspace_id=workspace.id,
            discipline_id=discipline.id,
            expected_lock_version=archived.lock_version,
        )


@pytest.mark.django_db
def test_subject_and_subsubject_archive_are_historical_and_workspace_scoped() -> None:
    workspace_a = _workspace(email="selectors-a@example.test")
    workspace_b = _workspace(email="selectors-b@example.test")
    discipline_a = create_discipline(workspace_id=workspace_a.id, name="Computação")
    discipline_b = create_discipline(workspace_id=workspace_b.id, name="Computação")
    subject_a = create_subject(
        workspace_id=workspace_a.id,
        discipline_id=discipline_a.id,
        name="Algoritmos",
    )
    subject_b = create_subject(
        workspace_id=workspace_b.id,
        discipline_id=discipline_b.id,
        name="Algoritmos",
    )
    subsubject_a = create_subsubject(
        workspace_id=workspace_a.id,
        subject_id=subject_a.id,
        name="Grafos",
    )
    create_subsubject(workspace_id=workspace_b.id, subject_id=subject_b.id, name="Grafos")

    archived_subsubject = archive_subsubject(
        workspace_id=workspace_a.id,
        subsubject_id=subsubject_a.id,
        expected_lock_version=1,
    )
    assert list(list_subsubjects(workspace_id=workspace_a.id, subject_id=subject_a.id)) == []
    archived_subject = archive_subject(
        workspace_id=workspace_a.id,
        subject_id=subject_a.id,
        expected_lock_version=1,
    )

    with pytest.raises(TaxonomyStateConflictError):
        create_subsubject(
            workspace_id=workspace_a.id,
            subject_id=subject_a.id,
            name="Árvores",
        )

    assert list(list_disciplines(workspace_id=workspace_a.id)) == [discipline_a]
    assert list(list_subjects(workspace_id=workspace_a.id, discipline_id=discipline_a.id)) == []
    assert list(
        list_archived_subjects(workspace_id=workspace_a.id, discipline_id=discipline_a.id)
    ) == [archived_subject]
    assert list(
        list_archived_subsubjects(workspace_id=workspace_a.id, subject_id=subject_a.id)
    ) == [archived_subsubject]
    assert get_subject(workspace_id=workspace_a.id, subject_id=subject_a.id) == archived_subject
    assert (
        get_subsubject(workspace_id=workspace_a.id, subsubject_id=subsubject_a.id)
        == archived_subsubject
    )
    with pytest.raises(TaxonomyNotFoundError):
        get_subject(workspace_id=workspace_b.id, subject_id=subject_a.id)
    with pytest.raises(TaxonomyNotFoundError):
        get_subsubject(workspace_id=workspace_b.id, subsubject_id=subsubject_a.id)


@pytest.mark.django_db
def test_taxonomy_migration_is_single_initial_node_with_v01_dependency() -> None:
    loader = MigrationLoader(connection)
    migration = loader.get_migration("taxonomy", "0001_initial")

    assert loader.graph.root_nodes("taxonomy") == [("taxonomy", "0001_initial")]
    assert migration.dependencies == [("accounts", "0001_initial")]
    assert {
        "taxonomy_discipline",
        "taxonomy_subject",
        "taxonomy_subsubject",
    }.issubset(connection.introspection.table_names())


def test_ct082_and_ct122_upgrade_v01_data_to_taxonomy_initial() -> None:
    probe = """
import json
import uuid
import django
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

django.setup()
executor = MigrationExecutor(connection)
v01_targets = [("auth", "0012_alter_user_first_name_max_length"), ("errors", "0001_initial")]
executor.migrate(v01_targets)
v01_apps = executor.loader.project_state(v01_targets).apps
User = v01_apps.get_model("accounts", "User")
Workspace = v01_apps.get_model("accounts", "Workspace")
Category = v01_apps.get_model("errors", "ErrorCategory")
user_id = uuid.UUID("11111111-1111-4111-8111-111111111111")
workspace_id = uuid.UUID("22222222-2222-4222-8222-222222222222")
user = User.objects.create(id=user_id, password="!", display_name="João", status="ACTIVE")
workspace = Workspace.objects.create(
    id=workspace_id,
    owner_user=user,
    name="Meu espaço",
    timezone_name="America/Sao_Paulo",
    locale="pt-BR",
    lock_version=1,
)
codes = [
    "CONCEPTUAL", "INTERPRETATION", "CALCULATION", "ATTENTION", "FORMULA_RULE",
    "PROCEDURE", "TRAP", "TIME_SHORTAGE", "GUESS", "OTHER",
]
for code in codes:
    Category.objects.create(
        workspace=workspace,
        code=code,
        display_name=code,
        name_key=code.casefold(),
        description=f"Categoria {code}",
    )
executor = MigrationExecutor(connection)
executor.migrate(executor.loader.graph.leaf_nodes())
final_apps = executor.loader.project_state().apps
FinalUser = final_apps.get_model("accounts", "User")
FinalWorkspace = final_apps.get_model("accounts", "Workspace")
FinalCategory = final_apps.get_model("errors", "ErrorCategory")
Discipline = final_apps.get_model("taxonomy", "Discipline")
applied = set(MigrationExecutor(connection).loader.applied_migrations)
current_workspace = FinalWorkspace.objects.get(pk=workspace_id)
print(json.dumps({
    "users": FinalUser.objects.filter(pk=user_id).count(),
    "workspaces": FinalWorkspace.objects.filter(pk=workspace_id).count(),
    "locale": current_workspace.locale,
    "timezone": current_workspace.timezone_name,
    "categories": FinalCategory.objects.filter(workspace_id=workspace_id).count(),
    "disciplines": Discipline.objects.count(),
    "accounts_v01": ("accounts", "0001_initial") in applied,
    "errors_v01": ("errors", "0001_initial") in applied,
    "taxonomy_v02": ("taxonomy", "0001_initial") in applied,
}))
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
    snapshot = json.loads(result.stdout.strip().splitlines()[-1])
    assert snapshot == {
        "users": 1,
        "workspaces": 1,
        "locale": "pt-BR",
        "timezone": "America/Sao_Paulo",
        "categories": 10,
        "disciplines": 0,
        "accounts_v01": True,
        "errors_v01": True,
        "taxonomy_v02": True,
    }
