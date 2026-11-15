"""Source reproduction must preserve integrity and never activate personal storage."""

import io
import json
import zipfile
from pathlib import Path

import pytest

from scripts import source_release as source
from shared.infrastructure import local_boundary as boundary


@pytest.mark.parametrize(
    "name",
    [
        "../escape",
        "C:/external",
        "/absolute",
        "x\\alias",
        "x:stream",
        "NUL.txt",
        ".local-r1.json",
        "user/secret.txt",
        "x.sqlite3-wal",
        "x.key",
    ],
)
def test_source_rejects_private_or_unsafe_members(name: str) -> None:
    with pytest.raises(ValueError):
        source.archive_bytes({name: b"synthetic"})


def test_source_build_is_deterministic_and_corruption_is_rejected() -> None:
    files = source.payload()
    raw = source.archive_bytes(files)
    assert source.archive_bytes(files) == raw
    manifest = source.verify_archive(raw)
    assert len(manifest["files"]) == len(files)
    assert manifest["distribution"].startswith("SOURCE_ONLY")
    output = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(raw)) as original, zipfile.ZipFile(output, "w") as altered:
        for name in original.namelist():
            altered.writestr(name, b"CORRUPTED" if name == "manage.py" else original.read(name))
    with pytest.raises(ValueError, match="integrity"):
        source.verify_archive(output.getvalue())


def test_duplicate_manifest_and_extra_members_are_rejected() -> None:
    raw = source.archive_bytes(source.payload())
    output = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(raw)) as original, zipfile.ZipFile(output, "w") as altered:
        for name in original.namelist():
            altered.writestr(name, original.read(name))
        altered.writestr("UNLISTED.txt", b"synthetic")
    with pytest.raises(ValueError, match="mismatch"):
        source.verify_archive(output.getvalue())


def test_prepare_new_root_is_synthetic_and_does_not_reuse_private_receipts(tmp_path: Path) -> None:
    destination = tmp_path / "new-instance"
    result = source.prepare(destination)
    marker = json.loads((destination / "candidate/.local-r1.json").read_text())
    assert result["real_use"] == "NOT_PROVISIONED_NOT_AUTHORIZED"
    assert marker["user_enabled"] is False
    assert marker["data_origin"] == "GENERATED_SYNTHETIC"
    assert (
        marker["root_identity"]["file_id"]
        == boundary._native(destination, require_existing=True)["file_id"]
    )
    assert not (destination / "user").exists()
    assert not (destination / "evidence").exists()
    before = (destination / "candidate/.local-r1.json").read_bytes()
    with pytest.raises(ValueError, match="must be new"):
        source.prepare(destination)
    assert (destination / "candidate/.local-r1.json").read_bytes() == before


def test_root_derivation_covers_candidate_and_qualified_layouts(tmp_path: Path) -> None:
    assert boundary.instance_root(tmp_path / "candidate") == tmp_path
    assert boundary.instance_root(tmp_path / "installed/release-001/code") == tmp_path
    assert (
        boundary.instance_root(tmp_path / "validation/s10-activation-rehearsal-001/code")
        == tmp_path
    )
