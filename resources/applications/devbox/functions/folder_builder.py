from pathlib import Path
import os
import sys
import sqlite3
import time


home_path = Path(__file__).resolve().parent
os.chdir(home_path)

current_path = home_path
projekt_root_path = None

while True:
    root_file = current_path / ".root"

    if root_file.is_file():
        content = root_file.read_text(encoding="utf-8").strip()

        if content == "project-root":
            projekt_root_path = current_path
            break

    parent_path = current_path.parent

    if parent_path == current_path:
        print("No project root found.")
        sys.exit(0)

    current_path = parent_path
    os.chdir(current_path)


database_file = projekt_root_path / "resources" / "organization" / "devbox_db.r0b"
table_name = "folder_structure"
applications_default_name = "applications"


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def utc_timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def table_exists(connection: sqlite3.Connection, name: str) -> bool:
    cursor = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name = ?
        """,
        (name,),
    )

    return cursor.fetchone() is not None


def get_table_columns(connection: sqlite3.Connection, name: str) -> list[str]:
    cursor = connection.execute(
        f"PRAGMA table_info({quote_identifier(name)})"
    )

    return [
        str(row[1])
        for row in cursor.fetchall()
    ]


def get_existing_applications_folder() -> Path | None:
    for item in projekt_root_path.iterdir():
        if item.is_dir() and item.name.lower() == applications_default_name:
            return item

    return None


def get_row_parts(row: sqlite3.Row, columns: list[str]) -> list[str]:
    if "relative_path" in columns:
        relative_path = row["relative_path"]

        if relative_path is not None and str(relative_path).strip():
            return [
                part.strip()
                for part in str(relative_path).replace("\\", "/").split("/")
                if part.strip()
            ]

    level_columns = [
        column
        for column in columns
        if column.lower().startswith("level_")
    ]

    level_columns.sort(
        key=lambda value: int(value.split("_", 1)[1])
        if value.split("_", 1)[1].isdigit()
        else 9999
    )

    parts = []

    for column in level_columns:
        value = row[column]

        if value is None:
            continue

        value = str(value).strip()

        if value:
            parts.append(value)

    return parts


def contains_placeholder(parts: list[str]) -> bool:
    for part in parts:
        if "<" in part or ">" in part:
            return True

    return False


def has_unsafe_part(parts: list[str]) -> bool:
    for part in parts:
        if part in {"", ".", ".."}:
            return True

        if "/" in part or "\\" in part:
            return True

    return False


def resolve_safe_path(parts: list[str]) -> Path | None:
    target_path = projekt_root_path.joinpath(*parts).resolve()
    root_path = projekt_root_path.resolve()

    try:
        target_path.relative_to(root_path)
    except ValueError:
        return None

    return target_path


def update_exists_state(
    connection: sqlite3.Connection,
    columns: list[str],
    rowid: int,
    exists_on_disk: int,
) -> None:
    updates = []
    values = []

    if "exists_on_disk" in columns:
        updates.append(f"{quote_identifier('exists_on_disk')} = ?")
        values.append(exists_on_disk)

    if "last_checked_at" in columns:
        updates.append(f"{quote_identifier('last_checked_at')} = ?")
        values.append(utc_timestamp())

    if "last_scanned_at" in columns:
        updates.append(f"{quote_identifier('last_scanned_at')} = ?")
        values.append(utc_timestamp())

    if not updates:
        return

    values.append(rowid)

    connection.execute(
        f"""
        UPDATE {quote_identifier(table_name)}
        SET {", ".join(updates)}
        WHERE rowid = ?
        """,
        values,
    )


def main() -> int:
    if not database_file.is_file():
        print(f"Database not found: {database_file}")
        return 1

    connection = sqlite3.connect(database_file)
    connection.row_factory = sqlite3.Row

    try:
        if not table_exists(connection, table_name):
            print(f"Table not found: {table_name}")
            return 1

        columns = get_table_columns(connection, table_name)

        order_parts = []

        if "sort_order" in columns:
            order_parts.append(quote_identifier("sort_order"))

        if "relative_path" in columns:
            order_parts.append(quote_identifier("relative_path"))

        order_sql = ""

        if order_parts:
            order_sql = " ORDER BY " + ", ".join(order_parts)

        cursor = connection.execute(
            f"""
            SELECT rowid, *
            FROM {quote_identifier(table_name)}
            {order_sql}
            """
        )

        rows = cursor.fetchall()

        existing_applications_folder = get_existing_applications_folder()
        applications_name = (
            existing_applications_folder.name
            if existing_applications_folder is not None
            else applications_default_name
        )

        created_count = 0
        existing_count = 0
        skipped_count = 0
        blocked_count = 0

        for row in rows:
            rowid = int(row["rowid"])
            parts = get_row_parts(row, columns)

            if not parts:
                skipped_count += 1
                continue

            if parts[0].lower() != applications_default_name:
                skipped_count += 1
                continue

            parts[0] = applications_name

            if contains_placeholder(parts):
                skipped_count += 1
                continue

            if has_unsafe_part(parts):
                blocked_count += 1
                print(f"Blocked unsafe path: {'/'.join(parts)}")
                continue

            target_path = resolve_safe_path(parts)

            if target_path is None:
                blocked_count += 1
                print(f"Blocked path outside project root: {'/'.join(parts)}")
                continue

            if target_path.exists() and not target_path.is_dir():
                blocked_count += 1
                print(f"Blocked existing non-folder path: {target_path}")
                update_exists_state(
                    connection=connection,
                    columns=columns,
                    rowid=rowid,
                    exists_on_disk=0,
                )
                continue

            if target_path.is_dir():
                existing_count += 1
                update_exists_state(
                    connection=connection,
                    columns=columns,
                    rowid=rowid,
                    exists_on_disk=1,
                )
                continue

            target_path.mkdir(parents=True, exist_ok=True)
            created_count += 1

            update_exists_state(
                connection=connection,
                columns=columns,
                rowid=rowid,
                exists_on_disk=1,
            )

            print(f"Created folder: {target_path}")

        connection.commit()

        print(f"projekt_root_path: {projekt_root_path}")
        print(f"database_file: {database_file}")
        print(f"table_name: {table_name}")
        print(f"created_count: {created_count}")
        print(f"existing_count: {existing_count}")
        print(f"skipped_count: {skipped_count}")
        print(f"blocked_count: {blocked_count}")

        return 0

    finally:
        connection.close()


if __name__ == "__main__":
    sys.exit(main())