"""Configuração do módulo técnico de gestão de dados."""

from django.apps import AppConfig


class DataManagementConfig(AppConfig):
    """Disponibilize os comandos operacionais de backup e restauração."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "modules.data_management"
    label = "data_management"
    verbose_name = "Gestão técnica de dados"
