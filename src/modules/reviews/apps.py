"""Configuração do módulo de revisões."""

from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    """Registre a fundação persistente de revisões."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "modules.reviews"
