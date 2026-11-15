#!/usr/bin/env python
"""Entrada de comandos do projeto Django."""

import sys
from pathlib import Path


def main() -> None:
    """Valide a entrada antes de carregar perfis ou abrir qualquer banco."""
    project_root = Path(__file__).resolve().parent
    sys.path.insert(0, str(project_root / "src"))
    from shared.infrastructure.local_boundary import configure_process, entry_settings

    entry_settings(sys.argv)
    configure_process()

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django não está disponível. Execute 'uv sync --locked' antes de continuar."
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
