"""Instrumente o comando Django de migração sem mudar sua semântica."""

import logging
from typing import Any

from django.core.management.base import CommandParser
from django.core.management.commands.migrate import Command as DjangoMigrateCommand

from modules.operations.correlation import correlation_scope
from modules.operations.events import EventCode, EventOutcome
from modules.operations.structured_logging import emit_event


class Command(DjangoMigrateCommand):
    """Acrescente correlação e eventos ao comando nativo migrate."""

    def add_arguments(self, parser: CommandParser) -> None:
        super().add_arguments(parser)
        parser.add_argument("--correlation-id", help="UUID técnico opcional para correlação.")

    def handle(self, *args: Any, **options: Any) -> str | None:
        supplied_id = options.pop("correlation_id", None)
        with correlation_scope(supplied_id):
            emit_event(
                EventCode.MIGRATION_STARTED,
                operation="database.migrate",
                outcome=EventOutcome.STARTED,
            )
            try:
                result = super().handle(*args, **options)
            except Exception as error:
                emit_event(
                    EventCode.MIGRATION_FAILED,
                    operation="database.migrate",
                    outcome=EventOutcome.FAILED,
                    level=logging.ERROR,
                    context={
                        "error_code": "MIGRATION_FAILURE",
                        "error_type": type(error).__name__,
                    },
                )
                raise
            emit_event(
                EventCode.MIGRATION_SUCCEEDED,
                operation="database.migrate",
                outcome=EventOutcome.SUCCEEDED,
            )
            return result
