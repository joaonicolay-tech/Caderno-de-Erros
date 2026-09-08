"""Verificações bloqueantes de rastreabilidade, migrações e cobertura por manifesto."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import cast
from urllib.parse import unquote

DEFINITION_SOURCES = {
    "RF": "docs/Caderno_de_Erros_Inteligente_Etapa_3_Requisitos_Funcionais.md",
    "RNF": "docs/Caderno_de_Erros_Inteligente_Etapa_4_Requisitos_Nao_Funcionais.md",
    "RN": "docs/Caderno_de_Erros_Inteligente_Etapa_5_Regras_de_Negocio.md",
    "FL": "docs/Caderno_de_Erros_Inteligente_Etapa_8_Fluxos_Principais.md",
    "CT": "docs/Caderno_de_Erros_Inteligente_Etapa_10_Plano_de_Testes.md",
    "ERR-V01": "docs/Caderno_de_Erros_Inteligente_Gate_de_Implementacao_Auditoria_Final.md",
    "ERR-V02": "docs/ADR-010_Fronteira_Rastreabilidade_e_Dados_V0.2.md",
    "ERR-V03": "docs/Caderno_de_Erros_Inteligente_Etapa_10_Plano_de_Testes.md",
}
DEFINITION_PATTERNS = {
    "RF": re.compile(r"^### `(RF-\d{3})`", re.MULTILINE),
    "RNF": re.compile(r"^### `(RNF-\d{3})`", re.MULTILINE),
    "RN": re.compile(r"^### `(RN-\d{3})`", re.MULTILINE),
    "FL": re.compile(r"^### `(FL-\d{3})`", re.MULTILINE),
    "CT": re.compile(r"^\| `(CT-\d{3})` \|", re.MULTILINE),
    "ERR-V01": re.compile(r"^\| `(ERR-V01-\d{3})` \|", re.MULTILINE),
    "ERR-V02": re.compile(r"^### `(ERR-V02-\d{3})`", re.MULTILINE),
    "ERR-V03": re.compile(r"^## Errata controlada V0\.3 — `(ERR-V03-\d{3})`", re.MULTILINE),
}
CORE_REFERENCE_PATTERN = re.compile(
    r"(?<![A-Z0-9-])(?:RF-\d{3}|RNF-\d{3}|RN-\d{3}|FL-\d{3}|CT-\d{3}|"
    r"ERR-V01-\d{3}|ERR-V02-\d{3}|ERR-V03-\d{3}|ADR-\d{3})(?![A-Z0-9-])"
)
MARKDOWN_LINK_PATTERN = re.compile(r"\]\((?P<target>[^)]+)\)")
TEST_SELECTOR_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class GateVerificationError(RuntimeError):
    """Uma condição obrigatória do gate não foi atendida."""


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise GateVerificationError(f"Chave JSON duplicada: {key}.")
        result[key] = value
    return result


def load_json_object(path: Path) -> dict[str, object]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_reject_duplicate_keys)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise GateVerificationError(f"JSON inválido ou inacessível: {path.name}.") from error
    if not isinstance(raw, dict):
        raise GateVerificationError(f"O documento {path.name} precisa ser um objeto JSON.")
    return cast(dict[str, object], raw)


def _text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise GateVerificationError(
            f"Arquivo obrigatório ausente ou inválido: {relative_path}."
        ) from error


def collect_definitions(root: Path) -> set[str]:
    definitions: list[str] = []
    for family, relative_path in DEFINITION_SOURCES.items():
        source = _text(root, relative_path)
        if family == "CT":
            try:
                source = source.split("## 9. Catálogo detalhado de casos", 1)[1].split(
                    "## 10. Casos críticos expandidos", 1
                )[0]
            except IndexError as error:
                raise GateVerificationError(
                    "A seção canônica dos casos de teste não foi encontrada."
                ) from error
        definitions.extend(DEFINITION_PATTERNS[family].findall(source))

    for adr_path in sorted((root / "docs").glob("ADR-[0-9][0-9][0-9]_*.md")):
        match = re.search(r"^# (ADR-\d{3})\b", adr_path.read_text(encoding="utf-8"), re.MULTILINE)
        if match is None:
            raise GateVerificationError(
                f"ADR sem identificador canônico no título: {adr_path.name}."
            )
        definitions.append(match.group(1))

    duplicates = sorted(
        identifier for identifier, count in Counter(definitions).items() if count > 1
    )
    if duplicates:
        raise GateVerificationError(f"Definições canônicas duplicadas: {', '.join(duplicates)}.")
    return set(definitions)


def verify_markdown_links(root: Path) -> None:
    markdown_files = [root / "README.md", *sorted((root / "docs").glob("*.md"))]
    broken: list[str] = []
    for markdown_file in markdown_files:
        content = markdown_file.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK_PATTERN.finditer(content):
            raw_target = match.group("target").strip().strip("<>")
            if raw_target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            target_without_fragment = unquote(raw_target.split("#", 1)[0])
            if not (markdown_file.parent / target_without_fragment).exists():
                broken.append(f"{markdown_file.relative_to(root)} -> {raw_target}")
    if broken:
        raise GateVerificationError(f"Links Markdown locais inválidos: {'; '.join(broken)}.")


def verify_references(root: Path, manifest: Mapping[str, object], definitions: set[str]) -> None:
    raw_required = manifest.get("required_identifiers")
    raw_scope = manifest.get("reference_scope")
    if not isinstance(raw_required, list) or not all(
        isinstance(item, str) for item in raw_required
    ):
        raise GateVerificationError("required_identifiers precisa ser uma lista de IDs.")
    if not isinstance(raw_scope, list) or not all(isinstance(item, str) for item in raw_scope):
        raise GateVerificationError("reference_scope precisa ser uma lista de arquivos.")

    required = cast(list[str], raw_required)
    if len(required) != len(set(required)):
        raise GateVerificationError("required_identifiers contém duplicação.")
    missing = sorted(set(required) - definitions)
    if missing:
        raise GateVerificationError(f"IDs obrigatórios sem definição: {', '.join(missing)}.")

    invalid_references: list[str] = []
    for relative_path in cast(list[str], raw_scope):
        content = _text(root, relative_path)
        for identifier in CORE_REFERENCE_PATTERN.findall(content):
            if identifier not in definitions:
                invalid_references.append(f"{relative_path}: {identifier}")
    if invalid_references:
        raise GateVerificationError(
            f"Referências a IDs inexistentes no escopo: {'; '.join(invalid_references)}."
        )


def _verify_test_target(root: Path, target: str) -> None:
    try:
        relative_path, selector = target.split("::", 1)
    except ValueError as error:
        raise GateVerificationError(f"Seletor de teste inválido: {target}.") from error
    if TEST_SELECTOR_PATTERN.fullmatch(selector) is None:
        raise GateVerificationError(f"Nome de teste inválido: {target}.")
    content = _text(root, relative_path)
    if re.search(rf"^def {re.escape(selector)}\(", content, re.MULTILINE) is None:
        raise GateVerificationError(f"Teste rastreado não existe: {target}.")


def verify_test_evidence(root: Path, manifest: Mapping[str, object]) -> None:
    raw_evidence = manifest.get("test_evidence")
    raw_pending = manifest.get("promotion_pending_cases")
    if not isinstance(raw_evidence, dict) or not isinstance(raw_pending, list):
        raise GateVerificationError("A matriz executável de testes está ausente.")
    evidence_map = cast(dict[str, object], raw_evidence)
    pending_cases = set(cast(list[str], raw_pending))
    v01_expected_cases = {
        "CT-001",
        "CT-002",
        "CT-073",
        "CT-074",
        "CT-081",
        "CT-099",
        "CT-104",
        "CT-123",
        "CT-127",
        "CT-129",
        "CT-130",
        "CT-131",
        "CT-132",
        "CT-133",
        "CT-134",
        "CT-135",
        "CT-136",
    }
    raw_expected_cases = manifest.get("expected_test_cases")
    if raw_expected_cases is None:
        expected_cases = v01_expected_cases
    elif isinstance(raw_expected_cases, list) and all(
        isinstance(item, str) for item in raw_expected_cases
    ):
        expected_cases = set(cast(list[str], raw_expected_cases))
        if len(expected_cases) != len(raw_expected_cases):
            raise GateVerificationError("expected_test_cases contém duplicação.")
    else:
        raise GateVerificationError("expected_test_cases precisa ser uma lista de CTs.")
    if set(evidence_map) != expected_cases:
        difference = sorted(set(evidence_map) ^ expected_cases)
        raise GateVerificationError(
            f"Matriz executável incompleta ou excedente: {', '.join(difference)}."
        )
    if pending_cases:
        raise GateVerificationError("Nenhum CT do marco pode permanecer pendente de promoção.")

    gate_script = _text(root, "scripts/quality.ps1")
    for case_id, raw_entry in evidence_map.items():
        if not isinstance(raw_entry, dict):
            raise GateVerificationError(f"Evidência inválida para {case_id}.")
        entry = cast(dict[str, object], raw_entry)
        expected_status = "stage9-pending" if case_id in pending_cases else "executable"
        if entry.get("status") != expected_status:
            raise GateVerificationError(f"Status incorreto para {case_id}.")
        raw_items = entry.get("evidence")
        if not isinstance(raw_items, list) or not raw_items:
            raise GateVerificationError(f"{case_id} não possui evidência.")
        for raw_item in raw_items:
            if not isinstance(raw_item, dict):
                raise GateVerificationError(f"Evidência malformada para {case_id}.")
            item = cast(dict[str, object], raw_item)
            kind = item.get("kind")
            target = item.get("target")
            if not isinstance(target, str):
                raise GateVerificationError(f"Alvo de evidência inválido para {case_id}.")
            if kind == "test":
                _verify_test_target(root, target)
            elif kind == "gate-step":
                if target not in gate_script:
                    raise GateVerificationError(f"Etapa do gate ausente para {case_id}: {target}.")
            elif kind == "documentation":
                _text(root, target)
            else:
                raise GateVerificationError(f"Tipo de evidência desconhecido para {case_id}.")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _migration_hashes(raw_hashes: object) -> dict[str, str]:
    if not isinstance(raw_hashes, dict):
        raise GateVerificationError("Manifesto de hashes das migrações é inválido.")
    expected_hashes: dict[str, str] = {}
    for raw_path, raw_bytes in raw_hashes.items():
        if (
            not isinstance(raw_path, str)
            or not isinstance(raw_bytes, list)
            or len(raw_bytes) != 32
            or not all(isinstance(item, int) and 0 <= item <= 255 for item in raw_bytes)
        ):
            raise GateVerificationError("Manifesto de hashes das migrações é inválido.")
        expected_hashes[raw_path] = bytes(cast(list[int], raw_bytes)).hex()
    return expected_hashes


def verify_migration_history(root: Path, manifest: Mapping[str, object]) -> None:
    raw_legacy_hashes = manifest.get("migration_sha256")
    if raw_legacy_hashes is not None:
        expected_hashes = _migration_hashes(raw_legacy_hashes)
    else:
        historical_hashes = _migration_hashes(manifest.get("historical_migration_sha256"))
        current_hashes = _migration_hashes(manifest.get("current_migration_sha256"))
        overlap = sorted(set(historical_hashes) & set(current_hashes))
        if overlap:
            raise GateVerificationError(
                f"Migrações repetidas entre histórico e marco atual: {', '.join(overlap)}."
            )
        expected_hashes = historical_hashes | current_hashes
    discovered = {
        path.relative_to(root).as_posix()
        for path in (root / "src" / "modules").glob("*/migrations/[0-9]*.py")
    }
    if discovered != set(expected_hashes):
        difference = sorted(discovered ^ set(expected_hashes))
        raise GateVerificationError(
            f"Conjunto de migrações protegido divergiu: {', '.join(difference)}."
        )
    changed = [
        relative_path
        for relative_path, expected_hash in expected_hashes.items()
        if _sha256(root / relative_path) != expected_hash
    ]
    if changed:
        raise GateVerificationError(f"Migrações protegidas alteradas: {', '.join(changed)}.")


def verify_repository(root: Path, manifest_path: Path) -> None:
    manifest = load_json_object(manifest_path)
    verify_markdown_links(root)
    definitions = collect_definitions(root)
    verify_references(root, manifest, definitions)
    verify_test_evidence(root, manifest)
    verify_migration_history(root, manifest)


def verify_coverage(root: Path, manifest_path: Path, coverage_path: Path) -> None:
    manifest = load_json_object(manifest_path)
    coverage = load_json_object(coverage_path)
    raw_policy = manifest.get("domain_coverage")
    raw_files = coverage.get("files")
    if not isinstance(raw_policy, dict) or not isinstance(raw_files, dict):
        raise GateVerificationError("Política ou relatório de cobertura inválido.")
    policy = cast(dict[str, object], raw_policy)
    threshold = policy.get("minimum_line_percent")
    policy_files = policy.get("files")
    if not isinstance(threshold, int) or threshold != 80:
        raise GateVerificationError("O limiar documental de cobertura precisa permanecer em 80%.")
    if not isinstance(policy_files, list) or not all(
        isinstance(item, str) for item in policy_files
    ):
        raise GateVerificationError("A lista de módulos de domínio é inválida.")

    normalized_reports = {
        str(path).replace("\\", "/"): report for path, report in raw_files.items()
    }
    below: list[str] = []
    for relative_path in cast(list[str], policy_files):
        if not (root / relative_path).is_file():
            raise GateVerificationError(
                f"Módulo de domínio configurado não existe: {relative_path}."
            )
        raw_report = normalized_reports.get(relative_path)
        if not isinstance(raw_report, dict):
            raise GateVerificationError(
                f"Cobertura ausente para módulo de domínio: {relative_path}."
            )
        summary = cast(dict[str, object], raw_report).get("summary")
        if not isinstance(summary, dict):
            raise GateVerificationError(f"Resumo de cobertura inválido: {relative_path}.")
        typed_summary = cast(dict[str, object], summary)
        covered = typed_summary.get("covered_lines")
        statements = typed_summary.get("num_statements")
        if not isinstance(covered, int) or not isinstance(statements, int) or statements <= 0:
            raise GateVerificationError(f"Contadores de cobertura inválidos: {relative_path}.")
        percent = covered * 100 / statements
        if percent < threshold:
            below.append(f"{relative_path} ({percent:.2f}%)")
    if below:
        raise GateVerificationError(f"Cobertura de domínio abaixo de 80%: {', '.join(below)}.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("repository", "coverage"))
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--coverage-file", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    root = arguments.root.resolve()
    manifest_path = (arguments.manifest or root / "quality" / "v01-gate.json").resolve()
    release = str(load_json_object(manifest_path).get("release", "release desconhecida"))
    try:
        if arguments.command == "repository":
            verify_repository(root, manifest_path)
            print(f"Rastreabilidade, Markdown e migrações protegidas de {release}: OK")
        else:
            if arguments.coverage_file is None:
                raise GateVerificationError("--coverage-file é obrigatório para cobertura.")
            verify_coverage(root, manifest_path, arguments.coverage_file.resolve())
            print(f"Cobertura de domínio/regras de {release} (mínimo 80% por módulo): OK")
    except GateVerificationError as error:
        print(f"ERRO: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
