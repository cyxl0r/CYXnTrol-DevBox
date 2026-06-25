from pathlib import Path
import sqlite3
import time

from create_devdbase_schema import quote_identifier, sync_table_schema

MAX_LEVELS = 12
BASIC_TABLE_NAME = "folder_structure_basic"
STRUCTURE_TABLE_NAME = "folder_structure"
APPLICATIONS_FOLDER_NAME = "applications"
APP_PLACEHOLDER = "<Softwareprojekt>"
SOURCE_BASIC_SCAN = "scanned_project_root_basic"
SOURCE_APP_TEMPLATE = "devbox_manual_app_template"
SOURCE_STRUCTURE = "resolved_folder_structure"
EXCLUDED_FOLDER_NAMES = {
    "__pycache__", ".git", ".hg", ".svn", ".mypy_cache",
    ".pytest_cache", ".ruff_cache", ".venv", "venv", "env",
}
BASE_COLUMNS = [
    ("sort_order", "INTEGER"), ("source_type", "TEXT"), ("folder_role", "TEXT"),
    ("app_folder_name", "TEXT"), ("depth", "INTEGER"), ("relative_path", "TEXT"),
    ("exists_on_disk", "INTEGER"), ("last_scanned_at", "TEXT"),
]
LEVEL_COLUMNS = [(f"level_{index}", "TEXT") for index in range(1, MAX_LEVELS + 1)]
TABLE_COLUMNS = BASE_COLUMNS + LEVEL_COLUMNS

class FolderRow:
    def __init__(self, sort_order: int, source_type: str, folder_role: str,
                 app_folder_name: str | None, relative_path: str,
                 exists_on_disk: int, last_scanned_at: str) -> None:
        self.sort_order = sort_order
        self.source_type = source_type
        self.folder_role = folder_role
        self.app_folder_name = app_folder_name
        self.relative_path = normalize_relative_path(relative_path)
        self.exists_on_disk = exists_on_disk
        self.last_scanned_at = last_scanned_at

    def as_tuple(self) -> tuple[object, ...]:
        parts = split_relative_path(self.relative_path)
        levels = [parts[index] if index < len(parts) else None for index in range(MAX_LEVELS)]
        return (
            self.sort_order, self.source_type, self.folder_role,
            self.app_folder_name, len(parts), self.relative_path,
            self.exists_on_disk, self.last_scanned_at, *levels,
        )

def utc_timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def split_relative_path(relative_path: str | Path) -> list[str]:
    return [part for part in str(relative_path).replace("\\", "/").split("/") if part]

def normalize_relative_path(path: Path | str) -> str:
    return (path.as_posix() if isinstance(path, Path) else str(path)).replace("\\", "/").strip("/")

def is_applications_part(value: str) -> bool:
    return str(value).lower() == APPLICATIONS_FOLDER_NAME.lower()

def is_app_placeholder_part(value: str) -> bool:
    return str(value).lower() == APP_PLACEHOLDER.lower()

def is_excluded_folder(folder_path: Path) -> bool:
    return folder_path.name.lower() in EXCLUDED_FOLDER_NAMES

def folder_role_from_parts(parts: list[str]) -> str:
    if not parts:
        return "project_root"
    if not is_applications_part(parts[0]):
        return "platform_folder"
    if len(parts) == 1:
        return "applications_root"
    if len(parts) == 2 and is_app_placeholder_part(parts[1]):
        return "application_template_root"
    if len(parts) >= 2 and is_app_placeholder_part(parts[1]):
        return "application_template_subfolder"
    if len(parts) == 2:
        return "application_folder"
    return "application_subfolder"

def app_name_from_parts(parts: list[str]) -> str | None:
    if len(parts) >= 2 and is_applications_part(parts[0]):
        return parts[1]
    return None

def find_applications_path(projekt_root_path: Path) -> Path:
    for child in projekt_root_path.iterdir():
        if child.is_dir() and is_applications_part(child.name):
            return child
    return projekt_root_path / APPLICATIONS_FOLDER_NAME

