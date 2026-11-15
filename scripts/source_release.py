"""Deterministic public source archive and explicit synthetic-only preparation."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import secrets
import stat
import sys
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

CODE = Path(__file__).absolute().parents[1]
MANIFEST = "SOURCE-MANIFEST.json"
V014 = "fb940bdc2903e2ea4e8875c297ef20c1737cfa7e85f4c505a4601761e0794b3c"  # pragma: allowlist secret -- public candidate digest


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_name(name: str) -> None:
    if not name or "\\" in name or ":" in name or "\x00" in name or name.startswith("/"):
        raise ValueError("Invalid source archive name")
    parts = name.split("/")
    if any(
        p in {"", ".", ".."}
        or p != p.rstrip(" .")
        or any(c in p for c in '*?<>|"')
        or p.split(".")[0].upper()
        in {
            "CON",
            "PRN",
            "AUX",
            "NUL",
            *(f"COM{i}" for i in range(10)),
            *(f"LPT{i}" for i in range(10)),
        }
        for p in parts
    ):
        raise ValueError("Unsafe source archive name")
    blocked = {
        ".git",
        ".venv",
        ".tools",
        "__pycache__",
        "evidence",
        "user",
        "backups",
        "installed",
        "validation",
    }
    if any(p.casefold() in blocked for p in parts) or PurePosixPath(name).name.casefold() in {
        ".local-r1.json",
        ".env",
        "secret.txt",
        "release-authorization.json",
    }:
        raise ValueError("Private instance material is not source")
    if name.lower().endswith(
        (".db", ".db3", ".sqlite", ".sqlite3", "-wal", "-shm", "-journal", ".pem", ".key", ".bak")
    ):
        raise ValueError("Database, backup or secret is not source")


def source_names(code: Path = CODE) -> list[str]:
    value = json.loads((code / "quality/source-files.json").read_text(encoding="utf-8"))
    names = value["files"]
    if not isinstance(names, list) or not all(isinstance(p, str) for p in names):
        raise ValueError("Source allowlist is required")
    if names != sorted(set(names)) or len({p.casefold() for p in names}) != len(names):
        raise ValueError("Source allowlist must be unique and sorted")
    for name in names:
        validate_name(name)
    return names


def payload(code: Path = CODE) -> dict[str, bytes]:
    result = {}
    for name in source_names(code):
        path = code / name
        # Check every component before reading; never follow a source alias.
        current = code
        for component in name.split("/"):
            current /= component
            info = current.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                raise ValueError("Source links/reparse points are prohibited")
        info = path.stat()
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ValueError("Source must be a regular unaliased file")
        raw = path.read_bytes()
        raw.decode("utf-8")
        result[name] = raw.replace(b"\r\n", b"\n")
    return result


def archive_bytes(files: dict[str, bytes]) -> bytes:
    if len({p.casefold() for p in files}) != len(files) or MANIFEST in files:
        raise ValueError("Duplicate or reserved source member")
    for name in files:
        validate_name(name)
    manifest = {
        "format": "CEI-PUBLIC-SOURCE-1",
        "version": "1.0.0",
        "route": "V1.0_LOCAL_R1",
        "distribution": "SOURCE_ONLY_SYNTHETIC_REPRODUCTION_NOT_UNIVERSAL_INSTALLER",
        "v014_reference_sha256": V014,
        "files": [
            {"path": p, "bytes": len(data), "sha256": digest(data)}
            for p, data in sorted(files.items())
        ],
    }
    material = {**files, MANIFEST: (json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode()}
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(material.items()):
            entry = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(entry, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return output.getvalue()


def verify_archive(raw: bytes) -> dict[str, Any]:
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        infos = archive.infolist()
        names = [i.filename for i in infos]
        if (
            len(names) > 1000
            or len({p.casefold() for p in names}) != len(names)
            or names.count(MANIFEST) != 1
        ):
            raise ValueError("Missing manifest or duplicate/excessive members")
        if sum(i.file_size for i in infos) > 50_000_000 or any(
            i.file_size > 5_000_000 for i in infos
        ):
            raise ValueError("Source archive exceeds size limits")
        for info in infos:
            validate_name(info.filename)
            if info.is_dir() or stat.S_ISLNK(info.external_attr >> 16):
                raise ValueError("Source archive cannot contain directories or links")
        manifest: dict[str, Any] = json.loads(archive.read(MANIFEST))
        if manifest.get("format") != "CEI-PUBLIC-SOURCE-1" or manifest.get("version") != "1.0.0":
            raise ValueError("Unknown source manifest")
        rows = manifest["files"]
        expected = {r["path"] for r in rows}
        if len(rows) != len(expected) or expected != set(names) - {MANIFEST}:
            raise ValueError("Manifest/member mismatch")
        for row in rows:
            data = archive.read(row["path"])
            if len(data) != row["bytes"] or digest(data) != row["sha256"]:
                raise ValueError("Source member integrity mismatch")
        allowlist = json.loads(archive.read("quality/source-files.json"))["files"]
        if allowlist != sorted(expected):
            raise ValueError("Source allowlist/member mismatch")
        if archive.testzip() is not None:
            raise ValueError("Source CRC failure")
        return manifest


def prepare(destination: Path, code: Path = CODE) -> dict[str, str]:
    """Create only new synthetic slots; never qualify or activate real data."""
    if os.name != "nt" or not destination.is_absolute() or destination.drive.upper() != "C:":
        raise ValueError("Synthetic reproduction requires an absolute local C: path on Windows")
    if any(p in {".", ".."} or p != p.rstrip(" .") for p in destination.parts[1:]):
        raise ValueError("Ambiguous synthetic destination")
    if str(destination).startswith("\\\\") or destination.exists():
        raise ValueError("Synthetic destination must be new and local")
    # Explicitly selected new root; inspect ancestors, reject aliases before creation.
    sys.path.insert(0, str(code / "src"))
    from shared.infrastructure.local_boundary import _native

    _native(destination.parent, require_existing=True)
    files = payload(code)
    destination.mkdir()
    _native(destination, require_existing=True)
    for slot in ("candidate", "validation", "backups"):
        (destination / slot).mkdir()
    (destination / "validation/tmp").mkdir()
    (destination / "validation/cache").mkdir()
    staged = destination / "candidate"
    for name, data in files.items():
        path = staged / name
        path.parent.mkdir(exist_ok=True, parents=True)
        with path.open("xb") as stream:
            stream.write(data)
    marker = {
        "route": "V1.0_LOCAL_R1",
        "version": "1.0.0",
        "root": str(destination),
        "root_identity": _native(destination, require_existing=True),
        "code_root": str(staged),
        "data_origin": "GENERATED_SYNTHETIC",
        "user_enabled": False,
        "source_distribution": "PUBLIC_SOURCE_SYNTHETIC_ONLY",
    }
    with (staged / ".local-r1.json").open("x", encoding="utf-8") as stream:
        json.dump(marker, stream, indent=2)
    with (destination / "validation/s8-secret.txt").open("x", encoding="utf-8") as stream:
        stream.write(secrets.token_urlsafe(64))
    return {"status": "PREPARED_SYNTHETIC_ONLY", "real_use": "NOT_PROVISIONED_NOT_AUTHORIZED"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("build").add_argument("--output", type=Path, required=True)
    sub.add_parser("verify").add_argument("archive", type=Path)
    sub.add_parser("prepare").add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    if args.action == "build":
        first = archive_bytes(payload())
        if archive_bytes(payload()) != first:
            raise RuntimeError("Source build was not deterministic")
        manifest = verify_archive(first)
        with args.output.open("xb") as stream:
            stream.write(first)
        print(
            json.dumps(
                {
                    "status": "SOURCE_BUILD_VERIFIED",
                    "sha256": digest(first),
                    "files": len(manifest["files"]),
                }
            )
        )
    elif args.action == "verify":
        manifest = verify_archive(args.archive.read_bytes())
        print(json.dumps({"status": "SOURCE_ARCHIVE_VERIFIED", "files": len(manifest["files"])}))
    else:
        print(json.dumps(prepare(args.destination)))


if __name__ == "__main__":
    main()
