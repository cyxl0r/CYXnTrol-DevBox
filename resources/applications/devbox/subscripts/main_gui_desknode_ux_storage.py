from __future__ import annotations

import sqlite3
from pathlib import Path

from subscripts.main_gui_desknode_ux_defaults import (
    DEFAULT_SETTINGS,
    DEFAULT_THEME_NAME,
    TABLE_NAME,
    normalize_settings,
    normalize_theme_name,
)
from subscripts.main_gui_desknode_ux_schema import (
    ensure_ux_table,
    quote_identifier,
)
from subscripts.main_gui_devbox_log import get_devbox_logger


LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")


def devbox_database_file(studio) -> Path:
    return (
        Path(studio.project_root_path)
        / "resources"
        / "organization"
        / "devbox_db.r0b"
    )


def _open_database(studio) -> sqlite3.Connection:
    database_file = devbox_database_file(studio)
    if not database_file.is_file():
        raise RuntimeError(f"DevBox-Datenbank nicht gefunden: {database_file}")
    return sqlite3.connect(database_file)


def _theme_names(connection: sqlite3.Connection) -> list[str]:
    cursor = connection.execute(
        f"SELECT {quote_identifier('theme_name')} "
        f"FROM {quote_identifier(TABLE_NAME)} "
        f"ORDER BY {quote_identifier('theme_name')} COLLATE NOCASE"
    )
    return [str(row[0]) for row in cursor.fetchall()]


def _resolve_theme_name(
    connection: sqlite3.Connection,
    theme_name: str | None,
) -> str:
    names = _theme_names(connection)
    if not names:
        raise RuntimeError("Kein deskNode-UX-Theme vorhanden.")
    if theme_name:
        normalized = normalize_theme_name(theme_name)
        for name in names:
            if name.casefold() == normalized.casefold():
                return name
        raise RuntimeError(f"UX-Theme nicht gefunden: {normalized}")
    for name in names:
        if name.casefold() == DEFAULT_THEME_NAME.casefold():
            return name
    return names[0]


def _insert_theme(
    connection: sqlite3.Connection,
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
        f"INSERT INTO {quote_identifier(TABLE_NAME)} "
        f"({columns}) VALUES ({placeholders})",
        [theme_name, *(normalized[name] for name in names)],
    )


def list_ux_theme_names(studio) -> list[str]:
    connection = _open_database(studio)
    try:
        ensure_ux_table(connection)
        return _theme_names(connection)
    finally:
        connection.close()


def load_ux_settings(
    studio,
    theme_name: str | None = None,
) -> dict[str, str | int]:
    connection = _open_database(studio)
    try:
        ensure_ux_table(connection)
        resolved_name = _resolve_theme_name(connection, theme_name)
        names = list(DEFAULT_SETTINGS)
        columns = ", ".join(quote_identifier(name) for name in names)
        row = connection.execute(
            f"SELECT {columns} FROM {quote_identifier(TABLE_NAME)} "
            f"WHERE {quote_identifier('theme_name')} = ?",
            (resolved_name,),
        ).fetchone()
        if row is None:
            raise RuntimeError("deskNode-Gestaltungsprofil konnte nicht geladen werden.")
        return normalize_settings(dict(zip(names, row)))
    finally:
        connection.close()


def save_ux_settings(
    studio,
    values: dict[str, object],
    theme_name: str | None = None,
) -> dict[str, str | int]:
    normalized = normalize_settings(values)
    connection = _open_database(studio)
    try:
        ensure_ux_table(connection)
        resolved_name = _resolve_theme_name(connection, theme_name)
        assignments = ", ".join(
            f"{quote_identifier(name)} = ?"
            for name in normalized
        )
        cursor = connection.execute(
            f"UPDATE {quote_identifier(TABLE_NAME)} "
            f"SET {assignments}, {quote_identifier('updated_at')} = CURRENT_TIMESTAMP "
            f"WHERE {quote_identifier('theme_name')} = ?",
            [*normalized.values(), resolved_name],
        )
        if cursor.rowcount != 1:
            connection.rollback()
            raise RuntimeError("deskNode-Gestaltungsprofil konnte nicht gespeichert werden.")
        connection.commit()
    finally:
        connection.close()
    return normalized


def create_ux_theme(
    studio,
    theme_name: str,
    base_values: dict[str, object] | None = None,
) -> str:
    normalized_name = normalize_theme_name(theme_name)
    connection = _open_database(studio)
    try:
        ensure_ux_table(connection)
        _insert_theme(
            connection,
            normalized_name,
            base_values or DEFAULT_SETTINGS,
        )
        connection.commit()
    except sqlite3.IntegrityError as error:
        connection.rollback()
        raise ValueError(
            f"Ein UX-Theme namens „{normalized_name}“ existiert bereits."
        ) from error
    finally:
        connection.close()
    return normalized_name


def rename_ux_theme(
    studio,
    current_name: str,
    new_name: str,
) -> str:
    normalized_name = normalize_theme_name(new_name)
    connection = _open_database(studio)
    try:
        ensure_ux_table(connection)
        current_name = _resolve_theme_name(connection, current_name)
        cursor = connection.execute(
            f"UPDATE {quote_identifier(TABLE_NAME)} "
            f"SET {quote_identifier('theme_name')} = ?, "
            f"{quote_identifier('updated_at')} = CURRENT_TIMESTAMP "
            f"WHERE {quote_identifier('theme_name')} = ?",
            (normalized_name, current_name),
        )
        if cursor.rowcount != 1:
            connection.rollback()
            raise RuntimeError("UX-Theme konnte nicht umbenannt werden.")
        connection.commit()
    except sqlite3.IntegrityError as error:
        connection.rollback()
        raise ValueError(
            f"Ein UX-Theme namens „{normalized_name}“ existiert bereits."
        ) from error
    finally:
        connection.close()
    return normalized_name


def delete_ux_theme(studio, theme_name: str) -> str:
    connection = _open_database(studio)
    try:
        ensure_ux_table(connection)
        resolved_name = _resolve_theme_name(connection, theme_name)
        names = _theme_names(connection)
        if len(names) <= 1:
            raise RuntimeError("Das letzte vorhandene UX-Theme kann nicht gelöscht werden.")
        connection.execute(
            f"DELETE FROM {quote_identifier(TABLE_NAME)} "
            f"WHERE {quote_identifier('theme_name')} = ?",
            (resolved_name,),
        )
        connection.commit()
        return _resolve_theme_name(connection, None)
    finally:
        connection.close()
