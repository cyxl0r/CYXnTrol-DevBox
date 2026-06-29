from __future__ import annotations

import sqlite3

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QWidget,
)

from subscripts.main_gui_desknode_symbol_refresh import (
    start_symbol_manufacturer_database_refresh,
)
from subscripts.main_gui_desknode_symbol_storage import (
    create_category,
    delete_category,
    get_category,
    list_categories,
    update_category,
)


PAGE_KEY = "desknode_symbol_management"


class CategoryEditor(QWidget):
    categories_changed = Signal()

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
        layout.addWidget(QLabel("Gerätekategorie:"))

        self.record_combo = QComboBox()
        self.record_combo.setObjectName("DeskNodeSymbolRecordCombo")
        self.record_combo.currentIndexChanged.connect(self._set_current)
        layout.addWidget(self.record_combo, stretch=1)

        self.new_button = QPushButton("+")
        self.new_button.setObjectName("DeskNodeSymbolActionButton")
        self.new_button.setToolTip("Neue Gerätekategorie anlegen")
        self.new_button.clicked.connect(self.create_new)
        layout.addWidget(self.new_button)

        self.edit_button = QPushButton("✎")
        self.edit_button.setObjectName("DeskNodeSymbolActionButton")
        self.edit_button.setToolTip("Aktuelle Gerätekategorie bearbeiten")
        self.edit_button.clicked.connect(self.edit_current)
        layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("−")
        self.delete_button.setObjectName("DeskNodeSymbolDangerButton")
        self.delete_button.setToolTip("Aktuelle Gerätekategorie löschen")
        self.delete_button.clicked.connect(self.delete_current)
        layout.addWidget(self.delete_button)

    def reload(self, selected_id: int | None = None) -> None:
        rows = list_categories(self.studio)
        current_id = selected_id if selected_id is not None else self.record_id
        self.record_combo.blockSignals(True)
        self.record_combo.clear()

        for row in rows:
            self.record_combo.addItem(
                f"{row['category_key']}  ·  #{row['record_id']}",
                int(row["record_id"]),
            )

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
        name, accepted = QInputDialog.getText(
            self,
            "Neue Gerätekategorie",
            "Kategoriename:",
        )

        if not accepted:
            return

        try:
            record_id = create_category(self.studio, name)
        except (sqlite3.Error, ValueError) as error:
            self.studio.set_status(str(error), "error", PAGE_KEY)
            return

        self.reload(record_id)
        self.categories_changed.emit()
        self.studio.append_log(
            f"Gerätekategorie angelegt: record_id={record_id}.",
            PAGE_KEY,
        )
        self._refresh_manufacturer_database("Gerätekategorie")

    def edit_current(self) -> None:
        if self.record_id is None:
            return

        try:
            category = get_category(self.studio, self.record_id)
        except (sqlite3.Error, ValueError) as error:
            self.studio.set_status(str(error), "error", PAGE_KEY)
            return

        name, accepted = QInputDialog.getText(
            self,
            "Gerätekategorie bearbeiten",
            "Kategoriename:",
            text=str(category["category_key"]),
        )

        if not accepted:
            return

        try:
            update_category(self.studio, self.record_id, name)
        except (sqlite3.Error, ValueError) as error:
            self.studio.set_status(str(error), "error", PAGE_KEY)
            return

        self.reload(self.record_id)
        self.categories_changed.emit()
        self.studio.append_log(
            f"Gerätekategorie bearbeitet: record_id={self.record_id}.",
            PAGE_KEY,
        )
        self._refresh_manufacturer_database("Gerätekategorie")

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
            "Gerätekategorie löschen",
            "Die aktuelle Gerätekategorie wirklich löschen?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            delete_category(self.studio, self.record_id)
        except (sqlite3.Error, ValueError) as error:
            self.studio.set_status(str(error), "error", PAGE_KEY)
            return

        self.reload()
        self.categories_changed.emit()
        self.studio.append_log("Gerätekategorie gelöscht.", PAGE_KEY)
        self._refresh_manufacturer_database("Gerätekategorie")
