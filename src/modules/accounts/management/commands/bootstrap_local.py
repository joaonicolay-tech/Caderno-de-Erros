"""Inicialize a identidade e o Workspace do perfil local."""

from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser

from shared.application.bootstrap import bootstrap_local_workspace


class Command(BaseCommand):
    help = "Cria ou recupera atomicamente o User e Workspace locais."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--timezone", required=True, help="Identificador IANA escolhido.")
        parser.add_argument("--workspace-name", default="Meu espaço")
        parser.add_argument("--display-name", default="")

    def handle(self, *args: Any, **options: Any) -> None:
        try:
            result = bootstrap_local_workspace(
                timezone_id=options["timezone"],
                workspace_name=options["workspace_name"],
                display_name=options["display_name"],
            )
        except ValueError as error:
            raise CommandError(str(error)) from error

        state = "criado" if result.created else "já existente"
        self.stdout.write(
            self.style.SUCCESS(
                f"Workspace local {state}: {result.workspace.id} "
                f"({result.workspace.timezone_name}); {len(result.categories)} categorias padrão."
            )
        )
