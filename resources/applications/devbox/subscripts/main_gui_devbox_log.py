from __future__ import annotations

import os
import re
import sqlite3
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any


LOGFILE_ENV_NAME = "_CYXLABS_DEVBOX_LOGFILE_PATH"
APPDATA_FOLDER_PARTS = ("CYXLabs", "CYXnTrol", "DevBox")
REGISTRY_TABLE_NAME = "script_log_registry"


def _quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def _timestamp() -> str:
    return datetime.now().astimezone().isoformat(timespec="milliseconds")


def _resolve_appdata_directory() -> Path:
    appdata_value = os.environ.get("APPDATA", "").strip()

    if appdata_value:
        return Path(appdata_value).expanduser()

    local_appdata_value = os.environ.get("LOCALAPPDATA", "").strip()

    if local_appdata_value:
        return Path(local_appdata_value).expanduser()

    return Path.home() / "AppData" / "Roaming"


def get_logfile_path() -> Path:
    configured_path = os.environ.get(LOGFILE_ENV_NAME, "").strip()

    if configured_path:
        return Path(configured_path).expanduser()

    return _resolve_appdata_directory().joinpath(
        *APPDATA_FOLDER_PARTS,
        "logfile.r0b",
    )


def _normalize_script_key(script_file: str | Path) -> str:
    source_path = Path(script_file)
    source_name = source_path.stem or source_path.name or "unknown_script"
    normalized_value = re.sub(r"[^a-z0-9_]+", "_", source_name.lower())
    normalized_value = normalized_value.strip("_")

    if not normalized_value:
        return "unknown_script"

    return normalized_value


def _table_name_for_script(script_key: str) -> str:
    return f"log_{script_key}"


def _open_connection(logfile_path: Path) -> sqlite3.Connection:
    logfile_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(logfile_path, timeout=5.0)
    connection.execute("PRAGMA busy_timeout = 5000")
    connection.execute("PRAGMA journal_mode = WAL")
    connection.execute("PRAGMA synchronous = NORMAL")
    return connection


def _ensure_log_schema(
    connection: sqlite3.Connection,
    script_key: str,
    script_name: str,
) -> str:
    table_name = _table_name_for_script(script_key)
    registry_table = _quote_identifier(REGISTRY_TABLE_NAME)
    log_table = _quote_identifier(table_name)
    current_timestamp = _timestamp()

    connection.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {registry_table} (
            script_key TEXT PRIMARY KEY,
            script_name TEXT NOT NULL,
            table_name TEXT NOT NULL UNIQUE,
            first_seen TEXT NOT NULL,
            last_seen TEXT NOT NULL
        )
        """
    )

    connection.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {log_table} (
            entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            level TEXT NOT NULL,
            message TEXT NOT NULL,
            details TEXT NOT NULL DEFAULT ''
        )
        """
    )

    connection.execute(
        f"""
        INSERT INTO {registry_table} (
            script_key,
            script_name,
            table_name,
            first_seen,
            last_seen
        )
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(script_key) DO UPDATE SET
            script_name = excluded.script_name,
            table_name = excluded.table_name,
            last_seen = excluded.last_seen
        """,
        (
            script_key,
            script_name,
            table_name,
            current_timestamp,
            current_timestamp,
        ),
    )

    return table_name


def write_log_entry(
    script_file: str | Path,
    level: str,
    message: object,
    details: object = "",
) -> None:
    script_path = Path(script_file)
    script_key = _normalize_script_key(script_path)
    script_name = script_path.name or f"{script_key}.py"
    logfile_path = get_logfile_path()
    normalized_level = str(level or "INFO").strip().upper() or "INFO"
    normalized_message = str(message or "")
    normalized_details = str(details or "")

    for retry_index in range(5):
        connection: sqlite3.Connection | None = None

        try:
            connection = _open_connection(logfile_path)
            table_name = _ensure_log_schema(
                connection,
                script_key,
                script_name,
            )
            connection.execute(
                f"""
                INSERT INTO {_quote_identifier(table_name)} (
                    timestamp,
                    level,
                    message,
                    details
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    _timestamp(),
                    normalized_level,
                    normalized_message,
                    normalized_details,
                ),
            )
            connection.commit()
            return
        except sqlite3.OperationalError as error:
            if "locked" not in str(error).lower() or retry_index == 4:
                return
            time.sleep(0.1 * (retry_index + 1))
        except Exception:
            return
        finally:
            if connection is not None:
                try:
                    connection.close()
                except Exception:
                    pass


class DevBoxLogger:
    def __init__(self, script_file: str | Path) -> None:
        self.script_file = Path(script_file)

    def log(
        self,
        level: str,
        message: object,
        details: object = "",
    ) -> None:
        write_log_entry(
            self.script_file,
            level,
            message,
            details,
        )

    def info(self, message: object, details: object = "") -> None:
        self.log("INFO", message, details)

    def warning(self, message: object, details: object = "") -> None:
        self.log("WARNING", message, details)

    def error(self, message: object, details: object = "") -> None:
        self.log("ERROR", message, details)

    def exception(self, message: object, error: BaseException | None = None) -> None:
        if error is None:
            details = traceback.format_exc()
        else:
            details = "".join(
                traceback.format_exception(
                    type(error),
                    error,
                    error.__traceback__,
                )
            )

        self.error(message, details)


def get_devbox_logger(script_file: str | Path) -> DevBoxLogger:
    return DevBoxLogger(script_file)


get_devbox_logger(__file__).info("Module loaded.")
