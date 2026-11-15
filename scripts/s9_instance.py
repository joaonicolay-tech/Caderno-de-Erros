"""Operações explícitas sobre a instância sintética selecionada pelo marcador local."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

CODE = Path(__file__).absolute().parents[1]
sys.path[:0] = [str(CODE), str(CODE / "src")]
from shared.infrastructure.local_boundary import (  # noqa: E402
    admit,
    configure_process,
    database_path,
    sqlite_path,
)


def probe() -> dict[str, Any]:
    from django.db import connection

    from modules.accounts.services import LOCAL_WORKSPACE_ID
    from modules.analytics import AnalyticsService
    from modules.operations.integrity import run_integrity_check
    from shared.domain.time import FixedClock, Instant
    from tests.local_snapshot import snapshot

    checker = run_integrity_check()
    if checker.total_findings:
        raise RuntimeError("Checker encontrou inconsistência.")
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA integrity_check")
        integrity = cursor.fetchall()
        cursor.execute("PRAGMA foreign_key_check")
        foreign_keys = cursor.fetchall()
    if integrity != [("ok",)] or foreign_keys:
        raise RuntimeError("Integridade SQLite/FK divergente.")
    analytics = AnalyticsService(
        workspace_id=LOCAL_WORKSPACE_ID,
        clock=FixedClock(Instant(datetime(2026, 11, 8, 15, tzinfo=UTC))),
    )
    metrics = {
        "activity": asdict(analytics.activity()),
        "reviews": asdict(analytics.reviews()),
        "error_categories": asdict(analytics.error_categories()),
        "performance": [asdict(value) for value in analytics.performance_pair()],
    }
    path = Path(str(connection.settings_dict["NAME"]))
    connection.close()
    return {
        "origin": "GENERATED_SYNTHETIC",
        "sqlite_integrity": integrity,
        "foreign_keys": foreign_keys,
        "checker": asdict(checker),
        "snapshot": snapshot(path),
        "metrics": metrics,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "operation", choices=["seed", "probe", "backup", "restore", "prepare", "apply", "cancel"]
    )
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--backup", type=Path)
    parser.add_argument("--destination", type=Path)
    parser.add_argument("--ticket")
    args = parser.parse_args()
    configure_process()
    output = admit(args.result, slots=frozenset({"validation", "evidence"}), require_existing=False)
    if output.exists():
        raise ValueError("Resultado existente preservado.")
    path = database_path(test=False)
    if args.operation == "seed" and path.exists():
        raise ValueError("Seed somente em banco novo; nenhum banco existente é adotado.")
    if args.operation != "seed":
        admit(path)
    os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.production_local"
    import django

    django.setup()
    from django.core.management import call_command
    from django.db import connections

    from modules.data_management.services import (
        create_sqlite_backup,
        manifest_path_for,
        restore_sqlite_backup,
    )
    from modules.data_management.ui_services import (
        apply_prepared_restore,
        cancel_prepared_restore,
        prepare_restore,
        preview_restore,
    )

    result: dict[str, Any]
    if args.operation == "seed":
        from tests.local_fixture import create_fixture

        call_command("migrate", interactive=False, verbosity=0)
        fixture = create_fixture(
            start=datetime(2026, 11, 5, 15, tzinfo=UTC), expected_d1="2026-11-06", secondary=False
        )
        result = {"fixture": fixture, "probe": probe()}
    elif args.operation == "probe":
        result = probe()
    elif args.operation == "backup":
        if args.backup is None:
            raise ValueError("Backup de saída obrigatório.")
        result = asdict(create_sqlite_backup(sqlite_path(args.backup)))
    elif args.operation == "restore":
        if args.backup is None or args.destination is None:
            raise ValueError("Backup e destino novo obrigatórios.")
        result = asdict(restore_sqlite_backup(admit(args.backup), sqlite_path(args.destination)))
    elif args.operation == "prepare":
        if args.backup is None:
            raise ValueError("Backup obrigatório.")
        backup = admit(args.backup)
        manifest = admit(manifest_path_for(backup))
        with backup.open("rb") as source, manifest.open("rb") as sidecar:
            preview = preview_restore(source, sidecar)
        with backup.open("rb") as source, manifest.open("rb") as sidecar:
            ticket = prepare_restore(source, sidecar, expected=preview)
        result = {"ticket": ticket, "preview": asdict(preview)}
    else:
        if args.ticket is None:
            raise ValueError("Ticket obrigatório.")
        if args.operation == "apply":
            result = apply_prepared_restore(args.ticket)
        else:
            cancel_prepared_restore(args.ticket)
            result = {"cancelled": args.ticket}
    connections.close_all()
    with output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, default=str)
    print(json.dumps({"operation": args.operation, "result": str(output)}))


if __name__ == "__main__":
    main()
