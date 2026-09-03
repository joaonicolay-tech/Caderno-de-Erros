"""Casos de uso transacionais de primeiro acesso e configuração."""

import uuid
from dataclasses import dataclass

from django.db import IntegrityError, transaction
from django.db.models import F

from shared.domain.time import Clock, SystemClock, TimeZoneId

from .exceptions import LocalBootstrapConflict, WorkspaceAccessDenied, WorkspaceConcurrencyError
from .models import User, UserStatus, Workspace, WorkspaceLocale

LOCAL_USER_ID = uuid.UUID("ad2f8669-2a08-5f83-942c-72bd456bf442")
LOCAL_WORKSPACE_ID = uuid.UUID("f09de31a-b61c-5a09-81fd-ae645ea6d838")
LOCAL_WORKSPACE_NAME = "Meu espaço"
TIMEZONE_CHANGE_NOTICE = (
    "A alteração muda o cálculo de hoje e os novos cálculos; "
    "instantes e datas históricas permanecem inalterados."
)


@dataclass(frozen=True, slots=True)
class LocalBootstrapResult:
    """Resultado idempotente da inicialização local."""

    user: User
    workspace: Workspace
    created: bool


@dataclass(frozen=True, slots=True)
class TimezoneChangeResult:
    """Resultado explícito da confirmação ou cancelamento de mudança."""

    workspace: Workspace
    changed: bool
    notice: str = TIMEZONE_CHANGE_NOTICE


def _timezone_value(timezone_id: TimeZoneId | str) -> str:
    return (timezone_id if isinstance(timezone_id, TimeZoneId) else TimeZoneId(timezone_id)).value


def _existing_local_result() -> LocalBootstrapResult:
    try:
        user = User.objects.get(pk=LOCAL_USER_ID)
        workspace = Workspace.objects.get(pk=LOCAL_WORKSPACE_ID)
    except (User.DoesNotExist, Workspace.DoesNotExist) as error:
        raise LocalBootstrapConflict(
            "A inicialização local concorrente não produziu um estado completo."
        ) from error
    if workspace.owner_user_id != user.id:
        raise LocalBootstrapConflict("O Workspace local pertence a outra identidade.")
    return LocalBootstrapResult(user=user, workspace=workspace, created=False)


def bootstrap_local_workspace(
    *,
    timezone_id: TimeZoneId | str,
    workspace_name: str = LOCAL_WORKSPACE_NAME,
    display_name: str = "",
) -> LocalBootstrapResult:
    """Crie uma única identidade/espaço local sem presumir o fuso do sistema."""
    timezone_name = _timezone_value(timezone_id)
    normalized_workspace_name = workspace_name.strip()
    normalized_display_name = display_name.strip()
    if not normalized_workspace_name:
        raise ValueError("O nome do Workspace não pode ser vazio.")
    if len(normalized_workspace_name) > 120:
        raise ValueError("O nome do Workspace deve ter no máximo 120 caracteres.")
    if len(normalized_display_name) > 120:
        raise ValueError("O nome de exibição deve ter no máximo 120 caracteres.")

    try:
        with transaction.atomic():
            user, user_created = User.objects.get_or_create(
                pk=LOCAL_USER_ID,
                defaults={
                    "display_name": normalized_display_name,
                    "email": None,
                    "status": UserStatus.ACTIVE,
                },
            )
            if user_created:
                user.set_unusable_password()
                user.save(update_fields=["password", "updated_at"])

            workspace, workspace_created = Workspace.objects.get_or_create(
                pk=LOCAL_WORKSPACE_ID,
                defaults={
                    "owner_user": user,
                    "name": normalized_workspace_name,
                    "timezone_name": timezone_name,
                    "locale": WorkspaceLocale.PT_BR,
                },
            )
            if workspace.owner_user_id != user.id:
                raise LocalBootstrapConflict("O Workspace local pertence a outra identidade.")
            return LocalBootstrapResult(
                user=user,
                workspace=workspace,
                created=user_created or workspace_created,
            )
    except IntegrityError:
        return _existing_local_result()


def get_workspace_for_owner(*, actor_user_id: uuid.UUID, workspace_id: uuid.UUID) -> Workspace:
    """Resolva o espaço sempre pelo identificador e pelo proprietário atual."""
    try:
        return Workspace.objects.get(pk=workspace_id, owner_user_id=actor_user_id)
    except Workspace.DoesNotExist as error:
        raise WorkspaceAccessDenied("Workspace não encontrado para a identidade atual.") from error


def change_workspace_timezone(
    *,
    actor_user_id: uuid.UUID,
    workspace_id: uuid.UUID,
    timezone_id: TimeZoneId | str,
    expected_lock_version: int,
    confirmed: bool,
    clock: Clock | None = None,
) -> TimezoneChangeResult:
    """Confirme a mudança com autorização e compare-and-swap de lock_version."""
    timezone_name = _timezone_value(timezone_id)
    workspace = get_workspace_for_owner(
        actor_user_id=actor_user_id,
        workspace_id=workspace_id,
    )
    if not confirmed or workspace.timezone_name == timezone_name:
        return TimezoneChangeResult(workspace=workspace, changed=False)

    current_clock = clock or SystemClock()
    updated = Workspace.objects.filter(
        pk=workspace.id,
        owner_user_id=actor_user_id,
        lock_version=expected_lock_version,
    ).update(
        timezone_name=timezone_name,
        lock_version=F("lock_version") + 1,
        updated_at=current_clock.now().value,
    )
    if updated != 1:
        raise WorkspaceConcurrencyError(
            "O Workspace mudou desde a confirmação; recarregue o valor atual."
        )
    workspace.refresh_from_db()
    return TimezoneChangeResult(workspace=workspace, changed=True)