def scan_basic_directories(projekt_root_path: Path) -> list[Path]:
    result = []

    def walk(current_path: Path) -> None:
        try:
            children = [child for child in current_path.iterdir()
                        if child.is_dir() and not is_excluded_folder(child)]
        except Exception as error:
            print(f"Folder scan skipped: {current_path} | {error}")
            return
        children.sort(key=lambda child: child.name.lower())
        for child in children:
            try:
                relative_path = child.relative_to(projekt_root_path)
            except ValueError:
                continue
            result.append(relative_path)
            if list(relative_path.parts) and is_applications_part(relative_path.parts[0]):
                continue
            walk(child)

    walk(projekt_root_path)
    result.sort(key=lambda path: path.as_posix().lower())
    return result

def build_rows(relative_paths: list[Path], source_type: str, scanned_at: str) -> list[FolderRow]:
    rows = []
    for sort_order, relative_path in enumerate(relative_paths, start=1):
        parts = list(relative_path.parts)
        rows.append(FolderRow(sort_order, source_type, folder_role_from_parts(parts),
                              app_name_from_parts(parts), normalize_relative_path(relative_path),
                              1, scanned_at))
    return rows

def ensure_table(connection: sqlite3.Connection, table_name: str) -> None:
    sync_table_schema(connection=connection, table_name=table_name, memory_table=TABLE_COLUMNS)

def delete_by_source(connection: sqlite3.Connection, table_name: str, source_type: str) -> None:
    connection.execute(
        f"DELETE FROM {quote_identifier(table_name)} WHERE {quote_identifier('source_type')} = ?",
        (source_type,),
    )

def clear_table(connection: sqlite3.Connection, table_name: str) -> None:
    connection.execute(f"DELETE FROM {quote_identifier(table_name)}")

def insert_rows(connection: sqlite3.Connection, table_name: str, rows: list[FolderRow]) -> None:
    if not rows:
        print(f"No folder rows to insert into {table_name}.")
        return
    column_names = [column_name for column_name, _ in TABLE_COLUMNS]
    column_sql = ", ".join(quote_identifier(column_name) for column_name in column_names)
    placeholder_sql = ", ".join("?" for _ in column_names)
    connection.executemany(
        f"INSERT INTO {quote_identifier(table_name)} ({column_sql}) VALUES ({placeholder_sql})",
        [row.as_tuple() for row in rows],
    )
    print(f"Inserted folder rows into {table_name}: {len(rows)}")

def refresh_basic_scan_rows(connection: sqlite3.Connection, rows: list[FolderRow]) -> None:
    ensure_table(connection, BASIC_TABLE_NAME)
    delete_by_source(connection, BASIC_TABLE_NAME, SOURCE_BASIC_SCAN)
    insert_rows(connection, BASIC_TABLE_NAME, rows)

def read_template_paths(connection: sqlite3.Connection) -> list[str]:
    ensure_table(connection, BASIC_TABLE_NAME)
    cursor = connection.execute(
        f"""
        SELECT {quote_identifier('relative_path')}
        FROM {quote_identifier(BASIC_TABLE_NAME)}
        WHERE {quote_identifier('relative_path')} IS NOT NULL
          AND (
              {quote_identifier('source_type')} = ?
              OR {quote_identifier('relative_path')} LIKE ?
          )
        ORDER BY {quote_identifier('sort_order')} ASC,
                 {quote_identifier('relative_path')} ASC
        """,
        (SOURCE_APP_TEMPLATE, f"%{APP_PLACEHOLDER}%"),
    )
    paths = []
    seen_paths = set()
    for row in cursor.fetchall():
        clean_path = normalize_relative_path(row[0])
        parts = split_relative_path(clean_path)
        if len(parts) < 2:
            continue
        if not is_applications_part(parts[0]):
            continue
        if not is_app_placeholder_part(parts[1]):
            continue
        path_key = clean_path.lower()
        if path_key in seen_paths:
            continue
        seen_paths.add(path_key)
        paths.append(clean_path)
    return paths

