from __future__ import annotations

import re
import sqlite3
from pathlib import Path

from subscripts.push_to_git_schema_desknode_pdf import create_legal_pdfs


FORM_FILES = (
    "README_FORM_DE.txt", "ARCHITECTURE_FORM_DE.txt", "RULES_CATALOG_FORM_DE.txt", "TODO_LIST_FORM_DE.txt",
    "README_FORM_EN.txt", "ARCHITECTURE_FORM_EN.txt", "RULES_CATALOG_FORM_EN.txt", "TODO_LIST_FORM_EN.txt",
)
PRODUCT_SLUG = "desknode"


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
           WHERE LOWER(COALESCE("product_slug", "")) = ?
              OR LOWER(COALESCE("product_name", "")) = ? LIMIT 1''',
        (PRODUCT_SLUG, PRODUCT_SLUG),
    ).fetchone()
    if row is None:
        raise LookupError("deskNode product data was not found.")
    return dict(row)


def _document_row(connection: sqlite3.Connection, language: str) -> dict[str, object]:
    return _first_row(connection, f"desknode_document_credentials_{language}")


def _license_row(connection: sqlite3.Connection, language: str) -> dict[str, object]:
    record = _first_row(connection, f"desknode_license_credentials_{language}")
    if not _as_text(record.get("license_text_markdown")).strip():
        raise LookupError(f"deskNode {language} license text is missing.")
    return record


def _strip_leading_heading(value: str) -> str:
    lines = value.strip().splitlines()
    if len(lines) >= 2 and lines[0].strip() and re.fullmatch(r"[=-]{3,}", lines[1].strip()):
        return "\n".join(lines[2:]).lstrip()
    return value.strip()


def _public_repository_reference(value: str) -> str:
    replacements = (
        ("<repository_root>\\applications\\deskNode", "<repository_root>"),
        ("<repository_root>/applications/deskNode", "<repository_root>"),
        ("<projectroot>\\applications\\deskNode", "<repository_root>"),
        ("<projectroot>/applications/deskNode", "<repository_root>"),
        ("<projectroot>\\", "<repository_root>\\"),
        ("<projectroot>/", "<repository_root>/"),
    )
    result = value
    for source, target in replacements:
        result = result.replace(source, target)
    return result

def _public_document(document: dict[str, object]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in document.items():
        text = _as_text(value)
        if text:
            text = _public_repository_reference(text)
            text = _strip_leading_heading(text)
        result[key] = text
    return result


def _fill_file(file_path: Path, values: dict[str, str]) -> None:
    if not file_path.is_file():
        raise FileNotFoundError(f"Document form not found: {file_path.name}")
    text = file_path.read_text(encoding="utf-8")
    text = text.replace(
        "Copyright (c) {{COPYRIGHT_YEAR}} {{AUTHOR_NAME}}",
        "Copyright (c) {{COPYRIGHT_YEAR}} {{COPYRIGHT_HOLDER}}",
    )
    text = text.replace(
        "Document status: {{PROJECT_STATUS}}",
        "Document status: {{PROJECT_STATUS_SUMMARY}}",
    )
    text = text.replace(
        "Dokumentstand: {{PROJECT_STATUS}}",
        "Dokumentstand: {{PROJECT_STATUS_SUMMARY}}",
    )
    for name, value in values.items():
        text = text.replace(f"{{{{{name}}}}}", value)
    unresolved = sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}", text)))
    if unresolved:
        raise RuntimeError(f"Unresolved document placeholders in {file_path.name}: {', '.join(unresolved)}")
    file_path.write_text(text, encoding="utf-8", newline="\n")


def _placeholders(product: dict[str, object], manufacturer: dict[str, object], document: dict[str, object]) -> dict[str, str]:
    value = lambda row, name: _as_text(row.get(name))
    copyright_holder = value(product, "copyright_holder") or value(product, "publisher") or value(manufacturer, "publisher_name")
    author_name = value(manufacturer, "author_name") or value(product, "author")
    display_name = copyright_holder or value(manufacturer, "author_display_name") or author_name
    publication_year = (
        _year(product.get("release_date"))
        or _year(product.get("copyright_year"))
        or _year(product.get("programming_start"))
    )
    status_lines = [line.strip() for line in value(document, "status").splitlines() if line.strip()]
    status_summary = status_lines[0] if status_lines else ""
    for prefix in ("Development status:", "Entwicklungsstatus:"):
        if status_summary.startswith(prefix):
            status_summary = status_summary[len(prefix):].strip()
            break
    result = {
        "LICENSE_NAME": value(product, "license_name"),
        "LICENSE_VERSION": value(product, "license_version"),
        "AUTHOR_NAME": author_name,
        "AUTHOR_DISPLAY_NAME": display_name,
        "COPYRIGHT_HOLDER": copyright_holder or author_name,
        "COPYRIGHT_YEAR": value(product, "copyright_year"),
        "PUBLICATION_YEAR": publication_year,
        "PROJECT_START_YEAR": _year(product.get("programming_start")),
        "COUNTRY": value(manufacturer, "country") or value(product, "country"),
        "COUNTRY_CODE": value(manufacturer, "country_code") or value(product, "country_code"),
        "PROJECT_STATUS_SUMMARY": status_summary,
    }
    mapping = {
        "short_description": "PROJECT_SHORT_DESCRIPTION",
        "long_description": "PROJECT_LONG_DESCRIPTION",
        "purpose": "PROJECT_PURPOSE",
        "context": "PROJECT_CONTEXT",
        "core_idea": "PROJECT_CORE_IDEA",
        "features_and_goals": "PROJECT_FEATURES_AND_GOALS",
        "architecture_overview": "PROJECT_ARCHITECTURE_OVERVIEW",
        "architecture": "PROJECT_ARCHITECTURE",
        "rules_catalog": "PROJECT_RULES_CATALOG",
        "status": "PROJECT_STATUS",
        "installation_and_start": "PROJECT_INSTALLATION_AND_START",
        "configuration": "PROJECT_CONFIGURATION",
        "technology": "PROJECT_TECHNOLOGY",
        "repository_note": "PROJECT_REPOSITORY_NOTE",
        "terms_of_use": "PROJECT_TERMS_OF_USE",
        "privacy_policy": "PROJECT_PRIVACY_POLICY",
        "todo_list": "PROJECT_TODO_LIST",
    }
    result.update({placeholder: value(document, column) for column, placeholder in mapping.items()})
    return result


def _legal_metadata(product: dict[str, object], manufacturer: dict[str, object]) -> dict[str, str]:
    value = lambda row, name: _as_text(row.get(name))
    holder = value(product, "copyright_holder") or value(product, "publisher") or value(manufacturer, "publisher_name")
    publication_year = (
        _year(product.get("release_date"))
        or _year(product.get("copyright_year"))
        or _year(product.get("programming_start"))
    )
    return {
        "product_name": value(product, "product_display_name") or value(product, "product_name") or "deskNode",
        "publication_year": publication_year,
        "publisher": holder or value(manufacturer, "author_display_name") or value(product, "author"),
        "country": value(manufacturer, "country") or value(product, "country"),
        "country_code": value(manufacturer, "country_code") or value(product, "country_code"),
        "license_name": value(product, "license_name"),
        "license_version": value(product, "license_version"),
        "copyright_holder": holder,
        "copyright_year": value(product, "copyright_year"),
    }


def _copy_file(source: Path, target: Path, required: bool) -> None:
    if source.is_file():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
        return
    if target.exists():
        target.unlink()
    if required:
        raise FileNotFoundError(f"Required document was not created: {source.name}")


def _write_license(source: dict[str, object], target: Path) -> None:
    text = _as_text(source.get("license_text_markdown")).strip()
    if not text:
        raise RuntimeError("License text is empty.")
    target.write_text(text + "\n", encoding="utf-8", newline="\n")


def _publish_outputs(context) -> None:
    root_jobs = (
        ("README_FORM_EN.txt", "readme.md"),
        ("README_FORM_DE.txt", "readme_de.md"),
        ("LICENSE_EN.md", "license.md"),
        ("LICENSE_DE.md", "license_de.md"),
    )
    document_jobs = (
        ("ARCHITECTURE_FORM_EN.txt", "en_architecture.md", True),
        ("ARCHITECTURE_FORM_DE.txt", "de_architektur.md", True),
        ("RULES_CATALOG_FORM_EN.txt", "en_rules_catalog.md", True),
        ("RULES_CATALOG_FORM_DE.txt", "de_regelkatalog.md", True),
        ("TODO_LIST_FORM_EN.txt", "en_todo_list.md", True),
        ("TODO_LIST_FORM_DE.txt", "de_todo_liste.md", True),
        ("TERMS_OF_USE_EN.pdf", "en_terms_of_use.pdf", True),
        ("TERMS_OF_USE_DE.pdf", "de_nutzungsbedingungen.pdf", True),
        ("PRIVACY_POLICY_EN.pdf", "en_privacy_policy.pdf", True),
        ("PRIVACY_POLICY_DE.pdf", "de_datenschutzbestimmungen.pdf", True),
    )
    for source_name, target_name in root_jobs:
        _copy_file(context.docs_path / source_name, context.root_dir / target_name, True)
    for source_name, target_name, required in document_jobs:
        _copy_file(context.docs_path / source_name, context.documents_path / target_name, required)


def build_documents(context, reporter) -> None:
    if not context.source_database_file.is_file():
        raise FileNotFoundError(f"DevBox database not found: {context.source_database_file}")
    connection = sqlite3.connect(context.source_database_file)
    connection.row_factory = sqlite3.Row
    try:
        product = _product(connection)
        manufacturer = _manufacturer(connection)
        german_document = _public_document(_document_row(connection, "de"))
        english_document = _public_document(_document_row(connection, "en"))
        german_license = _license_row(connection, "de")
        english_license = _license_row(connection, "en")
        german = _placeholders(product, manufacturer, german_document)
        english = _placeholders(product, manufacturer, english_document)
        for file_name in FORM_FILES:
            _fill_file(
                context.docs_path / file_name,
                german if file_name.endswith("_DE.txt") else english,
            )
        _write_license(english_license, context.docs_path / "LICENSE_EN.md")
        _write_license(german_license, context.docs_path / "LICENSE_DE.md")
        create_legal_pdfs(
            context=context,
            german_document=german_document,
            english_document=english_document,
            metadata=_legal_metadata(product, manufacturer),
            reporter=reporter,
        )
        _publish_outputs(context)
        reporter.info("deskNode documentation and legal files prepared for publish root.")
    finally:
        connection.close()
