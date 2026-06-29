from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import re
import sqlite3
import stat
import sys
import time


@dataclass
class TableCopyData:
    source_table_name: str
    target_table_name: str
    create_sql: str
    column_names: list[str]
    rows: list[tuple[object, ...]]
    reference_table_names: dict[str, str]


@dataclass
class SourceData:
    product_name: str
    product_family: str
    product_version: str
    author: str
    organization_name: str
    ux_theme_create_sql: str
    ux_theme_columns: list[str]
    ux_theme_rows: list[tuple[object, ...]]
    consumer_device_categories: TableCopyData
    consumer_devices: TableCopyData


@dataclass
class ManufacturerBuildResult:
    ux_theme_rows: int
    consumer_device_category_rows: int
    consumer_device_rows: int

def print_separator(
    left_width: int,
    right_width: int,
) -> None:
    print(
        "+"
        + "-" * (left_width + 2)
        + "+"
        + "-" * (right_width + 2)
        + "+"
    )


def print_table(
    values: list[tuple[str, str]],
) -> None:
    left_width = max(
        len("Variable"),
        *(len(variable_name) for variable_name, _ in values),
    )

    right_width = max(
        len("Inhalt"),
        *(len(variable_content) for _, variable_content in values),
    )

    print_separator(
        left_width=left_width,
        right_width=right_width,
    )

    print(
        f"| {'Variable'.ljust(left_width)} "
        f"| {'Inhalt'.ljust(right_width)} |"
    )

    print_separator(
        left_width=left_width,
        right_width=right_width,
    )

    for variable_name, variable_content in values:
        print(
            f"| {variable_name.ljust(left_width)} "
            f"| {variable_content.ljust(right_width)} |"
        )

    print_separator(
        left_width=left_width,
        right_width=right_width,
    )


def normalize_value(
    value: object,
) -> str:
    if value is None:
        return ""

    return str(value).strip()


def quote_identifier(
    identifier: str,
) -> str:
    escaped_identifier = identifier.replace(
        '"',
        '""',
    )

    return f'"{escaped_identifier}"'


def table_exists(
    connection: sqlite3.Connection,
    table_name: str,
) -> bool:
    cursor = connection.execute(
        """
        SELECT 1
        FROM sqlite_master
        WHERE type = 'table'
          AND name = ?
        """,
        (table_name,),
    )

    return cursor.fetchone() is not None


def ensure_table_exists(
    connection: sqlite3.Connection,
    table_name: str,
) -> None:
    if not table_exists(
        connection=connection,
        table_name=table_name,
    ):
        raise RuntimeError(
            f"Tabelle nicht gefunden: {table_name}"
        )


def ensure_columns_exist(
    connection: sqlite3.Connection,
    table_name: str,
    required_columns: tuple[str, ...],
) -> None:
    cursor = connection.execute(
        f"PRAGMA table_info({quote_identifier(table_name)})"
    )

    available_columns = {
        str(row[1])
        for row in cursor.fetchall()
    }

    missing_columns = [
        column_name
        for column_name in required_columns
        if column_name not in available_columns
    ]

    if missing_columns:
        raise RuntimeError(
            f"Fehlende Spalten in {table_name}: "
            f"{', '.join(missing_columns)}"
        )


def get_table_create_sql(
    connection: sqlite3.Connection,
    table_name: str,
) -> str:
    cursor = connection.execute(
        """
        SELECT sql
        FROM sqlite_master
        WHERE type = 'table'
          AND name = ?
        """,
        (table_name,),
    )

    row = cursor.fetchone()

    if row is None:
        raise RuntimeError(
            "Tabellenstruktur nicht gefunden: "
            f"{table_name}"
        )

    create_sql = row[0]

    if not create_sql:
        raise RuntimeError(
            "Tabellenstruktur ist leer: "
            f"{table_name}"
        )

    return str(create_sql)


def get_table_columns(
    connection: sqlite3.Connection,
    table_name: str,
) -> list[str]:
    cursor = connection.execute(
        f"PRAGMA table_info({quote_identifier(table_name)})"
    )

    column_names = [
        str(row[1])
        for row in cursor.fetchall()
    ]

    if not column_names:
        raise RuntimeError(
            "Tabelle enthält keine lesbaren Spalten: "
            f"{table_name}"
        )

    return column_names


