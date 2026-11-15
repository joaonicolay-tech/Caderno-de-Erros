"""Perfil determinístico e isolado para testes automatizados."""

import hashlib

from shared.infrastructure.local_boundary import database_path

from .base import *

CEI_PROFILE = "test"
DEBUG = False
SECRET_KEY = hashlib.sha256(b"cei-test-profile-not-for-production").hexdigest()
ALLOWED_HOSTS = ["testserver", "127.0.0.1", "localhost", "[::1]"]

CEI_TEST_DATABASE_PATH = database_path(test=True)
CEI_TEST_DATABASE_DIRECTORY = CEI_TEST_DATABASE_PATH.parent

DATABASES = {
    "default": sqlite_database(
        CEI_TEST_DATABASE_PATH,
        test_name=CEI_TEST_DATABASE_PATH,
    )
}
