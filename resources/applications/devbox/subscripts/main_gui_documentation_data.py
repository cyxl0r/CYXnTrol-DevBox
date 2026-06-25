from __future__ import annotations

from subscripts.main_gui_devbox_log import get_devbox_logger
LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")

from pathlib import Path
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from subscripts.main_gui_documentation_exporter import export_documentation_snapshot
from subscripts.main_gui_documentation_exchange import DocumentationExchangeError
from subscripts.main_gui_documentation_implementer import (
    find_latest_documentation_result,
    implement_latest_documentation_result,
)
from subscripts.main_gui_documentation_store import (
    database_file,
    insert_or_update_row,
    list_products,
    open_connection,
    read_columns,
    read_document_row,
    resolve_document_table,
    table_exists,
    value_to_text,
)
from subscripts.main_gui_documentation_view import (
    LABELS_DE,
    LABELS_EN,
    build_language_group,
    clear_layout,
)
class DocumentationDataForm(QFrame):
    def __init__(self, project_root_path: Path) -> None:
        super().__init__()
        self.project_root_path = Path(project_root_path).resolve()
        self.database_file = database_file(self.project_root_path)
        self.current_product_name = ""
        self.de_table_name: str | None = None
        self.en_table_name: str | None = None
        self.de_rowid: int | None = None
        self.en_rowid: int | None = None
        self.de_fields: dict[str, QTextEdit] = {}
        self.en_fields: dict[str, QTextEdit] = {}
        self.document_field_order: list[str] = []
        self.loading_dropdown = False
        self.setObjectName("DocumentationDataForm")
        self.build_ui()
        self.result_timer = QTimer(self)
        self.result_timer.setInterval(2000)
        self.result_timer.timeout.connect(self.refresh_implementer_state)
        self.result_timer.start()
        self.load_data()
    def build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(9)
        title = QLabel("Dokumentationen")
        title.setObjectName("StructureFormTitle")
        layout.addWidget(title)
        self.status_label = QLabel("Bereit.")
        self.status_label.setObjectName("StructureFormStatus")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        self.product_combo = QComboBox()
        self.product_combo.setObjectName("ProductDataCombo")
        self.product_combo.currentIndexChanged.connect(self.product_selection_changed)
        layout.addWidget(self.product_combo)
        action_row = QHBoxLayout()
        action_row.setSpacing(8)
        self.export_button = QPushButton("Export Snapshot")
        self.export_button.setObjectName("DocSnapshotButton")
        self.export_button.clicked.connect(self.export_snapshot)
        action_row.addWidget(self.export_button)
        self.implementer_button = QPushButton("Implementer")
        self.implementer_button.setObjectName("ImplementButton")
        self.implementer_button.clicked.connect(self.implement_latest_result)
        action_row.addWidget(self.implementer_button)
        action_row.addStretch(1)
        layout.addLayout(action_row)
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
        self.save_button = QPushButton("Dokumentationen speichern")
        self.save_button.setObjectName("StructureSaveButton")
        self.save_button.clicked.connect(self.save_data)
        save_row.addWidget(self.save_button)
        layout.addLayout(save_row)
    def load_data(self) -> None:
        if not self.database_file.is_file():
            self.build_fields({}, {}, [], False)
            self.product_combo.setEnabled(False)
            self.save_button.setEnabled(False)
            self.export_button.setEnabled(False)
            self.set_status(f"Datenbank nicht gefunden: {self.database_file}", True)
            self.refresh_implementer_state()
            return

        connection = open_connection(self.database_file)
        try:
            products = list_products(connection)
            self.reload_product_combo(products)
            enabled = bool(products)
            self.product_combo.setEnabled(enabled)
            self.save_button.setEnabled(False)
            self.export_button.setEnabled(False)
            if enabled:
                self.load_selected_product(connection)
            else:
                self.build_fields({}, {}, [], False)
                self.set_status("Noch kein Produkt-Datensatz vorhanden.", False)
        finally:
            connection.close()
        self.refresh_implementer_state()

    def reload_product_combo(self, products: list[dict[str, object]]) -> None:
        selected_product = self.current_product_name
        self.loading_dropdown = True
        self.product_combo.clear()
        for product in products:
            self.product_combo.addItem(str(product["label"]), str(product["product_name"]))
        index = self.product_combo.findData(selected_product)
        if index >= 0:
            self.product_combo.setCurrentIndex(index)
        self.loading_dropdown = False

    def product_selection_changed(self) -> None:
        if self.loading_dropdown or not self.database_file.is_file():
            return
        connection = open_connection(self.database_file)
        try:
            self.load_selected_product(connection)
        finally:
            connection.close()
        self.refresh_implementer_state()

    def load_selected_product(self, connection) -> None:
        self.current_product_name = str(self.product_combo.currentData() or "").strip()
        if not self.current_product_name:
            self.build_fields({}, {}, [], False)
            self.save_button.setEnabled(False)
            self.export_button.setEnabled(False)
            self.set_status("Kein Produkt ausgewählt.", False)
            return

        self.de_table_name = resolve_document_table(connection, self.current_product_name, "de")
        self.en_table_name = resolve_document_table(connection, self.current_product_name, "en")
        if self.de_table_name is None or self.en_table_name is None:
            self.de_rowid = None
            self.en_rowid = None
            self.build_fields({}, {}, [], False)
            self.save_button.setEnabled(False)
            self.export_button.setEnabled(False)
            self.set_status("Dokumentationstabellen fehlen. Produkt-Updater ausführen.", True)
            return

        self.de_rowid, de_values = read_document_row(connection, self.de_table_name)
        self.en_rowid, en_values = read_document_row(connection, self.en_table_name)
        self.document_field_order = read_columns(connection, self.de_table_name)
        self.build_fields(de_values, en_values, self.document_field_order, True)
        self.save_button.setEnabled(True)
        self.export_button.setEnabled(True)
        self.set_status("Dokumentationsdaten geladen.", False)

    def build_fields(
        self,
        de_values: dict[str, object],
        en_values: dict[str, object],
        field_order: list[str],
        enabled: bool,
    ) -> None:
        clear_layout(self.scroll_layout)
        self.de_fields.clear()
        self.en_fields.clear()
        self.scroll_layout.addWidget(
            build_language_group(
                "Deutsch", LABELS_DE, de_values, self.de_fields, field_order, enabled, value_to_text
            )
        )
        self.scroll_layout.addWidget(
            build_language_group(
                "English", LABELS_EN, en_values, self.en_fields, field_order, enabled, value_to_text
            )
        )
        self.scroll_layout.addStretch(1)

    def save_data(self) -> None:
        if not self.current_product_name or not self.de_table_name or not self.en_table_name:
            return
        connection = open_connection(self.database_file)
        try:
            if not table_exists(connection, self.de_table_name):
                raise RuntimeError(f"Tabelle nicht gefunden: {self.de_table_name}")
            if not table_exists(connection, self.en_table_name):
                raise RuntimeError(f"Tabelle nicht gefunden: {self.en_table_name}")
            self.de_rowid = insert_or_update_row(
                connection,
                self.de_table_name,
                self.de_rowid,
                self.collect_values(self.de_fields, self.de_table_name, connection),
            )
            self.en_rowid = insert_or_update_row(
                connection,
                self.en_table_name,
                self.en_rowid,
                self.collect_values(self.en_fields, self.en_table_name, connection),
            )
            connection.commit()
            self.set_status("Dokumentationsdaten gespeichert.", False)
            QMessageBox.information(self, "Gespeichert", "Dokumentationsdaten wurden gespeichert.")
        except Exception as exc:
            connection.rollback()
            self.set_status(f"Speichern fehlgeschlagen: {type(exc).__name__}: {exc}", True)
            QMessageBox.warning(self, "Fehler", str(exc))
        finally:
            connection.close()

    def export_snapshot(self) -> None:
        if not self.current_product_name or not self.export_button.isEnabled():
            return
        try:
            result = export_documentation_snapshot(self.project_root_path, self.current_product_name)
            self.set_status(f"Dokumentations-Snapshot erstellt: {result.archive_file.name}", False)
        except DocumentationExchangeError as exc:
            self.set_status(f"Snapshot fehlgeschlagen: {exc}", True)
            QMessageBox.warning(self, "Dokumentations-Snapshot", str(exc))
        except Exception as exc:
            message = f"{type(exc).__name__}: {exc}"
            self.set_status(f"Snapshot fehlgeschlagen: {message}", True)
            QMessageBox.warning(self, "Dokumentations-Snapshot", message)

    def refresh_implementer_state(self) -> None:
        result_file = find_latest_documentation_result()
        enabled = self.database_file.is_file() and result_file is not None
        self.implementer_button.setEnabled(enabled)
        if result_file is None:
            self.implementer_button.setToolTip("Keine Dokumentations-Result-ZIP in Downloads gefunden.")
        else:
            self.implementer_button.setToolTip(f"Jüngste Dokumentations-Result-ZIP: {result_file.name}")

    def implement_latest_result(self) -> None:
        if not self.implementer_button.isEnabled():
            return
        try:
            result = implement_latest_documentation_result(self.project_root_path)
            self.current_product_name = result.product_name
            self.load_data()
            cleanup_text = "Result-ZIP wurde aus Downloads entfernt." if result.result_deleted else (
                "Dokumentation wurde importiert, aber die Result-ZIP konnte nicht aus Downloads gelöscht werden."
            )
            self.set_status(f"Dokumentation für {result.product_name} implementiert.", False)
            QMessageBox.information(self, "Dokumentation implementiert", cleanup_text)
        except DocumentationExchangeError as exc:
            self.set_status(f"Implementierung fehlgeschlagen: {exc}", True)
            QMessageBox.warning(self, "Dokumentation implementieren", str(exc))
        except Exception as exc:
            message = f"{type(exc).__name__}: {exc}"
            self.set_status(f"Implementierung fehlgeschlagen: {message}", True)
            QMessageBox.warning(self, "Dokumentation implementieren", message)
        finally:
            self.refresh_implementer_state()

    def collect_values(self, field_store: dict[str, QTextEdit], table_name: str, connection) -> dict[str, object]:
        available_columns = set(read_columns(connection, table_name))
        values: dict[str, object] = {}
        for column_name, editor in field_store.items():
            if column_name in available_columns:
                text_value = editor.toPlainText().strip()
                values[column_name] = text_value or None
        return values

    def set_status(self, text: str, is_error: bool) -> None:
        self.status_label.setText(text)
        self.status_label.setProperty("error", is_error)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        self.status_label.update()
