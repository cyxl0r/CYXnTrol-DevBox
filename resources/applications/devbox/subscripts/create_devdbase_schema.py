import sqlite3
import sys


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def normalize_sqlite_type(column_type: str) -> str:
    valid_types = {
        "INTEGER",
        "TEXT",
        "REAL",
        "BLOB",
    }

    column_type = str(column_type).strip().upper()

    if column_type not in valid_types:
        print(f"Invalid SQLite column type: {column_type}")
        sys.exit(1)

    return column_type


def validate_memory_table(
    table_name: str,
    memory_table: list[tuple[str, str]],
) -> list[tuple[str, str]]:
    if not memory_table:
        print(f"No columns found for table: {table_name}")
        sys.exit(1)

    clean_columns = []
    seen_columns = set()

    for column_name, column_type in memory_table:
        column_name = str(column_name).strip()
        column_type = normalize_sqlite_type(column_type)

        if not column_name:
            continue

        column_key = column_name.lower()

        if column_key in seen_columns:
            print(f"Duplicate column name in table {table_name}: {column_name}")
            sys.exit(1)

        seen_columns.add(column_key)
        clean_columns.append((column_name, column_type))

    if not clean_columns:
        print(f"No valid columns found for table: {table_name}")
        sys.exit(1)

    return clean_columns


def table_exists(
    connection: sqlite3.Connection,
    table_name: str,
) -> bool:
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


def get_existing_columns(
    connection: sqlite3.Connection,
    table_name: str,
) -> dict[str, str]:
    cursor = connection.execute(
        f"PRAGMA table_info({quote_identifier(table_name)})"
    )

    columns = {}

    for row in cursor.fetchall():
        column_name = str(row[1])
        column_type = str(row[2]).upper()
        columns[column_name.lower()] = column_type

    return columns


def create_table(
    connection: sqlite3.Connection,
    table_name: str,
    memory_table: list[tuple[str, str]],
) -> None:
    columns = []

    for column_name, column_type in memory_table:
        sqlite_type = normalize_sqlite_type(column_type)
        columns.append(
            f"{quote_identifier(column_name)} {sqlite_type}"
        )

    column_sql = ",\n    ".join(columns)

    sql = f"""
    CREATE TABLE IF NOT EXISTS {quote_identifier(table_name)} (
        {column_sql}
    );
    """

    connection.execute(sql)
    print(f"Table created or confirmed: {table_name}")


def sync_table_schema(
    connection: sqlite3.Connection,
    table_name: str,
    memory_table: list[tuple[str, str]],
) -> bool:
    memory_table = validate_memory_table(
        table_name=table_name,
        memory_table=memory_table,
    )

    table_was_created = False

    if not table_exists(connection, table_name):
        create_table(
            connection=connection,
            table_name=table_name,
            memory_table=memory_table,
        )
        table_was_created = True
        return table_was_created

    existing_columns = get_existing_columns(
        connection=connection,
        table_name=table_name,
    )

    added_columns = 0

    for column_name, column_type in memory_table:
        column_key = column_name.lower()
        sqlite_type = normalize_sqlite_type(column_type)

        if column_key in existing_columns:
            existing_type = existing_columns[column_key]

            if existing_type and existing_type != sqlite_type:
                print(
                    f"Column exists with different type in {table_name}: "
                    f"{column_name} existing={existing_type} "
                    f"expected={sqlite_type}"
                )

            continue

        sql = (
            f"ALTER TABLE {quote_identifier(table_name)} "
            f"ADD COLUMN {quote_identifier(column_name)} {sqlite_type};"
        )

        connection.execute(sql)
        added_columns += 1
        print(f"Added column to {table_name}: {column_name} {sqlite_type}")

    if added_columns == 0:
        print(f"Table schema already complete: {table_name}")

    return table_was_created


def sync_document_table_pair(
    connection: sqlite3.Connection,
    base_table_name: str,
    document_memory_table: list[tuple[str, str]],
) -> None:
    for language_suffix in ("de", "en"):
        table_name = f"{base_table_name}_{language_suffix}"
        sync_table_schema(
            connection=connection,
            table_name=table_name,
            memory_table=document_memory_table,
        )


def drop_orphaned_document_table_pairs(
    connection: sqlite3.Connection,
    expected_base_table_names: list[str],
    table_suffix: str,
    protected_base_table_names: list[str],
) -> list[str]:
    expected_base_names = set(expected_base_table_names)
    protected_base_names = set(protected_base_table_names)
    allowed_base_names = expected_base_names | protected_base_names

    cursor = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name NOT LIKE 'sqlite_%'
        """
    )

    existing_table_names = [
        str(row[0])
        for row in cursor.fetchall()
    ]

    dropped_tables = []

    for table_name in existing_table_names:
        language_suffix = None

        if table_name.endswith("_de"):
            language_suffix = "_de"

        if table_name.endswith("_en"):
            language_suffix = "_en"

        if language_suffix is None:
            continue

        base_table_name = table_name[:-len(language_suffix)]

        if not base_table_name.endswith(f"_{table_suffix}"):
            continue

        if base_table_name in allowed_base_names:
            continue

        connection.execute(
            f"DROP TABLE IF EXISTS {quote_identifier(table_name)};"
        )

        dropped_tables.append(table_name)

    return dropped_tables
