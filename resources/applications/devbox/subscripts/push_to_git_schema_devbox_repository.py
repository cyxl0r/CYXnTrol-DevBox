from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from subscripts.main_gui_devbox_log import get_devbox_logger


MODULE_LOGGER = get_devbox_logger(__file__)
MODULE_LOGGER.info("Module loaded.")


@dataclass(frozen=True)
class RepositorySettings:
    product_slug: str
    url: str
    branch: str


def _find_product(connection: sqlite3.Connection, product_slug: str) -> sqlite3.Row:
    connection.row_factory = sqlite3.Row
    row = connection.execute(
        '''
        SELECT rowid, * FROM "product_credentials"
        WHERE LOWER(COALESCE("product_slug", "")) = ?
           OR LOWER(COALESCE("product_name", "")) = ?
        LIMIT 1
        ''',
        (product_slug.lower(), product_slug.lower()),
    ).fetchone()
    if row is None:
        raise LookupError(f"Product entry was not found: {product_slug}")
    return row


def _request_settings_with_qt(product_label: str) -> tuple[str, str] | None:
    from PySide6.QtWidgets import QApplication, QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QMessageBox

    app = QApplication.instance() or QApplication([])
    dialog = QDialog()
    dialog.setWindowTitle("Repository-Verbindung einrichten")
    layout = QFormLayout(dialog)
    message = (
        f'Für "{product_label}" sind noch keine Repository-Daten hinterlegt. '
        "Bitte geben Sie die Repository-URL ein. Git bzw. Git Credential Manager "
        "übernimmt eine mögliche Anmeldung."
    )
    QMessageBox.information(dialog, "Repository-Verbindung fehlt", message)
    url_field = QLineEdit()
    url_field.setPlaceholderText("https://... oder git@...")
    branch_field = QLineEdit("main")
    layout.addRow("Repository-URL", url_field)
    layout.addRow("Branch", branch_field)
    buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
    layout.addRow(buttons)
    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return None
    url = url_field.text().strip()
    branch = branch_field.text().strip() or "main"
    if not url:
        QMessageBox.warning(dialog, "Repository-Verbindung", "Eine Repository-URL ist erforderlich.")
        return None
    return url, branch


def _request_settings_with_tk(product_label: str) -> tuple[str, str] | None:
    import tkinter as tk
    from tkinter import messagebox, simpledialog

    root = tk.Tk()
    root.withdraw()
    messagebox.showwarning(
        "Repository-Verbindung fehlt",
        f'Für "{product_label}" sind noch keine Repository-Daten hinterlegt.',
        parent=root,
    )
    url = simpledialog.askstring("Repository-URL", "Repository-URL", parent=root)
    if not url or not url.strip():
        root.destroy()
        return None
    branch = simpledialog.askstring("Repository-Branch", "Branch", initialvalue="main", parent=root)
    root.destroy()
    return url.strip(), (branch or "main").strip() or "main"


def _request_settings(product_label: str) -> tuple[str, str]:
    try:
        response = _request_settings_with_qt(product_label)
    except ImportError:
        response = _request_settings_with_tk(product_label)
    if response is None:
        raise RuntimeError("Repository setup was cancelled by user.")
    return response


def ensure_repository_settings(
    database_file: Path,
    product_slug: str,
    reporter,
) -> RepositorySettings:
    if not database_file.is_file():
        raise FileNotFoundError(f"DevBox database not found: {database_file}")
    connection = sqlite3.connect(database_file)
    try:
        product = _find_product(connection, product_slug)
        url = str(product["repository_url"] or "").strip()
        branch = str(product["repository_branch"] or "").strip() or "main"
        label = str(product["product_display_name"] or product["product_name"] or product_slug)
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
            reporter.info("Repository data saved in product credentials.", label)
        return RepositorySettings(product_slug=product_slug, url=url, branch=branch)
    finally:
        connection.close()
