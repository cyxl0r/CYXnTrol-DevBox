from __future__ import annotations

from subscripts.main_gui_devbox_log import get_devbox_logger
LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")


import sqlite3
import time
from pathlib import Path


TABLE_NAME = "manufacturer_credentials"
INTERNAL_NAME = "__devbox_internal_key__"
EXCLUDED_COLUMNS = {
    "devbox_key_id",
    "devbox_key_payload",
    "devbox_key_created_at",
    "devbox_key_algorithm",
}
BASIC_COLUMNS = {
    "manufacturer_id", "manufacturer_name", "manufacturer_display_name",
    "product_family", "founded_year", "organization_type", "owner_name",
    "manufacturer_legal_name", "manufacturer_brand_name", "author_name",
    "author_display_name", "publisher_name", "vendor_name",
    "developer_name", "organization_name", "country", "country_code",
    "region", "city", "website_url", "support_url",
    "privacy_policy_url", "terms_url", "contact_email", "support_email",
    "created_at", "updated_at", "active", "notes",
}
PREFIX_LABELS = [
    ("apple_", "Apple"),
    ("google_", "Google / Android"),
    ("microsoft_", "Microsoft"),
    ("github_", "GitHub"),
    ("docker", "Docker / Container"),
    ("container_", "Docker / Container"),
    ("qnap_", "QNAP"),
    ("synology_", "Synology"),
    ("debian_", "Debian"),
    ("rpm_", "RPM"),
    ("code_signing_", "Code Signing"),
    ("windows_", "Windows"),
    ("macos_", "macOS"),
    ("ios_", "iOS"),
    ("android_", "Android"),
    ("ssh_", "SSH"),
]


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def utc_timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def label_from_column(column_name: str) -> str:
    return column_name.replace("_", " ").strip().title()


def group_for_column(column_name: str) -> str:
    if column_name in BASIC_COLUMNS:
        return "Basisdaten"

    for prefix, label in PREFIX_LABELS:
        if column_name.startswith(prefix):
            return label

    return "Weitere Daten"


def group_order() -> list[str]:
    result = ["Basisdaten"]

    for _, label in PREFIX_LABELS:
        if label not in result:
            result.append(label)

    result.append("Weitere Daten")
    return result


def database_file(project_root_path: Path) -> Path:
    return Path(project_root_path) / "resources" / "organization" / "devbox_db.r0b"


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


def read_columns(connection: sqlite3.Connection) -> list[tuple[str, str]]:
    cursor = connection.execute(f"PRAGMA table_info({quote_identifier(TABLE_NAME)})")
    return [(str(row[1]), str(row[2]).upper()) for row in cursor.fetchall()]


def find_data_row(connection: sqlite3.Connection, columns: dict[str, str]) -> int | None:
    checks = []
    params = []

    if "manufacturer_name" in columns:
        checks.append(f"({quote_identifier('manufacturer_name')} IS NULL OR {quote_identifier('manufacturer_name')} != ?)")
        params.append(INTERNAL_NAME)

    if "manufacturer_id" in columns:
        checks.append(f"({quote_identifier('manufacturer_id')} IS NULL OR {quote_identifier('manufacturer_id')} != ?)")
        params.append(0)

    where_sql = " AND ".join(checks) if checks else "1=1"
    cursor = connection.execute(
        f"""
        SELECT rowid
        FROM {quote_identifier(TABLE_NAME)}
        WHERE {where_sql}
        ORDER BY rowid ASC
        LIMIT 1
        """,
        params,
    )
    row = cursor.fetchone()
    return None if row is None else int(row[0])


def read_row_values(connection: sqlite3.Connection, rowid: int | None) -> dict[str, object]:
    if rowid is None:
        return {}

    cursor = connection.execute(
        f"SELECT * FROM {quote_identifier(TABLE_NAME)} WHERE rowid = ?",
        (rowid,),
    )
    row = cursor.fetchone()
    return {} if row is None else dict(row)


def value_to_text(value: object) -> str:
    if value is None:
        return ""

    if isinstance(value, bytes):
        return "BLOB/sensibles Feld - später"

    return str(value)


def next_manufacturer_id(connection: sqlite3.Connection) -> int:
    cursor = connection.execute(
        f"""
        SELECT MAX(CAST({quote_identifier('manufacturer_id')} AS INTEGER))
        FROM {quote_identifier(TABLE_NAME)}
        WHERE {quote_identifier('manufacturer_id')} IS NOT NULL
        """
    )
    row = cursor.fetchone()
    current_value = row[0] if row is not None else 0
    return 1 if current_value is None else max(1, int(current_value) + 1)


def insert_row(connection: sqlite3.Connection, values: dict[str, object]) -> int:
    columns = list(values.keys())
    column_sql = ", ".join(quote_identifier(column) for column in columns)
    placeholders = ", ".join("?" for _ in columns)
    cursor = connection.execute(
        f"""
        INSERT INTO {quote_identifier(TABLE_NAME)}
        ({column_sql})
        VALUES ({placeholders})
        """,
        [values[column] for column in columns],
    )
    return int(cursor.lastrowid)


def update_row(connection: sqlite3.Connection, rowid: int, values: dict[str, object]) -> None:
    if not values:
        return

    assignments = ", ".join(
        f"{quote_identifier(column)} = ?"
        for column in values
    )
    parameters = [values[column] for column in values]
    parameters.append(rowid)
    connection.execute(
        f"""
        UPDATE {quote_identifier(TABLE_NAME)}
        SET {assignments}
        WHERE rowid = ?
        """,
        parameters,
    )
