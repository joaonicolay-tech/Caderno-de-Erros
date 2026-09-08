"""Política mínima e controlada de contenção para escritas SQLite críticas."""

import sqlite3
import time
from collections.abc import Callable

from django.db import OperationalError

SQLITE_BUSY_TIMEOUT_SECONDS = 5.0
SQLITE_RETRY_DELAY_SECONDS = 0.150
SQLITE_MAX_RETRIES = 1


def is_sqlite_busy(error: OperationalError) -> bool:
    """Reconheça somente contenção SQLite, sem classificar outros erros como repetíveis."""
    cause = error.__cause__
    sqlite_code = getattr(cause, "sqlite_errorcode", None)
    if isinstance(sqlite_code, int) and sqlite_code & 0xFF in {
        sqlite3.SQLITE_BUSY,
        sqlite3.SQLITE_LOCKED,
    }:
        return True
    message = str(error).casefold()
    return any(
        marker in message
        for marker in (
            "sqlite_busy",
            "database is busy",
            "database is locked",
            "database table is locked",
        )
    )


def run_sqlite_critical_write[ResultT](
    operation: Callable[[], ResultT],
    *,
    sleep: Callable[[float], None] = time.sleep,
) -> ResultT:
    """Execute uma vez e repita uma única vez após 150 ms se o SQLite estiver ocupado."""
    try:
        return operation()
    except OperationalError as error:
        if not is_sqlite_busy(error):
            raise
        sleep(SQLITE_RETRY_DELAY_SECONDS)
        return operation()
