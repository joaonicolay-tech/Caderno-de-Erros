"""Configuração do módulo Errors."""

from django.apps import AppConfig


class ErrorsConfig(AppConfig):
    """Categorias padrão da fundação V0.1."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "modules.errors"
    label = "errors"
    verbose_name = "Categorias de erro"
