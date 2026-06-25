from __future__ import annotations

from subscripts.main_gui_devbox_log import get_devbox_logger
from subscripts.main_gui_tool_locations import start_registered_tool

LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")


import os
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel, QPushButton


def create_image_button(image_path: Path, tooltip: str) -> QPushButton:
    button = QPushButton()
    button.setObjectName("ImageButton")
    button.setToolTip(tooltip)
    button.setAccessibleName(tooltip)
    button.setMinimumSize(145, 36)

    image_path = Path(image_path)

    if image_path.is_file():
        button.setIcon(QIcon(str(image_path)))
    else:
        LOGGER.warning("Button image was not found.", str(image_path))

    button.setIconSize(QSize(132, 30))
    return button


def launch_registered_application(
    executable_path: Path,
    executable_name: str,
    status_label: QLabel,
    success_message: str,
) -> None:
    started, error_text = start_registered_tool(
        executable_path,
        executable_name,
    )

    if started:
        status_label.setText(success_message)
    else:
        status_label.setText(error_text)


def launch_installer(
    path: Path,
    status_label: QLabel,
    success_message: str,
) -> None:
    path = Path(path).resolve()

    if not path.is_file():
        status_label.setText(f"Installer nicht gefunden: {path}")
        return

    try:
        if path.suffix.lower() == ".msi" and sys.platform == "win32":
            subprocess.Popen(
                ["msiexec.exe", "/i", str(path)],
                cwd=str(path.parent),
            )
        elif hasattr(os, "startfile"):
            os.startfile(str(path))
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])

        status_label.setText(success_message)
        LOGGER.info("Installer started.", str(path))
    except OSError as error:
        status_label.setText(
            "Installer konnte nicht gestartet werden: "
            f"{type(error).__name__}: {error}"
        )
        LOGGER.error(
            "Could not start installer.",
            f"{path}: {type(error).__name__}: {error}",
        )


def launch_file(
    path: Path,
    status_label: QLabel,
    success_message: str,
) -> None:
    path = Path(path).resolve()

    if not path.exists():
        status_label.setText(f"File not found: {path}")
        return

    try:
        if hasattr(os, "startfile"):
            os.startfile(str(path))
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
        status_label.setText(success_message)
    except OSError as error:
        status_label.setText(
            f"Could not open file: {type(error).__name__}: {error}"
        )


def launch_python_script(
    path: Path,
    status_label: QLabel,
    success_message: str,
) -> None:
    path = Path(path).resolve()

    if not path.is_file():
        status_label.setText(f"File not found: {path}")
        return

    try:
        subprocess.Popen(
            [sys.executable, str(path)],
            cwd=str(path.parent),
        )
        status_label.setText(success_message)
    except OSError as error:
        status_label.setText(
            f"Could not run script: {type(error).__name__}: {error}"
        )
