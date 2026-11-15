"""Read literal local paths without following reparse points; pin bytes by handle."""

import ctypes as c
import hashlib
import ntpath
import os
from collections.abc import Iterator
from contextlib import contextmanager
from ctypes import wintypes as w
from typing import Any

k = c.WinDLL("kernel32", use_last_error=True)


class Info(c.Structure):
    _fields_ = [
        ("attrs", w.DWORD),
        ("created", w.FILETIME),
        ("accessed", w.FILETIME),
        ("written", w.FILETIME),
        ("volume", w.DWORD),
        ("size_hi", w.DWORD),
        ("size_lo", w.DWORD),
        ("links", w.DWORD),
        ("id_hi", w.DWORD),
        ("id_lo", w.DWORD),
    ]


k.CreateFileW.argtypes = [w.LPCWSTR, w.DWORD, w.DWORD, c.c_void_p, w.DWORD, w.DWORD, w.HANDLE]
k.CreateFileW.restype = w.HANDLE
k.GetFileInformationByHandle.argtypes = [w.HANDLE, c.POINTER(Info)]
k.GetFinalPathNameByHandleW.argtypes = [w.HANDLE, w.LPWSTR, w.DWORD, w.DWORD]
k.ReadFile.argtypes = [w.HANDLE, c.c_void_p, w.DWORD, c.POINTER(w.DWORD), c.c_void_p]
k.CloseHandle.argtypes = [w.HANDLE]
k.WriteFile.argtypes = [w.HANDLE, c.c_void_p, w.DWORD, c.POINTER(w.DWORD), c.c_void_p]
k.SetFilePointer.argtypes = [w.HANDLE, w.LONG, c.c_void_p, w.DWORD]
k.SetEndOfFile.argtypes = [w.HANDLE]
k.FlushFileBuffers.argtypes = [w.HANDLE]


@contextmanager
def guarded_handle(
    path: str, directory: bool = False, write: bool = False
) -> Iterator[tuple[Any, list[dict[str, Any]]]]:
    path = ntpath.abspath(path)
    if (
        not ntpath.isabs(path)
        or path.startswith("\\\\")
        or ntpath.splitdrive(path)[0].upper() != "C:"
    ):
        raise ValueError("only literal C: local paths permitted")
    parts = path.split("\\")
    handles: list[Any] = []
    metadata: list[dict[str, Any]] = []
    try:
        for index in range(1, len(parts) + 1):
            p = "\\".join(parts[:index]) + ("\\" if index == 1 else "")
            leaf = index == len(parts)
            access = (0x80000000 | (0x40000000 if write else 0)) if leaf and not directory else 0x80
            h = k.CreateFileW(p, access, 0 if leaf and write else 1, None, 3, 0x02200000, None)
            if h == c.c_void_p(-1).value:
                raise c.WinError(c.get_last_error())
            handles.append(h)
            info = Info()
            if not k.GetFileInformationByHandle(h, c.byref(info)):
                raise c.WinError(c.get_last_error())
            if info.attrs & 0x400:
                raise ValueError("REPARSE_REFUSED: " + p)
            if leaf and not directory and (info.attrs & 0x10 or info.links != 1):
                raise ValueError("NONREGULAR_OR_HARDLINK_REFUSED: " + p)
            if (not leaf or directory) and not info.attrs & 0x10:
                raise ValueError("DIRECTORY_REQUIRED: " + p)
            buf = c.create_unicode_buffer(32768)
            n = k.GetFinalPathNameByHandleW(h, buf, len(buf), 0)
            if not n or n >= len(buf):
                raise c.WinError(c.get_last_error())
            final = buf.value.removeprefix("\\\\?\\")
            if ntpath.normcase(ntpath.normpath(final)) != ntpath.normcase(ntpath.normpath(p)):
                raise ValueError("FINAL_PATH_MISMATCH: " + p)
            metadata.append(
                {
                    "path": p,
                    "final_path": final,
                    "volume_serial": info.volume,
                    "file_id": (info.id_hi << 32) | info.id_lo,
                    "links": info.links,
                    "attributes": info.attrs,
                }
            )
        yield handles[-1], metadata
    finally:
        for h in reversed(handles):
            k.CloseHandle(h)


def read_handle(handle: Any) -> bytes:
    chunks = []
    block = c.create_string_buffer(1024 * 1024)
    count = w.DWORD()
    while True:
        if not k.ReadFile(handle, block, len(block), c.byref(count), None):
            raise c.WinError(c.get_last_error())
        if not count.value:
            break
        chunks.append(block.raw[: count.value])
    return b"".join(chunks)


def validate(data: bytes, path: str, size: int | None = None, sha256: str | None = None) -> str:
    digest = hashlib.sha256(data).hexdigest()
    if size is not None and len(data) != size:
        raise ValueError("SIZE_MISMATCH: " + path)
    if sha256 is not None and digest.lower() != sha256.lower():
        raise ValueError("HASH_MISMATCH: " + path)
    return digest


def guarded_read(
    path: str, size: int | None = None, sha256: str | None = None
) -> tuple[bytes, dict[str, Any]]:
    with guarded_handle(path) as (h, metadata):
        data = read_handle(h)
        digest = validate(data, path, size, sha256)
        return data, {
            "path": ntpath.abspath(path),
            "size": len(data),
            "sha256": digest,
            "identity": metadata,
        }


def guarded_write(
    path: str, data: bytes, before_size: int, before_sha256: str, append: bool = False
) -> dict[str, Any]:
    with guarded_handle(path, write=True) as (h, metadata):
        before = read_handle(h)
        validate(before, path, before_size, before_sha256)
        output = before + data if append else data
        k.SetFilePointer(h, 0, None, 2 if append else 0)
        write_data = data if append else output
        count = w.DWORD()
        buf = c.create_string_buffer(write_data)
        if not k.WriteFile(h, buf, len(write_data), c.byref(count), None) or count.value != len(
            write_data
        ):
            raise c.WinError(c.get_last_error())
        if not k.SetEndOfFile(h) or not k.FlushFileBuffers(h):
            raise c.WinError(c.get_last_error())
        k.SetFilePointer(h, 0, None, 0)
        after = read_handle(h)
        if after != output:
            raise ValueError("WRITE_VERIFY_FAILED: " + path)
        return {
            "path": path,
            "size": len(after),
            "sha256": hashlib.sha256(after).hexdigest(),
            "identity": metadata,
        }


def guarded_create(path: str, data: bytes) -> dict[str, Any]:
    with guarded_handle(ntpath.dirname(path), directory=True):
        with open(path, "xb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        return guarded_read(path, len(data), hashlib.sha256(data).hexdigest())[1]
