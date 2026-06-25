from __future__ import annotations

import sqlite3
from pathlib import Path

from subscripts.main_gui_devbox_log import get_devbox_logger
from subscripts.push_to_git_schema_devbox_pdf import create_legal_pdfs


MODULE_LOGGER = get_devbox_logger(__file__)
MODULE_LOGGER.info("Module loaded.")


FORM_FILES = (
    "LICENSE_FORM_DE.txt", "README_FORM_DE.txt", "ARCHITECTURE_FORM_DE.txt",
    "RULES_CATALOG_FORM_DE.txt", "TODO_LIST_FORM_DE.txt", "TERMS_OF_USE_FORM_DE.txt",
    "PRIVACY_POLICY_FORM_DE.txt", "LICENSE_FORM_EN.txt", "README_FORM_EN.txt",
    "ARCHITECTURE_FORM_EN.txt", "RULES_CATALOG_FORM_EN.txt", "TODO_LIST_FORM_EN.txt",
    "TERMS_OF_USE_FORM_EN.txt", "PRIVACY_POLICY_FORM_EN.txt",
)


def _as_text(value: object) -> str:
    return "" if value is None or isinstance(value, bytes) else str(value)


def _year(value: object) -> str:
    text = _as_text(value)
    for index in range(max(0, len(text) - 3)):
        candidate = text[index:index + 4]
        if candidate.isdigit():
            return candidate
    return text


