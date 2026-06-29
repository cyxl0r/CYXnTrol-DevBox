from __future__ import annotations

from pathlib import Path
import os
import sqlite3
import sys


SOURCE_APP_TEMPLATE = "devbox_manual_app_template"
TEMPLATE_SUBFOLDER_ROLE = "application_template_subfolder"
TABLE_NAME = "folder_structure_basic"
APPLICATIONS_NAME = "applications"


def find_project_root() -> Path:
    current_path = Path(__file__).resolve().parent
    os.chdir(current_path)

    while True:
        root_file = current_path / ".root"

        if (
            root_file.is_file()
            and root_file.read_text(encoding="utf-8").strip() == "project-root"
        ):
            return current_path

        parent_path = current_path.parent

        if parent_path == current_path:
            raise RuntimeError("No project root found.")

        current_path = parent_path
        os.chdir(current_path)


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def split_path(relative_path: object) -> list[str]:
    return [
        part.strip()
        for part in str(relative_path or "").replace("\\", "/").split("/")
        if part.strip()
    ]


def is_application_placeholder(value: str) -> bool:
    return value.startswith("<") and value.endswith(">") and len(value) > 2


def find_applications_path(project_root_path: Path) -> Path | None:
    for child_path in project_root_path.iterdir():
        if child_path.is_dir() and child_path.name.casefold() == APPLICATIONS_NAME:
            return child_path

    return None


def table_columns(connection: sqlite3.Connection) -> set[str]:
    cursor = connection.execute(
        f"PRAGMA table_info({quote_identifier(TABLE_NAME)})"
    )
    return {str(row[1]).casefold() for row in cursor.fetchall()}


def read_template_subpaths(connection: sqlite3.Connection) -> list[tuple[str, ...]]:
    columns = table_columns(connection)
    required_columns = {
        "source_type",
        "folder_role",
        "relative_path",
    }

    if not required_columns.issubset(columns):
        missing_columns = ", ".join(sorted(required_columns - columns))
        raise RuntimeError(
            f"Missing columns in {TABLE_NAME}: {missing_columns}"
        )

    cursor = connection.execute(
        f"""
        SELECT {quote_identifier('relative_path')}
        FROM {quote_identifier(TABLE_NAME)}
        WHERE {quote_identifier('source_type')} = ?
          AND {quote_identifier('folder_role')} = ?
          AND {quote_identifier('relative_path')} IS NOT NULL
        ORDER BY {quote_identifier('sort_order')} ASC,
                 {quote_identifier('relative_path')} ASC
        """,
        (SOURCE_APP_TEMPLATE, TEMPLATE_SUBFOLDER_ROLE),
    )

    subpaths: set[tuple[str, ...]] = set()

    for row in cursor.fetchall():
        parts = split_path(row[0])

        if (
            len(parts) < 3
            or parts[0].casefold() != APPLICATIONS_NAME
            or not is_application_placeholder(parts[1])
        ):
            continue

        tail = tuple(parts[2:])

        if any(part in {"", ".", ".."} for part in tail):
            print(f"Skipped unsafe template path: {'/'.join(parts)}")
            continue

        subpaths.add(tail)

    return sorted(
        subpaths,
        key=lambda parts: (len(parts), "/".join(parts).casefold()),
    )


def is_empty_directory(folder_path: Path) -> bool:
    try:
        next(folder_path.iterdir())
    except StopIteration:
        return True
    except OSError as error:
        print(f"Could not inspect {folder_path}: {error}")

    return False


def create_template_subfolders(
    project_folder: Path,
    template_subpaths: list[tuple[str, ...]],
) -> int:
    project_root = project_folder.resolve()
    created_count = 0

    for subpath in template_subpaths:
        target_path = project_folder.joinpath(*subpath).resolve()

        try:
            target_path.relative_to(project_root)
        except ValueError:
            print(f"Blocked unsafe target path: {'/'.join(subpath)}")
            continue

        if target_path.exists() and not target_path.is_dir():
            print(f"Blocked file at template path: {target_path}")
            continue

        if not target_path.is_dir():
            target_path.mkdir(parents=True, exist_ok=True)
            created_count += 1
            print(f"Created folder: {target_path}")

    return created_count


def initialize_empty_projects(
    applications_path: Path,
    template_subpaths: list[tuple[str, ...]],
) -> tuple[int, int, int]:
    initialized_count = 0
    created_count = 0
    skipped_count = 0

    for project_folder in sorted(
        applications_path.iterdir(),
        key=lambda path: path.name.casefold(),
    ):
        if not project_folder.is_dir() or project_folder.is_symlink():
            continue

        if not is_empty_directory(project_folder):
            skipped_count += 1
            continue

        initialized_count += 1
        print(f"Initializing empty application project: {project_folder}")
        created_count += create_template_subfolders(
            project_folder,
            template_subpaths,
        )

    return initialized_count, created_count, skipped_count


def main() -> int:
    project_root_path = find_project_root()
    database_file = (
        project_root_path
        / "resources"
        / "organization"
        / "devbox_db.r0b"
    )

    if not database_file.is_file():
        print(f"Database not found: {database_file}")
        return 1

    applications_path = find_applications_path(project_root_path)

    if applications_path is None:
        print("Applications directory not found. Nothing to initialize.")
        return 0

    connection = sqlite3.connect(database_file)

    try:
        template_subpaths = read_template_subpaths(connection)
    finally:
        connection.close()

    if not template_subpaths:
        print("No application template subfolders found. Nothing to initialize.")
        return 0

    initialized_count, created_count, skipped_count = initialize_empty_projects(
        applications_path,
        template_subpaths,
    )

    print("Empty application project initialization completed.")
    print(f"Template subfolders: {len(template_subpaths)}")
    print(f"Initialized projects: {initialized_count}")
    print(f"Created subfolders: {created_count}")
    print(f"Skipped non-empty projects: {skipped_count}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(
            "Empty application project initialization failed: "
            f"{type(error).__name__}: {error}"
        )
        sys.exit(1)
