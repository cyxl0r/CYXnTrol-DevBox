from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
)

from subscripts.main_gui_desknode_symbol_storage import list_categories


class DeviceEditDialog(QDialog):
    def __init__(self, studio, device, parent=None) -> None:
        super().__init__(parent)
        self.studio = studio
        self.setWindowTitle("Verbrauchergerät bearbeiten")
        self.setMinimumWidth(480)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)

        self.name_input = QLineEdit(str(device["device_key"]))
        self.name_input.setObjectName("DeskNodeSymbolInput")
        form.addRow("Gerätename / Kennung", self.name_input)

        self.category_combo = QComboBox()
        self.category_combo.setObjectName("DeskNodeSymbolCategoryCombo")
        form.addRow("Gerätekategorie", self.category_combo)
        layout.addLayout(form)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Ok
        )
        self.button_box.accepted.connect(self._accept_if_valid)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        self.reload_categories(int(device["category_id"]))

    def reload_categories(self, selected_id: int) -> None:
        self.category_combo.clear()

        for category in list_categories(self.studio):
            self.category_combo.addItem(
                str(category["category_key"]),
                int(category["record_id"]),
            )

        index = self.category_combo.findData(selected_id)

        if index >= 0:
            self.category_combo.setCurrentIndex(index)

    def _accept_if_valid(self) -> None:
        if not self.name_input.text().strip():
            QMessageBox.warning(
                self,
                "Verbrauchergerät",
                "Ein Gerätename ist erforderlich.",
            )
            return

        if self.category_combo.currentData() is None:
            QMessageBox.warning(
                self,
                "Verbrauchergerät",
                "Eine Gerätekategorie ist erforderlich.",
            )
            return

        self.accept()
