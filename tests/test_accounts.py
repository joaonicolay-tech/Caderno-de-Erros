"""Identidade, Workspace, bootstrap e primeiro acesso da Etapa 3."""

import json
import os
import subprocess
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

import pytest
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import IntegrityError, connection
from django.db.migrations.loader import MigrationLoader
from django.db.models.deletion import ProtectedError

from modules.accounts.exceptions import WorkspaceAccessDenied, WorkspaceConcurrencyError
from modules.accounts.models import User, Workspace, WorkspaceLocale
from modules.accounts.services import (
    LOCAL_USER_ID,
    LOCAL_WORKSPACE_ID,
    TIMEZONE_CHANGE_NOTICE,
    change_workspace_timezone,
    get_workspace_for_owner,
)
from shared.application.bootstrap import bootstrap_local_workspace
from shared.domain.time import FixedClock, Instant

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.django_db
def test_custom_user_uses_uuid_and_framework_password_storage() -> None:
    user = User.objects.create_user(display_name="Estudante")

    assert isinstance(user.id, uuid.UUID)
    assert user.has_usable_password() is False
    assert user.is_active is True


@pytest.mark.django_db
def test_local_bootstrap_is_atomic_idempotent_and_persists_preferences() -> None:
    first = bootstrap_local_workspace(timezone_id="America/Sao_Paulo")
    second = bootstrap_local_workspace(timezone_id="Asia/Tokyo")

    assert first.created is True
    assert second.created is False
    assert first.user.id == second.user.id == LOCAL_USER_ID
    assert first.workspace.id == second.workspace.id == LOCAL_WORKSPACE_ID
    assert User.objects.count() == 1
    assert Workspace.objects.count() == 1

    persisted = Workspace.objects.get()
    assert persisted.locale == WorkspaceLocale.PT_BR
    assert persisted.timezone_name == "America/Sao_Paulo"
    assert persisted.lock_version == 1


