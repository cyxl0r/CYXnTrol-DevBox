from __future__ import annotations

from subscripts.main_gui_devbox_log import get_devbox_logger
LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")


import json
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path

from subscripts.main_gui_documentation_exchange import (
    DocumentationExchangeError,
    archive_member_path,
    create_temp_workspace,
    document_product_key,
    downloads_directory,
    is_zip_symlink,
    remove_path,
    validate_document_field_name,
)
from subscripts.main_gui_documentation_store import (
    database_file,
    insert_or_update_row,
    open_connection,
    read_columns,
    read_document_row,
    resolve_document_table,
)


RESULT_NAME_PATTERN = re.compile(
    r"^(?P<product_key>[a-z0-9][a-z0-9_-]*)_documentation_result_"
    r"(?P<timestamp>[A-Za-z0-9_-]+)\.zip$",
    re.IGNORECASE,
)
MAX_ARCHIVE_MEMBERS = 256
MAX_MEMBER_BYTES = 2 * 1024 * 1024


@dataclass(frozen=True)
class DocumentationImportResult:
    product_name: str
    result_file: Path
    result_deleted: bool


def find_latest_documentation_result() -> Path | None:
    downloads_path = downloads_directory()
    if not downloads_path.is_dir():
        return None

    candidates = [
        path
        for path in downloads_path.iterdir()
        if path.is_file() and RESULT_NAME_PATTERN.fullmatch(path.name)
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda path: (path.stat().st_mtime_ns, path.name.lower()))


def implement_latest_documentation_result(project_root_path: Path) -> DocumentationImportResult:
    result_file = find_latest_documentation_result()
    if result_file is None:
        raise DocumentationExchangeError("In Downloads wurde keine Dokumentations-Result-ZIP gefunden.")
    return implement_documentation_result(project_root_path, result_file)


def implement_documentation_result(
    project_root_path: Path,
    result_file: Path,
) -> DocumentationImportResult:
    project_root_path = Path(project_root_path).resolve()
    result_file = Path(result_file).resolve()
    match = RESULT_NAME_PATTERN.fullmatch(result_file.name)
    if match is None:
        raise DocumentationExchangeError("Die ausgewählte Datei entspricht keinem Dokumentations-Result-Schema.")
    if not result_file.is_file():
        raise DocumentationExchangeError(f"Result-ZIP nicht gefunden: {result_file}")

    workspace = create_temp_workspace(project_root_path)
    try:
        extract_result_archive(result_file, workspace)
        manifest = read_manifest(workspace)
        validate_result_identity(manifest, match.group("product_key"), match.group("timestamp"))
        product_name = str(manifest["product_name"])
        values_by_language = read_result_texts(workspace, manifest)
        write_result_to_database(project_root_path, product_name, values_by_language, manifest)
    except Exception:
        raise
    finally:
        remove_path(workspace)

    deleted = remove_path(result_file)
    return DocumentationImportResult(
        product_name=product_name,
        result_file=result_file,
        result_deleted=deleted,
    )


def extract_result_archive(result_file: Path, workspace: Path) -> None:
    try:
        with zipfile.ZipFile(result_file, "r") as archive:
            infos = archive.infolist()
            if not infos or len(infos) > MAX_ARCHIVE_MEMBERS:
                raise DocumentationExchangeError("Result-ZIP enthält eine ungültige Anzahl an Dateien.")

            names: set[str] = set()
            for info in infos:
                if info.is_dir():
                    continue
                if info.file_size > MAX_MEMBER_BYTES or info.compress_size > MAX_MEMBER_BYTES:
                    raise DocumentationExchangeError(f"ZIP-Datei ist zu groß: {info.filename}")
                if is_zip_symlink(info):
                    raise DocumentationExchangeError(f"ZIP enthält nicht erlaubten Symlink: {info.filename}")
                member_path = archive_member_path(info.filename)
                normalized_name = member_path.as_posix()
                if normalized_name in names:
                    raise DocumentationExchangeError(f"ZIP enthält eine doppelte Datei: {normalized_name}")
                names.add(normalized_name)
                target_file = workspace.joinpath(*member_path.parts)
                target_file.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(info, "r") as source, target_file.open("wb") as target:
                    target.write(source.read())
    except zipfile.BadZipFile as exc:
        raise DocumentationExchangeError("Result-Datei ist keine gültige ZIP-Datei.") from exc


