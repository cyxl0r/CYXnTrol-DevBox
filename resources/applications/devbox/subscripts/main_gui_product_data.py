from __future__ import annotations

from subscripts.main_gui_devbox_log import get_devbox_logger
LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")

from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QComboBox, QDialog, QFrame, QFormLayout, QHBoxLayout, QInputDialog, QLabel, QLineEdit, QMessageBox, QPushButton, QScrollArea, QVBoxLayout, QWidget
from subscripts.main_gui_metadata_defaults import PRODUCT_READ_ONLY_COLUMNS, product_create_values, product_update_values
from subscripts.main_gui_product_store import EXCLUDED_COLUMNS, KEY_TABLE_NAME, TABLE_NAME, create_product_with_folder, database_file, group_for_column, group_order, label_from_column, list_products, open_connection, read_columns, read_row_values, table_exists, update_row, value_to_text
from subscripts.main_gui_secret_store import decrypt_secret_text, encrypt_secret_text, read_encrypted_column_value
from subscripts.main_gui_product_wizard import ProductCreationWizard
from subscripts.main_gui_product_wizard_values import apply_wizard_values
from subscripts.main_gui_target_operating_systems import TargetOperatingSystemsDialog, parse_target_operating_systems, serialize_target_operating_systems
class ProductDataForm(QFrame):
    def __init__(self, project_root_path: Path) -> None:
        super().__init__()
        self.project_root_path = Path(project_root_path).resolve(); self.database_file = database_file(self.project_root_path)
        self.fields: dict[str, QLineEdit] = {}; self.sensitive_fields: dict[str, QLineEdit] = {}
        self.sensitive_buttons: dict[str, list[QPushButton]] = {}; self.pending_sensitive: dict[str, str] = {}
        self.column_types: dict[str, str] = {}; self.current_rowid: int | None = None; self.loading_dropdown = False
        self.target_operating_systems: list[str] = []; self.target_os_button: QPushButton | None = None
        self.setObjectName("ProductDataForm"); self.build_ui(); self.load_data()
    def build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(9)
        title = QLabel("Produkt-Daten"); title.setObjectName("StructureFormTitle"); layout.addWidget(title)
        self.status_label = QLabel("Bereit."); self.status_label.setObjectName("StructureFormStatus"); self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        picker = QHBoxLayout()
        self.product_combo = QComboBox(); self.product_combo.setObjectName("ProductDataCombo")
        self.product_combo.currentIndexChanged.connect(self.product_selection_changed)
        self.new_button = QPushButton("+"); self.new_button.setObjectName("StructureSaveButton")
        self.new_button.clicked.connect(self.create_product_record)
        picker.addWidget(self.product_combo, 1); picker.addWidget(self.new_button); layout.addLayout(picker)
        self.scroll = QScrollArea(); self.scroll.setObjectName("RoofDataScroll"); self.scroll.setWidgetResizable(True)
        self.scroll_widget = QWidget(); self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setContentsMargins(4, 4, 4, 4); self.scroll_layout.setSpacing(9)
        self.scroll.setWidget(self.scroll_widget); layout.addWidget(self.scroll, 1)
        save_row = QHBoxLayout(); save_row.addStretch(1)
        self.save_button = QPushButton("Produkt-Daten speichern"); self.save_button.setObjectName("StructureSaveButton")
        self.save_button.clicked.connect(self.save_data); save_row.addWidget(self.save_button); layout.addLayout(save_row)
    def load_data(self) -> None:
        if not self.database_file.is_file():
            self.set_status(f"Datenbank nicht gefunden: {self.database_file}", True)
            self.set_form_enabled(False)
            return
        connection = open_connection(self.database_file)
        try:
            if not table_exists(connection, TABLE_NAME):
                self.set_status(f"Tabelle nicht gefunden: {TABLE_NAME}", True)
                self.set_form_enabled(False)
                return
            self.column_types = {name: typ for name, typ in read_columns(connection) if name not in EXCLUDED_COLUMNS}
            self.reload_product_combo(connection); self.current_rowid = self.product_combo.currentData(); self.populate_current_product(connection)
        finally:
            connection.close()
    def reload_product_combo(self, connection, select_rowid: int | None = None) -> None:
        self.loading_dropdown = True
        self.product_combo.clear()
        for product in list_products(connection):
            self.product_combo.addItem(str(product["label"]), int(product["rowid"]))
        if select_rowid is not None:
            index = self.product_combo.findData(select_rowid)
            if index >= 0:
                self.product_combo.setCurrentIndex(index)
        self.loading_dropdown = False
    def populate_current_product(self, connection) -> None:
        enabled = self.current_rowid is not None
        values = read_row_values(connection, self.current_rowid)
        self.target_operating_systems = parse_target_operating_systems(values.get(self.target_os_column(), "[]"))
        self.build_fields(values, enabled)
        self.save_button.setEnabled(enabled)
        self.product_combo.setEnabled(enabled)
        text = "Produkt-Daten geladen." if enabled else "Noch kein Produkt-Datensatz vorhanden. Mit + anlegen."
        self.set_status(text, False)
    def product_selection_changed(self) -> None:
        if self.loading_dropdown:
            return
        self.pending_sensitive.clear()
        self.current_rowid = self.product_combo.currentData()
        connection = open_connection(self.database_file)
        try:
            self.populate_current_product(connection)
            if self.current_rowid is not None:
                self.set_status("Produkt-Datensatz gewechselt.", False)
        finally:
            connection.close()
    def create_product_record(self) -> None:
        try:
            wizard = ProductCreationWizard(self.project_root_path, self.window())
            wizard.setWindowModality(Qt.WindowModality.ApplicationModal)
            wizard.raise_()
            wizard.activateWindow()
            if wizard.exec() != QDialog.DialogCode.Accepted:
                return
        except Exception as exc:
            self.set_status(f"Produkt-Assistent konnte nicht geöffnet werden: {type(exc).__name__}: {exc}", True)
            QMessageBox.critical(self, "Produkt-Assistent", f"{type(exc).__name__}: {exc}")
            return
        wizard_values = wizard.product_values()
        product_name = str(wizard_values["product_name"])
        connection = open_connection(self.database_file)
        try:
            if self.product_name_exists(connection, product_name):
                raise ValueError("Ein Produkt mit diesem Produktnamen existiert bereits.")
            values = product_create_values(
                connection,
                self.project_root_path,
                product_name,
                list(wizard_values["target_operating_systems"]),
            )
            apply_wizard_values(values, self.column_types, wizard_values)
            self.current_rowid, folder, updater_code = create_product_with_folder(
                connection,
                self.project_root_path,
                product_name,
                values,
            )
            self.reload_product_combo(connection, self.current_rowid)
            self.populate_current_product(connection)
            self.set_status(
                f"Neuer Produkt-Datensatz angelegt. Ordner: {folder.name}. Updater-Code: {updater_code}",
                updater_code != 0,
            )
        except Exception as exc:
            connection.rollback()
            self.set_status(f"Anlegen fehlgeschlagen: {type(exc).__name__}: {exc}", True)
            QMessageBox.warning(self, "Fehler", str(exc))
        finally:
            connection.close()
    def product_name_exists(self, connection, product_name: str) -> bool:
        cursor = connection.execute(
            'SELECT rowid FROM "product_credentials" WHERE LOWER(TRIM("product_name")) = LOWER(TRIM(?)) LIMIT 1',
            (product_name,),
        )
        return cursor.fetchone() is not None
    def build_fields(self, values: dict[str, object], enabled: bool) -> None:
        clear_layout(self.scroll_layout)
        self.fields.clear()
        self.sensitive_fields.clear()
        self.sensitive_buttons.clear()
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
            title = QLabel(group_name)
            title.setObjectName("RoofDataGroupTitle")
            form.addRow(title)
            for column in columns:
                if column.lower() == "target_operating_systems":
                    form.addRow(label_from_column(column), self.make_target_os_button(enabled))
                    continue
                if self.is_sensitive(column):
                    form.addRow(label_from_column(column), self.make_sensitive_row(column, enabled))
                    continue
                editor = QLineEdit()
                editor.setObjectName("RoofDataInput")
                editor.setText(value_to_text(values.get(column)))
                editor.setEnabled(enabled)
                editor.setReadOnly(column in PRODUCT_READ_ONLY_COLUMNS)
                editor.setProperty("automatic", column in PRODUCT_READ_ONLY_COLUMNS)
                self.fields[column] = editor
                form.addRow(label_from_column(column), editor)
            self.scroll_layout.addWidget(box)
        self.scroll_layout.addStretch(1)
    def target_os_column(self) -> str:
        return next((column for column in self.column_types if column.lower() == "target_operating_systems"), "target_operating_systems")
    def make_target_os_button(self, enabled: bool) -> QPushButton:
        button = QPushButton("Bearbeiten"); button.setObjectName("TargetOperatingSystemsButton")
        button.setEnabled(enabled); button.clicked.connect(self.edit_target_operating_systems)
        self.target_os_button = button; self.refresh_target_os_button()
        return button
    def edit_target_operating_systems(self) -> None:
        dialog = TargetOperatingSystemsDialog(self.target_operating_systems)
        if not dialog.exec():
            return
        values = dialog.selected_operating_systems()
        if not values:
            QMessageBox.information(self, "Zielbetriebssysteme", "Mindestens ein Zielbetriebssystem muss ausgewählt werden.")
            return
        self.target_operating_systems = values; self.refresh_target_os_button()
        self.set_status("Zielbetriebssysteme vorgemerkt. Bitte speichern.", False)
    def refresh_target_os_button(self) -> None:
        if self.target_os_button is not None:
            self.target_os_button.setToolTip(", ".join(self.target_operating_systems) or "Keine Auswahl")
    def set_form_enabled(self, enabled: bool) -> None:
        for column, editor in self.fields.items():
            editor.setEnabled(enabled)
            editor.setReadOnly(column in PRODUCT_READ_ONLY_COLUMNS)
        for buttons in self.sensitive_buttons.values():
            for button in buttons:
                button.setEnabled(enabled)
        if self.target_os_button is not None:
            self.target_os_button.setEnabled(enabled)
        self.save_button.setEnabled(enabled)
        self.product_combo.setEnabled(enabled)
    def is_sensitive(self, column: str) -> bool:
        return self.column_types.get(column, "").upper() == "BLOB"
    def make_sensitive_row(self, column: str, enabled: bool) -> QWidget:
        row = QWidget(); row.setObjectName("SensitiveRow")
        layout = QHBoxLayout(row); layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(6)
        editor = QLineEdit("verschlüsselt"); editor.setObjectName("RoofDataInput"); editor.setEnabled(False)
        self.sensitive_fields[column] = editor
        set_button = QPushButton("Neuen Key"); set_button.setObjectName("SecretSetButton"); set_button.setEnabled(enabled)
        set_button.clicked.connect(lambda _=False, c=column: self.set_sensitive(c))
        copy_button = QPushButton("Kopieren"); copy_button.setObjectName("SecretCopyButton"); copy_button.setEnabled(enabled)
        copy_button.clicked.connect(lambda _=False, c=column: self.copy_sensitive(c))
        self.sensitive_buttons[column] = [set_button, copy_button]
        layout.addWidget(editor, 1)
        layout.addWidget(set_button)
        layout.addWidget(copy_button)
        return row
    def set_sensitive(self, column: str) -> None:
        if self.current_rowid is None:
            return
        text, ok = QInputDialog.getMultiLineText(self, f"{label_from_column(column)} neu eintragen", "Neuer Inhalt:")
        if ok and str(text):
            self.pending_sensitive[column] = str(text)
            self.set_status(f"Neuer Wert vorgemerkt: {label_from_column(column)}", False)
    def copy_sensitive(self, column: str) -> None:
        if self.current_rowid is None:
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
            return None if payload is None else decrypt_secret_text(connection, KEY_TABLE_NAME, column, payload)
        finally:
            connection.close()
    def save_data(self) -> None:
        if self.current_rowid is None:
            QMessageBox.information(self, "Kein Datensatz", "Bitte zuerst mit + einen Produkt-Datensatz anlegen.")
            return
        connection = open_connection(self.database_file)
        try:
            values = self.collect_values()
            for column, plain_text in self.pending_sensitive.items():
                values[column] = encrypt_secret_text(connection, KEY_TABLE_NAME, column, plain_text)
            values.update(product_update_values(connection))
            update_row(connection, self.current_rowid, values)
            connection.commit()
            self.pending_sensitive.clear()
            self.reload_product_combo(connection, self.current_rowid)
            self.populate_current_product(connection)
            self.set_status("Produkt-Daten gespeichert.", False)
            QMessageBox.information(self, "Gespeichert", "Produkt-Daten wurden gespeichert.")
        except Exception as exc:
            connection.rollback()
            self.set_status(f"Speichern fehlgeschlagen: {type(exc).__name__}: {exc}", True)
            QMessageBox.warning(self, "Fehler", str(exc))
        finally:
            connection.close()
    def collect_values(self) -> dict[str, object]:
        values: dict[str, object] = {}
        for column, editor in self.fields.items():
            if column in PRODUCT_READ_ONLY_COLUMNS:
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
        target_column = self.target_os_column()
        if target_column in self.column_types:
            values[target_column] = serialize_target_operating_systems(self.target_operating_systems)
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