def rename_create_table_sql(
    create_sql: str,
    target_table_name: str,
) -> str:
    pattern = re.compile(
        r"^(\s*CREATE\s+TABLE\s+"
        r"(?:IF\s+NOT\s+EXISTS\s+)?)(?:"
        r'"(?:[^"]|"")*"'
        r"|`[^`]*`"
        r"|\[[^\]]*\]"
        r"|[^\s(]+)",
        re.IGNORECASE,
    )

    renamed_sql, replacement_count = pattern.subn(
        lambda match: (
            match.group(1)
            + quote_identifier(target_table_name)
        ),
        create_sql,
        count=1,
    )

    if replacement_count != 1:
        raise RuntimeError(
            "CREATE-TABLE-Anweisung konnte nicht "
            "auf den Zieltabellennamen umgestellt werden."
        )

    return renamed_sql



def replace_referenced_table_names(
    create_sql: str,
    reference_table_names: dict[str, str],
) -> str:
    replaced_sql = create_sql

    for source_table_name, target_table_name in (
        reference_table_names.items()
    ):
        source_name = re.escape(source_table_name)
        target_identifier = quote_identifier(target_table_name)

        patterns = (
            (
                rf'"{source_name.replace('"', '""')}"',
                target_identifier,
            ),
            (
                rf"`{source_name}`",
                target_identifier,
            ),
            (
                rf"\[{source_name}\]",
                target_identifier,
            ),
            (
                rf"(?<![A-Za-z0-9_]){source_name}"
                rf"(?![A-Za-z0-9_])",
                target_identifier,
            ),
        )

        for pattern, replacement in patterns:
            replaced_sql = re.sub(
                pattern,
                replacement,
                replaced_sql,
                flags=re.IGNORECASE,
            )

    return replaced_sql


def read_table_copy_data(
    connection: sqlite3.Connection,
    source_table_name: str,
    target_table_name: str,
    required_columns: tuple[str, ...],
    reference_table_names: dict[str, str] | None = None,
) -> TableCopyData:
    ensure_table_exists(
        connection=connection,
        table_name=source_table_name,
    )

    ensure_columns_exist(
        connection=connection,
        table_name=source_table_name,
        required_columns=required_columns,
    )

    create_sql = get_table_create_sql(
        connection=connection,
        table_name=source_table_name,
    )

    column_names = get_table_columns(
        connection=connection,
        table_name=source_table_name,
    )

    quoted_columns = ", ".join(
        quote_identifier(column_name)
        for column_name in column_names
    )

    cursor = connection.execute(
        f"""
        SELECT {quoted_columns}
        FROM {quote_identifier(source_table_name)}
        """
    )

    return TableCopyData(
        source_table_name=source_table_name,
        target_table_name=target_table_name,
        create_sql=create_sql,
        column_names=column_names,
        rows=[
            tuple(row)
            for row in cursor.fetchall()
        ],
        reference_table_names=reference_table_names or {},
    )


def remove_existing_table(
    connection: sqlite3.Connection,
    table_name: str,
) -> None:
    if not table_exists(
        connection=connection,
        table_name=table_name,
    ):
        print(
            "Keine bestehende Tabelle in mnfctr_db.r0b gefunden: "
            f"{table_name}"
        )
        return

    connection.execute(
        f"DROP TABLE {quote_identifier(table_name)}"
    )

    print(
        "Bestehende Tabelle aus mnfctr_db.r0b entfernt: "
        f"{table_name}"
    )


def create_and_fill_copied_table(
    connection: sqlite3.Connection,
    table_data: TableCopyData,
) -> int:
    remove_existing_table(
        connection=connection,
        table_name=table_data.target_table_name,
    )

    target_create_sql = rename_create_table_sql(
        create_sql=table_data.create_sql,
        target_table_name=table_data.target_table_name,
    )

    target_create_sql = replace_referenced_table_names(
        create_sql=target_create_sql,
        reference_table_names=table_data.reference_table_names,
    )

    connection.execute(target_create_sql)

    if not table_data.rows:
        print(
            "Zieltabelle wurde erstellt, die Quelltabelle "
            "enthält keine Datensätze: "
            f"{table_data.source_table_name} -> "
            f"{table_data.target_table_name}"
        )
        return 0

    quoted_columns = ", ".join(
        quote_identifier(column_name)
        for column_name in table_data.column_names
    )

    placeholders = ", ".join(
        "?"
        for _ in table_data.column_names
    )

    insert_sql = (
        f"INSERT INTO {quote_identifier(table_data.target_table_name)} "
        f"({quoted_columns}) VALUES ({placeholders})"
    )

    connection.executemany(
        insert_sql,
        table_data.rows,
    )

    copied_row_count = len(table_data.rows)

    print(
        "Tabelle kopiert: "
        f"{table_data.source_table_name} -> "
        f"{table_data.target_table_name}; "
        f"Datensätze: {copied_row_count}"
    )

    return copied_row_count


