from __future__ import annotations

from subscripts.main_gui_devbox_log import get_devbox_logger
LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")


import sqlite3
import subprocess
import sys
import time
from pathlib import Path


TABLE_NAME = "product_credentials"
KEY_TABLE_NAME = "manufacturer_credentials"
EXCLUDED_COLUMNS = {
    "devbox_key_id",
    "devbox_key_payload",
    "devbox_key_created_at",
    "devbox_key_algorithm",
}
BASIC_COLUMNS = {
    "product_id", "product_name", "product_display_name",
    "product_short_name", "product_slug", "product_code_name",
    "product_family", "product_type", "product_description_short",
    "product_description_long", "programming_start", "release_date",
    "release_version", "build_number", "version_major", "version_minor",
    "version_patch", "version_suffix", "author", "publisher", "vendor",
    "copyright_holder", "copyright_year", "license_name", "license_version",
    "license_url", "country", "country_code", "language", "default_locale",
    "target_operating_systems", "created_at", "updated_at", "active", "deprecated", "internal_notes",
    "public_notes",
}
PREFIX_LABELS = [
    ("repository_", "Repository"),
    ("homepage_", "Web / Support"),
    ("download_", "Web / Support"),
    ("support_", "Web / Support"),
    ("documentation_", "Web / Support"),
    ("changelog_", "Web / Support"),
    ("privacy_", "Web / Support"),
    ("terms_", "Web / Support"),
    ("windows_", "Windows"),
    ("macos_", "macOS"),
    ("ios_", "iOS"),
    ("android_", "Android"),
    ("linux_", "Linux"),
    ("debian_", "Debian"),
    ("raspberrypi_", "Raspberry Pi"),
    ("docker", "Docker / Container"),
    ("container_", "Docker / Container"),
    ("proxmox_", "Proxmox"),
    ("qnap_", "QNAP"),
    ("synology_", "Synology"),
    ("update_", "Update / Keys"),
    ("api_", "API / Secrets"),
    ("oauth_", "API / Secrets"),
    ("service_account_", "API / Secrets"),
    ("encryption_", "API / Secrets"),
    ("public_key", "API / Secrets"),
    ("private_key", "API / Secrets"),
    ("secret_key", "API / Secrets"),
    ("signing_", "API / Secrets"),
    ("store_", "Store Listing"),
]


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def utc_timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def label_from_column(column_name: str) -> str:
    return column_name.replace("_", " ").strip().title()


def group_for_column(column_name: str) -> str:
    if column_name in BASIC_COLUMNS:
        return "Basisdaten"
    for prefix, label in PREFIX_LABELS:
        if column_name.startswith(prefix):
            return label
    return "Weitere Daten"


def group_order() -> list[str]:
    result = ["Basisdaten"]
    for _, label in PREFIX_LABELS:
        if label not in result:
            result.append(label)
    result.append("Weitere Daten")
    return result


def database_file(project_root_path: Path) -> Path:
    return Path(project_root_path) / "resources" / "organization" / "devbox_db.r0b"



def create_product_folder(project_root_path: Path, product_name: str) -> Path:
    folder_name = str(product_name).strip()
    if folder_name in {"", ".", ".."}:
        raise ValueError("Produktordnername ist leer oder ungültig.")
    for char in '<>:"/\\|?*':
        if char in folder_name:
            raise ValueError(f"Ungültiges Zeichen im Produktordnernamen: {char}")
    applications_path = Path(project_root_path) / "applications"
    target_path = applications_path / folder_name
    root_path = Path(project_root_path).resolve()
    resolved_target = target_path.resolve()
    try:
        resolved_target.relative_to(root_path)
    except ValueError as exc:
        raise ValueError("Produktordner liegt außerhalb des Projektroots.") from exc
    if resolved_target.exists() and not resolved_target.is_dir():
        raise ValueError(f"Pfad existiert bereits und ist kein Ordner: {resolved_target}")
    resolved_target.mkdir(parents=True, exist_ok=True)
    return resolved_target


def python_executable() -> Path:
    executable = Path(sys.executable)
    if executable.name.lower() == "pythonw.exe":
        python_exe = executable.with_name("python.exe")
        if python_exe.is_file():
            return python_exe
    return executable


