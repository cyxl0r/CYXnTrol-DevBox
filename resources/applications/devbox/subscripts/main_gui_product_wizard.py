from __future__ import annotations

from subscripts.main_gui_devbox_log import get_devbox_logger
LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")


from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from subscripts.main_gui_target_operating_systems import OPERATING_SYSTEMS

PRODUCT_TYPES = (
    ("desktop_application", "Desktop-Anwendung"),
    ("server_service", "Serverdienst"),
    ("command_line_tool", "CLI-Werkzeug"),
    ("library_framework", "Bibliothek / Framework"),
    ("mobile_application", "Mobile App"),
    ("build_tool", "Build- / Entwicklungstool"),
    ("automation_tool", "Automatisierungswerkzeug"),
    ("other", "Sonstiges"),
)


class ProductCreationWizard(QDialog):
    def __init__(self, project_root_path: Path, parent=None) -> None:
        super().__init__(parent)
        self.project_root_path = Path(project_root_path).resolve()
        self.product_family = self.project_root_path.name.strip()
        self.checkboxes: dict[str, QCheckBox] = {}
        self.setWindowTitle("Neues Produkt / Projekt")
        self.setModal(True)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.setMinimumWidth(640)
        self.resize(700, 500)
        self.build_ui()
        self.apply_style()
        self.update_page()
        QTimer.singleShot(0, self.activate_window)

    def activate_window(self) -> None:
        self.raise_()
        self.activateWindow()

    def build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.title = QLabel()
        self.title.setObjectName("ProductWizardTitle")
        self.hint = QLabel()
        self.hint.setObjectName("ProductWizardHint")
        self.hint.setWordWrap(True)

        self.pages = QStackedWidget()
        self.pages.addWidget(self.build_identity_page())
        self.pages.addWidget(self.build_os_page())
        self.pages.addWidget(self.build_summary_page())

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        self.cancel_button = self.make_button("Abbrechen", "ProductWizardCancelButton")
        self.back_button = self.make_button("Zurück", "ProductWizardBackButton")
        self.next_button = self.make_button("Weiter", "ProductWizardNextButton")
        self.create_button = self.make_button("Erstellen", "ProductWizardCreateButton")
        self.cancel_button.clicked.connect(self.reject)
        self.back_button.clicked.connect(self.go_back)
        self.next_button.clicked.connect(self.go_next)
        self.create_button.clicked.connect(self.finish)
        buttons.addWidget(self.cancel_button)
        buttons.addWidget(self.back_button)
        buttons.addWidget(self.next_button)
        buttons.addWidget(self.create_button)

        layout.addWidget(self.title)
        layout.addWidget(self.hint)
        layout.addWidget(self.pages, 1)
        layout.addLayout(buttons)

    def build_identity_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(2, 4, 2, 4)
        layout.setSpacing(10)

        self.product_name = QLineEdit()
        self.product_name.setPlaceholderText("z. B. deskNode")
        self.product_name.setObjectName("ProductWizardInput")
        self.product_type = self.make_combo(PRODUCT_TYPES)

        family_label = QLabel(self.product_family)
        family_label.setObjectName("ProductWizardFixedValue")

        layout.addWidget(self.field_label("Produkt-/Projektname *"))
        layout.addWidget(self.product_name)
        layout.addWidget(self.field_label("Produktart *"))
        layout.addWidget(self.product_type)
        layout.addWidget(self.field_label("Produktfamilie"))
        layout.addWidget(family_label)
        layout.addStretch(1)
        return page

    def build_os_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(2, 4, 2, 4)
        layout.setSpacing(10)

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(10)

        for index, (key, label) in enumerate(OPERATING_SYSTEMS):
            checkbox = QCheckBox(label)
            checkbox.setObjectName("ProductWizardSwitch")
            checkbox.setChecked(key == "windows")
            self.checkboxes[key] = checkbox
            grid.addWidget(checkbox, index // 2, index % 2)

        layout.addLayout(grid)
        layout.addStretch(1)
        return page

    def build_summary_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(2, 4, 2, 4)

        self.summary = QLabel()
        self.summary.setObjectName("ProductWizardSummary")
        self.summary.setWordWrap(True)
        layout.addWidget(self.summary)
        layout.addStretch(1)
        return page

    def make_combo(self, entries) -> QComboBox:
        combo = QComboBox()
        combo.setObjectName("ProductWizardCombo")
        combo.addItem("Bitte wählen …", "")

        for key, label in entries:
            combo.addItem(label, key)

        return combo

    def make_button(self, text: str, object_name: str) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName(object_name)
        return button

    def field_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("ProductWizardLabel")
        return label

    def selected_operating_systems(self) -> list[str]:
        return [
            key
            for key, _ in OPERATING_SYSTEMS
            if self.checkboxes[key].isChecked()
        ]

    def selected_operating_system_labels(self) -> list[str]:
        return [
            label
            for key, label in OPERATING_SYSTEMS
            if self.checkboxes[key].isChecked()
        ]

    def go_back(self) -> None:
        self.pages.setCurrentIndex(max(0, self.pages.currentIndex() - 1))
        self.update_page()

    def go_next(self) -> None:
        if not self.validate_current_page():
            return

        self.pages.setCurrentIndex(min(2, self.pages.currentIndex() + 1))
        self.update_page()

    def update_page(self) -> None:
        index = self.pages.currentIndex()
        titles = (
            (
                "1 / 3 · Grunddaten",
                "Lege Produkt-/Projektname und Produktart fest. Die Produktfamilie wird automatisch aus dem Namen des Projektrootordners übernommen.",
            ),
            (
                "2 / 3 · Zielbetriebssysteme",
                "Windows ist vorausgewählt. Ergänze alle weiteren vorgesehenen Zielsysteme.",
            ),
            (
                "3 / 3 · Zusammenfassung",
                "Prüfe die Angaben. Erst mit Erstellen werden Datenbank, Ordner und Struktur angelegt.",
            ),
        )
        self.title.setText(titles[index][0])
        self.hint.setText(titles[index][1])
        self.back_button.setVisible(index > 0)
        self.next_button.setVisible(index < 2)
        self.create_button.setVisible(index == 2)

        if index == 2:
            self.refresh_summary()

    def validate_current_page(self) -> bool:
        index = self.pages.currentIndex()

        if index == 0:
            if not self.product_name.text().strip() or not self.product_type.currentData():
                return self.show_required_message(
                    "Bitte Produkt-/Projektname und Produktart auswählen."
                )

        if index == 1 and not self.selected_operating_systems():
            return self.show_required_message(
                "Mindestens ein Zielbetriebssystem muss ausgewählt werden."
            )

        return True

    def show_required_message(self, text: str) -> bool:
        QMessageBox.information(self, "Pflichtangaben", text)
        return False

    def refresh_summary(self) -> None:
        values = self.product_values()
        operating_systems = ", ".join(self.selected_operating_system_labels())
        self.summary.setText(
            "<b>Neuer Produktdatensatz</b><br><br>"
            f"<b>Name:</b> {values['product_name']}<br>"
            f"<b>Produktart:</b> {self.product_type.currentText()}<br>"
            f"<b>Produktfamilie:</b> {self.product_family}<br>"
            f"<b>Zielbetriebssysteme:</b> {operating_systems}<br><br>"
            "<b>Automatisch:</b> IDs, Slug, UUIDs, Zeitstempel, Versionsstart 0.1.0, "
            "Produktordner, Dokumentationstabellen und globale App-Ordnerstruktur.<br><br>"
            "<b>Später in der Push2Git-Synchronisation:</b> Repository, Lizenz und Veröffentlichungsangaben."
        )

    def product_values(self) -> dict[str, object]:
        return {
            "product_name": self.product_name.text().strip(),
            "product_family": self.product_family,
            "product_type": str(self.product_type.currentData() or ""),
            "target_operating_systems": self.selected_operating_systems(),
        }

    def finish(self) -> None:
        values = self.product_values()
        required = (
            values["product_name"],
            values["product_type"],
            values["target_operating_systems"],
        )

        if not all(required):
            self.show_required_message("Bitte alle Pflichtfelder vollständig festlegen.")
            return

        self.accept()

    def apply_style(self) -> None:
        self.setStyleSheet("""
            QDialog { background: #090d12; color: #eef8ff; }
            QLabel#ProductWizardTitle { color: #ffffff; font-size: 14pt; font-weight: 800; }
            QLabel#ProductWizardHint { color: #8fb8c5; font-size: 10pt; }
            QLabel#ProductWizardLabel { color: #d8e8ef; font-weight: 700; }
            QLabel#ProductWizardFixedValue { min-height: 30px; background: rgba(5, 20, 28, 220); color: #66deef; border: 1px solid rgba(40, 173, 198, 110); border-radius: 7px; padding: 4px 8px; font-weight: 700; }
            QLabel#ProductWizardSummary { background: rgba(3, 12, 17, 220); border: 1px solid rgba(40, 173, 198, 150); border-radius: 9px; padding: 14px; color: #eafaff; }
            QLineEdit#ProductWizardInput, QComboBox#ProductWizardCombo { min-height: 30px; background: rgba(2, 10, 15, 220); color: #eef8ff; border: 1px solid rgba(40, 173, 198, 145); border-radius: 7px; padding: 4px 8px; }
            QLineEdit#ProductWizardInput:focus, QComboBox#ProductWizardCombo:hover { border-color: #00e4ff; }
            QComboBox#ProductWizardCombo QAbstractItemView { background: #071017; color: #edf7ff; selection-background-color: rgba(0, 145, 170, 170); }
            QCheckBox#ProductWizardSwitch { min-height: 40px; padding: 0 12px; border: 1px solid rgba(40, 173, 198, 145); border-radius: 8px; background: rgba(4, 14, 20, 210); font-weight: 700; }
            QCheckBox#ProductWizardSwitch:hover { border-color: #00d8ff; background: rgba(0, 115, 140, 55); }
            QCheckBox#ProductWizardSwitch::indicator { width: 36px; height: 20px; margin-right: 9px; border: 1px solid #587783; border-radius: 10px; background: #1c313a; }
            QCheckBox#ProductWizardSwitch::indicator:checked { border-color: #00e4ff; background: #007f95; }
            QPushButton#ProductWizardCancelButton, QPushButton#ProductWizardBackButton, QPushButton#ProductWizardNextButton, QPushButton#ProductWizardCreateButton { min-height: 30px; border-radius: 7px; padding: 4px 12px; font-weight: 700; }
            QPushButton#ProductWizardCancelButton, QPushButton#ProductWizardBackButton { color: #ffffff; background: rgba(15, 28, 36, 220); border: 1px solid #387486; }
            QPushButton#ProductWizardNextButton, QPushButton#ProductWizardCreateButton { color: #ffffff; background: rgba(0, 137, 161, 190); border: 1px solid #00e4ff; }
            QPushButton#ProductWizardCancelButton:hover, QPushButton#ProductWizardBackButton:hover { border-color: #00d8ff; }
            QPushButton#ProductWizardNextButton:hover, QPushButton#ProductWizardCreateButton:hover { background: rgba(0, 179, 205, 215); }
        """)
