"""Crie um backup consistente do banco SQLite configurado."""

from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser

from modules.data_management.exceptions import DataManagementError
from modules.data_management.services import create_sqlite_backup, manifest_path_for


class Command(BaseCommand):
    """Exponha a criação de snapshot como operação explícita."""

    help = "Cria e valida um backup SQLite da fundação V0.1."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--output", required=True, help="Novo arquivo SQLite de destino.")
        parser.add_argument("--database", default="default", help="Alias Django (padrão: default).")
        parser.add_argument("--correlation-id", help="UUID opcional para correlação dos logs.")

    def handle(self, *args: Any, **options: Any) -> None:
        del args
        output = Path(options["output"])
        try:
            result = create_sqlite_backup(
                output,
                database_alias=options["database"],
                correlation_id=options.get("correlation_id"),
            )
        except DataManagementError as error:
            raise CommandError(str(error)) from error
        self.stdout.write(
            self.style.SUCCESS(
                "Backup criado e validado: "
                f"{result.manifest.size_bytes} bytes; manifesto {manifest_path_for(output).name}."
            )
        )
