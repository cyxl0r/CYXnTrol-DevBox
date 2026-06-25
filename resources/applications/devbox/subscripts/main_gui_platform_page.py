from __future__ import annotations

from subscripts.main_gui_devbox_log import get_devbox_logger
from subscripts.main_gui_platform_actions import (
    create_image_button,
    launch_installer,
    launch_python_script,
    launch_registered_application,
)
from subscripts.main_gui_tool_locations import get_registered_tool_path

LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")


from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget


def build_platform_page(studio) -> QWidget:
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(10, 12, 10, 10)
    layout.setSpacing(14)

    title = QLabel("Entwicklungsplattform")
    title.setObjectName("HeaderLabel")
    title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    layout.addWidget(title)

    subtitle = QLabel(
        "Grundlegende Projektplattform-Dateien und Installer für die "
        "Entwicklungsumgebung."
    )
    subtitle.setWordWrap(True)
    subtitle.setObjectName("Subtitle")
    layout.addWidget(subtitle)

    status_label = QLabel("Bereit.")
    status_label.setObjectName("PlatformStatus")
    status_label.setWordWrap(True)
    layout.addWidget(status_label)

    layout.addWidget(build_project_panel(studio, status_label))
    layout.addStretch(1)
    layout.addWidget(build_applications_panel(studio, status_label))
    layout.addWidget(build_installer_panel(studio, status_label))
    return page


def build_project_panel(studio, status_label: QLabel) -> QFrame:
    panel = create_panel()
    panel_layout = panel.layout()

    title = QLabel("Projektplattform")
    title.setObjectName("HeaderLabel")
    panel_layout.addWidget(title)

    buttons = QHBoxLayout()
    buttons.setSpacing(10)

    functions_path = (
        studio.project_root_path
        / "resources"
        / "applications"
        / "devbox"
        / "functions"
    )
    proof_of_concept_icon = (
        studio.project_root_path
        / "resources"
        / "graphics"
        / "batch_path7.png"
    )
    folder_icon = (
        studio.project_root_path
        / "resources"
        / "graphics"
        / "batch_path10.png"
    )

    proof_of_concept_button = create_image_button(
        proof_of_concept_icon,
        "Global Snapshot for Proof of Concept",
    )
    proof_of_concept_button.clicked.connect(
        lambda: launch_python_script(
            functions_path / "pof_root_snapshoter.py",
            status_label,
            "Global Snapshot for Proof of Concept wird erstellt.",
        )
    )
    buttons.addWidget(proof_of_concept_button)

    folder_button = create_image_button(
        folder_icon,
        "Projektordner öffnen",
    )
    folder_button.clicked.connect(
        lambda: launch_python_script(
            functions_path / "open_platform_folder.py",
            status_label,
            "Projektordner wird geöffnet.",
        )
    )
    buttons.addWidget(folder_button)

    repository_icon = (
        studio.project_root_path
        / "resources"
        / "graphics"
        / "batch_path9.png"
    )
    repository_button = create_image_button(
        repository_icon,
        "Repository-Site",
    )
    repository_button.clicked.connect(studio.open_repository_page)
    buttons.addWidget(repository_button)

    structure_icon = (
        studio.project_root_path
        / "resources"
        / "graphics"
        / "batch_path12.png"
    )
    structure_button = create_image_button(
        structure_icon,
        "Struktur-Einstellungen",
    )
    structure_button.setObjectName("StructureSettingsButton")
    structure_button.setProperty("active", False)
    structure_button.clicked.connect(
        lambda: studio.toggle_structure_settings_panel()
    )
    studio.register_structure_settings_button(structure_button)
    buttons.addWidget(structure_button)
    buttons.addStretch(1)

    panel_layout.addLayout(buttons)
    return panel


def build_applications_panel(studio, status_label: QLabel) -> QFrame:
    panel = create_panel()
    panel_layout = panel.layout()

    title = QLabel("Anwendungen")
    title.setObjectName("HeaderLabel")
    panel_layout.addWidget(title)

    buttons = QHBoxLayout()
    buttons.setSpacing(10)

    button_definitions = [
        (
            "inkscape",
            "inkscape.exe",
            "batch_path6.png",
            "batch_path11.png",
            "Inkscape starten",
            "Inkscape wird gestartet.",
        ),
        (
            "gimp",
            "gimp.exe",
            "batch_path8.png",
            "batch_path13.png",
            "GIMP starten",
            "GIMP wird gestartet.",
        ),
    ]

    for button_definition in button_definitions:
        buttons.addWidget(
            create_registered_app_button(
                studio,
                status_label,
                *button_definition,
            )
        )

    buttons.addStretch(1)
    panel_layout.addLayout(buttons)
    return panel


def build_installer_panel(studio, status_label: QLabel) -> QFrame:
    panel = create_panel()
    panel_layout = panel.layout()

    title = QLabel("Software für die Entwicklungsumgebung")
    title.setObjectName("HeaderLabel")
    panel_layout.addWidget(title)

    buttons = QHBoxLayout()
    buttons.setSpacing(10)
    installer_root = (
        studio.project_root_path
        / "resources"
        / "third_party_installers"
    )

    installers = [
        ("Python Manager", "python-manager-26.2.msix"),
        (".NET SDK", "dotnet-sdk-8.0.422-win-x64.exe"),
        ("WiX Toolset", "wix314.exe"),
        ("GIMP installieren", "gimp-3.2.4-setup.exe"),
        (
            "Inkscape installieren",
            "inkscape-1.4.2_2025-05-13_f4327f4-x64.msi",
        ),
    ]

    for label, filename in installers:
        button = QPushButton(label)
        button.setObjectName("SecondaryButton")
        button.setMinimumWidth(145)
        button.clicked.connect(
            lambda checked=False, p=installer_root / filename, name=label:
            launch_installer(p, status_label, f"{name} gestartet.")
        )
        buttons.addWidget(button)

    buttons.addStretch(1)
    panel_layout.addLayout(buttons)
    return panel


def create_panel() -> QFrame:
    panel = QFrame()
    panel.setObjectName("GridContainer")

    layout = QVBoxLayout(panel)
    layout.setContentsMargins(14, 14, 14, 14)
    layout.setSpacing(10)
    return panel


def create_registered_app_button(
    studio,
    status_label: QLabel,
    tool_key: str,
    executable_name: str,
    found_icon_name: str,
    missing_icon_name: str,
    tooltip: str,
    success_message: str,
) -> QPushButton:
    executable_path = get_registered_tool_path(
        tool_key,
        executable_name,
    )
    icon_name = found_icon_name if executable_path else missing_icon_name
    icon_path = (
        studio.project_root_path
        / "resources"
        / "graphics"
        / icon_name
    )
    button = create_image_button(icon_path, tooltip)
    button.setEnabled(executable_path is not None)

    if executable_path is not None:
        button.clicked.connect(
            lambda checked=False, p=executable_path, n=executable_name:
            launch_registered_application(
                p,
                n,
                status_label,
                success_message,
            )
        )

    return button
