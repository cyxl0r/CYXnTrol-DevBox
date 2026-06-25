from __future__ import annotations

from subscripts.main_gui_devbox_log import get_devbox_logger
LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")


import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QLabel,
    QVBoxLayout,
)


OPERATING_SYSTEMS = (
    ("windows", "Windows"),
    ("linux", "Linux"),
    ("macos", "macOS"),
    ("android", "Android"),
    ("ios", "iOS"),
    ("debian_linux", "Debian/Linux (Raspberry Pi / Server)"),
    ("synology_nas", "Synology NAS (DSM)"),
    ("qnap_nas", "QNAP NAS (QTS / QuTS hero)"),
)


def parse_target_operating_systems(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]

    try:
        parsed = json.loads(str(value or "[]"))
    except (TypeError, ValueError, json.JSONDecodeError):
        return []

    return [str(item) for item in parsed] if isinstance(parsed, list) else []


def serialize_target_operating_systems(values: list[str]) -> str:
    valid_keys = {key for key, _ in OPERATING_SYSTEMS}
    selected = [key for key, _ in OPERATING_SYSTEMS if key in valid_keys and key in values]
    return json.dumps(selected, ensure_ascii=False, separators=(",", ":"))


class TargetOperatingSystemsDialog(QDialog):
    def __init__(self, selected_values: list[str] | None = None) -> None:
        super().__init__()
        self.selected_values = set(selected_values or ["windows"])
        self.checkboxes: dict[str, QCheckBox] = {}
        self.setWindowTitle("OS-Konfiguration")
        self.setModal(True)
        self.setMinimumWidth(560)
        self.build_ui()
        self.apply_style()

    def build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("Zielbetriebssysteme")
        title.setObjectName("TargetOsTitle")
        hint = QLabel("Aktiviere alle Betriebssysteme, für die dieses Produkt vorgesehen ist.")
        hint.setObjectName("TargetOsHint")
        hint.setWordWrap(True)

        grid = QGridLayout()
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(10)

        for index, (key, label) in enumerate(OPERATING_SYSTEMS):
            checkbox = QCheckBox(label)
            checkbox.setObjectName("TargetOsSwitch")
            checkbox.setChecked(key in self.selected_values)
            self.checkboxes[key] = checkbox
            grid.addWidget(checkbox, index // 2, index % 2)

        buttons = QDialogButtonBox()
        cancel_button = buttons.addButton("Abbrechen", QDialogButtonBox.RejectRole)
        accept_button = buttons.addButton("Übernehmen", QDialogButtonBox.AcceptRole)
        cancel_button.setObjectName("TargetOsCancelButton")
        accept_button.setObjectName("TargetOsAcceptButton")
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)

        layout.addWidget(title)
        layout.addWidget(hint)
        layout.addLayout(grid)
        layout.addWidget(buttons)

    def apply_style(self) -> None:
        self.setStyleSheet("""
            QDialog { background: #090d12; color: #eef8ff; }
            QLabel#TargetOsTitle { color: #ffffff; font-size: 14pt; font-weight: 800; }
            QLabel#TargetOsHint { color: #8fb8c5; font-size: 10pt; }
            QCheckBox#TargetOsSwitch {
                min-height: 40px; padding: 0 12px; border: 1px solid rgba(40, 173, 198, 145);
                border-radius: 8px; background: rgba(4, 14, 20, 210); font-weight: 700;
            }
            QCheckBox#TargetOsSwitch:hover { border-color: #00d8ff; background: rgba(0, 115, 140, 55); }
            QCheckBox#TargetOsSwitch::indicator {
                width: 36px; height: 20px; margin-right: 9px; border: 1px solid #587783;
                border-radius: 10px; background: #1c313a;
            }
            QCheckBox#TargetOsSwitch::indicator:checked {
                border-color: #00e4ff; background: #007f95;
            }
            QPushButton#TargetOsCancelButton, QPushButton#TargetOsAcceptButton {
                min-height: 30px; border-radius: 7px; padding: 4px 12px; font-weight: 700;
            }
            QPushButton#TargetOsCancelButton {
                color: #ffffff; background: rgba(8, 19, 27, 230);
                border: 1px solid rgba(78, 131, 147, 180);
            }
            QPushButton#TargetOsAcceptButton {
                color: #ffffff; background: rgba(0, 145, 170, 170);
                border: 1px solid #00e4ff;
            }
        """)

    def selected_operating_systems(self) -> list[str]:
        return [
            key
            for key, _ in OPERATING_SYSTEMS
            if self.checkboxes[key].isChecked()
        ]

    def accept(self) -> None:
        if not self.selected_operating_systems():
            return

        super().accept()
