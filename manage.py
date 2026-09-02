#!/usr/bin/env python
"""Entrada de comandos do projeto Django."""

import os
import sys
from pathlib import Path


def main() -> None:
    """Execute comandos administrativos com desenvolvimento como perfil padrão."""
    project_root = Path(__file__).resolve().parent
    sys.path.insert(0, str(project_root / "src"))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django não está disponível. Execute 'uv sync --locked' antes de continuar."
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