def verify_copied_table(
    connection: sqlite3.Connection,
    target_table_name: str,
    expected_row_count: int,
) -> None:
    ensure_table_exists(
        connection=connection,
        table_name=target_table_name,
    )

    cursor = connection.execute(
        f"""
        SELECT COUNT(*)
        FROM {quote_identifier(target_table_name)}
        """
    )

    actual_row_count = int(cursor.fetchone()[0])

    if actual_row_count != expected_row_count:
        raise RuntimeError(
            "Kopierte Tabelle enthält nicht die erwartete "
            "Datensatzanzahl:"
            f"\nTabelle: {target_table_name}"
            f"\nErwartet: {expected_row_count}"
            f"\nGefunden: {actual_row_count}"
        )

def delete_database_until_removed(
    manufacture_db: Path,
) -> None:
    if not manufacture_db.exists():
        print(
            "Keine bestehende manufacturer database gefunden."
        )
        return

    if manufacture_db.is_dir():
        raise RuntimeError(
            "manufacture_db verweist auf einen Ordner "
            "statt auf eine Datenbankdatei:"
            f"\n{manufacture_db}"
        )

    print()
    print("Bestehende manufacturer database wird gelöscht:")
    print(manufacture_db)

    delete_attempt = 0

    while manufacture_db.exists():
        delete_attempt += 1

        try:
            os.chmod(
                manufacture_db,
                stat.S_IWRITE,
            )

        except OSError:
            pass

        try:
            manufacture_db.unlink()

        except OSError as error:
            print(
                "Löschen fehlgeschlagen. "
                f"Neuer Versuch #{delete_attempt} ..."
            )
            print(error)
            time.sleep(0.25)
            continue

        time.sleep(0.05)

    print(
        "Bestehende manufacturer database sicher gelöscht."
    )


