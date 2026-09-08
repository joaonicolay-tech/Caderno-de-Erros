"""Configuração do módulo de tentativas."""

from django.apps import AppConfig


class AttemptsConfig(AppConfig):
    """Registre a fundação persistente de tentativas."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "modules.attempts"
