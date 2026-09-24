"""Configuração Django para busca e filtros persistidos."""

from django.apps import AppConfig


class SearchConfig(AppConfig):
    """Registre o schema mínimo de filtros salvos."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "modules.search"
    label = "search"
    verbose_name = "Busca e filtros"
