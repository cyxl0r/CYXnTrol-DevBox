from __future__ import annotations

from subscripts.main_gui_devbox_log import get_devbox_logger
LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")


import sqlite3
from pathlib import Path

from subscripts.main_gui_metadata_common import (
    MANUFACTURER_TABLE_NAME,
    as_text,
    first_value,
    next_integer_value,
    project_family,
    quote_identifier,
    real_manufacturer_row,
    table_columns,
    utc_timestamp,
)


MANUFACTURER_READ_ONLY_COLUMNS = frozenset({
    "manufacturer_id",
    "product_family",
    "created_at",
    "updated_at",
})


def manufacturer_create_values(
    connection: sqlite3.Connection,
    user_values: dict[str, object],
    project_root_path: Path | None = None,
) -> dict[str, object]:
    columns = table_columns(connection, MANUFACTURER_TABLE_NAME)
    values = dict(user_values)
    now = utc_timestamp()
    manufacturer_name = first_value(values.get(columns.get("manufacturer_name", "")))
    brand_name = first_value(values.get(columns.get("manufacturer_brand_name", "")), manufacturer_name)
    author_name = first_value(values.get(columns.get("author_name", "")))
    organization_type = first_value(values.get(columns.get("organization_type", "")))
    defaults: dict[str, object] = {
        "manufacturer_id": next_integer_value(
            connection,
            MANUFACTURER_TABLE_NAME,
            columns.get("manufacturer_id", "manufacturer_id"),
        ),
        "manufacturer_display_name": manufacturer_name,
        "manufacturer_brand_name": brand_name,
        "author_display_name": author_name,
        "publisher_name": brand_name,
        "developer_name": brand_name,
        "created_at": now,
        "updated_at": now,
        "active": 1,
    }
    if project_root_path is not None:
        defaults["product_family"] = project_family(project_root_path)
    if organization_type != "fantasy_organization":
        defaults["organization_name"] = brand_name

    for key, value in defaults.items():
        column = columns.get(key)
        if column is not None and not first_value(values.get(column)):
            values[column] = value
    return values


def manufacturer_update_values(connection: sqlite3.Connection) -> dict[str, object]:
    columns = table_columns(connection, MANUFACTURER_TABLE_NAME)
    column = columns.get("updated_at")
    return {} if column is None else {column: utc_timestamp()}


def sync_manufacturer_defaults(connection: sqlite3.Connection, project_root_path: Path | None = None) -> int:
    result = real_manufacturer_row(connection)
    if result is None:
        return 0

    rowid, manufacturer = result
    columns = table_columns(connection, MANUFACTURER_TABLE_NAME)
    updates: dict[str, object] = {}
    now = utc_timestamp()
    name = first_value(manufacturer.get(columns.get("manufacturer_name", "")))
    brand = first_value(manufacturer.get(columns.get("manufacturer_brand_name", "")), name)
    author = first_value(manufacturer.get(columns.get("author_name", "")))
    organization_type = first_value(manufacturer.get(columns.get("organization_type", "")))
    defaults: dict[str, object] = {
        "manufacturer_id": next_integer_value(
            connection,
            MANUFACTURER_TABLE_NAME,
            columns.get("manufacturer_id", "manufacturer_id"),
        ),
        "manufacturer_display_name": name,
        "manufacturer_brand_name": brand,
        "author_display_name": author,
        "publisher_name": brand,
        "developer_name": brand,
        "created_at": now,
        "updated_at": now,
        "active": 1,
    }
    if project_root_path is not None:
        defaults["product_family"] = project_family(project_root_path)
    if organization_type != "fantasy_organization":
        defaults["organization_name"] = brand

    for key, value in defaults.items():
        column = columns.get(key)
        if column is not None and not first_value(manufacturer.get(column)):
            updates[column] = value

    family_column = columns.get("product_family")
    if project_root_path is not None and family_column is not None:
        family = project_family(project_root_path)
        if as_text(manufacturer.get(family_column)) != family:
            updates[family_column] = family

    if not updates:
        return 0
    updated_column = columns.get("updated_at")
    if updated_column is not None:
        updates[updated_column] = now
    assignments = ", ".join(f"{quote_identifier(column)} = ?" for column in updates)
    connection.execute(
        f"UPDATE {quote_identifier(MANUFACTURER_TABLE_NAME)} SET {assignments} WHERE rowid = ?",
        [updates[column] for column in updates] + [rowid],
    )
    return 1
