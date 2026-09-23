"""Comando manual de manutenção da retenção S2D, separado do checker."""

from typing import Any

from django.core.management.base import BaseCommand

from modules.operations.retention import purge_expired_question_deletion_events


class Command(BaseCommand):
    help = "Expurga eventos sanitizados de exclusão após 90 * 24 horas em UTC."

    def handle(self, *args: Any, **options: Any) -> None:
        del args, options
        count = purge_expired_question_deletion_events()
        self.stdout.write(f"Eventos de exclusão expirados expurgados: {count}.")