def read_source_data(
    source_db: Path,
) -> SourceData:
    product_name = "deskNode"
    ux_source_table_name = "ux-deskNode"
    category_source_table_name = (
        "desknode_consumer_device_categories"
    )
    device_source_table_name = (
        "desknode_consumer_devices"
    )

    if not source_db.is_file():
        raise RuntimeError(
            "source_db wurde nicht gefunden:"
            f"\n{source_db}"
        )

    connection = sqlite3.connect(source_db)

    try:
        ensure_table_exists(
            connection=connection,
            table_name="product_credentials",
        )

        ensure_columns_exist(
            connection=connection,
            table_name="product_credentials",
            required_columns=(
                "product_name",
                "product_family",
                "release_version",
                "author",
            ),
        )

        ensure_table_exists(
            connection=connection,
            table_name="manufacturer_credentials",
        )

        ensure_columns_exist(
            connection=connection,
            table_name="manufacturer_credentials",
            required_columns=(
                "manufacturer_id",
                "manufacturer_name",
                "author_name",
                "active",
            ),
        )

        ensure_table_exists(
            connection=connection,
            table_name=ux_source_table_name,
        )

        product_cursor = connection.execute(
            """
            SELECT
                product_family,
                release_version,
                author
            FROM product_credentials
            WHERE product_name = ?
            LIMIT 1
            """,
            (product_name,),
        )

        product_row = product_cursor.fetchone()

        if product_row is None:
            raise RuntimeError(
                "Produktdatensatz nicht gefunden:"
                f"\nproduct_name = {product_name}"
            )

        product_family = normalize_value(
            product_row[0]
        )

        product_version = normalize_value(
            product_row[1]
        )

        author = normalize_value(
            product_row[2]
        )

        manufacturer_cursor = connection.execute(
            """
            SELECT
                manufacturer_name
            FROM manufacturer_credentials
            WHERE author_name = ?
              AND active = 1
            ORDER BY manufacturer_id ASC
            LIMIT 1
            """,
            (author,),
        )

        manufacturer_row = manufacturer_cursor.fetchone()

        if manufacturer_row is None:
            raise RuntimeError(
                "Kein aktiver Herstellerdatensatz "
                "für den Produktautor gefunden:"
                f"\nauthor_name = {author}"
            )

        organization_name = normalize_value(
            manufacturer_row[0]
        )

        if not organization_name:
            raise RuntimeError(
                "Der gefundene Herstellerdatensatz enthält "
                "keinen manufacturer_name."
            )

        ux_theme_create_sql = get_table_create_sql(
            connection=connection,
            table_name=ux_source_table_name,
        )

        ux_theme_columns = get_table_columns(
            connection=connection,
            table_name=ux_source_table_name,
        )

        quoted_columns = ", ".join(
            quote_identifier(column_name)
            for column_name in ux_theme_columns
        )

        ux_theme_cursor = connection.execute(
            f"""
            SELECT {quoted_columns}
            FROM {quote_identifier(ux_source_table_name)}
            """
        )

        consumer_device_categories = read_table_copy_data(
            connection=connection,
            source_table_name=category_source_table_name,
            target_table_name="consumer_device_categories",
            required_columns=(
                "record_id",
                "category_key",
                "translation_key",
                "created_at",
                "updated_at",
            ),
        )

        consumer_devices = read_table_copy_data(
            connection=connection,
            source_table_name=device_source_table_name,
            target_table_name="consumer_devices",
            required_columns=(
                "record_id",
                "device_key",
                "category_id",
                "translation_key",
                "created_at",
                "updated_at",
            ),
            reference_table_names={
                category_source_table_name:
                    "consumer_device_categories",
            },
        )

        ux_theme_rows = [
            tuple(row)
            for row in ux_theme_cursor.fetchall()
        ]

    finally:
        connection.close()

    return SourceData(
        product_name=product_name,
        product_family=product_family,
        product_version=product_version,
        author=author,
        organization_name=organization_name,
        ux_theme_create_sql=ux_theme_create_sql,
        ux_theme_columns=ux_theme_columns,
        ux_theme_rows=ux_theme_rows,
        consumer_device_categories=consumer_device_categories,
        consumer_devices=consumer_devices,
    )

def remove_existing_ux_theme_table(
    connection: sqlite3.Connection,
) -> None:
    target_table_name = "ux_themes"

    if not table_exists(
        connection=connection,
        table_name=target_table_name,
    ):
        print(
            "Keine bestehende ux_themes-Tabelle "
            "in mnfctr_db.r0b gefunden."
        )
        return

    connection.execute(
        f"DROP TABLE {quote_identifier(target_table_name)}"
    )

    print(
        "Bestehende ux_themes-Tabelle "
        "aus mnfctr_db.r0b entfernt."
    )


def create_and_fill_ux_theme_table(
    connection: sqlite3.Connection,
    source_data: SourceData,
) -> int:
    target_table_name = "ux_themes"

    remove_existing_ux_theme_table(
        connection=connection,
    )

    target_create_sql = rename_create_table_sql(
        create_sql=source_data.ux_theme_create_sql,
        target_table_name=target_table_name,
    )

    connection.execute(target_create_sql)

    if not source_data.ux_theme_rows:
        print(
            "ux_themes wurde erstellt. "
            "Die Quelltabelle ux-deskNode enthält "
            "keine Datensätze."
        )
        return 0

    quoted_columns = ", ".join(
        quote_identifier(column_name)
        for column_name in source_data.ux_theme_columns
    )

    placeholders = ", ".join(
        "?"
        for _ in source_data.ux_theme_columns
    )

    insert_sql = (
        f"INSERT INTO {quote_identifier(target_table_name)} "
        f"({quoted_columns}) "
        f"VALUES ({placeholders})"
    )

    connection.executemany(
        insert_sql,
        source_data.ux_theme_rows,
    )

    copied_row_count = len(source_data.ux_theme_rows)

    print(
        "ux-deskNode wurde als ux_themes "
        "in mnfctr_db.r0b kopiert:"
    )
    print(f"Datensätze: {copied_row_count}")

    return copied_row_count


