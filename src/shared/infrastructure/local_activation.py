"""Private installed-mode activation; no live release is inferred from a flag."""

from __future__ import annotations

import ctypes
import hashlib
import json
import re
from ctypes import wintypes
from pathlib import Path
from typing import Any

from shared.infrastructure.local_boundary import ROOT, BoundaryError, _Info, _native, admit

_VERIFIED_PAYLOADS: set[tuple[str, str]] = set()


def validate_private_aces(owner: str, aces: list[dict[str, Any]], expected_owner: str) -> None:
    trusted = {expected_owner, "S-1-5-18", "S-1-5-32-544"}
    if (
        owner not in trusted
        or len(aces) != 3
        or {row.get("sid") for row in aces} != trusted
        or any(row.get("type") != 0 or row.get("mask") != 0x1F01FF for row in aces)
    ):
        raise BoundaryError("Proteção privada deixou de corresponder à instalação qualificada.")


def require_private_policy(path: Path, expected_owner: str) -> None:
    if path != ROOT:
        path = admit(path, slots=frozenset({"user", "backups", "installed", "validation"}))
    identity = _native(path, require_existing=True)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    api = ctypes.WinDLL("advapi32", use_last_error=True)
    kernel.CreateFileW.argtypes = [
        wintypes.LPCWSTR,
        wintypes.DWORD,
        wintypes.DWORD,
        ctypes.c_void_p,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.HANDLE,
    ]
    kernel.CreateFileW.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.GetFileInformationByHandle.argtypes = [wintypes.HANDLE, ctypes.POINTER(_Info)]
    kernel.LocalFree.argtypes = [ctypes.c_void_p]
    api.GetSecurityInfo.argtypes = [
        wintypes.HANDLE,
        ctypes.c_int,
        wintypes.DWORD,
        *([ctypes.POINTER(ctypes.c_void_p)] * 5),
    ]
    api.GetSecurityInfo.restype = wintypes.DWORD
    api.GetAce.argtypes = [ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(ctypes.c_void_p)]
    api.GetAce.restype = wintypes.BOOL
    api.ConvertSidToStringSidW.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_wchar_p)]
    api.ConvertSidToStringSidW.restype = wintypes.BOOL
    api.GetSecurityDescriptorControl.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_ushort),
        ctypes.POINTER(wintypes.DWORD),
    ]
    api.GetSecurityDescriptorControl.restype = wintypes.BOOL

    def sid(pointer: Any) -> str:
        output = ctypes.c_wchar_p()
        if not api.ConvertSidToStringSidW(pointer, ctypes.byref(output)):
            raise BoundaryError("SID de proteção indisponível.")
        try:
            if output.value is None:
                raise BoundaryError("SID privado vazio.")
            return output.value
        finally:
            kernel.LocalFree(ctypes.cast(output, ctypes.c_void_p))

    handle = kernel.CreateFileW(str(path), 0x20080, 1, None, 3, 0x02200000, None)
    if handle == ctypes.c_void_p(-1).value:
        raise BoundaryError("Não foi possível verificar a proteção privada.")
    try:
        info = _Info()
        if not kernel.GetFileInformationByHandle(handle, ctypes.byref(info)):
            raise BoundaryError("Identidade privada indisponível.")
        if (
            info.volume != identity["volume_serial"]
            or (info.id_hi << 32 | info.id_lo) != identity["file_id"]
        ):
            raise BoundaryError("Identidade privada mudou durante a verificação.")
        owner, group, dacl, sacl, descriptor = (ctypes.c_void_p() for _ in range(5))
        result = api.GetSecurityInfo(
            handle,
            1,
            7,
            ctypes.byref(owner),
            ctypes.byref(group),
            ctypes.byref(dacl),
            ctypes.byref(sacl),
            ctypes.byref(descriptor),
        )
        if result:
            raise BoundaryError("Descritor privado indisponível.")
        try:
            if not dacl.value:
                raise BoundaryError("DACL privada ausente.")
            entries = []
            for index in range(ctypes.c_ushort.from_address(dacl.value + 4).value):
                ace = ctypes.c_void_p()
                if not api.GetAce(dacl, index, ctypes.byref(ace)) or ace.value is None:
                    raise BoundaryError("ACE privada não verificável.")
                entries.append(
                    {
                        "type": ctypes.c_ubyte.from_address(ace.value).value,
                        "mask": ctypes.c_uint32.from_address(ace.value + 4).value,
                        "sid": sid(ace.value + 8),
                    }
                )
            validate_private_aces(sid(owner), entries, expected_owner)
            control = ctypes.c_ushort()
            revision = wintypes.DWORD()
            if not api.GetSecurityDescriptorControl(
                descriptor, ctypes.byref(control), ctypes.byref(revision)
            ):
                raise BoundaryError("Herança privada não verificável.")
            if path == ROOT and not control.value & 0x1000:
                raise BoundaryError("Raiz privada voltou a herdar permissões externas.")
        finally:
            kernel.LocalFree(descriptor)
    finally:
        kernel.CloseHandle(handle)


