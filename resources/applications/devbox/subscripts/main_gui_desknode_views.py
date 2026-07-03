from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from subscripts.main_gui_desknode_ux_view import build_desknode_ux_design_view
from subscripts.main_gui_desknode_version import show_desknode_version, version_controls
from subscripts.main_gui_devbox_log import get_devbox_logger
from subscripts.main_gui_pages import add_status_and_log, add_title


LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")

PAGE_KEY = "desknode"


def build_desknode_execution_view(
    studio,
    start_process: Callable,
    open_ux_design: Callable[[], None],
    open_symbol_management: Callable[[], None],
    open_repository: Callable[[], None],
) -> QWidget:
    """Build the regular deskNode execution surface."""
    page = QWidget()
    page.setObjectName("DeskNodeExecutionView")
    layout = QVBoxLayout(page)
    layout.setContentsMargins(10, 12, 10, 10)
    layout.setSpacing(14)

    add_title(
        layout,
        "deskNode",
        "Lokale Ausführung von deskNode und dem deskNode-Daemon. "
        "Die Konsolenausgabe des gestarteten Prozesses erscheint unten live.",
    )

    target_label = QLabel("Ziel: applications/deskNode/logic/supervisor.py")
    target_label.setObjectName("PathLabel")
    target_label.setWordWrap(True)
    layout.addWidget(target_label)

    button_row = QHBoxLayout()
    button_row.setSpacing(12)

    execute_desknode_button = QPushButton("Execute deskNode")
    execute_desknode_button.setObjectName("DeskNodeExecuteButton")
    execute_desknode_button.setMinimumWidth(210)
    execute_desknode_button.clicked.connect(
        lambda _checked=False: start_process(
            studio=studio,
            button=execute_desknode_button,
            launch_mode="deskNode",
        )
    )
    button_row.addWidget(execute_desknode_button)

    execute_daemon_button = QPushButton("Execute Daemon")
    execute_daemon_button.setObjectName("DeskNodeExecuteButton")
    execute_daemon_button.setMinimumWidth(210)
    execute_daemon_button.clicked.connect(
        lambda _checked=False: start_process(
            studio=studio,
            button=execute_daemon_button,
            launch_mode="daemon",
        )
    )
    button_row.addWidget(execute_daemon_button)

    version_button = QPushButton("Version")
    version_button.setObjectName("DeskNodeVersionButton")
    version_button.setMinimumWidth(160)
    studio.desknode_version_button = version_button
    version_button.clicked.connect(
        lambda _checked=False: show_desknode_version(studio)
    )
    button_row.addWidget(version_button)

    ux_design_button = QPushButton("Oberflächengestaltung")
    ux_design_button.setObjectName("DeskNodeUxDesignButton")
    ux_design_button.setMinimumWidth(205)
    ux_design_button.clicked.connect(
        lambda _checked=False: open_ux_design()
    )
    button_row.addWidget(ux_design_button)

    symbol_management_button = QPushButton("Symbolverwaltung")
    symbol_management_button.setObjectName("DeskNodeSymbolManagementButton")
    symbol_management_button.setMinimumWidth(205)
    symbol_management_button.clicked.connect(
        lambda _checked=False: open_symbol_management()
    )
    button_row.addWidget(symbol_management_button)

    repository_button = QPushButton("Repository")
    repository_button.setObjectName("DeskNodeSymbolManagementButton")
    repository_button.setMinimumWidth(160)
    repository_button.clicked.connect(
        lambda _checked=False: open_repository()
    )
    button_row.addWidget(repository_button)

    button_row.addStretch(1)
    layout.addLayout(button_row)
    layout.addWidget(version_controls(studio))
    add_status_and_log(studio, layout, PAGE_KEY)
    return page


def build_desknode_ux_design_view_placeholder(
    studio,
    return_to_execution: Callable[[], None],
) -> QWidget:
    """Compatibility wrapper for the deskNode design-workspace factory."""
    return build_desknode_ux_design_view(studio, return_to_execution)
