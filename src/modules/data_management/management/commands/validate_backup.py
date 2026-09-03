"""Valide manifesto, checksum e integridade de um backup."""

from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser

from modules.data_management.exceptions import DataManagementError
from modules.data_management.services import validate_sqlite_backup


class Command(BaseCommand):
    """Exponha validação independente sem modificar bancos."""

    help = "Valida manifesto, SHA-256 e integridade interna de um backup SQLite."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--backup", required=True, help="Arquivo SQLite de backup.")
        parser.add_argument("--manifest", help="Manifesto; por padrão usa o sidecar derivado.")
        parser.add_argument("--correlation-id", help="UUID opcional para correlação dos logs.")

    def handle(self, *args: Any, **options: Any) -> None:
        del args
        try:
            result = validate_sqlite_backup(
                options["backup"],
                manifest_path=options.get("manifest"),
                correlation_id=options.get("correlation_id"),
            )
        except DataManagementError as error:
            raise CommandError(str(error)) from error
        self.stdout.write(
            self.style.SUCCESS(
                f"Backup válido: formato {result.manifest.format_version}; "
                f"{result.manifest.size_bytes} bytes."
            )
        )
