"""Perfil de produção local, sem exposição de rede por padrão."""

from .base import *

CEI_PROFILE = "production_local"
DEBUG = False
SECRET_KEY = required_production_secret()
ALLOWED_HOSTS = local_allowed_hosts()

DATABASES = {
    "default": sqlite_database(
        configured_path(
            "CEI_PRODUCTION_LOCAL_DB",
            BASE_DIR / "var" / "production_local.sqlite3",
        )
    )
}

SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Apply the declared frame policy to actual production HTTP responses.
MIDDLEWARE = [*MIDDLEWARE, "django.middleware.clickjacking.XFrameOptionsMiddleware"]
