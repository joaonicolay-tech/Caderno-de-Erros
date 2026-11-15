"""Servidor de qualificação sintética com encerramento cooperativo do próprio worker."""

from __future__ import annotations

import argparse
import ctypes
import json
import os
import sys
import threading
from ctypes import wintypes
from pathlib import Path
from wsgiref.simple_server import WSGIRequestHandler, make_server

CODE = Path(__file__).absolute().parents[1]
sys.path.insert(0, str(CODE / "src"))
from shared.infrastructure.local_boundary import (  # noqa: E402
    admit,
    configure_process,
)


def own_identity() -> dict[str, int]:
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    kernel.GetProcessTimes.argtypes = [wintypes.HANDLE, *([ctypes.POINTER(wintypes.FILETIME)] * 4)]
    created, exited, system, user = (wintypes.FILETIME() for _ in range(4))
    if not kernel.GetProcessTimes(kernel.GetCurrentProcess(), created, exited, system, user):
        raise OSError(ctypes.get_last_error(), "Não foi possível identificar o próprio processo.")
    return {
        "pid": os.getpid(),
        "birth_filetime": (created.dwHighDateTime << 32) | created.dwLowDateTime,
    }


class QuietHandler(WSGIRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        # Os eventos estruturados da aplicação registram resultado sem payload HTTP.
        return


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ready", type=Path, required=True)
    parser.add_argument("--port", type=int, default=0)
    args = parser.parse_args()
    configure_process()
    ready = admit(args.ready, slots=frozenset({"validation"}), require_existing=False)
    if ready.exists() or not 0 <= args.port <= 65535:
        raise ValueError("Use ready novo e porta local válida.")
    os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.production_local"
    from django.contrib.staticfiles.handlers import StaticFilesHandler
    from django.core.wsgi import get_wsgi_application
    from django.db import connections

    app = StaticFilesHandler(get_wsgi_application())
    server = make_server("127.0.0.1", args.port, app, handler_class=QuietHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=False)
    thread.start()
    with ready.open("x", encoding="utf-8") as output:
        json.dump(
            {
                **own_identity(),
                "port": server.server_port,
                "host": "127.0.0.1",
                "code_root": str(CODE),
                "origin": "GENERATED_SYNTHETIC",
                "shutdown": "stdin stop/EOF; server shutdown+join+close; actual worker exits",
            },
            output,
        )
    try:
        for command in sys.stdin:
            if command.strip() == "stop":
                break
    finally:
        server.shutdown()
        thread.join(timeout=15)
        server.server_close()
        connections.close_all()
        if thread.is_alive():
            raise RuntimeError("Servidor não encerrou cooperativamente.")


if __name__ == "__main__":
    main()
