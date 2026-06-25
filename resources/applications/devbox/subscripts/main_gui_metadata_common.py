from __future__ import annotations

from subscripts.main_gui_devbox_log import get_devbox_logger
LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")


import re
import sqlite3
import time
import unicodedata
from pathlib import Path


INTERNAL_MANUFACTURER_NAME = "__devbox_internal_key__"
MANUFACTURER_TABLE_NAME = "manufacturer_credentials"
PRODUCT_TABLE_NAME = "product_credentials"


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def utc_timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def utc_year() -> str:
    return time.strftime("%Y", time.gmtime())


def table_columns(connection: sqlite3.Connection, table_name: str) -> dict[str, str]:
    cursor = connection.execute(f"PRAGMA table_info({quote_identifier(table_name)})")
    return {str(row[1]).lower(): str(row[1]) for row in cursor.fetchall()}


def table_exists(connection: sqlite3.Connection, table_name: str) -> bool:
    cursor = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    )
    return cursor.fetchone() is not None


def as_text(value: object) -> str:
    return "" if value is None else str(value).strip()


def first_value(*values: object) -> str:
    for value in values:
        text = as_text(value)
        if text:
            return text
    return ""


def slugify(value: object) -> str:
    normalized = unicodedata.normalize("NFKD", as_text(value))
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", ascii_value).strip("_").lower()
    return slug or "product"


def project_family(project_root_path: Path) -> str:
    return Path(project_root_path).resolve().name.strip()


def next_integer_value(connection: sqlite3.Connection, table_name: str, column_name: str) -> int:
    cursor = connection.execute(
        f"""
        SELECT MAX(CAST({quote_identifier(column_name)} AS INTEGER))
        FROM {quote_identifier(table_name)}
        WHERE {quote_identifier(column_name)} IS NOT NULL
        """
    )
    value = cursor.fetchone()[0]
    return 1 if value is None else int(value) + 1


def real_manufacturer_row(connection: sqlite3.Connection) -> tuple[int, dict[str, object]] | None:
    if not table_exists(connection, MANUFACTURER_TABLE_NAME):
        return None

    columns = table_columns(connection, MANUFACTURER_TABLE_NAME)
    checks: list[str] = []
    parameters: list[object] = []
    name_column = columns.get("manufacturer_name")
    id_column = columns.get("manufacturer_id")

    if name_column is not None:
        checks.append(f"({quote_identifier(name_column)} IS NULL OR {quote_identifier(name_column)} != ?)")
        parameters.append(INTERNAL_MANUFACTURER_NAME)
    if id_column is not None:
        checks.append(f"({quote_identifier(id_column)} IS NULL OR {quote_identifier(id_column)} != ?)")
        parameters.append(0)

    where_sql = " AND ".join(checks) if checks else "1=1"
    active_column = columns.get("active")
    order_sql = "rowid ASC"
    if active_column is not None:
        order_sql = f"COALESCE({quote_identifier(active_column)}, 0) DESC, rowid ASC"

    cursor = connection.execute(
        f"""
        SELECT rowid, *
        FROM {quote_identifier(MANUFACTURER_TABLE_NAME)}
        WHERE {where_sql}
        ORDER BY {order_sql}
        LIMIT 1
        """,
        parameters,
    )
    row = cursor.fetchone()
    return None if row is None else (int(row["rowid"]), dict(row))
