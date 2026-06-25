from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from main_gui_metadata_defaults import product_create_values, quote_identifier


INITIAL_PRODUCT_NAME = "DevBox"


@dataclass(frozen=True)
class ProductSeedResult:
    seeded: bool
    product_name: str | None
    product_display_name: str | None
    reason: str


def table_row_count(connection: sqlite3.Connection, table_name: str) -> int:
    cursor = connection.execute(
        f"SELECT COUNT(*) FROM {quote_identifier(table_name)}"
    )
    return int(cursor.fetchone()[0])


def insert_seed_row(
    connection: sqlite3.Connection,
    table_name: str,
    values: dict[str, object],
) -> None:
    if not values:
        raise ValueError("Product table has no recognized seed columns.")
    columns = list(values)
    column_sql = ", ".join(quote_identifier(column) for column in columns)
    value_sql = ", ".join("?" for _ in columns)
    connection.execute(
        f"INSERT INTO {quote_identifier(table_name)} ({column_sql}) VALUES ({value_sql})",
        [values[column] for column in columns],
    )


def seed_initial_product(
    connection: sqlite3.Connection,
    product_table_name: str,
    projekt_root_path: Path,
    database_was_created: bool,
) -> ProductSeedResult:
    if not database_was_created:
        return ProductSeedResult(False, None, None, "database already existed")
    if table_row_count(connection, product_table_name) > 0:
        return ProductSeedResult(False, None, None, "product table already contains rows")
    values = product_create_values(
        connection=connection,
        project_root_path=projekt_root_path,
        product_name=INITIAL_PRODUCT_NAME,
    )
    insert_seed_row(connection, product_table_name, values)
    return ProductSeedResult(
        seeded=True,
        product_name=INITIAL_PRODUCT_NAME,
        product_display_name=str(values.get("product_display_name", "")),
        reason="initial DevBox product seeded",
    )
