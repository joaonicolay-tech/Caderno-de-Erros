from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.verify_v01 import (
    DEFINITION_SOURCES,
    GateVerificationError,
    collect_definitions,
    load_json_object,
    verify_coverage,
    verify_markdown_links,
    verify_migration_history,
    verify_repository,
    verify_test_evidence,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "quality" / "v01-gate.json"
V02_MANIFEST_PATH = PROJECT_ROOT / "quality" / "v02-stage1-gate.json"
V03_MANIFEST_PATH = PROJECT_ROOT / "quality" / "v03-stage1-gate.json"
V03_STAGE2_MANIFEST_PATH = PROJECT_ROOT / "quality" / "v03-stage2-gate.json"
V03_STAGE3_MANIFEST_PATH = PROJECT_ROOT / "quality" / "v03-stage3-gate.json"
V03_STAGE4_MANIFEST_PATH = PROJECT_ROOT / "quality" / "v03-stage4-gate.json"
V03_STAGE5_MANIFEST_PATH = PROJECT_ROOT / "quality" / "v03-stage5-gate.json"
V05_S2A_MIGRATIONS_PATH = PROJECT_ROOT / "quality" / "v05-s2a-migrations.json"
V05_S2B_MIGRATIONS_PATH = PROJECT_ROOT / "quality" / "v05-s2b-migrations.json"
STAGE1_MANIFEST_REVISION = "".join(
    ("b64552c1cc6201a82245", "61a6c25f29a2bb8f4a47")  # pragma: allowlist secret
)
STAGE2_MANIFEST_REVISION = "".join(
    ("fdd001b0b23b2cb09e48", "2714e8a68f02c334a90b")  # pragma: allowlist secret
)
STAGE3_MANIFEST_REVISION = "".join(
    ("9176d28a68036bf2aac4", "6df5cba9feac09515b96")  # pragma: allowlist secret
)
STAGE4_MANIFEST_REVISION = "".join(
    ("7b06d30cee61494d742a", "29a4a9fe893531525eab")  # pragma: allowlist secret
)


def _manifest() -> dict[str, object]:
    return load_json_object(MANIFEST_PATH)


def _coverage_report(percent: int = 100) -> dict[str, object]:
    manifest = _manifest()
    policy = manifest["domain_coverage"]
    assert isinstance(policy, dict)
    paths = policy["files"]
    assert isinstance(paths, list)
    return {
        "files": {
            path: {"summary": {"covered_lines": percent, "num_statements": 100}}
            for path in paths
            if isinstance(path, str)
        }
    }


def test_current_repository_satisfies_v03_stage1_contract() -> None:
    verify_test_evidence(PROJECT_ROOT, load_json_object(V03_MANIFEST_PATH))


def test_current_repository_satisfies_v03_stage3_contract() -> None:
    verify_test_evidence(PROJECT_ROOT, load_json_object(V03_STAGE3_MANIFEST_PATH))


def test_current_repository_satisfies_v03_stage4_contract() -> None:
    verify_test_evidence(PROJECT_ROOT, load_json_object(V03_STAGE4_MANIFEST_PATH))


def test_current_repository_satisfies_v03_stage5_contract() -> None:
    verify_repository(
        PROJECT_ROOT,
        V03_STAGE5_MANIFEST_PATH,
        V05_S2B_MIGRATIONS_PATH,
    )


@pytest.mark.parametrize(
    ("revision", "manifest"),
    [
        (
            STAGE1_MANIFEST_REVISION,
            "v03-stage1-gate.json",
        ),
        (
            STAGE2_MANIFEST_REVISION,
            "v03-stage2-gate.json",
        ),
        (
            STAGE3_MANIFEST_REVISION,
            "v03-stage3-gate.json",
        ),
        (
            STAGE4_MANIFEST_REVISION,
            "v03-stage4-gate.json",
        ),
    ],
)
def test_v03_historical_manifests_are_immutable(revision: str, manifest: str) -> None:
    completed = subprocess.run(
        ["git", "show", f"{revision}:quality/{manifest}"],  # noqa: S607
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
    )
    # Git may materialize tracked JSON as CRLF on Windows; content still must match its stage blob.
    current = (PROJECT_ROOT / "quality" / manifest).read_text(encoding="utf-8")
    assert current.replace("\r\n", "\n").encode() == completed.stdout


def test_v02_stage1_manifest_matches_protected_v020_baseline_byte_for_byte() -> None:
    completed = subprocess.run(
        ["git", "show", "v0.2.0:quality/v02-stage1-gate.json"],  # noqa: S607
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
    )

    assert V02_MANIFEST_PATH.read_bytes() == completed.stdout


def test_v03_stage2_manifest_matches_completed_stage_byte_for_byte() -> None:
    completed = subprocess.run(
        ["git", "show", "fdd001b:quality/v03-stage2-gate.json"],  # noqa: S607
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
    )

    assert V03_STAGE2_MANIFEST_PATH.read_bytes() == completed.stdout


def test_v01_manifest_remains_strict_about_later_migrations() -> None:
    with pytest.raises(GateVerificationError, match="Conjunto de migrações protegido divergiu"):
        verify_repository(PROJECT_ROOT, MANIFEST_PATH)


def test_duplicate_json_key_is_blocking(tmp_path: Path) -> None:
    duplicated = tmp_path / "duplicated.json"
    duplicated.write_text('{"release": "V0.1", "release": "V0.2"}', encoding="utf-8")

    with pytest.raises(GateVerificationError, match="duplicada"):
        load_json_object(duplicated)


def test_broken_local_markdown_link_is_blocking(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "README.md").write_text("[ausente](docs/ausente.md)\n", encoding="utf-8")

    with pytest.raises(GateVerificationError, match="Links Markdown locais"):
        verify_markdown_links(tmp_path)


def test_duplicate_canonical_definition_is_blocking(tmp_path: Path) -> None:
    for relative_path in DEFINITION_SOURCES.values():
        source = PROJECT_ROOT / relative_path
        destination = tmp_path / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source.read_bytes())

    rf_document = tmp_path / DEFINITION_SOURCES["RF"]
    with rf_document.open("a", encoding="utf-8") as stream:
        stream.write("\n### `RF-001` — definição duplicada de teste\n")

    with pytest.raises(GateVerificationError, match="Definições canônicas duplicadas: RF-001"):
        collect_definitions(tmp_path)


