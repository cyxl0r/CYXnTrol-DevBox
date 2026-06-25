from __future__ import annotations

from subscripts.main_gui_devbox_log import get_devbox_logger
LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")


import sqlite3
from pathlib import Path

from subscripts.main_gui_product_store import TABLE_NAME as PRODUCT_TABLE_NAME
from subscripts.main_gui_product_store import database_file, quote_identifier


def open_connection(db_file: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(db_file)
    connection.row_factory = sqlite3.Row
    return connection


def table_exists(connection: sqlite3.Connection, table_name: str) -> bool:
    cursor = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name = ?
        """,
        (table_name,),
    )
    return cursor.fetchone() is not None


def document_table_name(product_name: str, language: str) -> str:
    normalized_name = str(product_name).strip().lower().replace(" ", "_")
    return f"{normalized_name}_document_credentials_{language}"


def resolve_document_table(
    connection: sqlite3.Connection,
    product_name: str,
    language: str,
) -> str | None:
    expected_name = document_table_name(product_name, language)
    cursor = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND lower(name) = lower(?)
        LIMIT 1
        """,
        (expected_name,),
    )
    row = cursor.fetchone()
    return None if row is None else str(row["name"])


def read_columns(connection: sqlite3.Connection, table_name: str) -> list[str]:
    cursor = connection.execute(
        f"PRAGMA table_info({quote_identifier(table_name)})"
    )
    return [str(row[1]) for row in cursor.fetchall()]


def read_document_row(
    connection: sqlite3.Connection,
    table_name: str,
) -> tuple[int | None, dict[str, object]]:
    cursor = connection.execute(
        f"SELECT rowid, * FROM {quote_identifier(table_name)} ORDER BY rowid ASC LIMIT 1"
    )
    row = cursor.fetchone()
    if row is None:
        return None, {}
    return int(row["rowid"]), dict(row)


def product_label(row: sqlite3.Row) -> str:
    for column in (
        "product_display_name",
        "product_name",
        "product_short_name",
        "product_slug",
    ):
        if column in row.keys() and row[column]:
            return str(row[column])
    return f"Datensatz {row['rowid']}"


def list_products(connection: sqlite3.Connection) -> list[dict[str, object]]:
    if not table_exists(connection, PRODUCT_TABLE_NAME):
        return []
    cursor = connection.execute(
        f"SELECT rowid, * FROM {quote_identifier(PRODUCT_TABLE_NAME)} ORDER BY rowid ASC"
    )
    result = []
    for row in cursor.fetchall():
        product_name = str(row["product_name"] or "").strip()
        if product_name:
            result.append(
                {
                    "rowid": int(row["rowid"]),
                    "product_name": product_name,
                    "label": product_label(row),
                }
            )
    return result


def insert_or_update_row(
    connection: sqlite3.Connection,
    table_name: str,
    rowid: int | None,
    values: dict[str, object],
) -> int:
    if rowid is None:
        columns = list(values.keys())
        if not columns:
            cursor = connection.execute(
                f"INSERT INTO {quote_identifier(table_name)} DEFAULT VALUES"
            )
        else:
            column_sql = ", ".join(quote_identifier(column) for column in columns)
            placeholders = ", ".join("?" for _ in columns)
            cursor = connection.execute(
                f"INSERT INTO {quote_identifier(table_name)} ({column_sql}) VALUES ({placeholders})",
                [values[column] for column in columns],
            )
        return int(cursor.lastrowid)
    if not values:
        return rowid
    assignments = ", ".join(
        f"{quote_identifier(column)} = ?" for column in values
    )
    parameters = [values[column] for column in values]
    parameters.append(rowid)
    connection.execute(
        f"UPDATE {quote_identifier(table_name)} SET {assignments} WHERE rowid = ?",
        parameters,
    )
    return rowid


def value_to_text(value: object) -> str:
    return "" if value is None else str(value)