def activation_paths(value: dict[str, Any], code: Path) -> tuple[Path, str]:
    purpose = value.get("activation_purpose", "REAL_USE")
    if purpose == "REAL_USE":
        if not str(code).lower().startswith((str(ROOT / "installed") + "\\").lower()):
            raise BoundaryError("Uso real permitido somente na instalação qualificada.")
        storage = ROOT / "user"
    elif purpose == "SYNTHETIC_REHEARSAL":
        if (
            code.name != "code"
            or code.parent.parent != ROOT / "validation"
            or re.fullmatch(r"s10-activation-rehearsal-[0-9]{3}", code.parent.name) is None
            or value.get("data_origin") != "GENERATED_SYNTHETIC"
        ):
            raise BoundaryError("Ensaio sintético não pode ativar instalação ou dados reais.")
        storage = code.parent / "user"
    else:
        raise BoundaryError("Finalidade de ativação não admitida.")
    if (
        value.get("database_slot") != (storage / "cei.sqlite3").relative_to(ROOT).as_posix()
        or value.get("secret_slot") != (storage / "secret.txt").relative_to(ROOT).as_posix()
    ):
        raise BoundaryError("Slots de ativação não correspondem à finalidade fixa.")
    return storage, purpose


def validate_activation_document(
    document: dict[str, Any], expected: dict[str, Any], *, synthetic: bool = False
) -> None:
    if (
        document.get("schema") != "CEI_LOCAL_RELEASE_AUTHORIZATION_1"
        or document.get("purpose") != ("SYNTHETIC_REHEARSAL" if synthetic else "REAL_USE")
        or document.get("approved") is not True
        or document.get("source")
        != ("EXECUTOR_SYNTHETIC_TEST" if synthetic else "USER_MESSAGE_THIS_CHAT")
        or not document.get("decision_text")
        or not document.get("decision_reference")
        or any(document.get(key) != value for key, value in expected.items())
    ):
        raise BoundaryError("Uso real exige a decisão final expressa vinculada ao artefato.")


def validate_real_marker(value: dict[str, Any], code: Path) -> None:
    storage, purpose = activation_paths(value, code)
    owner = value.get("owner_sid")
    if not isinstance(owner, str) or not owner.startswith("S-1-5-"):
        raise BoundaryError("Titular da instalação privada ausente.")
    for path in (ROOT, storage, ROOT / "backups", code):
        require_private_policy(path, owner)
    digest = value.get("release_authorization_sha256")
    if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
        raise BoundaryError("Uso real ainda aguarda a decisão final de liberação.")
    authorization = admit(
        storage / "release-authorization.json",
        slots=frozenset({"validation"})
        if purpose == "SYNTHETIC_REHEARSAL"
        else frozenset({"user"}),
    )
    require_private_policy(authorization, owner)
    raw = authorization.read_bytes()
    if hashlib.sha256(raw).hexdigest() != digest:
        raise BoundaryError("Decisão final diverge do vínculo privado.")
    expected: dict[str, Any] = {
        "code_root": str(code),
        "release_zip_sha256": value.get("release_zip_sha256"),
        "release_manifest_sha256": value.get("release_manifest_sha256"),
        "owner_sid": owner,
        "root_identity": {key: value["root_identity"][key] for key in ("file_id", "volume_serial")},
    }
    if any(
        not isinstance(expected[key], str) or re.fullmatch(r"[0-9a-f]{64}", expected[key]) is None
        for key in ("release_zip_sha256", "release_manifest_sha256")
    ):
        raise BoundaryError("Artefato final sem identidade exata.")
    validate_activation_document(
        json.loads(raw), expected, synthetic=purpose == "SYNTHETIC_REHEARSAL"
    )
    manifest_path = admit(
        code / "RELEASE-MANIFEST.json", slots=frozenset({"installed", "validation"})
    )
    manifest_raw = manifest_path.read_bytes()
    if hashlib.sha256(manifest_raw).hexdigest() != expected["release_manifest_sha256"]:
        raise BoundaryError("Manifesto instalado mudou após a liberação.")
    cache_key = (str(code), expected["release_manifest_sha256"])
    if cache_key not in _VERIFIED_PAYLOADS:
        manifest = json.loads(manifest_raw)
        for row in manifest["files"]:
            name = row["path"]
            if (
                not isinstance(name, str)
                or name.startswith("/")
                or "\\" in name
                or ":" in name
                or any(part in {"", ".", ".."} for part in name.split("/"))
            ):
                raise BoundaryError("Manifesto instalado contém caminho não admitido.")
            path = admit(code / name, slots=frozenset({"installed", "validation"}))
            require_private_policy(path, owner)
            content = path.read_bytes()
            if len(content) != row["bytes"] or hashlib.sha256(content).hexdigest() != row["sha256"]:
                raise BoundaryError("Arquivo instalado diverge do artefato aprovado.")
        _VERIFIED_PAYLOADS.add(cache_key)
    for path in (storage / "cei.sqlite3", storage / "secret.txt", storage / "tmp"):
        require_private_policy(path, owner)
