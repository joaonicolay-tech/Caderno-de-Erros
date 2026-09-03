"""Bootstrap transacional da fundação completa da V0.1."""

import logging
from dataclasses import dataclass

from django.db import transaction

from modules.accounts.models import User, Workspace
from modules.accounts.services import bootstrap_local_workspace as bootstrap_identity
from modules.errors.models import ErrorCategory
from modules.errors.services import seed_standard_error_categories
from modules.operations.correlation import correlation_scope
from modules.operations.events import EventCode, EventOutcome
from modules.operations.structured_logging import emit_event
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
    correlation_id: str | None = None,
) -> CompleteLocalBootstrapResult:
    """Execute Accounts e seed como uma operação atômica e idempotente."""
    with correlation_scope(correlation_id):
        emit_event(
            EventCode.BOOTSTRAP_STARTED,
            operation="workspace.bootstrap",
            outcome=EventOutcome.STARTED,
        )
        try:
            identity = bootstrap_identity(
                timezone_id=timezone_id,
                workspace_name=workspace_name,
                display_name=display_name,
            )
            seed = seed_standard_error_categories(identity.workspace)
        except Exception as error:
            emit_event(
                EventCode.BOOTSTRAP_FAILED,
                operation="workspace.bootstrap",
                outcome=EventOutcome.FAILED,
                level=logging.ERROR,
                context={
                    "error_code": "BOOTSTRAP_FAILURE",
                    "error_type": type(error).__name__,
                },
            )
            raise

        result = CompleteLocalBootstrapResult(
            user=identity.user,
            workspace=identity.workspace,
            categories=seed.categories,
            created=identity.created or seed.created_count > 0,
        )
        emit_event(
            EventCode.BOOTSTRAP_SUCCEEDED,
            operation="workspace.bootstrap",
            outcome=EventOutcome.SUCCEEDED,
            context={
                "workspace_id": str(identity.workspace.id),
                "category_count": len(seed.categories),
                "created": result.created,
            },
        )
        return result
