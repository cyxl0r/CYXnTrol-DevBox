from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re
import sqlite3


CATEGORY_TABLE = "desknode_consumer_device_categories"
DEVICE_TABLE = "desknode_consumer_devices"


def database_path(studio) -> Path:
    return (
        Path(studio.project_root_path)
        / "resources"
        / "organization"
        / "devbox_db.r0b"
    )


def graphics_path(studio) -> Path:
    return Path(studio.project_root_path) / "resources" / "graphics"


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def current_timestamp() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def normalize_key(value: str, separator: str) -> str:
    normalized = value.strip().casefold()
    normalized = normalized.replace("ä", "ae")
    normalized = normalized.replace("ö", "oe")
    normalized = normalized.replace("ü", "ue")
    normalized = normalized.replace("ß", "ss")
    normalized = re.sub(r"[^a-z0-9]+", separator, normalized)
    return normalized.strip(separator)


def normalized_category_key(value: str) -> str:
    return normalize_key(value, "_")


def normalized_device_key(value: str) -> str:
    return normalize_key(value, "-")


def category_translation_key(category_key: str) -> str:
    return f"graphic_category.{category_key}"


def device_translation_key(device_key: str) -> str:
    return f"graphic_item.{device_key.replace('-', '_')}"


def connect(studio) -> sqlite3.Connection:
    path = database_path(studio)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def ensure_symbol_tables(studio) -> None:
    connection = connect(studio)

    try:
        connection.executescript(
            f"""
            CREATE TABLE IF NOT EXISTS {quote_identifier(CATEGORY_TABLE)} (
                record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_key TEXT NOT NULL COLLATE NOCASE UNIQUE,
                translation_key TEXT NOT NULL COLLATE NOCASE UNIQUE,
                sort_order INTEGER NOT NULL DEFAULT 100,
                is_active INTEGER NOT NULL DEFAULT 1
                    CHECK (is_active IN (0, 1)),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS {quote_identifier(DEVICE_TABLE)} (
                record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_key TEXT NOT NULL COLLATE NOCASE UNIQUE,
                category_id INTEGER NOT NULL,
                translation_key TEXT NOT NULL COLLATE NOCASE UNIQUE,
                source_filename TEXT NOT NULL COLLATE NOCASE UNIQUE,
                sort_order INTEGER NOT NULL DEFAULT 100,
                is_active INTEGER NOT NULL DEFAULT 1
                    CHECK (is_active IN (0, 1)),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (category_id)
                    REFERENCES {quote_identifier(CATEGORY_TABLE)} (record_id)
                    ON UPDATE RESTRICT
                    ON DELETE RESTRICT
            );
            """
        )
        connection.commit()
    finally:
        connection.close()


def next_sort_order(
    connection: sqlite3.Connection,
    table_name: str,
) -> int:
    row = connection.execute(
        f"SELECT MAX(sort_order) FROM {quote_identifier(table_name)}"
    ).fetchone()
    current_value = int(row[0] or 0)
    return current_value + 10


def list_categories(studio) -> list[sqlite3.Row]:
    ensure_symbol_tables(studio)
    connection = connect(studio)

    try:
        return connection.execute(
            f"""
            SELECT *
            FROM {quote_identifier(CATEGORY_TABLE)}
            ORDER BY sort_order ASC, category_key COLLATE NOCASE ASC
            """
        ).fetchall()
    finally:
        connection.close()


def get_category(studio, record_id: int) -> sqlite3.Row:
    connection = connect(studio)

    try:
        row = connection.execute(
            f"""
            SELECT *
            FROM {quote_identifier(CATEGORY_TABLE)}
            WHERE record_id = ?
            """,
            (record_id,),
        ).fetchone()
    finally:
        connection.close()

    if row is None:
        raise ValueError("Die gewählte Gerätekategorie existiert nicht mehr.")

    return row


def create_category(studio, category_name: str) -> int:
    category_key = normalized_category_key(category_name)

    if not category_key:
        raise ValueError("Ein Kategoriename ist erforderlich.")

    translation_key = category_translation_key(category_key)
    timestamp = current_timestamp()
    connection = connect(studio)

    try:
        cursor = connection.execute(
            f"""
            INSERT INTO {quote_identifier(CATEGORY_TABLE)} (
                category_key, translation_key, sort_order, is_active,
                created_at, updated_at
            ) VALUES (?, ?, ?, 1, ?, ?)
            """,
            (
                category_key,
                translation_key,
                next_sort_order(connection, CATEGORY_TABLE),
                timestamp,
                timestamp,
            ),
        )
        connection.commit()
        return int(cursor.lastrowid)
    finally:
        connection.close()


def update_category(
    studio,
    record_id: int,
    category_name: str,
) -> None:
    category_key = normalized_category_key(category_name)

    if not category_key:
        raise ValueError("Ein Kategoriename ist erforderlich.")

    connection = connect(studio)

    try:
        cursor = connection.execute(
            f"""
            UPDATE {quote_identifier(CATEGORY_TABLE)}
            SET
                category_key = ?,
                translation_key = ?,
                updated_at = ?
            WHERE record_id = ?
            """,
            (
                category_key,
                category_translation_key(category_key),
                current_timestamp(),
                record_id,
            ),
        )

        if cursor.rowcount != 1:
            raise ValueError("Die gewählte Gerätekategorie existiert nicht mehr.")

        connection.commit()
    finally:
        connection.close()


def delete_category(studio, record_id: int) -> None:
    connection = connect(studio)

    try:
        device_count = connection.execute(
            f"""
            SELECT COUNT(*) FROM {quote_identifier(DEVICE_TABLE)}
            WHERE category_id = ?
            """,
            (record_id,),
        ).fetchone()[0]

        if int(device_count) > 0:
            raise ValueError(
                "Die Kategorie enthält noch Verbrauchergeräte und "
                "kann deshalb nicht gelöscht werden."
            )

        connection.execute(
            f"DELETE FROM {quote_identifier(CATEGORY_TABLE)} WHERE record_id = ?",
            (record_id,),
        )
        connection.commit()
    finally:
        connection.close()
