from typing import Any

from django.db.backends.sqlite3.base import DatabaseWrapper as SQLiteWrapper

from shared.infrastructure.local_boundary import sqlite_path


class DatabaseWrapper(SQLiteWrapper):
    def get_new_connection(self, conn_params: dict[str, Any]) -> Any:
        conn_params["database"] = str(sqlite_path(conn_params["database"]))
        return super().get_new_connection(conn_params)
