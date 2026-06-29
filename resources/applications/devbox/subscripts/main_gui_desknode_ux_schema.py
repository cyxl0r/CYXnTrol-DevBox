from __future__ import annotations

import sqlite3

from subscripts.main_gui_desknode_ux_defaults import (
    DEFAULT_SETTINGS,
    DEFAULT_THEME_NAME,
    TABLE_NAME,
    normalize_settings,
)
from subscripts.main_gui_devbox_log import get_devbox_logger


LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def _column_type(value: str | int) -> str:
    return "INTEGER" if isinstance(value, int) else "TEXT"


def _column_default(value: str | int) -> str:
    if isinstance(value, int):
        return str(value)
    return "'" + value.replace("'", "''") + "'"


def table_exists(connection: sqlite3.Connection) -> bool:
    cursor = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (TABLE_NAME,),
    )
    return cursor.fetchone() is not None


def table_columns(connection: sqlite3.Connection) -> set[str]:
    cursor = connection.execute(
        f"PRAGMA table_info({quote_identifier(TABLE_NAME)})"
    )
    return {str(row[1]) for row in cursor.fetchall()}


def _table_sql(connection: sqlite3.Connection) -> str:
    row = connection.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?",
        (TABLE_NAME,),
    ).fetchone()
    return str(row[0] or "") if row else ""


def create_table_sql(table_name: str) -> str:
    columns = [
        '"record_id" INTEGER PRIMARY KEY AUTOINCREMENT',
        '"theme_name" TEXT NOT NULL COLLATE NOCASE UNIQUE',
    ]
    for name, default in DEFAULT_SETTINGS.items():
        columns.append(
            f"{quote_identifier(name)} {_column_type(default)} "
            f"NOT NULL DEFAULT {_column_default(default)}"
        )
    columns.extend(
        [
            '"created_at" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP',
            '"updated_at" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP',
        ]
    )
    return (
        f"CREATE TABLE {quote_identifier(table_name)} "
        f"({', '.join(columns)})"
    )


def _insert_theme(
    connection: sqlite3.Connection,
    table_name: str,
    theme_name: str,
    settings: dict[str, object],
) -> None:
    normalized = normalize_settings(settings)
    names = list(DEFAULT_SETTINGS)
    columns = ", ".join(
        [quote_identifier("theme_name")]
        + [quote_identifier(name) for name in names]
    )
    placeholders = ", ".join("?" for _ in range(len(names) + 1))
    connection.execute(
        f"INSERT INTO {quote_identifier(table_name)} "
        f"({columns}) VALUES ({placeholders})",
        [theme_name, *(normalized[name] for name in names)],
    )


def legacy_table_needs_migration(connection: sqlite3.Connection) -> bool:
    columns = table_columns(connection)
    compact_sql = "".join(_table_sql(connection).split()).lower()
    return (
        "theme_name" not in columns
        or 'check("record_id"=1)' in compact_sql
    )


def migrate_legacy_single_theme_table(
    connection: sqlite3.Connection,
) -> None:
    legacy_columns = table_columns(connection)
    setting_names = [
        name
        for name in DEFAULT_SETTINGS
        if name in legacy_columns
    ]
    legacy_settings: dict[str, object] = dict(DEFAULT_SETTINGS)

    if setting_names:
        columns = ", ".join(
            quote_identifier(name)
            for name in setting_names
        )
        row = connection.execute(
            f"SELECT {columns} FROM {quote_identifier(TABLE_NAME)} "
            "ORDER BY record_id ASC LIMIT 1"
        ).fetchone()
        if row is not None:
            legacy_settings.update(dict(zip(setting_names, row)))

    temporary_table = f"{TABLE_NAME}__migration"
    connection.execute(
        f"DROP TABLE IF EXISTS {quote_identifier(temporary_table)}"
    )
    connection.execute(create_table_sql(temporary_table))
    _insert_theme(
        connection,
        temporary_table,
        DEFAULT_THEME_NAME,
        legacy_settings,
    )
    connection.execute(f"DROP TABLE {quote_identifier(TABLE_NAME)}")
    connection.execute(
        f"ALTER TABLE {quote_identifier(temporary_table)} "
        f"RENAME TO {quote_identifier(TABLE_NAME)}"
    )
    LOGGER.info("Legacy deskNode UX table migrated to named themes.")


def add_missing_setting_columns(connection: sqlite3.Connection) -> None:
    available = table_columns(connection)
    for name, default in DEFAULT_SETTINGS.items():
        if name not in available:
            connection.execute(
                f"ALTER TABLE {quote_identifier(TABLE_NAME)} "
                f"ADD COLUMN {quote_identifier(name)} {_column_type(default)} "
                f"NOT NULL DEFAULT {_column_default(default)}"
            )


def ensure_ux_table(connection: sqlite3.Connection) -> None:
    if not table_exists(connection):
        connection.execute(create_table_sql(TABLE_NAME))
    elif legacy_table_needs_migration(connection):
        migrate_legacy_single_theme_table(connection)

    add_missing_setting_columns(connection)
    row = connection.execute(
        f"SELECT 1 FROM {quote_identifier(TABLE_NAME)} LIMIT 1"
    ).fetchone()
    if row is None:
        _insert_theme(
            connection,
            TABLE_NAME,
            DEFAULT_THEME_NAME,
            DEFAULT_SETTINGS,
        )
    connection.commit()
