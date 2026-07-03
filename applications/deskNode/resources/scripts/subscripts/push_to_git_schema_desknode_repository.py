from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


PRODUCT_SLUG = "desknode"


@dataclass(frozen=True)
class RepositorySettings:
    url: str
    branch: str


def _find_product(connection: sqlite3.Connection) -> sqlite3.Row:
    connection.row_factory = sqlite3.Row
    row = connection.execute(
        '''
        SELECT rowid, * FROM "product_credentials"
        WHERE LOWER(COALESCE("product_slug", "")) = ?
           OR LOWER(COALESCE("product_name", "")) = ?
        LIMIT 1
        ''',
        (PRODUCT_SLUG, PRODUCT_SLUG),
    ).fetchone()
    if row is None:
        raise LookupError("deskNode product data was not found.")
    return row


def _request_settings(product_label: str) -> tuple[str, str]:
    from PySide6.QtWidgets import QApplication, QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QMessageBox

    _app = QApplication.instance() or QApplication([])
    dialog = QDialog()
    dialog.setWindowTitle("Repository-Verbindung einrichten")
    layout = QFormLayout(dialog)
    QMessageBox.information(
        dialog,
        "Repository-Verbindung fehlt",
        f'Für "{product_label}" sind noch keine Repository-Daten hinterlegt. '
        "Bitte geben Sie die Repository-URL und den Branch ein.",
    )
    url_field = QLineEdit()
    url_field.setPlaceholderText("https://... oder git@...")
    branch_field = QLineEdit("main")
    layout.addRow("Repository-URL", url_field)
    layout.addRow("Branch", branch_field)
    buttons = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
    )
    layout.addRow(buttons)
    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)
    if dialog.exec() != QDialog.DialogCode.Accepted:
        raise RuntimeError("Repository setup was cancelled by user.")
    url = url_field.text().strip()
    branch = branch_field.text().strip() or "main"
    if not url:
        raise ValueError("A repository URL is required.")
    return url, branch


def ensure_repository_settings(database_file: Path, reporter) -> RepositorySettings:
    if not database_file.is_file():
        raise FileNotFoundError(f"DevBox database not found: {database_file}")
    connection = sqlite3.connect(database_file)
    try:
        product = _find_product(connection)
        url = str(product["repository_url"] or "").strip()
        branch = str(product["repository_branch"] or "").strip() or "main"
        label = str(product["product_display_name"] or product["product_name"] or "deskNode")
        if not url:
            reporter.warning("Repository data missing; setup dialog requested.", label)
            url, branch = _request_settings(label)
            connection.execute(
                '''
                UPDATE "product_credentials"
                SET "repository_url" = ?, "repository_branch" = ?, "updated_at" = ?
                WHERE rowid = ?
                ''',
                (url, branch, datetime.now(timezone.utc).isoformat(), product["rowid"]),
            )
            connection.commit()
            reporter.info("deskNode repository data saved in product credentials.", label)
        return RepositorySettings(url=url, branch=branch)
    finally:
        connection.close()
