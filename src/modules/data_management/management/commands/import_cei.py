"""Import CEI-EXPORT-1.0 into an empty compatible installation."""

from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser

from modules.data_management.portability import (
    ExportValidationError,
    import_into_empty,
    validate_export,
)


class Command(BaseCommand):
    help = "Import a validated CEI-EXPORT-1.0 into a migrated empty installation."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--package", required=True)

    def handle(self, *args: Any, **options: Any) -> None:
        del args
        package_path = Path(str(options["package"])).expanduser()
        try:
            with package_path.open("rb") as source:
                package = validate_export(source)
            counts = import_into_empty(package=package)
        except (OSError, ExportValidationError) as error:
            raise CommandError("Importação CEI recusada antes de mutação ou revertida.") from error
        self.stdout.write(self.style.SUCCESS(f"Importação concluída: {counts}"))
