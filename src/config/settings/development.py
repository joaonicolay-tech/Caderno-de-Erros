"""Perfil de desenvolvimento estritamente local."""

import hashlib
import os

from .base import *

CEI_PROFILE = "development"
DEBUG = True
SECRET_KEY = (
    os.environ.get("CEI_SECRET_KEY")
    or hashlib.sha256(b"cei-development-profile-not-for-production").hexdigest()
)
ALLOWED_HOSTS = local_allowed_hosts()

DATABASES = {
    "default": sqlite_database(
        configured_path("CEI_DEVELOPMENT_DB", BASE_DIR / "var" / "development.sqlite3")
    )
}