def run_devenv_db_fld_updtr(project_root_path: Path) -> int:
    script_file = Path(project_root_path) / "resources" / "applications" / "devbox" / "functions" / "devenv_db_fld_updtr.py"
    if not script_file.is_file():
        return -1
    process = subprocess.run([str(python_executable()), str(script_file)], cwd=str(script_file.parent))
    return int(process.returncode)


def create_product_with_folder(connection: sqlite3.Connection, project_root_path: Path, product_name: str, values: dict[str, object]) -> tuple[int, Path, int]:
    rowid = insert_row(connection, values)
    product_folder = create_product_folder(project_root_path, product_name)
    connection.commit()
    updater_code = run_devenv_db_fld_updtr(project_root_path)
    return rowid, product_folder, updater_code

def open_connection(db_file: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(db_file)
    connection.row_factory = sqlite3.Row
    return connection


def table_exists(connection: sqlite3.Connection, table_name: str) -> bool:
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


def read_columns(connection: sqlite3.Connection) -> list[tuple[str, str]]:
    cursor = connection.execute(f"PRAGMA table_info({quote_identifier(TABLE_NAME)})")
    return [(str(row[1]), str(row[2]).upper()) for row in cursor.fetchall()]


def value_to_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return "verschlüsselt"
    return str(value)


def product_label(row: sqlite3.Row) -> str:
    for column in ("product_display_name", "product_name", "product_short_name", "product_slug"):
        if column in row.keys() and row[column]:
            return str(row[column])
    if "product_id" in row.keys() and row["product_id"] is not None:
        return f"Produkt {row['product_id']}"
    return f"Datensatz {row['rowid']}"


def list_products(connection: sqlite3.Connection) -> list[dict[str, object]]:
    cursor = connection.execute(
        f"""
        SELECT rowid, *
        FROM {quote_identifier(TABLE_NAME)}
        ORDER BY COALESCE({quote_identifier('product_display_name')},
                          {quote_identifier('product_name')},
                          {quote_identifier('product_short_name')},
                          {quote_identifier('product_slug')},
                          CAST({quote_identifier('product_id')} AS TEXT),
                          CAST(rowid AS TEXT)) ASC
        """
    )
    rows = cursor.fetchall()
    return [{"rowid": int(row["rowid"]), "label": product_label(row)} for row in rows]


def read_row_values(connection: sqlite3.Connection, rowid: int | None) -> dict[str, object]:
    if rowid is None:
        return {}
    cursor = connection.execute(
        f"SELECT * FROM {quote_identifier(TABLE_NAME)} WHERE rowid = ?",
        (rowid,),
    )
    row = cursor.fetchone()
    return {} if row is None else dict(row)


def next_product_id(connection: sqlite3.Connection) -> int:
    cursor = connection.execute(
        f"""
        SELECT MAX(CAST({quote_identifier('product_id')} AS INTEGER))
        FROM {quote_identifier(TABLE_NAME)}
        WHERE {quote_identifier('product_id')} IS NOT NULL
        """
    )
    row = cursor.fetchone()
    current_value = row[0] if row is not None else 0
    return 1 if current_value is None else max(1, int(current_value) + 1)


def insert_row(connection: sqlite3.Connection, values: dict[str, object]) -> int:
    columns = list(values.keys())
    column_sql = ", ".join(quote_identifier(column) for column in columns)
    placeholders = ", ".join("?" for _ in columns)
    cursor = connection.execute(
        f"""
        INSERT INTO {quote_identifier(TABLE_NAME)}
        ({column_sql})
        VALUES ({placeholders})
        """,
        [values[column] for column in columns],
    )
    return int(cursor.lastrowid)


def update_row(connection: sqlite3.Connection, rowid: int, values: dict[str, object]) -> None:
    if not values:
        return
    assignments = ", ".join(f"{quote_identifier(column)} = ?" for column in values)
    parameters = [values[column] for column in values]
    parameters.append(rowid)
    connection.execute(
        f"""
        UPDATE {quote_identifier(TABLE_NAME)}
        SET {assignments}
        WHERE rowid = ?
        """,
        parameters,
    )
