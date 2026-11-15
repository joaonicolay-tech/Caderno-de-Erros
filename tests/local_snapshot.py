"""Snapshots read-only de fixtures locais; nenhuma dependência de probe histórico."""

import hashlib
import json
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any

from shared.infrastructure.local_boundary import admit

V044 = [
    ("auth", "0012_alter_user_first_name_max_length"),
    ("attempts", "0002_review_receipt_constraints"),
    ("errors", "0002_learning_classification"),
    ("questions", "0002_question_catalog"),
    ("reviews", "0002_activation_review_cycle"),
    ("taxonomy", "0001_initial"),
]


def snapshot(path: Path) -> dict[str, Any]:
    path = admit(path)
    with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)) as database:
        database.execute("BEGIN")
        schema = database.execute(
            "SELECT type,name,tbl_name,sql FROM sqlite_master ORDER BY type,name"
        ).fetchall()
        tables = [
            row[0]
            for row in database.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
        ]
        counts = {}
        rows = {}
        for name in tables:
            quoted = '"' + name.replace('"', '""') + '"'
            values = database.execute("SELECT * FROM " + quoted).fetchall()  # noqa: S608 -- identificador escapado de schema sintético próprio
            counts[name] = len(values)
            rows[name] = sorted(values, key=repr)
        database.rollback()
    return {
        "schema": schema,
        "counts": counts,
        "rows_sha256": hashlib.sha256(
            json.dumps(rows, sort_keys=True, default=str).encode()
        ).hexdigest(),
    }
