"""Entrada ASGI segura para produção local."""

import os

from django.core.asgi import get_asgi_application

from shared.infrastructure.local_boundary import configure_process, entry_settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production_local")
entry_settings([])
configure_process()

application = get_asgi_application()