def read_manifest(workspace: Path) -> dict[str, object]:
    manifest_file = workspace / "documentation_manifest.json"
    if not manifest_file.is_file():
        raise DocumentationExchangeError("documentation_manifest.json fehlt im Result-ZIP.")
    try:
        manifest = json.loads(manifest_file.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        raise DocumentationExchangeError(f"Manifest kann nicht gelesen werden: {exc}") from exc
    if not isinstance(manifest, dict):
        raise DocumentationExchangeError("Manifest hat kein gültiges Objektformat.")
    return manifest


def validate_result_identity(manifest: dict[str, object], product_key: str, timestamp: str) -> None:
    required_values = {
        "schema_version": 1,
        "snapshot_kind": "documentation_snapshot",
        "product_key": product_key,
        "snapshot_timestamp": timestamp,
    }
    for field, expected_value in required_values.items():
        if manifest.get(field) != expected_value:
            raise DocumentationExchangeError(
                f"Result-ZIP stimmt bei {field!r} nicht mit seinem Dateinamen überein."
            )

    product_name = str(manifest.get("product_name") or "").strip()
    if not product_name or document_product_key(product_name) != product_key.lower():
        raise DocumentationExchangeError("Produktname im Manifest passt nicht zum Dokumentationsschlüssel.")

    fields = manifest.get("document_fields")
    if not isinstance(fields, list) or not fields:
        raise DocumentationExchangeError("Manifest enthält keine Dokumentfelder.")
    normalized_fields = [validate_document_field_name(str(field)) for field in fields]
    if len(set(normalized_fields)) != len(normalized_fields):
        raise DocumentationExchangeError("Manifest enthält doppelte Dokumentfelder.")

    if manifest.get("languages") != ["de", "en"]:
        raise DocumentationExchangeError("Manifest enthält keine gültige Sprachreihenfolge.")


def read_result_texts(workspace: Path, manifest: dict[str, object]) -> dict[str, dict[str, str]]:
    fields = [str(field) for field in manifest["document_fields"]]
    expected_files = {
        f"{language}/{field}.txt"
        for language in ("de", "en")
        for field in fields
    }
    actual_files = {
        file.relative_to(workspace).as_posix()
        for file in workspace.rglob("*")
        if file.is_file() and file.relative_to(workspace).parts[0] in {"de", "en"}
    }
    if actual_files != expected_files:
        missing = sorted(expected_files - actual_files)
        unexpected = sorted(actual_files - expected_files)
        details = []
        if missing:
            details.append("fehlend: " + ", ".join(missing))
        if unexpected:
            details.append("unerwartet: " + ", ".join(unexpected))
        raise DocumentationExchangeError("Dokumentdateien passen nicht zum Manifest (" + "; ".join(details) + ").")

    result: dict[str, dict[str, str]] = {}
    for language in ("de", "en"):
        language_values: dict[str, str] = {}
        for field in fields:
            text_file = workspace / language / f"{field}.txt"
            try:
                language_values[field] = text_file.read_text(encoding="utf-8-sig")
            except Exception as exc:
                raise DocumentationExchangeError(
                    f"Textdatei kann nicht gelesen werden: {language}/{field}.txt | {exc}"
                ) from exc
        result[language] = language_values
    return result


def write_result_to_database(
    project_root_path: Path,
    product_name: str,
    values_by_language: dict[str, dict[str, str]],
    manifest: dict[str, object],
) -> None:
    db_file = database_file(project_root_path)
    if not db_file.is_file():
        raise DocumentationExchangeError(f"Datenbank nicht gefunden: {db_file}")

    expected_fields = [str(field) for field in manifest["document_fields"]]
    connection = open_connection(db_file)
    try:
        product_exists = connection.execute(
            'SELECT 1 FROM "product_credentials" WHERE "product_name" = ? LIMIT 1',
            (product_name,),
        ).fetchone()
        if product_exists is None:
            raise DocumentationExchangeError(f"Produkt aus Result-ZIP existiert nicht: {product_name}")

        tables = {
            language: resolve_document_table(connection, product_name, language)
            for language in ("de", "en")
        }
        if any(table_name is None for table_name in tables.values()):
            raise DocumentationExchangeError("Die Dokumentationstabellen des Produkts fehlen.")

        for language, table_name in tables.items():
            assert table_name is not None
            current_fields = read_columns(connection, table_name)
            if current_fields != expected_fields:
                raise DocumentationExchangeError(
                    f"Dokumentschema stimmt für {language} nicht mit dem Result-ZIP überein."
                )

        connection.execute("BEGIN")
        for language, table_name in tables.items():
            assert table_name is not None
            rowid, _ = read_document_row(connection, table_name)
            insert_or_update_row(connection, table_name, rowid, values_by_language[language])
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
