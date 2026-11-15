"""Fronteira Windows: admissão lexical antes de consultar o alvo."""

import ctypes
import json
import ntpath
import os
import sys
import tempfile
import uuid
from ctypes import wintypes
from pathlib import Path
from typing import Any

CODE = Path(__file__).absolute().parents[3]


def instance_root(code: Path) -> Path:
    """Derive the instance from its fixed layout, never an environment override."""
    if code.name == "code" and code.parent.parent.name in {"installed", "validation"}:
        return code.parents[2]
    return code.parent


ROOT = instance_root(CODE)
DATA_SLOTS = frozenset({"validation", "backups"})
_REAL_USE = False
_USER_ACTIVE = False
_ACTIVE_USER_DIR = ROOT / "user"
_RESERVED = frozenset(
    {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(10)), *(f"LPT{i}" for i in range(10))}
)


class BoundaryError(ValueError):
    """Operação recusada sem consultar um alvo externo."""


class _Info(ctypes.Structure):
    _fields_ = [
        ("attributes", wintypes.DWORD),
        ("created", wintypes.FILETIME),
        ("accessed", wintypes.FILETIME),
        ("written", wintypes.FILETIME),
        ("volume", wintypes.DWORD),
        ("size_hi", wintypes.DWORD),
        ("size_lo", wintypes.DWORD),
        ("links", wintypes.DWORD),
        ("id_hi", wintypes.DWORD),
        ("id_lo", wintypes.DWORD),
    ]


def lexical(path: Path | str, *, slots: frozenset[str] | None = None) -> Path:
    """Rejeite fora da allowlist antes de stat, resolve, open ou API nativa."""
    if slots is None:
        slots = frozenset({"user", "backups"}) if _REAL_USE else DATA_SLOTS
    raw = str(path)
    if not raw or raw.startswith(("\\\\", "//")) or not ntpath.isabs(raw):
        raise BoundaryError("Use um caminho absoluto do perímetro Local r1.")
    parts = raw.replace("/", "\\").split("\\")
    if parts[0].lower() != "c:" or any(
        p in {"", ".", ".."}
        or p != p.rstrip(" .")
        or any(c in p for c in ":*?<>|\x00")
        or p.split(".", 1)[0].upper() in _RESERVED
        for p in parts[1:]
    ):
        raise BoundaryError("Caminho ambíguo, dispositivo ou escape recusado.")
    normalized = ntpath.normcase(ntpath.normpath(raw))
    prefix = ntpath.normcase(str(ROOT)) + "\\"
    if not normalized.startswith(prefix):
        raise BoundaryError("Caminho externo ao perímetro Local r1 recusado.")
    if normalized[len(prefix) :].split("\\", 1)[0] not in slots:
        raise BoundaryError("Slot não admitido para esta operação.")
    return Path(ntpath.normpath(raw))


def _native(path: Path, *, require_existing: bool) -> dict[str, int]:
    if os.name != "nt":
        raise BoundaryError("Esta rota exige Windows nativo.")
    k = ctypes.WinDLL("kernel32", use_last_error=True)
    k.CreateFileW.argtypes = [
        wintypes.LPCWSTR,
        wintypes.DWORD,
        wintypes.DWORD,
        ctypes.c_void_p,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.HANDLE,
    ]
    k.CreateFileW.restype = wintypes.HANDLE
    k.GetFileInformationByHandle.argtypes = [wintypes.HANDLE, ctypes.POINTER(_Info)]
    k.GetFinalPathNameByHandleW.argtypes = [
        wintypes.HANDLE,
        wintypes.LPWSTR,
        wintypes.DWORD,
        wintypes.DWORD,
    ]
    k.CloseHandle.argtypes = [wintypes.HANDLE]
    parts = str(path).split("\\")
    handles = []
    result: dict[str, int] = {}
    try:
        for i in range(1, len(parts) + 1):
            expected = "\\".join(parts[:i]) + ("\\" if i == 1 else "")
            h = k.CreateFileW(expected, 0x80, 3, None, 3, 0x02200000, None)
            if h == ctypes.c_void_p(-1).value:
                error = ctypes.get_last_error()
                if error == 2 and i == len(parts) and not require_existing:
                    return result
                raise BoundaryError(
                    f"Identidade do objeto admitido indisponível (WinError {error})."
                )
            handles.append(h)
            info = _Info()
            if not k.GetFileInformationByHandle(h, ctypes.byref(info)):
                raise BoundaryError("Não foi possível conferir a identidade nativa.")
            if info.attributes & 0x400:
                raise BoundaryError("Reparse point ou junction recusado.")
            if not info.attributes & 0x10 and info.links != 1:
                raise BoundaryError("Arquivo com alias por hardlink recusado.")
            final = ctypes.create_unicode_buffer(32768)
            length = k.GetFinalPathNameByHandleW(h, final, len(final), 0)
            if not length or length >= len(final):
                raise BoundaryError("Caminho físico não demonstrado.")
            actual = final.value.removeprefix("\\\\?\\")
            if ntpath.normcase(ntpath.normpath(actual)) != ntpath.normcase(
                ntpath.normpath(expected)
            ):
                raise BoundaryError("Caminho físico divergente; operação recusada.")
            result = {
                "volume_serial": info.volume,
                "file_id": (info.id_hi << 32) | info.id_lo,
                "links": info.links,
                "attributes": info.attributes,
            }
        return result
    finally:
        for h in reversed(handles):
            k.CloseHandle(h)


def admit(
    path: Path | str, *, slots: frozenset[str] | None = None, require_existing: bool = True
) -> Path:
    result = lexical(path, slots=slots)
    _native(result, require_existing=require_existing)
    return result


def directory(path: Path | str) -> Path:
    result = admit(path, require_existing=False)
    if not result.exists():
        result.mkdir()
    return admit(result)


