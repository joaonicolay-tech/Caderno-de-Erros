"""Carregue a fixture sintética V0.2 somente no perfil de teste descartável."""

from django.core.management.base import BaseCommand, CommandError, CommandParser

from modules.questions.fixture import FIXTURE_SEED, FixtureSafetyError, load_v02_fixture


class Command(BaseCommand):
    help = "Carrega a fixture sintética V0.2 no banco descartável do perfil de teste."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--seed", default=FIXTURE_SEED)

    def handle(self, *args: object, **options: object) -> None:
        del args
        try:
            result = load_v02_fixture(seed=str(options["seed"]))
        except FixtureSafetyError as error:
            raise CommandError(str(error)) from error
        self.stdout.write(
            self.style.SUCCESS(
                "Fixture V0.2 carregada: "
                f"{result.question_count} questões, {result.revision_count} revisões e "
                f"{result.alternative_count} alternativas."
            )
        )
