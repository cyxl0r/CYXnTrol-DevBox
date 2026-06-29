from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)


def build_preview() -> QFrame:
    preview = QFrame()
    preview.setObjectName("DeskNodeUxPreview")
    layout = QVBoxLayout(preview)
    layout.setContentsMargins(18, 18, 18, 18)
    layout.setSpacing(12)

    title = QLabel("deskNode")
    title.setObjectName("HeaderLabel")
    layout.addWidget(title)

    section = QLabel("Vorschau")
    section.setObjectName("DeskNodePreviewSection")
    layout.addWidget(section)

    path = QLabel("Ziel: applications/deskNode/logic/supervisor.py")
    path.setObjectName("PathLabel")
    path.setWordWrap(True)
    layout.addWidget(path)

    run_button = QPushButton("deskNode ausführen")
    run_button.setObjectName("DeskNodeExecuteButton")
    layout.addWidget(run_button)

    running_button = QPushButton("Daemon wird ausgeführt")
    running_button.setObjectName("DeskNodeExecuteButton")
    running_button.setProperty("running", True)
    layout.addWidget(running_button)

    disabled_button = QPushButton("Deaktivierte Schaltfläche")
    disabled_button.setObjectName("DeskNodeExecuteButton")
    disabled_button.setEnabled(False)
    layout.addWidget(disabled_button)

    version = QLineEdit("0.1.0")
    version.setObjectName("DeskNodeVersionInput")
    layout.addWidget(version)

    status = QLabel("Status: Daemon wird gestartet.")
    status.setObjectName("StatusPanel")
    status.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(status)

    log_title = QLabel("Ausgabe")
    log_title.setObjectName("DeskNodePreviewSection")
    layout.addWidget(log_title)

    log = QTextEdit("> Tapo-Suche gestartet ...\n> Gerät erkannt ...")
    log.setObjectName("LogBox")
    log.setReadOnly(True)
    log.setMinimumHeight(120)
    layout.addWidget(log, stretch=1)
    return preview
