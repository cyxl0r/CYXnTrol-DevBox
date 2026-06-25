from __future__ import annotations

from subscripts.main_gui_devbox_log import get_devbox_logger
LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")


from PySide6.QtWidgets import (
    QFormLayout,
    QFrame,
    QLabel,
    QLineEdit,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from subscripts.main_gui_manufacturer_setup_store import current_year


def wizard_input(placeholder: str = "") -> QLineEdit:
    field = QLineEdit()
    field.setObjectName("ManufacturerWizardInput")
    field.setPlaceholderText(placeholder)
    return field


def build_basic_page(wizard) -> QWidget:
    page = QWidget()
    form = QFormLayout(page)
    form.setContentsMargins(2, 4, 2, 4)
    form.setSpacing(10)

    family_value = QLabel(wizard.product_family)
    family_value.setObjectName("ManufacturerWizardFixedValue")
    family_value.setToolTip("Automatisch aus dem Namen des Projektrootordners abgeleitet.")

    wizard.manufacturer_name = wizard_input("z. B. CYXLabs")
    wizard.founded_year = wizard.make_year_input(current_year())
    wizard.country = wizard_input("z. B. Germany")
    wizard.country.setText("Germany")
    wizard.country_code = wizard_input("z. B. DE")
    wizard.country_code.setText("DE")
    wizard.country_code.setMaxLength(2)

    form.addRow(wizard.field_label("Produktfamilie"), family_value)
    form.addRow(wizard.field_label("Manufaktur- / Dachname *"), wizard.manufacturer_name)
    form.addRow(wizard.field_label("Gründungsjahr *"), wizard.founded_year)
    form.addRow(wizard.field_label("Land *"), wizard.country)
    form.addRow(wizard.field_label("Ländercode (ISO 3166-1 Alpha-2) *"), wizard.country_code)
    return page


def build_organization_page(wizard) -> QWidget:
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(2, 4, 2, 4)
    layout.setSpacing(10)

    instruction = QLabel(
        "Lege die Organisationsform sowie die dauerhaft zu verwendenden Rollenangaben "
        "für die Manufaktur fest."
    )
    instruction.setObjectName("ManufacturerWizardHint")
    instruction.setWordWrap(True)
    layout.addWidget(instruction)

    wizard.formal_radio = QRadioButton("Formale Organisation")
    wizard.formal_radio.setObjectName("ManufacturerWizardRadio")
    wizard.fantasy_radio = QRadioButton("Fantasie- / Markenorganisation")
    wizard.fantasy_radio.setObjectName("ManufacturerWizardRadio")
    wizard.organization_group.addButton(wizard.formal_radio)
    wizard.organization_group.addButton(wizard.fantasy_radio)
    wizard.organization_group.buttonToggled.connect(wizard.update_organization_form)
    layout.addWidget(wizard.formal_radio)
    layout.addWidget(wizard.fantasy_radio)

    wizard.organization_form = QFrame()
    wizard.organization_form.setObjectName("ManufacturerWizardCard")
    organization_layout = QFormLayout(wizard.organization_form)
    organization_layout.setContentsMargins(12, 10, 12, 12)
    organization_layout.setSpacing(9)

    wizard.organization_name = wizard_input("Name der formalen Organisation")
    wizard.owner_name = wizard_input("Name der Person hinter der Markenorganisation")
    wizard.organization_name_label = wizard.field_label("Name der Organisation *")
    wizard.owner_name_label = wizard.field_label("Person hinter der Organisation *")
    organization_layout.addRow(wizard.organization_name_label, wizard.organization_name)
    organization_layout.addRow(wizard.owner_name_label, wizard.owner_name)
    layout.addWidget(wizard.organization_form)

    roles = QFrame()
    roles.setObjectName("ManufacturerWizardCard")
    roles_layout = QFormLayout(roles)
    roles_layout.setContentsMargins(12, 10, 12, 12)
    roles_layout.setSpacing(9)
    roles_title = QLabel("Manufaktur-Rollen")
    roles_title.setObjectName("ManufacturerWizardSectionTitle")
    roles_layout.addRow(roles_title)
    wizard.author_name = wizard_input("Name der verantwortlichen Person")
    wizard.author_display_name = wizard_input("Öffentlich angezeigter Autorenname")
    wizard.publisher_name = wizard_input("z. B. CYXLabs")
    wizard.developer_name = wizard_input("z. B. CYXLabs")
    wizard.vendor_name = wizard_input("Optional, nur wenn abweichend")
    roles_layout.addRow(wizard.field_label("Autor / Urheber *"), wizard.author_name)
    roles_layout.addRow(wizard.field_label("Autor-Anzeigename *"), wizard.author_display_name)
    roles_layout.addRow(wizard.field_label("Herausgeber / Publisher *"), wizard.publisher_name)
    roles_layout.addRow(wizard.field_label("Entwicklername *"), wizard.developer_name)
    roles_layout.addRow(wizard.field_label("Anbieter / Vendor"), wizard.vendor_name)
    layout.addWidget(roles)
    layout.addStretch(1)

    wizard.organization_name.textChanged.connect(wizard.refresh_role_defaults)
    wizard.owner_name.textChanged.connect(wizard.refresh_role_defaults)
    wizard.manufacturer_name.textChanged.connect(wizard.refresh_role_defaults)
    wizard.update_organization_form()
    return page


def build_contact_page(wizard) -> QWidget:
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(2, 4, 2, 4)
    layout.setSpacing(10)

    hint = QLabel(
        "Diese Angaben werden für spätere README-, Lizenz-, Support- und "
        "Veröffentlichungsdokumente gespeichert. Nicht vorhandene öffentliche "
        "Adressen können leer bleiben."
    )
    hint.setObjectName("ManufacturerWizardHint")
    hint.setWordWrap(True)
    layout.addWidget(hint)

    card = QFrame()
    card.setObjectName("ManufacturerWizardCard")
    form = QFormLayout(card)
    form.setContentsMargins(12, 10, 12, 12)
    form.setSpacing(9)

    wizard.region = wizard_input("Optional")
    wizard.city = wizard_input("Optional")
    wizard.website_url = wizard_input("z. B. https://example.org")
    wizard.contact_email = wizard_input("z. B. kontakt@example.org")
    wizard.support_email = wizard_input("z. B. support@example.org")
    wizard.support_url = wizard_input("z. B. https://example.org/support")
    wizard.privacy_policy_url = wizard_input("Optional")
    wizard.terms_url = wizard_input("Optional")

    form.addRow(wizard.field_label("Region / Bundesland"), wizard.region)
    form.addRow(wizard.field_label("Stadt"), wizard.city)
    form.addRow(wizard.field_label("Domain / Website"), wizard.website_url)
    form.addRow(wizard.field_label("Kontaktadresse (E-Mail)"), wizard.contact_email)
    form.addRow(wizard.field_label("Supportadresse (E-Mail)"), wizard.support_email)
    form.addRow(wizard.field_label("Support-URL"), wizard.support_url)
    form.addRow(wizard.field_label("Datenschutz-URL"), wizard.privacy_policy_url)
    form.addRow(wizard.field_label("Nutzungsbedingungen-URL"), wizard.terms_url)
    layout.addWidget(card)
    layout.addStretch(1)
    return page


def build_devbox_page(wizard) -> QWidget:
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(2, 4, 2, 4)
    layout.setSpacing(10)

    hint = QLabel(
        "Diese Angaben gehören zum Produkt DevBox selbst. Sie können von den "
        "Dach-Daten abweichen und werden direkt im DevBox-Produktdatensatz gespeichert."
    )
    hint.setObjectName("ManufacturerWizardHint")
    hint.setWordWrap(True)
    layout.addWidget(hint)

    card = QFrame()
    card.setObjectName("ManufacturerWizardCard")
    form = QFormLayout(card)
    form.setContentsMargins(12, 10, 12, 12)
    form.setSpacing(9)

    display_name = QLabel(f"{wizard.product_family} DevBox")
    display_name.setObjectName("ManufacturerWizardFixedValue")
    license_name = QLabel("Zero-Clause BSD License · 0BSD")
    license_name.setObjectName("ManufacturerWizardFixedValue")
    wizard.devbox_author = wizard_input("Autor / Urheber von DevBox")
    wizard.devbox_publisher = wizard_input("Herausgeber von DevBox")
    wizard.devbox_vendor = wizard_input("Optional, nur wenn abweichend")
    wizard.devbox_copyright_holder = wizard_input("Copyright-Inhaber")
    wizard.devbox_homepage_url = wizard_input("Optional")
    wizard.devbox_support_url = wizard_input("Optional")

    form.addRow(wizard.field_label("DevBox-Produktname"), display_name)
    form.addRow(wizard.field_label("Lizenz"), license_name)
    form.addRow(wizard.field_label("DevBox-Autor / Urheber *"), wizard.devbox_author)
    form.addRow(wizard.field_label("DevBox-Herausgeber *"), wizard.devbox_publisher)
    form.addRow(wizard.field_label("DevBox-Anbieter / Vendor"), wizard.devbox_vendor)
    form.addRow(wizard.field_label("DevBox-Copyright-Inhaber *"), wizard.devbox_copyright_holder)
    form.addRow(wizard.field_label("DevBox-Homepage"), wizard.devbox_homepage_url)
    form.addRow(wizard.field_label("DevBox-Support-URL"), wizard.devbox_support_url)
    layout.addWidget(card)
    layout.addStretch(1)
    return page


def build_summary_page(wizard) -> QWidget:
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(2, 4, 2, 4)
    wizard.summary = QLabel()
    wizard.summary.setObjectName("ManufacturerWizardSummary")
    wizard.summary.setWordWrap(True)
    layout.addWidget(wizard.summary)
    layout.addStretch(1)
    return page
