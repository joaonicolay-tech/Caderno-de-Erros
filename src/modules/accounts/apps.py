"""Configuração do módulo Accounts/Workspace."""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Identidade local e fronteira de autorização por Workspace."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "modules.accounts"
    label = "accounts"
    verbose_name = "Identidade e espaços"
