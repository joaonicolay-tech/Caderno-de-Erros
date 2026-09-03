"""Configuração da infraestrutura operacional."""

from django.apps import AppConfig


class OperationsConfig(AppConfig):
    """Registre a inicialização segura da aplicação."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "modules.operations"
    verbose_name = "Operações"
    _initialization_logged = False

    def ready(self) -> None:
        """Emita uma única evidência de inicialização por processo."""
        if self._initialization_logged:
            return

        from django.conf import settings

        from .correlation import correlation_scope
        from .events import EventCode, EventOutcome
        from .structured_logging import emit_event

        with correlation_scope():
            emit_event(
                EventCode.APPLICATION_INITIALIZED,
                operation="application.initialize",
                outcome=EventOutcome.SUCCEEDED,
                context={"profile": settings.CEI_PROFILE, "version": "0.1.0"},
            )
        self._initialization_logged = True
