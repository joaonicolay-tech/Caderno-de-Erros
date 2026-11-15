"""Import CEI-EXPORT-1.0 into an empty compatible installation."""

from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser


class Command(BaseCommand):
    help = "Importação lógica CEI desabilitada na rota V1.0 Local r1."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--package", required=True)

    def handle(self, *args: Any, **options: Any) -> None:
        raise CommandError(
            "Importação lógica CEI desabilitada na rota V1.0 Local r1; nenhum arquivo foi aberto."
        )
