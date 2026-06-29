from __future__ import annotations

import sqlite3

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton

from subscripts.main_gui_desknode_version_data import (
    read_desknode_version,
    save_desknode_version,
)
from subscripts.main_gui_desknode_version_refresh import (
    start_manufacturer_database_refresh,
)
from subscripts.main_gui_devbox_log import get_devbox_logger


LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")

PAGE_KEY = "desknode"


def version_controls(studio) -> QFrame:
    panel = QFrame()
    panel.setObjectName("DeskNodeVersionPanel")
    panel.hide()

    layout = QHBoxLayout(panel)
    layout.setContentsMargins(12, 8, 12, 8)
    layout.setSpacing(10)

    label = QLabel("deskNode-Version")
    label.setObjectName("HeaderLabel")
    layout.addWidget(label)

    version_input = QLineEdit()
    version_input.setObjectName("DeskNodeVersionInput")
    version_input.setPlaceholderText("z. B. 0.1.0")
    version_input.setClearButtonEnabled(True)
    version_input.setMinimumWidth(260)
    layout.addWidget(version_input, stretch=1)

    save_button = QPushButton("Speichern")
    save_button.setObjectName("DeskNodeVersionSaveButton")
    save_button.setMinimumWidth(150)
    layout.addWidget(save_button)

    studio.desknode_version_panel = panel
    studio.desknode_version_input = version_input
    studio.desknode_version_save_button = save_button

    save_button.clicked.connect(
        lambda _checked=False: save_version_and_refresh_database(studio)
    )

    return panel


def show_desknode_version(studio) -> None:
    panel = getattr(studio, "desknode_version_panel", None)
    version_input = getattr(studio, "desknode_version_input", None)

    if panel is None or version_input is None:
        studio.set_status(
            "Versionseingabe konnte nicht vorbereitet werden.",
            "error",
            PAGE_KEY,
        )
        studio.append_log(
            "Fehler: deskNode-Versionseingabe fehlt.",
            PAGE_KEY,
        )
        return

    try:
        version_text = read_desknode_version(studio)
    except (OSError, RuntimeError, sqlite3.Error) as error:
        studio.set_status(
            "deskNode-Version konnte nicht geladen werden.",
            "error",
            PAGE_KEY,
        )
        studio.append_log(
            f"Fehler beim Laden der deskNode-Version: {error}",
            PAGE_KEY,
        )
        LOGGER.warning(
            "deskNode version could not be loaded.",
            str(error),
        )
        return

    version_input.setText(version_text)
    panel.show()
    version_input.setFocus()
    version_input.selectAll()
    studio.set_status(
        "deskNode-Version geladen.",
        "neutral",
        PAGE_KEY,
    )
    studio.append_log(
        f"deskNode-Version geladen: {version_text or '(leer)'}",
        PAGE_KEY,
    )
    LOGGER.info(
        "deskNode version loaded.",
        f"version={version_text}",
    )


def save_version_and_refresh_database(studio) -> None:
    version_input = getattr(studio, "desknode_version_input", None)

    if version_input is None:
        studio.set_status("Versionseingabe fehlt.", "error", PAGE_KEY)
        return

    version_text = version_input.text().strip()

    if not version_text:
        studio.set_status(
            "Die deskNode-Version darf nicht leer sein.",
            "warning",
            PAGE_KEY,
        )
        studio.append_log(
            "Speichern abgebrochen: Die deskNode-Version ist leer.",
            PAGE_KEY,
        )
        return

    try:
        save_desknode_version(studio, version_text)
    except (OSError, RuntimeError, sqlite3.Error) as error:
        studio.set_status(
            "deskNode-Version konnte nicht gespeichert werden.",
            "error",
            PAGE_KEY,
        )
        studio.append_log(
            f"Fehler beim Speichern der deskNode-Version: {error}",
            PAGE_KEY,
        )
        LOGGER.warning(
            "deskNode version could not be stored.",
            str(error),
        )
        return

    studio.append_log(
        f"deskNode-Version gespeichert: {version_text}",
        PAGE_KEY,
    )
    LOGGER.info(
        "deskNode version stored.",
        f"version={version_text}",
    )
    start_manufacturer_database_refresh(
        studio,
        saved_subject="Version",
        controls_to_lock=(
            "desknode_version_button",
            "desknode_version_save_button",
            "desknode_version_input",
        ),
    )