def _quote(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def _first_row(connection: sqlite3.Connection, table_name: str) -> dict[str, object]:
    row = connection.execute(f"SELECT * FROM {_quote(table_name)} LIMIT 1").fetchone()
    return dict(row) if row is not None else {}


def _manufacturer(connection: sqlite3.Connection) -> dict[str, object]:
    try:
        row = connection.execute(
            '''SELECT * FROM "manufacturer_credentials"
               WHERE "manufacturer_name" IS NULL OR "manufacturer_name" != ? LIMIT 1''',
            ("__devbox_internal_key__",),
        ).fetchone()
    except sqlite3.OperationalError:
        return {}
    return dict(row) if row is not None else {}


def _product(connection: sqlite3.Connection) -> dict[str, object]:
    row = connection.execute(
        '''SELECT * FROM "product_credentials"
           WHERE LOWER(COALESCE("product_slug", "")) = "devbox"
              OR LOWER(COALESCE("product_name", "")) = "devbox" LIMIT 1'''
    ).fetchone()
    if row is None:
        raise LookupError("DevBox product data was not found.")
    return dict(row)


def _document_row(connection: sqlite3.Connection, language: str) -> dict[str, object]:
    return _first_row(connection, f"devbox_document_credentials_{language}")


def _fill_file(file_path: Path, values: dict[str, str]) -> None:
    if not file_path.is_file():
        raise FileNotFoundError(f"Document form not found: {file_path.name}")
    text = file_path.read_text(encoding="utf-8")
    for name, value in values.items():
        text = text.replace(f"{{{{{name}}}}}", value)
    file_path.write_text(text, encoding="utf-8")


def _placeholders(product: dict[str, object], manufacturer: dict[str, object], document: dict[str, object]) -> dict[str, str]:
    value = lambda row, name: _as_text(row.get(name))
    result = {
        "LICENSE_NAME": value(product, "license_name"), "LICENSE_VERSION": value(product, "license_version"),
        "AUTHOR_NAME": value(manufacturer, "author_name") or value(product, "author"),
        "AUTHOR_DISPLAY_NAME": value(manufacturer, "author_display_name") or value(product, "author"),
        "COPYRIGHT_YEAR": value(product, "copyright_year"), "PUBLICATION_YEAR": _year(product.get("release_date")),
        "PROJECT_START_YEAR": _year(product.get("programming_start")),
        "COUNTRY": value(manufacturer, "country") or value(product, "country"),
        "COUNTRY_CODE": value(manufacturer, "country_code") or value(product, "country_code"),
    }
    mapping = {
        "short_description": "PROJECT_SHORT_DESCRIPTION", "long_description": "PROJECT_LONG_DESCRIPTION",
        "purpose": "PROJECT_PURPOSE", "context": "PROJECT_CONTEXT", "core_idea": "PROJECT_CORE_IDEA",
        "features_and_goals": "PROJECT_FEATURES_AND_GOALS", "architecture_overview": "PROJECT_ARCHITECTURE_OVERVIEW",
        "architecture": "PROJECT_ARCHITECTURE", "rules_catalog": "PROJECT_RULES_CATALOG", "status": "PROJECT_STATUS",
        "installation_and_start": "PROJECT_INSTALLATION_AND_START", "configuration": "PROJECT_CONFIGURATION",
        "technology": "PROJECT_TECHNOLOGY", "repository_note": "PROJECT_REPOSITORY_NOTE",
        "terms_of_use": "PROJECT_TERMS_OF_USE", "privacy_policy": "PROJECT_PRIVACY_POLICY",
        "todo_list": "PROJECT_TODO_LIST",
    }
    result.update({placeholder: value(document, column) for column, placeholder in mapping.items()})
    return result


def _copy_file(source: Path, target: Path, required: bool) -> None:
    if source.is_file():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
        return
    if target.exists():
        target.unlink()
    if required:
        raise FileNotFoundError(f"Required document was not created: {source.name}")


def _publish_outputs(context) -> None:
    root_jobs = (("README_FORM_EN.txt", "readme.md"), ("README_FORM_DE.txt", "readme_de.md"), ("LICENSE_FORM_EN.txt", "license.md"), ("LICENSE_FORM_DE.txt", "license_de.md"))
    document_jobs = (
        ("ARCHITECTURE_FORM_EN.txt", "en_architecture.md", True), ("ARCHITECTURE_FORM_DE.txt", "de_architektur.md", True),
        ("RULES_CATALOG_FORM_EN.txt", "en_rules_catalog.md", True), ("RULES_CATALOG_FORM_DE.txt", "de_regelkatalog.md", True),
        ("TODO_LIST_FORM_EN.txt", "en_todo_list.md", True), ("TODO_LIST_FORM_DE.txt", "de_todo_liste.md", True),
        ("TERMS_OF_USE_EN.pdf", "en_terms_of_use.pdf", False), ("TERMS_OF_USE_DE.pdf", "de_nutzungsbedingungen.pdf", False),
        ("PRIVACY_POLICY_EN.pdf", "en_privacy_policy.pdf", False), ("PRIVACY_POLICY_DE.pdf", "de_datenschutzbestimmungen.pdf", False),
    )
    for source_name, target_name in root_jobs:
        _copy_file(context.docs_path / source_name, context.root_dir / target_name, True)
    for source_name, target_name, required in document_jobs:
        _copy_file(context.docs_path / source_name, context.documents_path / target_name, required)


def build_documents(context, reporter) -> None:
    if not context.database_file.is_file():
        raise FileNotFoundError(f"DevBox database not found: {context.database_file}")
    connection = sqlite3.connect(context.database_file)
    connection.row_factory = sqlite3.Row
    try:
        product = _product(connection)
        manufacturer = _manufacturer(connection)
        german = _placeholders(product, manufacturer, _document_row(connection, "de"))
        english = _placeholders(product, manufacturer, _document_row(connection, "en"))
        for file_name in FORM_FILES:
            _fill_file(context.docs_path / file_name, german if file_name.endswith("_DE.txt") else english)
        create_legal_pdfs(context, _document_row(connection, "de"), _document_row(connection, "en"), reporter)
        _publish_outputs(context)
        reporter.info("Documentation and legal files prepared for publish root.")
    finally:
        connection.close()
    context.database_file.unlink(missing_ok=True)
