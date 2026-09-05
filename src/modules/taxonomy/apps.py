"""Configuração do módulo de taxonomia."""

from django.apps import AppConfig


class TaxonomyConfig(AppConfig):
    """Registre o domínio acadêmico sem acoplá-lo à interface."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "modules.taxonomy"
    verbose_name = "Taxonomia"
