"""Adopt a UI-prepared backup only after the local server has stopped."""

import json
from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser

from modules.data_management.exceptions import BackupValidationError, RestoreError
from modules.data_management.ui_services import UIRecoveryError, apply_prepared_restore


class Command(BaseCommand):
    help = "Apply a validated restore ticket offline; keep the validated pre-backup."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--ticket", required=True)

    def handle(self, *args: Any, **options: Any) -> None:
        del args
        try:
            result = apply_prepared_restore(str(options["ticket"]))
        except (
            UIRecoveryError,
            OSError,
            ValueError,
            KeyError,
            TypeError,
            BackupValidationError,
            RestoreError,
        ) as error:
            raise CommandError(
                "Restore recusado; banco ativo preservado ou pré-backup disponível."
            ) from error
        self.stdout.write(
            self.style.SUCCESS(json.dumps(result, ensure_ascii=False, sort_keys=True))
        )
