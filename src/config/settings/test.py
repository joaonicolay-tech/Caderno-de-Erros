"""Perfil determinístico e isolado para testes automatizados."""

import hashlib
import tempfile
from pathlib import Path

from .base import *

CEI_PROFILE = "test"
DEBUG = False
SECRET_KEY = hashlib.sha256(b"cei-test-profile-not-for-production").hexdigest()
ALLOWED_HOSTS = ["testserver", "127.0.0.1", "localhost", "[::1]"]

_test_database_directory = tempfile.TemporaryDirectory(prefix="cei-tests-")
CEI_TEST_DATABASE_DIRECTORY = Path(_test_database_directory.name).resolve()
CEI_TEST_DATABASE_PATH = CEI_TEST_DATABASE_DIRECTORY / "test.sqlite3"

DATABASES = {
    "default": sqlite_database(
        CEI_TEST_DATABASE_PATH,
        test_name=CEI_TEST_DATABASE_PATH,
    )
}
