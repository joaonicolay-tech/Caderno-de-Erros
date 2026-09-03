"""Restaure um backup somente em novo destino isolado."""

from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser

from modules.data_management.exceptions import DataManagementError
from modules.data_management.services import restore_sqlite_backup


class Command(BaseCommand):
    """Exponha restauração validada sem trocar o banco ativo."""

    help = "Restaura e reconcilia um backup V0.1 em novo arquivo isolado."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--backup", required=True, help="Arquivo SQLite de backup.")
        parser.add_argument("--destination", required=True, help="Novo arquivo SQLite isolado.")
        parser.add_argument("--manifest", help="Manifesto; por padrão usa o sidecar derivado.")
        parser.add_argument("--database", default="default", help="Alias Django protegido.")
        parser.add_argument("--correlation-id", help="UUID opcional para correlação dos logs.")

    def handle(self, *args: Any, **options: Any) -> None:
        del args
        try:
            result = restore_sqlite_backup(
                options["backup"],
                options["destination"],
                manifest_path=options.get("manifest"),
                database_alias=options["database"],
                correlation_id=options.get("correlation_id"),
            )
        except DataManagementError as error:
            raise CommandError(str(error)) from error
        self.stdout.write(
            self.style.SUCCESS(
                "Restauração isolada validada: "
                f"{result.reconciliation.user_count} usuário, "
                f"{result.reconciliation.workspace_count} Workspace e "
                f"{result.reconciliation.category_count} categorias."
            )
        )
