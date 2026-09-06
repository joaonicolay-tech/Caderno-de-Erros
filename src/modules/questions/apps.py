"""Configuração Django do módulo Questions."""

from django.apps import AppConfig


class QuestionsConfig(AppConfig):
    """Registre o módulo dos catálogos internos de origem e questões."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "modules.questions"
    label = "questions"
    verbose_name = "Questões"
