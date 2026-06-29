from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from subscripts.main_gui_desknode_ux_defaults import (
    DEFAULT_SETTINGS,
    FONT_ROLES,
    OUTLINE_STYLES,
)
from subscripts.main_gui_desknode_ux_widgets import build_rgba_input


FONT_LABELS = {
    "headline": "Große Überschrift",
    "section": "Bereichsüberschrift",
    "body": "Standardtext",
    "button": "Schaltflächentext",
    "input": "Eingabefeldtext",
    "status": "Statusmeldung",
    "log": "Protokolltext",
}

COLOR_LABELS = {
    "page_background_rgba": "Seitenhintergrund",
    "panel_rgba": "Bereichsfläche",
    "input_rgba": "Eingabefeld",
    "button_rgba": "Schaltfläche",
    "button_hover_rgba": "Schaltfläche bei Mauskontakt",
    "button_pressed_rgba": "Schaltfläche gedrückt",
    "button_running_rgba": "Prozess läuft",
    "button_running_hover_rgba": "Prozess läuft bei Mauskontakt",
    "button_disabled_rgba": "Deaktivierte Schaltfläche",
    "outline_default_rgba": "Standardkontur",
    "outline_hover_rgba": "Kontur bei Mauskontakt",
    "outline_running_rgba": "Kontur Prozess läuft",
    "outline_running_hover_rgba": "Kontur Prozess läuft bei Mauskontakt",
    "outline_disabled_rgba": "Deaktivierte Kontur",
    "status_rgba": "Statusfläche",
    "log_rgba": "Protokollhintergrund",
    "path_rgba": "Pfadhintergrund",
    "glow_on_rgba": "Glow-on",
    "glow_off_rgba": "Glow-off",
    "non_off_rgba": "Non-off",
}


def build_editor(view) -> QScrollArea:
    scroll = QScrollArea()
    scroll.setObjectName("DeskNodeUxScroll")
    scroll.setWidgetResizable(True)
    container = QWidget()
    layout = QVBoxLayout(container)
    layout.setContentsMargins(12, 12, 12, 12)
    tabs = QTabWidget()
    tabs.setObjectName("DeskNodeUxTabs")
    tabs.addTab(build_color_tab(view), "Farben")
    tabs.addTab(build_font_tab(view), "Schrift")
    tabs.addTab(build_shape_tab(view), "Formen und Konturen")
    layout.addWidget(tabs)
    scroll.setWidget(container)
    return scroll


def build_color_tab(view) -> QWidget:
    tab = QWidget()
    form = QFormLayout(tab)
    form.setContentsMargins(16, 16, 16, 16)
    form.setHorizontalSpacing(18)
    form.setVerticalSpacing(10)

    for key, label in COLOR_LABELS.items():
        editor, field = build_rgba_input(
            str(DEFAULT_SETTINGS[key]),
            view.update_preview,
        )
        view.color_inputs[key] = field
        form.addRow(QLabel(label), editor)
    return tab


def build_font_tab(view) -> QWidget:
    tab = QWidget()
    layout = QVBoxLayout(tab)
    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(10)
    hint = QLabel(
        "Die Auswahl liest .ttf- und .otf-Dateien rekursiv aus "
        "resources/fonts."
    )
    hint.setWordWrap(True)
    hint.setObjectName("DeskNodeUxHint")
    layout.addWidget(hint)

    for role in FONT_ROLES:
        layout.addWidget(build_font_group(view, role))

    reload_button = QPushButton("Schriftdateien neu einlesen")
    reload_button.setObjectName("DeskNodeUxActionButton")
    reload_button.clicked.connect(
        lambda _checked=False: view.reload_font_choices()
    )
    layout.addWidget(reload_button, alignment=Qt.AlignmentFlag.AlignLeft)
    layout.addStretch(1)
    return tab


def build_font_group(view, role: str) -> QGroupBox:
    group = QGroupBox(FONT_LABELS[role])
    group.setObjectName("DeskNodeUxFontGroup")
    grid = QGridLayout(group)
    grid.setHorizontalSpacing(10)
    grid.setVerticalSpacing(7)
    combo = QComboBox()
    combo.setObjectName("DeskNodeUxFontCombo")
    color_editor, color_field = build_rgba_input(
        str(DEFAULT_SETTINGS[f"{role}_font_rgba"]),
        view.update_preview,
    )
    size = QSpinBox()
    size.setRange(6, 72)
    size.setValue(int(DEFAULT_SETTINGS[f"{role}_font_size"]))
    size.setObjectName("DeskNodeUxNumberInput")
    bold = QCheckBox("Fett")
    italic = QCheckBox("Kursiv")
    underline = QCheckBox("Unterstrichen")
    grid.addWidget(QLabel("Schriftdatei"), 0, 0)
    grid.addWidget(combo, 0, 1, 1, 4)
    grid.addWidget(QLabel("Farbe"), 1, 0)
    grid.addWidget(color_editor, 1, 1)
    grid.addWidget(QLabel("Größe"), 1, 2)
    grid.addWidget(size, 1, 3)
    grid.addWidget(bold, 2, 1)
    grid.addWidget(italic, 2, 2)
    grid.addWidget(underline, 2, 3)
    view.font_controls[role] = (combo, color_field, size, bold, italic, underline)
    combo.currentIndexChanged.connect(lambda _index: view.update_preview())
    size.valueChanged.connect(lambda _value: view.update_preview())
    bold.toggled.connect(lambda _value: view.update_preview())
    italic.toggled.connect(lambda _value: view.update_preview())
    underline.toggled.connect(lambda _value: view.update_preview())
    return group


def build_shape_tab(view) -> QWidget:
    tab = QWidget()
    form = QFormLayout(tab)
    form.setContentsMargins(16, 16, 16, 16)
    form.setHorizontalSpacing(18)
    form.setVerticalSpacing(12)
    limits = {
        "panel_radius": ("Eckenradius Bereiche", 0, 64),
        "button_radius": ("Eckenradius Schaltflächen", 0, 64),
        "input_radius": ("Eckenradius Eingabefelder", 0, 64),
        "outline_default_width": ("Konturstärke Standard", 0, 12),
        "outline_running_width": ("Konturstärke Prozess läuft", 0, 12),
    }
    for key, (label, minimum, maximum) in limits.items():
        input_field = QSpinBox()
        input_field.setRange(minimum, maximum)
        input_field.setValue(int(DEFAULT_SETTINGS[key]))
        input_field.setObjectName("DeskNodeUxNumberInput")
        input_field.valueChanged.connect(lambda _value: view.update_preview())
        view.number_controls[key] = input_field
        form.addRow(QLabel(label), input_field)

    view.outline_style_combo = QComboBox()
    view.outline_style_combo.setObjectName("DeskNodeUxFontCombo")
    view.outline_style_combo.addItems(OUTLINE_STYLES)
    view.outline_style_combo.currentIndexChanged.connect(
        lambda _index: view.update_preview()
    )
    form.addRow(QLabel("Konturart"), view.outline_style_combo)
    return tab