def verify_ux_theme_copy(
    connection: sqlite3.Connection,
    expected_row_count: int,
) -> None:
    target_table_name = "ux_themes"

    ensure_table_exists(
        connection=connection,
        table_name=target_table_name,
    )

    cursor = connection.execute(
        f"""
        SELECT COUNT(*)
        FROM {quote_identifier(target_table_name)}
        """
    )

    copied_row_count = int(cursor.fetchone()[0])

    if copied_row_count != expected_row_count:
        raise RuntimeError(
            "Die kopierte ux_themes-Tabelle enthält "
            "nicht die erwartete Datensatzanzahl:"
            f"\nErwartet: {expected_row_count}"
            f"\nGefunden: {copied_row_count}"
        )


def create_manufacturer_database(
    manufacture_db: Path,
    source_data: SourceData,
) -> ManufacturerBuildResult:
    manufacture_db.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(manufacture_db)

    try:
        connection.execute("PRAGMA foreign_keys = OFF")
        connection.execute("BEGIN")

        connection.execute(
            """
            CREATE TABLE master_data (
                product_name TEXT NOT NULL,
                product_family TEXT NOT NULL,
                product_version TEXT NOT NULL,
                author TEXT NOT NULL,
                organization_name TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            INSERT INTO master_data (
                product_name,
                product_family,
                product_version,
                author,
                organization_name
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                source_data.product_name,
                source_data.product_family,
                source_data.product_version,
                source_data.author,
                source_data.organization_name,
            ),
        )

        copied_ux_theme_rows = create_and_fill_ux_theme_table(
            connection=connection,
            source_data=source_data,
        )

        verify_ux_theme_copy(
            connection=connection,
            expected_row_count=copied_ux_theme_rows,
        )

        copied_category_rows = create_and_fill_copied_table(
            connection=connection,
            table_data=source_data.consumer_device_categories,
        )

        verify_copied_table(
            connection=connection,
            target_table_name="consumer_device_categories",
            expected_row_count=copied_category_rows,
        )

        copied_device_rows = create_and_fill_copied_table(
            connection=connection,
            table_data=source_data.consumer_devices,
        )

        verify_copied_table(
            connection=connection,
            target_table_name="consumer_devices",
            expected_row_count=copied_device_rows,
        )

        connection.commit()

    except sqlite3.Error:
        connection.rollback()
        raise

    except RuntimeError:
        connection.rollback()
        raise

    finally:
        connection.close()

    if not manufacture_db.is_file():
        raise RuntimeError(
            "Die neue manufacturer database wurde "
            "nicht gespeichert:"
            f"\n{manufacture_db}"
        )

    return ManufacturerBuildResult(
        ux_theme_rows=copied_ux_theme_rows,
        consumer_device_category_rows=copied_category_rows,
        consumer_device_rows=copied_device_rows,
    )

def main() -> int:
    home_path = Path(__file__).resolve().parent

    manufacture_db = (
        home_path
        / ".."
        / ".."
        / "data"
        / "mnfctr_db.r0b"
    ).resolve()

    source_db = (
        home_path
        / ".."
        / ".."
        / ".."
        / ".."
        / "resources"
        / "organization"
        / "devbox_db.r0b"
    ).resolve()

    try:
        source_data = read_source_data(
            source_db=source_db,
        )

        delete_database_until_removed(
            manufacture_db=manufacture_db,
        )

        build_result = create_manufacturer_database(
            manufacture_db=manufacture_db,
            source_data=source_data,
        )

    except sqlite3.Error as error:
        print()
        print("SQLite-Fehler:")
        print(error)
        return 1

    except RuntimeError as error:
        print()
        print("Fehler:")
        print(error)
        return 1

    print()
    print("deskNode manufacturer database created")
    print()

    print_table(
        [
            ("home_path", str(home_path)),
            ("manufacture_db", str(manufacture_db)),
            ("source_db", str(source_db)),
            ("product_name", source_data.product_name),
            ("product_family", source_data.product_family),
            ("product_version", source_data.product_version),
            ("author", source_data.author),
            ("organization_name", source_data.organization_name),
            ("ux_source_table", "ux-deskNode"),
            ("ux_target_table", "ux_themes"),
            ("ux_theme_rows", str(build_result.ux_theme_rows)),
            (
                "consumer_device_category_rows",
                str(build_result.consumer_device_category_rows),
            ),
            (
                "consumer_device_rows",
                str(build_result.consumer_device_rows),
            ),
        ]
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())