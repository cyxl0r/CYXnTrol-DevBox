from __future__ import annotations

from subscripts.main_gui_devbox_log import get_devbox_logger
LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")


import json
from dataclasses import dataclass
from pathlib import Path

from subscripts.main_gui_documentation_exchange import (
    DocumentationExchangeError,
    create_temp_workspace,
    document_product_key,
    open_explorer_and_select_file,
    output_snapshot_directory,
    provider_timestamp,
    remove_path,
    validate_document_field_name,
    write_zip,
)
from subscripts.main_gui_documentation_store import (
    database_file,
    open_connection,
    read_columns,
    read_document_row,
    resolve_document_table,
    value_to_text,
)


@dataclass(frozen=True)
class DocumentationSnapshotResult:
    archive_file: Path
    product_name: str
    product_key: str
    snapshot_timestamp: str


def export_documentation_snapshot(
    project_root_path: Path,
    product_name: str,
) -> DocumentationSnapshotResult:
    project_root_path = Path(project_root_path).resolve()
    product_name = str(product_name).strip()
    if not product_name:
        raise DocumentationExchangeError("Kein Produkt für den Dokumentations-Snapshot ausgewählt.")

    db_file = database_file(project_root_path)
    if not db_file.is_file():
        raise DocumentationExchangeError(f"Datenbank nicht gefunden: {db_file}")

    product_key = document_product_key(product_name)
    timestamp = provider_timestamp(project_root_path)
    workspace = create_temp_workspace(project_root_path)

    try:
        de_values, en_values, fields = read_documentation_values(db_file, product_name)
        write_snapshot_contents(
            workspace,
            product_name,
            product_key,
            timestamp,
            fields,
            de_values,
            en_values,
        )
        archive_file = output_snapshot_directory() / (
            f"{product_key}_documentation_snapshot_{timestamp}.zip"
        )
        write_zip(workspace, archive_file)
        open_explorer_and_select_file(archive_file)
        return DocumentationSnapshotResult(
            archive_file=archive_file,
            product_name=product_name,
            product_key=product_key,
            snapshot_timestamp=timestamp,
        )
    finally:
        remove_path(workspace)


def read_documentation_values(
    db_file: Path,
    product_name: str,
) -> tuple[dict[str, object], dict[str, object], list[str]]:
    connection = open_connection(db_file)
    try:
        de_table = resolve_document_table(connection, product_name, "de")
        en_table = resolve_document_table(connection, product_name, "en")
        if de_table is None or en_table is None:
            raise DocumentationExchangeError("Die deutschen oder englischen Dokumentationstabellen fehlen.")

        de_fields = read_columns(connection, de_table)
        en_fields = read_columns(connection, en_table)
        if de_fields != en_fields:
            raise DocumentationExchangeError(
                "Die deutsche und englische Dokumenttabellenstruktur ist nicht identisch."
            )
        fields = [validate_document_field_name(field) for field in de_fields]
        _, de_values = read_document_row(connection, de_table)
        _, en_values = read_document_row(connection, en_table)
        return de_values, en_values, fields
    finally:
        connection.close()


def write_snapshot_contents(
    workspace: Path,
    product_name: str,
    product_key: str,
    timestamp: str,
    fields: list[str],
    de_values: dict[str, object],
    en_values: dict[str, object],
) -> None:
    for language, values in (("de", de_values), ("en", en_values)):
        language_dir = workspace / language
        language_dir.mkdir(parents=True, exist_ok=False)
        for field in fields:
            (language_dir / f"{field}.txt").write_text(
                value_to_text(values.get(field)),
                encoding="utf-8",
            )

    manifest = {
        "schema_version": 1,
        "snapshot_kind": "documentation_snapshot",
        "product_name": product_name,
        "product_key": product_key,
        "snapshot_timestamp": timestamp,
        "document_fields": fields,
        "languages": ["de", "en"],
    }
    (workspace / "documentation_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    result_name = f"{product_key}_documentation_result_{timestamp}.zip"
    order_text = (
        "# ChatGPT Order\n\n"
        f"This is the documentation snapshot for product: {product_name}\n\n"
        "Every TXT file in `de/` and `en/` requires a complete text update. "
        "Fill or revise every document field in the respective language.\n\n"
        "Do not rename, delete, add, or move files and folders. "
        "Do not modify `documentation_manifest.json`.\n\n"
        "Package the complete unchanged folder structure into exactly one ZIP archive.\n\n"
        f"Required ZIP filename: `{result_name}`\n"
    )
    (workspace / "chatgpt_order.md").write_text(order_text, encoding="utf-8")
