from __future__ import annotations

from pathlib import Path
import os
import shutil
import sqlite3
from uuid import uuid4

from subscripts.main_gui_desknode_symbol_storage import (
    CATEGORY_TABLE,
    DEVICE_TABLE,
    connect,
    current_timestamp,
    device_translation_key,
    graphics_path,
    next_sort_order,
    normalized_device_key,
    quote_identifier,
)


def list_devices(studio) -> list[sqlite3.Row]:
    connection = connect(studio)

    try:
        return connection.execute(
            f"""
            SELECT devices.*, categories.category_key AS category_key
            FROM {quote_identifier(DEVICE_TABLE)} AS devices
            INNER JOIN {quote_identifier(CATEGORY_TABLE)} AS categories
                ON categories.record_id = devices.category_id
            ORDER BY devices.sort_order ASC,
                     devices.device_key COLLATE NOCASE ASC
            """
        ).fetchall()
    finally:
        connection.close()


def get_device(studio, record_id: int) -> sqlite3.Row:
    connection = connect(studio)

    try:
        row = connection.execute(
            f"""
            SELECT devices.*, categories.category_key AS category_key
            FROM {quote_identifier(DEVICE_TABLE)} AS devices
            INNER JOIN {quote_identifier(CATEGORY_TABLE)} AS categories
                ON categories.record_id = devices.category_id
            WHERE devices.record_id = ?
            """,
            (record_id,),
        ).fetchone()
    finally:
        connection.close()

    if row is None:
        raise ValueError("Das gewählte Verbrauchergerät existiert nicht mehr.")

    return row


def validate_png_source(source_file: Path | None) -> Path:
    if source_file is None:
        raise ValueError("Für ein neues Gerät ist genau eine PNG-Datei erforderlich.")

    source_file = Path(source_file).resolve()

    if not source_file.is_file():
        raise ValueError(f"PNG-Quelldatei nicht gefunden: {source_file}")

    if source_file.suffix.casefold() != ".png":
        raise ValueError("Es darf ausschließlich eine PNG-Datei verwendet werden.")

    return source_file


def copy_png_to_target(source_file: Path, target_file: Path) -> None:
    target_file.parent.mkdir(parents=True, exist_ok=True)
    temporary_file = target_file.with_name(
        f".{target_file.name}.{uuid4().hex}.tmp"
    )

    try:
        shutil.copy2(source_file, temporary_file)
        os.replace(temporary_file, target_file)
    except Exception:
        temporary_file.unlink(missing_ok=True)
        raise


def create_device(
    studio,
    device_name: str,
    category_id: int | None,
    png_source: Path | None,
) -> int:
    device_key = normalized_device_key(device_name)

    if not device_key:
        raise ValueError("Ein Gerätename ist erforderlich.")

    if category_id is None:
        raise ValueError("Eine Gerätekategorie ist erforderlich.")

    source_file = validate_png_source(png_source)
    timestamp = current_timestamp()
    connection = connect(studio)
    target_file: Path | None = None
    copied_file = False

    try:
        connection.execute("BEGIN")
        category_row = connection.execute(
            f"SELECT record_id FROM {quote_identifier(CATEGORY_TABLE)} WHERE record_id = ?",
            (int(category_id),),
        ).fetchone()

        if category_row is None:
            raise ValueError("Die ausgewählte Gerätekategorie existiert nicht mehr.")

        pending_filename = f"__pending__{uuid4().hex}.png"
        cursor = connection.execute(
            f"""
            INSERT INTO {quote_identifier(DEVICE_TABLE)} (
                device_key, category_id, translation_key, source_filename,
                sort_order, is_active, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, 1, ?, ?)
            """,
            (
                device_key,
                int(category_id),
                device_translation_key(device_key),
                pending_filename,
                next_sort_order(connection, DEVICE_TABLE),
                timestamp,
                timestamp,
            ),
        )
        record_id = int(cursor.lastrowid)
        target_file = graphics_path(studio) / f"symbol_source_{record_id}.png"

        if target_file.exists():
            raise RuntimeError(
                "Ziel-PNG existiert bereits und wird nicht überschrieben: "
                f"{target_file}"
            )

        copy_png_to_target(source_file, target_file)
        copied_file = True
        connection.execute(
            f"""
            UPDATE {quote_identifier(DEVICE_TABLE)}
            SET source_filename = ?
            WHERE record_id = ?
            """,
            (target_file.name, record_id),
        )
        connection.commit()
        return record_id

    except Exception:
        connection.rollback()

        if copied_file and target_file is not None:
            target_file.unlink(missing_ok=True)

        raise
    finally:
        connection.close()


def update_device(
    studio,
    record_id: int,
    device_name: str,
    category_id: int | None,
) -> None:
    device_key = normalized_device_key(device_name)

    if not device_key:
        raise ValueError("Ein Gerätename ist erforderlich.")

    if category_id is None:
        raise ValueError("Eine Gerätekategorie ist erforderlich.")

    connection = connect(studio)

    try:
        connection.execute("BEGIN")
        category_row = connection.execute(
            f"SELECT record_id FROM {quote_identifier(CATEGORY_TABLE)} WHERE record_id = ?",
            (int(category_id),),
        ).fetchone()

        if category_row is None:
            raise ValueError("Die ausgewählte Gerätekategorie existiert nicht mehr.")

        cursor = connection.execute(
            f"""
            UPDATE {quote_identifier(DEVICE_TABLE)}
            SET
                device_key = ?,
                category_id = ?,
                translation_key = ?,
                updated_at = ?
            WHERE record_id = ?
            """,
            (
                device_key,
                int(category_id),
                device_translation_key(device_key),
                current_timestamp(),
                record_id,
            ),
        )

        if cursor.rowcount != 1:
            raise ValueError("Das gewählte Verbrauchergerät existiert nicht mehr.")

        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def delete_device(studio, record_id: int) -> None:
    connection = connect(studio)
    source_filename = ""

    try:
        row = connection.execute(
            f"""
            SELECT source_filename
            FROM {quote_identifier(DEVICE_TABLE)}
            WHERE record_id = ?
            """,
            (record_id,),
        ).fetchone()

        if row is None:
            raise ValueError("Das gewählte Verbrauchergerät existiert nicht mehr.")

        source_filename = str(row[0])
        connection.execute(
            f"DELETE FROM {quote_identifier(DEVICE_TABLE)} WHERE record_id = ?",
            (record_id,),
        )
        connection.commit()
    finally:
        connection.close()

    target_file = graphics_path(studio) / source_filename

    if target_file.is_file():
        target_file.unlink()
