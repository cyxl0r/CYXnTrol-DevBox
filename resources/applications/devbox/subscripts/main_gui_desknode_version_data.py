from __future__ import annotations

import sqlite3
from pathlib import Path

from subscripts.main_gui_devbox_log import get_devbox_logger


LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")

PRODUCT_NAME = "deskNode"
PRODUCT_TABLE_NAME = "product_credentials"
VERSION_COLUMN_NAME = "release_version"


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def devbox_database_file(studio) -> Path:
    return (
        Path(studio.project_root_path)
        / "resources"
        / "organization"
        / "devbox_db.r0b"
    )


def table_columns(
    connection: sqlite3.Connection,
    table_name: str,
) -> set[str]:
    cursor = connection.execute(
        f"PRAGMA table_info({quote_identifier(table_name)})"
    )
    return {str(row[1]) for row in cursor.fetchall()}


def verify_product_table(
    connection: sqlite3.Connection,
) -> None:
    cursor = connection.execute(
        """
        SELECT 1
        FROM sqlite_master
        WHERE type = 'table'
          AND name = ?
        """,
        (PRODUCT_TABLE_NAME,),
    )

    if cursor.fetchone() is None:
        raise RuntimeError(
            f"Tabelle nicht gefunden: {PRODUCT_TABLE_NAME}"
        )

    required_columns = {
        "product_name",
        VERSION_COLUMN_NAME,
    }
    available_columns = table_columns(
        connection,
        PRODUCT_TABLE_NAME,
    )
    missing_columns = sorted(
        required_columns.difference(available_columns)
    )

    if missing_columns:
        raise RuntimeError(
            "Fehlende Spalten in product_credentials: "
            + ", ".join(missing_columns)
        )


def read_desknode_version(studio) -> str:
    database_file = devbox_database_file(studio)

    if not database_file.is_file():
        raise RuntimeError(
            "DevBox-Datenbank nicht gefunden: "
            f"{database_file}"
        )

    connection = sqlite3.connect(database_file)

    try:
        verify_product_table(connection)
        cursor = connection.execute(
            f"""
            SELECT {quote_identifier(VERSION_COLUMN_NAME)}
            FROM {quote_identifier(PRODUCT_TABLE_NAME)}
            WHERE lower(trim({quote_identifier('product_name')}))
                  = lower(trim(?))
            LIMIT 1
            """,
            (PRODUCT_NAME,),
        )
        row = cursor.fetchone()

        if row is None:
            raise RuntimeError(
                "deskNode-Datensatz nicht gefunden in "
                "product_credentials."
            )

        return str(row[0] or "").strip()

    finally:
        connection.close()


def save_desknode_version(
    studio,
    version_text: str,
) -> None:
    database_file = devbox_database_file(studio)

    if not database_file.is_file():
        raise RuntimeError(
            "DevBox-Datenbank nicht gefunden: "
            f"{database_file}"
        )

    connection = sqlite3.connect(database_file)

    try:
        verify_product_table(connection)
        cursor = connection.execute(
            f"""
            UPDATE {quote_identifier(PRODUCT_TABLE_NAME)}
            SET {quote_identifier(VERSION_COLUMN_NAME)} = ?
            WHERE lower(trim({quote_identifier('product_name')}))
                  = lower(trim(?))
            """,
            (
                version_text,
                PRODUCT_NAME,
            ),
        )

        if cursor.rowcount != 1:
            connection.rollback()
            raise RuntimeError(
                "deskNode-Datensatz konnte nicht eindeutig "
                "aktualisiert werden."
            )

        connection.commit()

    finally:
        connection.close()