def test_changed_historical_migration_is_blocking() -> None:
    manifest = copy.deepcopy(load_json_object(V03_STAGE5_MANIFEST_PATH))
    hashes = manifest["migration_sha256"]
    assert isinstance(hashes, dict)
    first_migration = next(iter(hashes))
    hashes[first_migration] = [0] * 32

    with pytest.raises(GateVerificationError, match="Migrações protegidas alteradas"):
        verify_migration_history(
            PROJECT_ROOT,
            manifest,
            load_json_object(V05_S2B_MIGRATIONS_PATH),
        )


def test_missing_test_evidence_is_blocking() -> None:
    manifest = copy.deepcopy(_manifest())
    evidence = manifest["test_evidence"]
    assert isinstance(evidence, dict)
    case = evidence["CT-129"]
    assert isinstance(case, dict)
    case["evidence"] = [
        {"kind": "test", "target": "tests/test_error_categories.py::test_inexistente"}
    ]

    with pytest.raises(GateVerificationError, match="Teste rastreado não existe"):
        verify_test_evidence(PROJECT_ROOT, manifest)


def test_domain_coverage_at_threshold_is_accepted(tmp_path: Path) -> None:
    coverage_path = tmp_path / "coverage.json"
    coverage_path.write_text(json.dumps(_coverage_report(80)), encoding="utf-8")

    verify_coverage(PROJECT_ROOT, MANIFEST_PATH, coverage_path)


def test_domain_coverage_below_threshold_returns_nonzero(tmp_path: Path) -> None:
    coverage_path = tmp_path / "coverage.json"
    coverage_path.write_text(json.dumps(_coverage_report(79)), encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/verify_v01.py",
            "coverage",
            "--coverage-file",
            str(coverage_path),
        ],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 1
    assert "Cobertura de domínio abaixo de 80%" in completed.stderr


def test_authoritative_gate_has_no_security_bypass() -> None:
    gate = (PROJECT_ROOT / "scripts" / "quality.ps1").read_text(encoding="utf-8")

    assert '$ErrorActionPreference = "Stop"' in gate
    assert "SkipVulnerabilityAudit" not in gate
    assert 'Invoke-Tool "detectar segredos"' in gate
    assert "Invoke-PipAudit" in gate
    assert '"pip-audit" "--local" "--strict"' in gate


def test_pytest_uses_an_isolated_temporary_directory_for_each_gate_run() -> None:
    gate = (PROJECT_ROOT / "scripts" / "quality.ps1").read_text(encoding="utf-8")
    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")

    assert '"cei-pytest-" + [Guid]::NewGuid().ToString("N")' in gate
    assert '"--basetemp=$pytestBaseTemp"' in gate
    assert "--basetemp=.tools/pytest-tmp" not in pyproject
