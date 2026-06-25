from __future__ import annotations

from subscripts.main_gui_devbox_log import get_devbox_logger
LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")


from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
)

from subscripts.main_gui_manufacturer_setup_store import persist_first_start_values
from subscripts.main_gui_manufacturer_wizard_pages import (
    build_basic_page,
    build_contact_page,
    build_devbox_page,
    build_organization_page,
    build_summary_page,
)
from subscripts.main_gui_manufacturer_wizard_style import apply_manufacturer_wizard_style
from subscripts.main_gui_manufacturer_wizard_values import (
    devbox_values,
    manufacturer_values,
    summary_html,
)


class ManufacturerFirstStartWizard(QDialog):
    def __init__(self, project_root_path: Path, parent=None) -> None:
        super().__init__(parent)
        self.project_root_path = Path(project_root_path).resolve()
        self.product_family = self.project_root_path.name.strip()
        self.organization_group = QButtonGroup(self)
        self.setWindowTitle("DevBox · Manufaktur einrichten")
        self.setModal(True)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.setMinimumWidth(700)
        self.resize(780, 650)
        self.build_ui()
        apply_manufacturer_wizard_style(self)
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
        self.title.setObjectName("ManufacturerWizardTitle")
        self.hint = QLabel()
        self.hint.setObjectName("ManufacturerWizardHint")
        self.hint.setWordWrap(True)
        self.pages = QStackedWidget()
        self.pages.addWidget(build_basic_page(self))
        self.pages.addWidget(build_organization_page(self))
        self.pages.addWidget(build_contact_page(self))
        self.pages.addWidget(build_devbox_page(self))
        self.pages.addWidget(build_summary_page(self))

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        self.cancel_button = self.make_button("Abbrechen", "ManufacturerWizardCancelButton")
        self.back_button = self.make_button("Zurück", "ManufacturerWizardBackButton")
        self.next_button = self.make_button("Weiter", "ManufacturerWizardNextButton")
        self.finish_button = self.make_button("Einrichtung abschließen", "ManufacturerWizardFinishButton")
        self.cancel_button.clicked.connect(self.reject)
        self.back_button.clicked.connect(self.go_back)
        self.next_button.clicked.connect(self.go_next)
        self.finish_button.clicked.connect(self.finish)
        for button in (self.cancel_button, self.back_button, self.next_button, self.finish_button):
            buttons.addWidget(button)

        layout.addWidget(self.title)
        layout.addWidget(self.hint)
        layout.addWidget(self.pages, 1)
        layout.addLayout(buttons)

    def make_button(self, text: str, object_name: str) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName(object_name)
        return button

    def field_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("ManufacturerWizardLabel")
        return label

    def make_year_input(self, current_year: int) -> QSpinBox:
        input_box = QSpinBox()
        input_box.setObjectName("ManufacturerWizardSpinBox")
        input_box.setRange(1000, current_year)
        input_box.setValue(current_year)
        return input_box

    def organization_type(self) -> str:
        if self.formal_radio.isChecked():
            return "formal_organization"
        if self.fantasy_radio.isChecked():
            return "fantasy_organization"
        return ""

    def set_text_if_empty(self, field, value: str) -> None:
        if not field.text().strip() and value:
            field.setText(value)

    def update_organization_form(self) -> None:
        formal = self.formal_radio.isChecked()
        fantasy = self.fantasy_radio.isChecked()
        self.organization_name_label.setVisible(formal)
        self.organization_name.setVisible(formal)
        self.owner_name_label.setVisible(fantasy)
        self.owner_name.setVisible(fantasy)
        self.refresh_role_defaults()

    def refresh_role_defaults(self) -> None:
        manufacturer_name = self.manufacturer_name.text().strip()
        owner_name = self.owner_name.text().strip()
        organization_name = self.organization_name.text().strip()
        person_name = owner_name if self.fantasy_radio.isChecked() else ""
        self.set_text_if_empty(self.author_name, person_name)
        self.set_text_if_empty(self.author_display_name, person_name)
        self.set_text_if_empty(self.publisher_name, manufacturer_name)
        self.set_text_if_empty(self.developer_name, manufacturer_name)
        if not hasattr(self, "devbox_author"):
            return

        copyright_holder = person_name or organization_name or manufacturer_name
        self.set_text_if_empty(self.devbox_author, self.author_name.text().strip() or person_name)
        self.set_text_if_empty(self.devbox_publisher, self.publisher_name.text().strip() or manufacturer_name)
        self.set_text_if_empty(self.devbox_vendor, self.vendor_name.text().strip())
        self.set_text_if_empty(self.devbox_copyright_holder, copyright_holder)
        self.set_text_if_empty(self.devbox_homepage_url, self.website_url.text().strip())
        self.set_text_if_empty(self.devbox_support_url, self.support_url.text().strip())

    def go_back(self) -> None:
        self.pages.setCurrentIndex(max(0, self.pages.currentIndex() - 1))
        self.update_page()

    def go_next(self) -> None:
        if not self.validate_current_page():
            return
        self.pages.setCurrentIndex(min(self.pages.count() - 1, self.pages.currentIndex() + 1))
        self.update_page()

    def update_page(self) -> None:
        index = self.pages.currentIndex()
        titles = (
            (
                "1 / 5 · Manufaktur-Grunddaten",
                "Lege Dachname, Gründungsjahr und Land fest. Die Produktfamilie wird aus dem Projektroot übernommen.",
            ),
            (
                "2 / 5 · Organisationsform und Rollen",
                "Lege fest, wer hinter der Manufaktur steht und welche Autoren-, Publisher- und Entwicklerangaben verwendet werden.",
            ),
            (
                "3 / 5 · Kontakt und Präsenz",
                "Trage vorhandene öffentliche Domain-, Kontakt- und Supportangaben ein. Nicht vorhandene Angaben bleiben leer.",
            ),
            (
                "4 / 5 · DevBox-Produktdaten",
                "Lege die Autoren-, Herausgeber- und Copyright-Angaben für DevBox als eigenständiges Produkt fest.",
            ),
            (
                "5 / 5 · Zusammenfassung",
                "Erst mit Abschluss werden der echte Manufakturdatensatz und die DevBox-Produktdaten gespeichert.",
            ),
        )
        self.title.setText(titles[index][0])
        self.hint.setText(titles[index][1])
        self.back_button.setVisible(index > 0)
        self.next_button.setVisible(index < self.pages.count() - 1)
        self.finish_button.setVisible(index == self.pages.count() - 1)
        self.refresh_role_defaults()
        if index == self.pages.count() - 1:
            self.refresh_summary()

    def validate_current_page(self) -> bool:
        index = self.pages.currentIndex()
        if index == 0:
            if not self.manufacturer_name.text().strip():
                return self.show_required_message("Bitte den Manufaktur- / Dachnamen eintragen.")
            if not self.country.text().strip():
                return self.show_required_message("Bitte das Land eintragen.")
            country_code = self.country_code.text().strip()
            if len(country_code) != 2 or not country_code.isalpha():
                return self.show_required_message(
                    "Bitte einen zweistelligen Ländercode nach ISO 3166-1 Alpha-2 eintragen."
                )
            return True
        if index == 1:
            organization_type = self.organization_type()
            if not organization_type:
                return self.show_required_message("Bitte die Organisationsform auswählen.")
            if organization_type == "formal_organization" and not self.organization_name.text().strip():
                return self.show_required_message("Bitte den Namen der formalen Organisation eintragen.")
            if organization_type == "fantasy_organization" and not self.owner_name.text().strip():
                return self.show_required_message(
                    "Bitte die Person hinter der Markenorganisation eintragen."
                )
            for field, label in (
                (self.author_name, "Autor / Urheber"),
                (self.author_display_name, "Autor-Anzeigename"),
                (self.publisher_name, "Herausgeber / Publisher"),
                (self.developer_name, "Entwicklername"),
            ):
                if not field.text().strip():
                    return self.show_required_message(f"Bitte {label} eintragen.")
            return True
        if index == 3:
            for field, label in (
                (self.devbox_author, "DevBox-Autor / Urheber"),
                (self.devbox_publisher, "DevBox-Herausgeber"),
                (self.devbox_copyright_holder, "DevBox-Copyright-Inhaber"),
            ):
                if not field.text().strip():
                    return self.show_required_message(f"Bitte {label} eintragen.")
        return True

    def show_required_message(self, text: str) -> bool:
        QMessageBox.information(self, "Pflichtangaben", text)
        return False

    def values(self) -> dict[str, object]:
        return manufacturer_values(self)

    def devbox_values(self) -> dict[str, object]:
        return devbox_values(self)

    def refresh_summary(self) -> None:
        self.summary.setText(summary_html(self.values(), self.devbox_values()))

    def finish(self) -> None:
        if self.validate_current_page():
            self.accept()

    def persist(self) -> int:
        return persist_first_start_values(
            self.project_root_path,
            self.values(),
            self.devbox_values(),
        )
