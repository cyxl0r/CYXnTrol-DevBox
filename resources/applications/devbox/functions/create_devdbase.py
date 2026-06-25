from pathlib import Path
import importlib.util
import os
import shutil
import sqlite3
import sys
import tempfile


def find_project_root() -> Path:
    home_path = Path(__file__).resolve().parent
    os.chdir(home_path)
    current_path = home_path

    while True:
        root_file = current_path / ".root"

        if root_file.is_file():
            content = root_file.read_text(encoding="utf-8").strip()

            if content == "project-root":
                return current_path

        parent_path = current_path.parent

        if parent_path == current_path:
            print("No project root found.")
            sys.exit(0)

        current_path = parent_path
        os.chdir(current_path)


def add_subscript_path(projekt_root_path: Path) -> Path:
    devbox_path = (
        projekt_root_path
        / "resources"
        / "applications"
        / "devbox"
    )
    subscript_path = devbox_path / "subscripts"

    if not subscript_path.is_dir():
        print(f"DevBox subscript folder not found: {subscript_path}")
        sys.exit(1)

    for required_path in (subscript_path, devbox_path):
        required_path_text = str(required_path)

        while required_path_text in sys.path:
            sys.path.remove(required_path_text)

        sys.path.insert(0, required_path_text)

    return subscript_path


def load_module_from_path(module_name: str, module_path: Path):
    if not module_path.is_file():
        print(f"Module not found: {module_path}")
        sys.exit(1)

    spec = importlib.util.spec_from_file_location(module_name, module_path)

    if spec is None or spec.loader is None:
        print(f"Could not load module: {module_path}")
        sys.exit(1)

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def create_temp_path(projekt_root_path: Path) -> Path:
    provider_file = (
        projekt_root_path
        / "platform"
        / "tools"
        / "random_string_provider.py"
    )
    provider = load_module_from_path("random_string_provider", provider_file)
    random_string = provider.generate_string(length=128, variant=1)
    return Path(tempfile.gettempdir()) / random_string


def print_summary(
    projekt_root_path: Path,
    temp_path: Path,
    database_file: Path,
    applications_path: Path,
    database_was_created: bool,
    application_folders: list[Path],
    table_names: list[str],
) -> None:
    print(f"projekt_root_path: {projekt_root_path}")
    print(f"temp_path: {temp_path}")
    print(f"database_file: {database_file}")
    print(f"applications_path: {applications_path}")
    print(f"database_was_created: {database_was_created}")
    print("application_folders:")

    for folder_path in application_folders:
        print(f"- {folder_path}")

    print("table_names:")

    for table_name in table_names:
        print(f"- {table_name}")


def main() -> int:
    projekt_root_path = find_project_root()
    add_subscript_path(projekt_root_path)

    from create_devdbase_folder_structure import sync_folder_structure_tables
    from main_gui_metadata_defaults import (
        sync_manufacturer_defaults,
        sync_product_defaults,
    )
    from create_devdbase_key_store import generate_and_store_manufacturer_key
    from create_devdbase_product_seed import seed_initial_product
    from create_devdbase_runtime import remove_dir_until_gone
    from create_devdbase_schema import (
        drop_orphaned_document_table_pairs,
        sync_document_table_pair,
        sync_table_schema,
    )
    from create_devdbase_sources import (
        get_application_document_table_names,
        read_credentials_tables,
        safe_extract_zip,
    )

    temp_path = create_temp_path(projekt_root_path)
    table_suffix = "document_credentials"
    dvb_table = f"devbox_{table_suffix}"
    database_file = (
        projekt_root_path
        / "resources"
        / "organization"
        / "devbox_db.r0b"
    )
    database_was_created = not database_file.is_file()
    applications_path = projekt_root_path / "applications"
    roof_credentials_file = (
        projekt_root_path
        / "resources"
        / "organization"
        / "roof_credentials.r0b"
    )

    try:
        table_credentials_path = temp_path / "table_credentials"
        table_credentials_path.mkdir(parents=True, exist_ok=True)
        credentials_zip_file = temp_path / "credentials.zip"

        if not roof_credentials_file.is_file():
            print(f"roof_credentials.r0b not found: {roof_credentials_file}")
            return 1

        shutil.copy2(src=roof_credentials_file, dst=credentials_zip_file)
        safe_extract_zip(credentials_zip_file, table_credentials_path)
        xl_file = table_credentials_path / "credentials.xlsx"

        if not xl_file.is_file():
            print(f"credentials.xlsx not found after extraction: {xl_file}")
            return 1

        m_table_name, p_table_name, _d_table_name, m_t, p_t, d_t = read_credentials_tables(xl_file)
        database_file.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(database_file)
        connection.row_factory = sqlite3.Row

        try:
            manufacturer_table_was_created = sync_table_schema(
                connection=connection,
                table_name=m_table_name,
                memory_table=m_t,
            )
            generate_and_store_manufacturer_key(
                connection=connection,
                manufacturer_table_name=m_table_name,
            )

            if manufacturer_table_was_created:
                print(
                    f"Manufacturer table was created and internal key "
                    f"was initialized: {m_table_name}"
                )

            sync_table_schema(
                connection=connection,
                table_name=p_table_name,
                memory_table=p_t,
            )

            manufacturer_default_count = sync_manufacturer_defaults(connection)
            product_default_count = sync_product_defaults(
                connection=connection,
                project_root_path=projekt_root_path,
            )

            if manufacturer_default_count:
                print("Manufacturer automatic defaults synchronized.")

            if product_default_count:
                print(f"Product automatic defaults synchronized: {product_default_count}")

            seed_result = seed_initial_product(
                connection=connection,
                product_table_name=p_table_name,
                projekt_root_path=projekt_root_path,
                database_was_created=database_was_created,
            )

            if seed_result.seeded:
                print(
                    f"Initial DevBox product seeded: "
                    f"{seed_result.product_display_name}"
                )
            else:
                print(f"Initial DevBox product seed skipped: {seed_result.reason}")

            error_level, table_names, application_folders = (
                get_application_document_table_names(
                    applications_path=applications_path,
                    table_suffix=table_suffix,
                )
            )

            sync_document_table_pair(connection, dvb_table, d_t)

            for table_name in table_names:
                sync_document_table_pair(connection, table_name, d_t)

            sync_folder_structure_tables(
                connection=connection,
                projekt_root_path=projekt_root_path,
                applications_path=applications_path,
            )

            if applications_path.is_dir():
                dropped_tables = drop_orphaned_document_table_pairs(
                    connection=connection,
                    expected_base_table_names=table_names,
                    table_suffix=table_suffix,
                    protected_base_table_names=[dvb_table],
                )

                for dropped_table in dropped_tables:
                    print(f"Dropped orphaned document table: {dropped_table}")

                if not dropped_tables:
                    print("No orphaned document tables found.")
            else:
                print(
                    "Applications folder not found. "
                    "Orphaned document tables were not removed."
                )

            connection.commit()
        finally:
            connection.close()

        print_summary(
            projekt_root_path=projekt_root_path,
            temp_path=temp_path,
            database_file=database_file,
            applications_path=applications_path,
            database_was_created=database_was_created,
            application_folders=application_folders,
            table_names=table_names,
        )
        print(f"error_level: {error_level}")
        return 0
    finally:
        if temp_path.exists():
            remove_dir_until_gone(temp_path)


if __name__ == "__main__":
    sys.exit(main())
