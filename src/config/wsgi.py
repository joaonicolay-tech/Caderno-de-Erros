"""Entrada WSGI segura para produção local."""

import os

from django.core.wsgi import get_wsgi_application

from shared.infrastructure.local_boundary import configure_process, entry_settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production_local")
entry_settings([])
configure_process()

application = get_wsgi_application()
