from __future__ import annotations

from subscripts.main_gui_devbox_log import get_devbox_logger
LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")


import sqlite3
import subprocess
import sys
import time
from pathlib import Path


TABLE_NAME = "folder_structure_basic"
SOURCE_APP_TEMPLATE = "devbox_manual_app_template"
APP_PLACEHOLDER = "<Softwareprojekt>"
APPLICATIONS_FOLDER_NAME = "applications"
MAX_LEVELS = 12
SORT_ORDER_OFFSET = 100000


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def utc_timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sanitize_folder_name(folder_name: str) -> str:
    value = str(folder_name).strip()
    for forbidden_char in '<>:"/\\|?*':
        value = value.replace(forbidden_char, "")
    value = value.strip()
    return "" if value in {"", ".", ".."} else value


def split_path(relative_path: str) -> list[str]:
    return [
        part
        for part in str(relative_path).replace("\\", "/").split("/")
        if part
    ]


def database_file(project_root_path: Path) -> Path:
    return Path(project_root_path) / "resources" / "organization" / "devbox_db.r0b"



def python_executable() -> Path:
    executable_path = Path(sys.executable)

    if executable_path.name.lower() == "pythonw.exe":
        python_path = executable_path.with_name("python.exe")

        if python_path.is_file():
            return python_path

    return executable_path


def run_empty_project_initializer(project_root_path: Path) -> int:
    script_file = (
        Path(project_root_path)
        / "resources"
        / "applications"
        / "devbox"
        / "functions"
        / "initialize_empty_application_projects.py"
    )

    if not script_file.is_file():
        raise FileNotFoundError(
            f"Project initializer not found: {script_file}"
        )

    process = subprocess.run(
        [str(python_executable()), str(script_file)],
        cwd=str(script_file.parent),
    )

    return int(process.returncode)


def applications_folder_name(project_root_path: Path) -> str:
    for item in Path(project_root_path).iterdir():
        if item.is_dir() and item.name.lower() == APPLICATIONS_FOLDER_NAME:
            return item.name
    return "applications"


def open_connection(db_file: Path) -> sqlite3.Connection:
    db_file.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_file)
    ensure_table(connection)
    connection.commit()
    return connection


def ensure_table(connection: sqlite3.Connection) -> None:
    columns = [
        ("sort_order", "INTEGER"),
        ("source_type", "TEXT"),
        ("folder_role", "TEXT"),
        ("app_folder_name", "TEXT"),
        ("depth", "INTEGER"),
        ("relative_path", "TEXT"),
        ("exists_on_disk", "INTEGER"),
        ("last_scanned_at", "TEXT"),
    ]
    columns += [(f"level_{index}", "TEXT") for index in range(1, MAX_LEVELS + 1)]
    column_sql = ", ".join(
        f"{quote_identifier(name)} {column_type}"
        for name, column_type in columns
    )
    connection.execute(
        f"CREATE TABLE IF NOT EXISTS {quote_identifier(TABLE_NAME)} ({column_sql})"
    )
    existing_columns = {
        str(row[1]).lower()
        for row in connection.execute(
            f"PRAGMA table_info({quote_identifier(TABLE_NAME)})"
        ).fetchall()
    }
    for name, column_type in columns:
        if name.lower() not in existing_columns:
            connection.execute(
                f"ALTER TABLE {quote_identifier(TABLE_NAME)} "
                f"ADD COLUMN {quote_identifier(name)} {column_type}"
            )


def load_template_paths(db_file: Path) -> list[str]:
    if not db_file.is_file():
        return []
    connection = open_connection(db_file)
    try:
        cursor = connection.execute(
            f"""
            SELECT {quote_identifier('relative_path')}
            FROM {quote_identifier(TABLE_NAME)}
            WHERE {quote_identifier('source_type')} = ?
              AND {quote_identifier('relative_path')} IS NOT NULL
            ORDER BY {quote_identifier('sort_order')} ASC,
                     {quote_identifier('relative_path')} ASC
            """,
            (SOURCE_APP_TEMPLATE,),
        )
        return [
            str(row[0]).replace("\\", "/").strip("/")
            for row in cursor.fetchall()
            if row[0]
        ]
    finally:
        connection.close()


def save_template_rows(db_file: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    columns = list(rows[0].keys())
    connection = open_connection(db_file)
    try:
        connection.execute(
            f"DELETE FROM {quote_identifier(TABLE_NAME)} "
            f"WHERE {quote_identifier('source_type')} = ?",
            (SOURCE_APP_TEMPLATE,),
        )
        column_sql = ", ".join(quote_identifier(column) for column in columns)
        placeholder_sql = ", ".join("?" for _ in columns)
        sql = (
            f"INSERT INTO {quote_identifier(TABLE_NAME)} "
            f"({column_sql}) VALUES ({placeholder_sql})"
        )
        connection.executemany(
            sql,
            [tuple(row[column] for column in columns) for row in rows],
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def make_row(
    applications_name: str,
    sort_order: int,
    role: str,
    parts: list[str],
) -> dict[str, object]:
    row = {
        "sort_order": sort_order,
        "source_type": SOURCE_APP_TEMPLATE,
        "folder_role": role,
        "app_folder_name": APP_PLACEHOLDER,
        "depth": len(parts),
        "relative_path": "/".join(parts),
        "exists_on_disk": 0,
        "last_scanned_at": utc_timestamp(),
    }
    for index in range(1, MAX_LEVELS + 1):
        row[f"level_{index}"] = parts[index - 1] if index <= len(parts) else None
    return row