@pytest.mark.django_db
def test_invalid_timezone_rejects_bootstrap_without_partial_data() -> None:
    with pytest.raises(ValueError, match="Fuso IANA desconhecido"):
        bootstrap_local_workspace(timezone_id="Brasil/Fuso-Inexistente")

    assert User.objects.count() == 0
    assert Workspace.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("arguments", "message"),
    [
        ({"workspace_name": "   "}, "não pode ser vazio"),
        ({"workspace_name": "x" * 121}, "Workspace deve ter no máximo"),
        ({"display_name": "x" * 121}, "exibição deve ter no máximo"),
    ],
)
def test_bootstrap_rejects_documented_name_limits_without_partial_data(
    arguments: dict[str, str],
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        bootstrap_local_workspace(timezone_id="America/Sao_Paulo", **arguments)

    assert User.objects.count() == 0
    assert Workspace.objects.count() == 0


@pytest.mark.django_db
def test_bootstrap_rolls_back_user_if_workspace_creation_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_workspace(*args: object, **kwargs: object) -> None:
        raise RuntimeError("falha controlada")

    monkeypatch.setattr(Workspace.objects, "get_or_create", fail_workspace)

    with pytest.raises(RuntimeError, match="falha controlada"):
        bootstrap_local_workspace(timezone_id="America/Sao_Paulo")

    assert User.objects.count() == 0
    assert Workspace.objects.count() == 0


@pytest.mark.django_db
def test_workspace_rejects_invalid_timezone_during_model_validation() -> None:
    user = User.objects.create_user()
    workspace = Workspace(
        owner_user=user,
        name="Espaço",
        timezone_name="UTC+3",
    )

    with pytest.raises(ValidationError) as captured:
        workspace.full_clean()

    assert captured.value.error_dict["timezone_name"][0].code == "invalid_timezone"


@pytest.mark.django_db(transaction=True)
def test_workspace_owner_foreign_key_is_enforced() -> None:
    with pytest.raises(IntegrityError):
        Workspace.objects.create(
            owner_user_id=uuid.uuid4(),
            name="Órfão",
            timezone_name="UTC",
        )


@pytest.mark.django_db
def test_workspace_protects_its_owner_from_deletion() -> None:
    bootstrap = bootstrap_local_workspace(
        timezone_id="America/Sao_Paulo",
        display_name="João",
    )

    with pytest.raises(ProtectedError):
        bootstrap.user.delete()

    assert User.objects.filter(pk=bootstrap.user.id).exists()
    assert Workspace.objects.filter(pk=bootstrap.workspace.id).exists()


@pytest.mark.django_db
def test_workspace_queries_and_changes_are_scoped_by_owner() -> None:
    owner_a = User.objects.create_user(email="a@example.test")
    owner_b = User.objects.create_user(email="b@example.test")
    workspace_a = Workspace.objects.create(
        owner_user=owner_a,
        name="Espaço A",
        timezone_name="America/Sao_Paulo",
    )
    workspace_b = Workspace.objects.create(
        owner_user=owner_b,
        name="Espaço B",
        timezone_name="Asia/Tokyo",
    )

    assert get_workspace_for_owner(actor_user_id=owner_a.id, workspace_id=workspace_a.id).id == (
        workspace_a.id
    )
    with pytest.raises(WorkspaceAccessDenied):
        get_workspace_for_owner(actor_user_id=owner_a.id, workspace_id=workspace_b.id)
    with pytest.raises(WorkspaceAccessDenied):
        change_workspace_timezone(
            actor_user_id=owner_a.id,
            workspace_id=workspace_b.id,
            timezone_id="UTC",
            expected_lock_version=workspace_b.lock_version,
            confirmed=True,
        )

    workspace_b.refresh_from_db()
    assert workspace_b.timezone_name == "Asia/Tokyo"


@pytest.mark.django_db
def test_timezone_change_requires_confirmation_and_persists_after_confirmation() -> None:
    bootstrap = bootstrap_local_workspace(timezone_id="America/Sao_Paulo")
    workspace = bootstrap.workspace

    cancelled = change_workspace_timezone(
        actor_user_id=bootstrap.user.id,
        workspace_id=workspace.id,
        timezone_id="Asia/Tokyo",
        expected_lock_version=workspace.lock_version,
        confirmed=False,
    )
    assert cancelled.changed is False
    assert cancelled.notice == TIMEZONE_CHANGE_NOTICE
    workspace.refresh_from_db()
    assert workspace.timezone_name == "America/Sao_Paulo"

    fixed_clock = FixedClock(Instant(datetime(2026, 9, 2, 18, 30, tzinfo=UTC)))
    confirmed = change_workspace_timezone(
        actor_user_id=bootstrap.user.id,
        workspace_id=workspace.id,
        timezone_id="Asia/Tokyo",
        expected_lock_version=workspace.lock_version,
        confirmed=True,
        clock=fixed_clock,
    )
    assert confirmed.changed is True
    assert confirmed.workspace.timezone_name == "Asia/Tokyo"
    assert confirmed.workspace.lock_version == 2
    assert confirmed.workspace.updated_at == fixed_clock.now().value

    persisted_in_later_operation = get_workspace_for_owner(
        actor_user_id=bootstrap.user.id,
        workspace_id=workspace.id,
    )
    assert persisted_in_later_operation.timezone_name == "Asia/Tokyo"


@pytest.mark.django_db
def test_timezone_change_rejects_invalid_value_and_stale_version() -> None:
    bootstrap = bootstrap_local_workspace(timezone_id="America/Sao_Paulo")

    with pytest.raises(ValueError, match="Fuso IANA desconhecido"):
        change_workspace_timezone(
            actor_user_id=bootstrap.user.id,
            workspace_id=bootstrap.workspace.id,
            timezone_id="Invalido/Sem-Zona",
            expected_lock_version=1,
            confirmed=True,
        )
    with pytest.raises(WorkspaceConcurrencyError):
        change_workspace_timezone(
            actor_user_id=bootstrap.user.id,
            workspace_id=bootstrap.workspace.id,
            timezone_id="UTC",
            expected_lock_version=99,
            confirmed=True,
        )

    bootstrap.workspace.refresh_from_db()
    assert bootstrap.workspace.timezone_name == "America/Sao_Paulo"
    assert bootstrap.workspace.lock_version == 1


@pytest.mark.django_db
def test_bootstrap_management_command_is_idempotent(capsys: pytest.CaptureFixture[str]) -> None:
    call_command("bootstrap_local", timezone="America/Sao_Paulo")
    call_command("bootstrap_local", timezone="Asia/Tokyo")

    output = capsys.readouterr().out
    assert "criado" in output
    assert "já existente" in output
    assert User.objects.count() == 1
    assert Workspace.objects.count() == 1


@pytest.mark.django_db
def test_first_accounts_migration_contains_custom_user_and_no_default_user_table() -> None:
    loader = MigrationLoader(connection)

    assert loader.graph.root_nodes("accounts") == [("accounts", "0001_initial")]
    tables = set(connection.introspection.table_names())
    assert "accounts_user" in tables
    assert "accounts_workspace" in tables
    assert "errors_error_category" in tables
    assert "auth_user" not in tables


def test_migrations_apply_from_an_empty_disposable_database() -> None:
    probe = """
import json
import django
from django.core.management import call_command
from django.db import connection

django.setup()
call_command("migrate", verbosity=0, interactive=False)
tables = set(connection.introspection.table_names())
print(json.dumps({
    "custom_user": "accounts_user" in tables,
    "workspace": "accounts_workspace" in tables,
    "categories": "errors_error_category" in tables,
    "default_user": "auth_user" in tables,
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
        "custom_user": True,
        "workspace": True,
        "categories": True,
        "default_user": False,
    }