def marker() -> dict[str, Any]:
    path = admit(CODE / ".local-r1.json", slots=frozenset({"candidate", "installed", "validation"}))
    value: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    if (
        value.get("route") != "V1.0_LOCAL_R1"
        or value.get("root") != str(ROOT)
        or (value.get("user_enabled") is not False and value.get("user_enabled") is not True)
        or value.get("code_root", str(ROOT / "candidate")) != str(CODE)
    ):
        raise BoundaryError("Marcador Local r1 inválido ou uso real ainda não autorizado.")
    actual = _native(ROOT, require_existing=True)
    expected = value["root_identity"]
    if any(actual[k] != expected[k] for k in ("file_id", "volume_serial")):
        raise BoundaryError("Identidade da raiz diverge do marcador.")
    if value["user_enabled"] is True:
        from shared.infrastructure.local_activation import validate_real_marker

        validate_real_marker(value, CODE)
    return value


def configure_process() -> None:
    if sys.flags.optimize:
        raise BoundaryError("Execução otimizada não admitida na qualificação.")
    global _REAL_USE, _USER_ACTIVE, _ACTIVE_USER_DIR
    value = marker()
    _USER_ACTIVE = value["user_enabled"] is True
    _REAL_USE = False
    if _USER_ACTIVE:
        from shared.infrastructure.local_activation import activation_paths

        _ACTIVE_USER_DIR, purpose = activation_paths(value, CODE)
        _REAL_USE = purpose == "REAL_USE"
    for variable in (
        "CEI_PRODUCTION_LOCAL_DB",
        "CEI_DEVELOPMENT_DB",
        "DATABASE_URL",
        "CEI_LOCAL_ROOT",
        "PYTHONHOME",
    ):
        if variable in os.environ:
            raise BoundaryError("Override de banco, runtime ou raiz recusado.")
    tmp = runtime_temporary_dir()
    os.environ["TEMP"] = str(tmp)
    os.environ["TMP"] = str(tmp)
    tempfile.tempdir = str(tmp)


def runtime_temporary_dir() -> Path:
    return admit((_ACTIVE_USER_DIR if _USER_ACTIVE else ROOT / "validation") / "tmp")


def recovery_directory() -> Path:
    return directory((_ACTIVE_USER_DIR if _USER_ACTIVE else ROOT / "validation") / "recovery")


def marked_validation_file(field: str, default: str, *, require_existing: bool) -> Path:
    value = marker().get(field, default)
    if not isinstance(value, str):
        raise BoundaryError("Slot do marcador deve ser um caminho relativo explícito.")
    relative = value.replace("\\", "/")
    if (
        not relative.startswith("validation/")
        or ":" in relative
        or any(x in {"", ".", ".."} for x in relative.split("/"))
    ):
        raise BoundaryError("Slot do marcador fora da validação sintética.")
    if field == "database_slot" and not relative.endswith(".sqlite3"):
        raise BoundaryError("Banco de validação deve ser um arquivo SQLite próprio.")
    return admit(
        ROOT / relative, slots=frozenset({"validation"}), require_existing=require_existing
    )


def database_path(*, test: bool) -> Path:
    if test:
        if _USER_ACTIVE:
            raise BoundaryError("Perfil de teste não opera sobre a instalação de uso real.")
        folder = directory(ROOT / "validation" / f"test-{os.getpid()}-{uuid.uuid4().hex}")
        return admit(folder / "test.sqlite3", require_existing=False)
    if _USER_ACTIVE:
        return admit(
            _ACTIVE_USER_DIR / "cei.sqlite3",
            slots=frozenset({"user"}) if _REAL_USE else frozenset({"validation"}),
        )
    return marked_validation_file(
        "database_slot", "validation/s8-baseline.sqlite3", require_existing=False
    )


def production_secret(secret_path: Path | None = None) -> str:
    if _USER_ACTIVE and secret_path is None:
        secret_path = _ACTIVE_USER_DIR / "secret.txt"
    path = (
        admit(secret_path)
        if secret_path is not None
        else marked_validation_file(
            "secret_slot", "validation/s8-secret.txt", require_existing=True
        )
    )
    value = path.read_text(encoding="utf-8").strip()
    if len(value) < 50:
        raise BoundaryError("Segredo exclusivo ausente ou insuficiente.")
    return value


def sqlite_path(path: Path | str) -> Path:
    value = admit(path, require_existing=False)
    for suffix in ("-wal", "-shm", "-journal"):
        admit(str(value) + suffix, require_existing=False)
    return value


def entry_settings(arguments: list[str]) -> str:
    if any(arg == "--pythonpath" or arg.startswith("--pythonpath=") for arg in arguments):
        raise BoundaryError("Override do caminho de módulos recusado.")
    settings = os.environ.get("DJANGO_SETTINGS_MODULE", "config.settings.production_local")
    for i, arg in enumerate(arguments):
        if arg.startswith("--settings="):
            settings = arg.split("=", 1)[1]
        elif arg == "--settings" and i + 1 < len(arguments):
            settings = arguments[i + 1]
    if settings not in {"config.settings.production_local", "config.settings.test"}:
        raise BoundaryError("Perfil não admitido pela rota Local r1.")
    if "runserver" in arguments:
        if settings != "config.settings.production_local":
            raise BoundaryError("Uso exige production_local.")
        for arg in arguments[arguments.index("runserver") + 1 :]:
            if arg.startswith("--"):
                continue
            if not arg.isdigit() and not (arg.startswith("127.0.0.1:") and arg[10:].isdigit()):
                raise BoundaryError("Servidor permitido somente em 127.0.0.1.")
    os.environ["DJANGO_SETTINGS_MODULE"] = settings
    return settings
