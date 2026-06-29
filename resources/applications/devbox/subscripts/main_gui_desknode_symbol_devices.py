from __future__ import annotations

import sqlite3

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from subscripts.main_gui_desknode_symbol_device_data import (
    create_device,
    delete_device,
    get_device,
    list_devices,
    update_device,
)
from subscripts.main_gui_desknode_symbol_drop import PngDropField
from subscripts.main_gui_desknode_symbol_edit_dialogs import DeviceEditDialog
from subscripts.main_gui_desknode_symbol_refresh import (
    start_symbol_manufacturer_database_refresh,
)
from subscripts.main_gui_desknode_symbol_storage import list_categories


PAGE_KEY = "desknode_symbol_management"


class DeviceCreateDialog(QDialog):
    def __init__(self, studio, parent=None) -> None:
        super().__init__(parent)
        self.studio = studio
        self.setWindowTitle("Neues Verbrauchergerät")
        self.setMinimumWidth(480)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)

        self.name_input = QLineEdit()
        self.name_input.setObjectName("DeskNodeSymbolInput")
        self.name_input.setPlaceholderText("z. B. guitar-amp")
        form.addRow("Gerätename / Kennung", self.name_input)

        self.category_combo = QComboBox()
        self.category_combo.setObjectName("DeskNodeSymbolCategoryCombo")
        form.addRow("Gerätekategorie", self.category_combo)

        self.png_drop = PngDropField()
        form.addRow("PNG-Quelle", self.png_drop)
        layout.addLayout(form)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Ok
        )
        self.button_box.accepted.connect(self._accept_if_valid)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        self.reload_categories()

    def reload_categories(self) -> None:
        self.category_combo.clear()

        for category in list_categories(self.studio):
            self.category_combo.addItem(
                str(category["category_key"]),
                int(category["record_id"]),
            )

    def _accept_if_valid(self) -> None:
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Verbrauchergerät", "Ein Gerätename ist erforderlich.")
            return

        if self.category_combo.currentData() is None:
            QMessageBox.warning(self, "Verbrauchergerät", "Zuerst muss eine Gerätekategorie angelegt werden.")
            return

        if self.png_drop.source_file is None:
            QMessageBox.warning(self, "Verbrauchergerät", "Es muss genau eine PNG-Datei ausgewählt werden.")
            return

        self.accept()


class DeviceEditor(QWidget):
    devices_changed = Signal()

    def __init__(self, studio) -> None:
        super().__init__()
        self.studio = studio
        self.record_id: int | None = None
        self._build()
        self.reload()

    def _build(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(QLabel("Verbrauchergerät:"))

        self.record_combo = QComboBox()
        self.record_combo.setObjectName("DeskNodeSymbolRecordCombo")
        self.record_combo.currentIndexChanged.connect(self._set_current)
        layout.addWidget(self.record_combo, stretch=1)

        self.new_button = QPushButton("+")
        self.new_button.setObjectName("DeskNodeSymbolActionButton")
        self.new_button.setToolTip("Neues Verbrauchergerät anlegen")
        self.new_button.clicked.connect(self.create_new)
        layout.addWidget(self.new_button)

        self.edit_button = QPushButton("✎")
        self.edit_button.setObjectName("DeskNodeSymbolActionButton")
        self.edit_button.setToolTip("Aktuelles Verbrauchergerät bearbeiten")
        self.edit_button.clicked.connect(self.edit_current)
        layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("−")
        self.delete_button.setObjectName("DeskNodeSymbolDangerButton")
        self.delete_button.setToolTip("Aktuelles Verbrauchergerät löschen")
        self.delete_button.clicked.connect(self.delete_current)
        layout.addWidget(self.delete_button)

    def reload(self, selected_id: int | None = None) -> None:
        rows = list_devices(self.studio)
        current_id = selected_id if selected_id is not None else self.record_id
        self.record_combo.blockSignals(True)
        self.record_combo.clear()

        for row in rows:
            label = (
                f"{row['device_key']}  ·  "
                f"{row['category_key']}  ·  #{row['record_id']}"
            )
            self.record_combo.addItem(label, int(row["record_id"]))

        self.record_combo.blockSignals(False)

        if not rows:
            self.record_id = None
            self.edit_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            return

        index = next(
            (
                item_index
                for item_index in range(self.record_combo.count())
                if self.record_combo.itemData(item_index) == current_id
            ),
            0,
        )
        self.record_combo.setCurrentIndex(index)
        self._set_current()

    def _set_current(self) -> None:
        record_id = self.record_combo.currentData()
        self.record_id = int(record_id) if record_id is not None else None
        is_selected = self.record_id is not None
        self.edit_button.setEnabled(is_selected)
        self.delete_button.setEnabled(is_selected)

    def create_new(self) -> None:
        dialog = DeviceCreateDialog(self.studio, self)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        try:
            record_id = create_device(
                studio=self.studio,
                device_name=dialog.name_input.text(),
                category_id=dialog.category_combo.currentData(),
                png_source=dialog.png_drop.source_file,
            )
        except (OSError, sqlite3.Error, RuntimeError, ValueError) as error:
            self.studio.set_status(str(error), "error", PAGE_KEY)
            return

        self.reload(record_id)
        self.devices_changed.emit()
        self.studio.append_log(
            f"Verbrauchergerät angelegt: record_id={record_id}.",
            PAGE_KEY,
        )
        self._refresh_manufacturer_database("Verbrauchergerät")

    def edit_current(self) -> None:
        if self.record_id is None:
            return

        try:
            device = get_device(self.studio, self.record_id)
        except (sqlite3.Error, ValueError) as error:
            self.studio.set_status(str(error), "error", PAGE_KEY)
            return

        dialog = DeviceEditDialog(self.studio, device, self)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        try:
            update_device(
                studio=self.studio,
                record_id=self.record_id,
                device_name=dialog.name_input.text(),
                category_id=dialog.category_combo.currentData(),
            )
        except (sqlite3.Error, ValueError) as error:
            self.studio.set_status(str(error), "error", PAGE_KEY)
            return

        self.reload(self.record_id)
        self.devices_changed.emit()
        self.studio.append_log(
            f"Verbrauchergerät bearbeitet: record_id={self.record_id}.",
            PAGE_KEY,
        )
        self._refresh_manufacturer_database("Verbrauchergerät")

    def _refresh_manufacturer_database(
        self,
        saved_subject: str,
    ) -> None:
        controls = getattr(
            self.studio,
            "desknode_symbol_refresh_controls",
            (),
        )
        start_symbol_manufacturer_database_refresh(
            studio=self.studio,
            saved_subject=saved_subject,
            controls_to_lock=controls,
        )

    def delete_current(self) -> None:
        if self.record_id is None:
            return

        answer = QMessageBox.question(
            self,
            "Verbrauchergerät löschen",
            "Das aktuelle Verbrauchergerät und seine registrierte "
            "PNG-Quelle wirklich löschen?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            delete_device(self.studio, self.record_id)
        except (OSError, sqlite3.Error, ValueError) as error:
            self.studio.set_status(str(error), "error", PAGE_KEY)
            return

        self.reload()
        self.devices_changed.emit()
        self.studio.append_log("Verbrauchergerät gelöscht.", PAGE_KEY)
        self._refresh_manufacturer_database("Verbrauchergerät")
