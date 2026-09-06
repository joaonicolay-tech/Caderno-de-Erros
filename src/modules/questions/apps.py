"""Configuração Django do módulo Questions."""

from django.apps import AppConfig


class QuestionsConfig(AppConfig):
    """Registre o módulo que abriga o catálogo interno de origem."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "modules.questions"
    label = "questions"
    verbose_name = "Questões"
