from __future__ import annotations

from subscripts.main_gui_devbox_log import get_devbox_logger
LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")


import sqlite3
import subprocess
import sys
import time
from pathlib import Path

from subscripts.main_gui_metadata_defaults import (
    MANUFACTURER_TABLE_NAME,
    PRODUCT_TABLE_NAME,
    manufacturer_create_values,
    quote_identifier,
    real_manufacturer_row,
    sync_project_family,
    table_exists,
    utc_timestamp,
)
from subscripts.main_gui_metadata_common import utc_year
from subscripts.main_gui_roof_store import database_file, insert_row, open_connection


MANUFACTURER_SETUP_COLUMNS = {
    "product_family": "TEXT",
    "founded_year": "INTEGER",
    "organization_type": "TEXT",
    "owner_name": "TEXT",
}


class FirstStartPreparationError(RuntimeError):
    pass


def current_year() -> int:
    return int(time.strftime("%Y", time.localtime()))


def python_executable() -> Path:
    executable = Path(sys.executable)
    if executable.name.lower() == "pythonw.exe":
        python_exe = executable.with_name("python.exe")
        if python_exe.is_file():
            return python_exe
    return executable


def setup_required(project_root_path: Path) -> bool:
    project_root_path = Path(project_root_path).resolve()
    db_file = database_file(project_root_path)
    if not db_file.is_file():
        initialize_database(project_root_path)

    connection = open_connection(db_file)
    try:
        if not table_exists(connection, MANUFACTURER_TABLE_NAME):
            raise FirstStartPreparationError(
                f"Die Tabelle {MANUFACTURER_TABLE_NAME} konnte nicht erstellt werden."
            )
        ensure_setup_columns(connection)
        sync_project_family(connection, project_root_path)
        connection.commit()
        return real_manufacturer_row(connection) is None
    finally:
        connection.close()


def initialize_database(project_root_path: Path) -> None:
    script_file = (
        Path(project_root_path)
        / "resources"
        / "applications"
        / "devbox"
        / "functions"
        / "create_devdbase.py"
    )
    if not script_file.is_file():
        raise FirstStartPreparationError(
            "Die DevBox-Datenbank fehlt und create_devdbase.py wurde nicht gefunden: "
            f"{script_file}"
        )

    completed = subprocess.run(
        [str(python_executable()), str(script_file)],
        cwd=str(script_file.parent),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    db_file = database_file(project_root_path)
    if completed.returncode == 0 and db_file.is_file():
        return

    output = "\n".join(
        part.strip()
        for part in (completed.stdout, completed.stderr)
        if part and part.strip()
    )
    details = output or f"Rückgabecode: {completed.returncode}"
    raise FirstStartPreparationError(
        "Die DevBox-Datenbank konnte nicht initialisiert werden.\n\n"
        f"{details}"
    )


def ensure_setup_columns(connection: sqlite3.Connection) -> None:
    existing_columns = {
        str(row[1]).lower()
        for row in connection.execute(
            f"PRAGMA table_info({quote_identifier(MANUFACTURER_TABLE_NAME)})"
        ).fetchall()
    }
    for column_name, column_type in MANUFACTURER_SETUP_COLUMNS.items():
        if column_name.lower() not in existing_columns:
            connection.execute(
                f"ALTER TABLE {quote_identifier(MANUFACTURER_TABLE_NAME)} "
                f"ADD COLUMN {quote_identifier(column_name)} {column_type}"
            )


def table_column_map(connection: sqlite3.Connection, table_name: str) -> dict[str, str]:
    return {
        str(row[1]).lower(): str(row[1])
        for row in connection.execute(
            f"PRAGMA table_info({quote_identifier(table_name)})"
        ).fetchall()
    }


def update_devbox_product(
    connection: sqlite3.Connection,
    selected_values: dict[str, object],
) -> None:
    if not table_exists(connection, PRODUCT_TABLE_NAME):
        raise FirstStartPreparationError(
            f"Die Tabelle {PRODUCT_TABLE_NAME} konnte nicht erstellt werden."
        )

    columns = table_column_map(connection, PRODUCT_TABLE_NAME)
    product_name_column = columns.get("product_name")
    if product_name_column is None:
        raise FirstStartPreparationError(
            f"Die Tabelle {PRODUCT_TABLE_NAME} enthält keine Produktnamen."
        )

    row = connection.execute(
        f"""
        SELECT rowid
        FROM {quote_identifier(PRODUCT_TABLE_NAME)}
        WHERE LOWER({quote_identifier(product_name_column)}) = ?
        ORDER BY rowid ASC
        LIMIT 1
        """,
        ("devbox",),
    ).fetchone()
    if row is None:
        raise FirstStartPreparationError(
            "Der DevBox-Produktdatensatz konnte in der neuen Datenbank nicht gefunden werden."
        )

    updates = {
        columns[key]: value
        for key, value in selected_values.items()
        if key in columns
    }
    if "copyright_year" in columns:
        updates[columns["copyright_year"]] = int(utc_year())
    if "updated_at" in columns:
        updates[columns["updated_at"]] = utc_timestamp()

    assignments = ", ".join(
        f"{quote_identifier(column)} = ?"
        for column in updates
    )
    connection.execute(
        f"""
        UPDATE {quote_identifier(PRODUCT_TABLE_NAME)}
        SET {assignments}
        WHERE rowid = ?
        """,
        [updates[column] for column in updates] + [int(row[0])],
    )


def persist_first_start_values(
    project_root_path: Path,
    selected_values: dict[str, object],
    devbox_values: dict[str, object],
) -> int:
    project_root_path = Path(project_root_path).resolve()
    connection = open_connection(database_file(project_root_path))
    try:
        ensure_setup_columns(connection)
        if real_manufacturer_row(connection) is not None:
            raise RuntimeError("Ein echter Manufakturdatensatz ist bereits vorhanden.")

        columns = table_column_map(connection, MANUFACTURER_TABLE_NAME)
        mapped_values = {
            columns[key]: value
            for key, value in selected_values.items()
            if key in columns
        }
        values = manufacturer_create_values(connection, mapped_values, project_root_path)
        rowid = insert_row(connection, values)
        update_devbox_product(connection, devbox_values)
        sync_project_family(connection, project_root_path)
        connection.commit()
        return rowid
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
