"""Configuração comum e invariantes dos perfis locais."""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

from shared.infrastructure.local_boundary import (
    configure_process,
    database_path,
    production_secret,
    runtime_temporary_dir,
)

configure_process()

BASE_DIR = Path(__file__).resolve().parents[3]

LOCAL_ALLOWED_HOSTS = frozenset({"127.0.0.1", "localhost", "[::1]"})
DATABASE_TIMEOUT_SECONDS = 5.0
# `no-referrer` serializa o Origin como `null` em POSTs de formulário. Esta
# política preserva o Origin apenas no mesmo host e não envia Referer a terceiros.
FORM_POST_REFERRER_POLICY = "same-origin"

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "modules.accounts.apps.AccountsConfig",
    "modules.attempts.apps.AttemptsConfig",
    "modules.questions.apps.QuestionsConfig",
    "modules.domain.apps.DomainConfig",
    "modules.search.apps.SearchConfig",
    "modules.taxonomy.apps.TaxonomyConfig",
    "modules.errors.apps.ErrorsConfig",
    "modules.reviews.apps.ReviewsConfig",
    "modules.operations.apps.OperationsConfig",
    "modules.data_management.apps.DataManagementConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "modules.operations.middleware.LocalCorrelationMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "src" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": ["shared.application.context_processors.product_identity"],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "src" / "static"]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "structured": {"()": "modules.operations.structured_logging.StructuredJsonFormatter"}
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "structured",
        }
    },
    "root": {"handlers": ["console"], "level": "WARNING"},
    "loggers": {
        "cei": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        }
    },
}


def local_allowed_hosts() -> list[str]:
    """Leia hosts externos, recusando qualquer interface não local."""
    raw_hosts = os.environ.get("CEI_ALLOWED_HOSTS", ",".join(sorted(LOCAL_ALLOWED_HOSTS)))
    hosts = [host.strip() for host in raw_hosts.split(",") if host.strip()]
    invalid_hosts = sorted(set(hosts) - LOCAL_ALLOWED_HOSTS)
    if invalid_hosts:
        invalid = ", ".join(invalid_hosts)
        raise ImproperlyConfigured(
            f"Produção local aceita somente hosts locais; valores recusados: {invalid}."
        )
    if not hosts:
        raise ImproperlyConfigured("CEI_ALLOWED_HOSTS não pode resultar em uma lista vazia.")
    return hosts


def configured_path(variable: str, default: Path) -> Path:
    """A rota não aceita troca de banco por variáveis herdadas."""
    del default
    if variable in os.environ:
        raise ImproperlyConfigured("Override de banco recusado na rota Local r1.")
    return database_path(test=False)


def required_production_secret() -> str:
    """Exija uma chave externa suficientemente longa para produção local."""
    return production_secret()


def sqlite_database(path: Path, *, test_name: Path | None = None) -> dict[str, object]:
    """Construa a configuração SQLite comum, com timeout explícito."""
    database: dict[str, object] = {
        "ENGINE": "shared.infrastructure.sqlite_backend",
        "NAME": path,
        "OPTIONS": {"timeout": DATABASE_TIMEOUT_SECONDS},
    }
    if test_name is not None:
        database["TEST"] = {"NAME": test_name}
    return database


FILE_UPLOAD_TEMP_DIR = str(runtime_temporary_dir())
