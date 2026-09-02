"""Entrada ASGI segura para produção local."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production_local")

application = get_asgi_application()
