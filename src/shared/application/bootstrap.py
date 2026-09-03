"""Bootstrap transacional da fundação completa da V0.1."""

from dataclasses import dataclass

from django.db import transaction

from modules.accounts.models import User, Workspace
from modules.accounts.services import bootstrap_local_workspace as bootstrap_identity
from modules.errors.models import ErrorCategory
from modules.errors.services import seed_standard_error_categories
from shared.domain.time import TimeZoneId


@dataclass(frozen=True, slots=True)
class CompleteLocalBootstrapResult:
    """User, Workspace e catálogo padrão obtidos numa única transação."""

    user: User
    workspace: Workspace
    categories: tuple[ErrorCategory, ...]
    created: bool


@transaction.atomic
def bootstrap_local_workspace(
    *,
    timezone_id: TimeZoneId | str,
    workspace_name: str = "Meu espaço",
    display_name: str = "",
) -> CompleteLocalBootstrapResult:
    """Execute Accounts e seed como uma operação atômica e idempotente."""
    identity = bootstrap_identity(
        timezone_id=timezone_id,
        workspace_name=workspace_name,
        display_name=display_name,
    )
    seed = seed_standard_error_categories(identity.workspace)
    return CompleteLocalBootstrapResult(
        user=identity.user,
        workspace=identity.workspace,
        categories=seed.categories,
        created=identity.created or seed.created_count > 0,
    )
