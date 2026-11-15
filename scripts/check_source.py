"""Public allowlist, local links, migration baseline and offline secret scan."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any
from unittest.mock import patch
from urllib.parse import unquote

from detect_secrets.core.secrets_collection import SecretsCollection
from detect_secrets.settings import default_settings

from scripts.source_release import CODE, digest, payload


def check() -> dict[str, Any]:
    files = payload()
    baseline = json.loads(files["quality/source-baseline.json"])
    current = {p: digest(raw) for p, raw in files.items()}
    for row in baseline["source_files"]:
        if "/migrations/" in row["path"] or row["path"] == "src/modules/errors/catalog.py":
            if current.get(row["path"]) != row["sha256"]:
                raise RuntimeError("Qualified migration/catalog baseline changed")
    for name, raw in files.items():
        text = raw.decode("utf-8")
        if re.search(r"(?i)[a-z]:[\\/]+Users[\\/]+[^\\/\s<]", text):
            raise RuntimeError("Personal home path in public source: " + name)
        if name.endswith(".md"):
            for link in re.findall(r"\]\(([^)]+)\)", text):
                link = link.strip("<>").split("#", 1)[0]
                if not link or ":" in link:
                    continue
                target = (CODE / Path(name).parent / unquote(link)).absolute()
                if not target.is_file():
                    raise RuntimeError("Broken public source link: " + name)
    collection = SecretsCollection()
    with (
        default_settings() as settings,
        patch(
            "socket.socket.connect", side_effect=RuntimeError("Secret scanner must stay offline")
        ),
        patch(
            "subprocess.Popen", side_effect=RuntimeError("Secret scanner cannot spawn processes")
        ),
        patch(
            "detect_secrets.core.scan.log.warning",
            side_effect=RuntimeError("Secret scan read failure"),
        ),
        patch(
            "detect_secrets.core.scan.log.error",
            side_effect=RuntimeError("Secret detector unavailable"),
        ),
    ):
        if not settings.plugins:
            raise RuntimeError("No active secret detectors")
        for name in files:
            collection.scan_file(str(CODE / name))
    findings: dict[str, Any] = collection.json()
    # Baseline stores hashes of public files. Match only the digest token on a
    # literal sha256 field; never suppress another token or an entire file.
    public_hashes = {row["sha256"] for row in baseline["source_files"]} | {
        baseline["audited_public_base"],
        baseline["v014_reference_sha256"],
    }
    for filename in list(findings):
        lines = Path(filename).read_text(encoding="utf-8").splitlines()
        retained = []
        for row in findings[filename]:
            match = re.fullmatch(
                r'\s*"(?:sha256|audited_public_base|v014_reference_sha256)": "([a-f0-9]{40}|[a-f0-9]{64})",?\s*',
                lines[row["line_number"] - 1],
            )
            approved = (
                Path(filename) == CODE / "quality/source-baseline.json"
                and match is not None
                and match[1] in public_hashes
                and hashlib.sha1(match[1].encode(), usedforsecurity=False).hexdigest()
                == row["hashed_secret"]
            )
            if not approved:
                retained.append(row)
        findings[filename] = retained
        if not findings[filename]:
            del findings[filename]
    if findings:
        print(json.dumps(findings, indent=2))
        raise RuntimeError("Unreviewed potential secret in public source")
    return {
        "source_files": len(files),
        "secrets": "PASS_OFFLINE_SCAN",  # pragma: allowlist secret -- public status label, not a credential
        "links": "PASS",
        "migrations_catalog": "UNCHANGED",
    }


if __name__ == "__main__":
    print(json.dumps(check()))
