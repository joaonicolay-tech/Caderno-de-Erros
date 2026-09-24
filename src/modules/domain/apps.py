"""Domain application and transition history."""

from django.apps import AppConfig


class DomainConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "modules.domain"
    label = "domain"
    verbose_name = "Domínio"
