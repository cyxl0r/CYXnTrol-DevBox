from __future__ import annotations

from subscripts.main_gui_devbox_log import get_devbox_logger
LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")


from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QFrame, QFormLayout, QHBoxLayout, QInputDialog, QLabel,
    QLineEdit, QMessageBox, QPushButton, QScrollArea, QVBoxLayout, QWidget,
)

from subscripts.main_gui_metadata_defaults import (
    MANUFACTURER_READ_ONLY_COLUMNS,
    manufacturer_create_values,
    manufacturer_update_values,
    sync_product_defaults,
    sync_project_family,
)
from subscripts.main_gui_roof_store import (
    EXCLUDED_COLUMNS, TABLE_NAME, database_file, find_data_row, group_for_column,
    group_order, insert_row, label_from_column, open_connection, read_columns,
    read_row_values, table_exists, update_row, value_to_text,
)
from subscripts.main_gui_secret_store import (
    decrypt_secret_text, encrypt_secret_text, read_encrypted_column_value,
)


class RoofDataForm(QFrame):
    def __init__(self, project_root_path: Path) -> None:
        super().__init__()
        self.project_root_path = Path(project_root_path).resolve()
        self.database_file = database_file(self.project_root_path)
        self.fields: dict[str, QLineEdit] = {}
        self.sensitive_fields: dict[str, QLineEdit] = {}
        self.pending_sensitive: dict[str, str] = {}
        self.column_types: dict[str, str] = {}
        self.current_rowid: int | None = None
        self.setObjectName("RoofDataForm")
        self.build_ui()
        self.load_data()

    def build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(9)
        title = QLabel("Dach-Daten")
        title.setObjectName("StructureFormTitle")
        layout.addWidget(title)
        self.status_label = QLabel("Bereit.")
        self.status_label.setObjectName("StructureFormStatus")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        self.scroll = QScrollArea()
        self.scroll.setObjectName("RoofDataScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setContentsMargins(4, 4, 4, 4)
        self.scroll_layout.setSpacing(9)
        self.scroll.setWidget(self.scroll_widget)
        layout.addWidget(self.scroll, 1)
        save_row = QHBoxLayout()
        save_row.addStretch(1)
        self.save_button = QPushButton("Dach-Daten speichern")
        self.save_button.setObjectName("StructureSaveButton")
        self.save_button.clicked.connect(self.save_data)
        save_row.addWidget(self.save_button)
        layout.addLayout(save_row)

    def load_data(self) -> None:
        if not self.database_file.is_file():
            self.set_status(f"Datenbank nicht gefunden: {self.database_file}", True)
            self.save_button.setEnabled(False)
            return
        connection = open_connection(self.database_file)
        try:
            if not table_exists(connection, TABLE_NAME):
                self.set_status(f"Tabelle nicht gefunden: {TABLE_NAME}", True)
                self.save_button.setEnabled(False)
                return
            self.column_types = {
                name: typ for name, typ in read_columns(connection)
                if name not in EXCLUDED_COLUMNS
            }
            self.current_rowid = find_data_row(connection, self.column_types)
            self.build_fields(read_row_values(connection, self.current_rowid))
            self.set_status("Dach-Daten geladen.", False)
        finally:
            connection.close()

    def build_fields(self, values: dict[str, object]) -> None:
        clear_layout(self.scroll_layout)
        self.fields.clear()
        self.sensitive_fields.clear()
        grouped: dict[str, list[str]] = {}
        for column in self.column_types:
            grouped.setdefault(group_for_column(column), []).append(column)
        for group_name in group_order():
            columns = grouped.get(group_name)
            if not columns:
                continue
            box = QFrame()
            box.setObjectName("RoofDataGroup")
            form = QFormLayout(box)
            form.setContentsMargins(10, 8, 10, 10)
            form.setSpacing(6)
            label = QLabel(group_name)
            label.setObjectName("RoofDataGroupTitle")
            form.addRow(label)
            for column in columns:
                if self.is_sensitive(column):
                    form.addRow(label_from_column(column), self.make_sensitive_row(column))
                    continue
                editor = QLineEdit()
                editor.setObjectName("RoofDataInput")
                editor.setText(value_to_text(values.get(column)))
                editor.setReadOnly(column in MANUFACTURER_READ_ONLY_COLUMNS)
                editor.setProperty("automatic", column in MANUFACTURER_READ_ONLY_COLUMNS)
                self.fields[column] = editor
                form.addRow(label_from_column(column), editor)
            self.scroll_layout.addWidget(box)
        self.scroll_layout.addStretch(1)

    def is_sensitive(self, column: str) -> bool:
        return self.column_types.get(column, "").upper() == "BLOB"

    def make_sensitive_row(self, column: str) -> QWidget:
        row = QWidget()
        row.setObjectName("SensitiveRow")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        editor = QLineEdit("verschlüsselt")
        editor.setObjectName("RoofDataInput")
        editor.setEnabled(False)
        self.sensitive_fields[column] = editor
        set_button = QPushButton("Neuen Key")
        set_button.setObjectName("SecretSetButton")
        set_button.clicked.connect(lambda _=False, c=column: self.set_sensitive(c))
        copy_button = QPushButton("Kopieren")
        copy_button.setObjectName("SecretCopyButton")
        copy_button.clicked.connect(lambda _=False, c=column: self.copy_sensitive(c))
        layout.addWidget(editor, 1)
        layout.addWidget(set_button)
        layout.addWidget(copy_button)
        return row

    def set_sensitive(self, column: str) -> None:
        text, ok = QInputDialog.getMultiLineText(
            self, f"{label_from_column(column)} neu eintragen", "Neuer Inhalt:"
        )
        if ok and str(text):
            self.pending_sensitive[column] = str(text)
            self.set_status(f"Neuer Wert vorgemerkt: {label_from_column(column)}", False)

    def copy_sensitive(self, column: str) -> None:
        if self.current_rowid is None:
            QMessageBox.information(self, "Nicht gespeichert", "Bitte zuerst Dach-Daten speichern.")
            return
        try:
            plain_text = self.pending_sensitive.get(column) or self.read_sensitive(column)
            if plain_text is None:
                QMessageBox.information(self, "Leer", "Für dieses Feld ist noch kein Wert gespeichert.")
                return
            QApplication.clipboard().setText(plain_text)
            self.set_status(f"In Zwischenablage kopiert: {label_from_column(column)}", False)
        except Exception as exc:
            self.set_status(f"Entschlüsseln fehlgeschlagen: {type(exc).__name__}: {exc}", True)
            QMessageBox.warning(self, "Fehler", str(exc))

    def read_sensitive(self, column: str) -> str | None:
        connection = open_connection(self.database_file)
        try:
            payload = read_encrypted_column_value(connection, TABLE_NAME, self.current_rowid, column)
            return None if payload is None else decrypt_secret_text(connection, TABLE_NAME, column, payload)
        finally:
            connection.close()

    def save_data(self) -> None:
        connection = open_connection(self.database_file)
        try:
            values = self.collect_values()
            for column, plain_text in self.pending_sensitive.items():
                values[column] = encrypt_secret_text(connection, TABLE_NAME, column, plain_text)
            if self.current_rowid is None:
                values = manufacturer_create_values(connection, values, self.project_root_path)
                self.current_rowid = insert_row(connection, values)
            else:
                values.update(manufacturer_update_values(connection))
                update_row(connection, self.current_rowid, values)
            product_default_count = sync_product_defaults(connection, self.project_root_path)
            family_sync_count = sync_project_family(connection, self.project_root_path)
            connection.commit()
            self.pending_sensitive.clear()
            self.build_fields(read_row_values(connection, self.current_rowid))
            text = "Dach-Daten gespeichert."
            if product_default_count:
                text += f" Produkt-Automatik aktualisiert: {product_default_count}."
            if family_sync_count:
                text += f" Familienzuordnung aktualisiert: {family_sync_count}."
            self.set_status(text, False)
            QMessageBox.information(self, "Gespeichert", "Dach-Daten wurden gespeichert.")
        except Exception as exc:
            connection.rollback()
            self.set_status(f"Speichern fehlgeschlagen: {type(exc).__name__}: {exc}", True)
            QMessageBox.warning(self, "Fehler", str(exc))
        finally:
            connection.close()

    def collect_values(self) -> dict[str, object]:
        values: dict[str, object] = {}
        for column, editor in self.fields.items():
            if column in MANUFACTURER_READ_ONLY_COLUMNS:
                continue
            text = editor.text().strip()
            column_type = self.column_types.get(column, "TEXT").upper()
            if text == "":
                values[column] = None
            elif column_type == "INTEGER":
                values[column] = int(text)
            elif column_type == "REAL":
                values[column] = float(text.replace(",", "."))
            else:
                values[column] = text
        return values

    def set_status(self, text: str, is_error: bool) -> None:
        self.status_label.setText(text)
        self.status_label.setProperty("error", is_error)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        self.status_label.update()


def clear_layout(layout) -> None:
    while layout is not None and layout.count():
        item = layout.takeAt(0)
        if item.widget() is not None:
            item.widget().deleteLater()
        if item.layout() is not None:
            clear_layout(item.layout())