def ensure_placeholder_root(connection: sqlite3.Connection, applications_name: str) -> None:
    for template_path in read_template_paths(connection):
        if len(split_relative_path(template_path)) == 2:
            return
    row = FolderRow(
        100000, SOURCE_APP_TEMPLATE, "application_template_root",
        APP_PLACEHOLDER, f"{applications_name}/{APP_PLACEHOLDER}",
        0, utc_timestamp(),
    )
    insert_rows(connection, BASIC_TABLE_NAME, [row])

def get_application_folders(applications_path: Path) -> list[Path]:
    if not applications_path.is_dir():
        return []
    folders = [child for child in applications_path.iterdir()
               if child.is_dir() and not is_excluded_folder(child)]
    folders.sort(key=lambda child: child.name.lower())
    return folders

def template_tail(relative_path: str) -> list[str]:
    parts = split_relative_path(relative_path)
    if len(parts) < 2:
        return []
    if not is_applications_part(parts[0]):
        return []
    if not is_app_placeholder_part(parts[1]):
        return []
    return parts[2:]

def add_structure_row(rows: list[FolderRow], sort_order: int, folder_role: str,
                      app_name: str | None, relative_path: str,
                      exists_on_disk: int, scanned_at: str) -> int:
    rows.append(FolderRow(sort_order, SOURCE_STRUCTURE, folder_role, app_name,
                          relative_path, exists_on_disk, scanned_at))
    return sort_order + 1

def build_resolved_structure_rows(projekt_root_path: Path, applications_path: Path,
                                  basic_rows: list[FolderRow], template_paths: list[str],
                                  scanned_at: str) -> list[FolderRow]:
    rows = []
    sort_order = 1
    template_tails = [template_tail(path) for path in template_paths]
    template_tails = [tail for tail in template_tails if tail]

    for basic_row in basic_rows:
        sort_order = add_structure_row(
            rows, sort_order, basic_row.folder_role, basic_row.app_folder_name,
            basic_row.relative_path, basic_row.exists_on_disk, scanned_at,
        )

    app_root_name = applications_path.name if applications_path.exists() else APPLICATIONS_FOLDER_NAME
    app_folders = get_application_folders(applications_path)
    expanded_rows = 0

    for app_folder in app_folders:
        app_root_parts = [app_root_name, app_folder.name]
        app_root_rel = "/".join(app_root_parts)
        sort_order = add_structure_row(
            rows, sort_order, "application_folder", app_folder.name,
            app_root_rel, 1, scanned_at,
        )
        for tail_parts in template_tails:
            resolved_rel = "/".join(app_root_parts + tail_parts)
            exists_on_disk = int((projekt_root_path / resolved_rel).is_dir())
            sort_order = add_structure_row(
                rows, sort_order, "application_template_subfolder",
                app_folder.name, resolved_rel, exists_on_disk, scanned_at,
            )
            expanded_rows += 1

    print(
        f"Folder structure: apps={len(app_folders)}, "
        f"templates={len(template_paths)}, expanded={expanded_rows}"
    )
    return rows

def sync_folder_structure_tables(connection: sqlite3.Connection, projekt_root_path: Path,
                                 applications_path: Path) -> None:
    scanned_at = utc_timestamp()
    real_applications_path = find_applications_path(projekt_root_path)
    basic_paths = scan_basic_directories(projekt_root_path)
    basic_rows = build_rows(basic_paths, SOURCE_BASIC_SCAN, scanned_at)
    refresh_basic_scan_rows(connection, basic_rows)
    ensure_placeholder_root(connection, real_applications_path.name)
    template_paths = read_template_paths(connection)
    structure_rows = build_resolved_structure_rows(
        projekt_root_path, real_applications_path, basic_rows, template_paths, scanned_at,
    )
    ensure_table(connection, STRUCTURE_TABLE_NAME)
    clear_table(connection, STRUCTURE_TABLE_NAME)
    insert_rows(connection, STRUCTURE_TABLE_NAME, structure_rows)
    if not real_applications_path.is_dir():
        print(f"Applications folder not found during folder scan: {real_applications_path}")
