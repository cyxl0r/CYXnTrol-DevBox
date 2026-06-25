from __future__ import annotations

from subscripts.main_gui_devbox_log import get_devbox_logger
LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")


import json
import sqlite3
import uuid
from pathlib import Path

from subscripts.main_gui_metadata_common import (
    MANUFACTURER_TABLE_NAME,
    PRODUCT_TABLE_NAME,
    as_text,
    first_value,
    next_integer_value,
    project_family,
    quote_identifier,
    real_manufacturer_row,
    slugify,
    table_columns,
    table_exists,
    utc_timestamp,
    utc_year,
)


PRODUCT_READ_ONLY_COLUMNS = frozenset({
    "product_id",
    "product_name",
    "product_family",
    "product_slug",
    "product_uuid",
    "application_uuid",
    "created_at",
    "updated_at",
})


def product_defaults_from_manufacturer(
    connection: sqlite3.Connection,
    product_columns: dict[str, str],
) -> dict[str, object]:
    result = real_manufacturer_row(connection)
    if result is None:
        return {}

    _, manufacturer = result
    mapping = {
        "author": "author_name",
        "publisher": "publisher_name",
        "vendor": "vendor_name",
        "copyright_holder": "manufacturer_legal_name",
        "country": "country",
        "country_code": "country_code",
    }
    values: dict[str, object] = {}
    for product_key, manufacturer_key in mapping.items():
        product_column = product_columns.get(product_key)
        manufacturer_value = manufacturer.get(manufacturer_key)
        if product_column is not None and first_value(manufacturer_value):
            values[product_column] = manufacturer_value
    return values


def product_create_values(
    connection: sqlite3.Connection,
    project_root_path: Path,
    product_name: str,
    target_operating_systems: list[str] | None = None,
) -> dict[str, object]:
    columns = table_columns(connection, PRODUCT_TABLE_NAME)
    now = utc_timestamp()
    product_name = as_text(product_name)
    family = project_family(project_root_path)
    display_name = f"{family} {product_name}".strip()
    values = product_defaults_from_manufacturer(connection, columns)
    defaults = {
        "product_id": next_integer_value(
            connection,
            PRODUCT_TABLE_NAME,
            columns.get("product_id", "product_id"),
        ),
        "product_name": product_name,
        "product_display_name": display_name,
        "product_short_name": product_name,
        "product_slug": slugify(product_name),
        "product_uuid": str(uuid.uuid4()),
        "application_uuid": str(uuid.uuid4()),
        "programming_start": utc_timestamp(),
        "release_version": "0.1.0",
        "build_number": 0,
        "version_major": 0,
        "version_minor": 1,
        "version_patch": 0,
        "copyright_year": utc_year(),
        "product_family": family,
        "target_operating_systems": json.dumps(
            target_operating_systems or ["windows"],
            ensure_ascii=False,
            separators=(",", ":"),
        ),
        "update_channel": "development",
        "created_at": now,
        "updated_at": now,
        "active": 1,
        "deprecated": 0,
    }
    for key, value in defaults.items():
        column = columns.get(key)
        if column is not None:
            values[column] = value
    return values


def product_update_values(connection: sqlite3.Connection) -> dict[str, object]:
    columns = table_columns(connection, PRODUCT_TABLE_NAME)
    column = columns.get("updated_at")
    return {} if column is None else {column: utc_timestamp()}


def sync_product_defaults(connection: sqlite3.Connection, project_root_path: Path) -> int:
    if not table_exists(connection, PRODUCT_TABLE_NAME):
        return 0

    columns = table_columns(connection, PRODUCT_TABLE_NAME)
    cursor = connection.execute(
        f"SELECT rowid, * FROM {quote_identifier(PRODUCT_TABLE_NAME)} ORDER BY rowid ASC"
    )
    changed_count = 0
    family = project_family(project_root_path)
    for row in cursor.fetchall():
        rowid = int(row["rowid"])
        row_values = dict(row)
        product_name = first_value(row_values.get(columns.get("product_name", "")))
        if not product_name:
            continue
        creation_values = product_create_values(connection, project_root_path, product_name)
        updates: dict[str, object] = {}
        for column, value in creation_values.items():
            if not first_value(row_values.get(column)):
                updates[column] = value
        family_column = columns.get("product_family")
        if family_column is not None and as_text(row_values.get(family_column)) != family:
            updates[family_column] = family
        if not updates:
            continue
        updated_column = columns.get("updated_at")
        if updated_column is not None:
            updates[updated_column] = utc_timestamp()
        assignments = ", ".join(f"{quote_identifier(column)} = ?" for column in updates)
        connection.execute(
            f"UPDATE {quote_identifier(PRODUCT_TABLE_NAME)} SET {assignments} WHERE rowid = ?",
            [updates[column] for column in updates] + [rowid],
        )
        changed_count += 1
    return changed_count


def sync_project_family(connection: sqlite3.Connection, project_root_path: Path) -> int:
    family = project_family(project_root_path)
    changed_count = 0

    if table_exists(connection, MANUFACTURER_TABLE_NAME):
        manufacturer_columns = table_columns(connection, MANUFACTURER_TABLE_NAME)
        family_column = manufacturer_columns.get("product_family")
        updated_column = manufacturer_columns.get("updated_at")
        manufacturer = real_manufacturer_row(connection)
        if manufacturer is not None and family_column is not None:
            rowid, data = manufacturer
            if as_text(data.get(family_column)) != family:
                values = {family_column: family}
                if updated_column is not None:
                    values[updated_column] = utc_timestamp()
                assignments = ", ".join(f"{quote_identifier(column)} = ?" for column in values)
                connection.execute(
                    f"UPDATE {quote_identifier(MANUFACTURER_TABLE_NAME)} SET {assignments} WHERE rowid = ?",
                    [values[column] for column in values] + [rowid],
                )
                changed_count += 1

    if table_exists(connection, PRODUCT_TABLE_NAME):
        product_columns = table_columns(connection, PRODUCT_TABLE_NAME)
        family_column = product_columns.get("product_family")
        updated_column = product_columns.get("updated_at")
        if family_column is not None:
            cursor = connection.execute(
                f"SELECT rowid, {quote_identifier(family_column)} FROM {quote_identifier(PRODUCT_TABLE_NAME)}"
            )
            for row in cursor.fetchall():
                if as_text(row[family_column]) == family:
                    continue
                values = {family_column: family}
                if updated_column is not None:
                    values[updated_column] = utc_timestamp()
                assignments = ", ".join(f"{quote_identifier(column)} = ?" for column in values)
                connection.execute(
                    f"UPDATE {quote_identifier(PRODUCT_TABLE_NAME)} SET {assignments} WHERE rowid = ?",
                    [values[column] for column in values] + [int(row["rowid"])],
                )
                changed_count += 1

    return changed_count
