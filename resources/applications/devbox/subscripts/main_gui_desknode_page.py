from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

from PySide6.QtCore import QProcess, QProcessEnvironment, QTimer
from PySide6.QtWidgets import QPushButton, QWidget

from subscripts.main_gui_desknode_ux_apply import apply_desknode_ux_settings
from subscripts.main_gui_desknode_ux_storage import load_ux_settings
from subscripts.main_gui_desknode_ux_view import build_desknode_ux_design_view
from subscripts.main_gui_desknode_symbol_management import (
    build_desknode_symbol_management_view,
)
from subscripts.main_gui_desknode_views import build_desknode_execution_view
from subscripts.main_gui_devbox_log import get_devbox_logger


LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")

PAGE_KEY = "desknode"
PRODUCT_DIRECTORY_NAME = "deskNode"
SUPERVISOR_SCRIPT_NAME = "supervisor.py"
PROJECT_ROOT_ENV_NAME = "_CYXLABS_DEVBOX_PROJECT_ROOT_PATH"
STOP_TIMEOUT_MS = 2500


def build_desknode_page(studio) -> QWidget:
    """Build the deskNode page with execution and design-workspace views."""
    from PySide6.QtWidgets import QStackedLayout

    page = QWidget()
    stack = QStackedLayout(page)
    execution_view = build_desknode_execution_view(
        studio=studio,
        start_process=start_desknode_process,
        open_ux_design=lambda: open_ux_design_view(),
        open_symbol_management=lambda: open_symbol_management_view(),
    )
    ux_design_view = build_desknode_ux_design_view(
        studio=studio,
        return_to_execution=lambda: stack.setCurrentWidget(execution_view),
    )
    symbol_management_view = build_desknode_symbol_management_view(
        studio=studio,
        return_to_execution=lambda: stack.setCurrentWidget(execution_view),
    )

    def open_ux_design_view() -> None:
        ux_design_view.reload_settings()
        stack.setCurrentWidget(ux_design_view)

    def open_symbol_management_view() -> None:
        reload_data = getattr(symbol_management_view, "reload_data", None)

        if callable(reload_data):
            reload_data()

        stack.setCurrentWidget(symbol_management_view)

    stack.addWidget(execution_view)
    stack.addWidget(ux_design_view)
    stack.addWidget(symbol_management_view)
    studio.desknode_execution_view = execution_view
    studio.desknode_ux_design_view = ux_design_view
    studio.desknode_symbol_management_view = symbol_management_view

    def initialize_ux_profile() -> None:
        try:
            selected_theme = getattr(
                studio,
                "desknode_ux_theme_name",
                None,
            )
            settings = load_ux_settings(studio, selected_theme)
            apply_desknode_ux_settings(studio, settings)
            studio.append_log(
                "deskNode-Gestaltungsprofil aus ux-deskNode geladen.",
                PAGE_KEY,
            )
        except (OSError, RuntimeError, ValueError, sqlite3.Error) as error:
            studio.append_log(
                f"deskNode-Gestaltungsprofil konnte nicht geladen werden: {error}",
                PAGE_KEY,
            )
            LOGGER.warning("deskNode UX profile could not be loaded.", str(error))

    QTimer.singleShot(0, initialize_ux_profile)
    return page

def desk_node_supervisor_script(studio) -> Path:
    return (
        Path(studio.project_root_path)
        / "applications"
        / PRODUCT_DIRECTORY_NAME
        / "logic"
        / SUPERVISOR_SCRIPT_NAME
    )


def python_executable() -> Path:
    executable = Path(sys.executable).resolve()

    if executable.name.casefold() == "pythonw.exe":
        console_executable = executable.with_name("python.exe")

        if console_executable.is_file():
            return console_executable

    return executable


def active_processes(studio) -> dict[str, QProcess]:
    processes = getattr(studio, "desknode_processes", None)

    if isinstance(processes, dict):
        return processes

    processes: dict[str, QProcess] = {}
    studio.desknode_processes = processes
    return processes


def set_execute_button_running(button: QPushButton, is_running: bool) -> None:
    button.setProperty("running", is_running)
    button.style().unpolish(button)
    button.style().polish(button)
    button.update()


def force_stop_if_needed(process: QProcess) -> None:
    if process.state() != QProcess.ProcessState.NotRunning:
        process.kill()


def request_desknode_stop(studio, process: QProcess, launch_mode: str) -> None:
    if bool(process.property("stop_requested")):
        studio.set_status(
            f"deskNode {launch_mode} wird bereits gestoppt.",
            "warning",
            PAGE_KEY,
        )
        return

    process.setProperty("stop_requested", True)
    process.terminate()
    QTimer.singleShot(STOP_TIMEOUT_MS, lambda: force_stop_if_needed(process))
    studio.set_status(
        f"Stopp für deskNode {launch_mode} angefordert.",
        "warning",
        PAGE_KEY,
    )
    studio.append_log(
        f"Stopp angefordert: deskNode {launch_mode}.",
        PAGE_KEY,
    )
    LOGGER.info(
        "deskNode process stop requested.",
        f"mode={launch_mode}",
    )


def start_desknode_process(studio, button: QPushButton, launch_mode: str) -> None:
    processes = active_processes(studio)
    existing_process = processes.get(launch_mode)

    if (
        existing_process is not None
        and existing_process.state() != QProcess.ProcessState.NotRunning
    ):
        request_desknode_stop(studio, existing_process, launch_mode)
        return

    supervisor_script = desk_node_supervisor_script(studio)

    if not supervisor_script.is_file():
        message = f"deskNode-Supervisor nicht gefunden: {supervisor_script}"
        studio.set_status("deskNode-Supervisor nicht gefunden.", "error", PAGE_KEY)
        studio.append_log(message, PAGE_KEY)
        LOGGER.warning("deskNode start blocked.", message)
        return

    process = QProcess(studio)
    process.setProperty("stop_requested", False)
    environment = QProcessEnvironment.systemEnvironment()
    environment.insert(PROJECT_ROOT_ENV_NAME, str(studio.project_root_path))
    process.setProcessEnvironment(environment)
    process.setProgram(str(python_executable()))
    process.setArguments([str(supervisor_script), launch_mode])
    process.setWorkingDirectory(str(supervisor_script.parent))
    process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)

    def append_process_output() -> None:
        output = bytes(process.readAllStandardOutput()).decode(
            "utf-8",
            "replace",
        )
        output = output.rstrip()

        if output:
            studio.append_log(output, PAGE_KEY)

    def finish_process(exit_code: int, _exit_status) -> None:
        append_process_output()
        set_execute_button_running(button, False)

        if processes.get(launch_mode) is process:
            processes.pop(launch_mode, None)

        if bool(process.property("stop_requested")):
            studio.set_status(
                f"deskNode {launch_mode} gestoppt.",
                "success",
                PAGE_KEY,
            )
            studio.append_log(
                f"deskNode {launch_mode} wurde gestoppt.",
                PAGE_KEY,
            )
            LOGGER.info(
                "deskNode process stopped.",
                f"mode={launch_mode}; exit_code={exit_code}",
            )
            return

        if exit_code == 0:
            studio.set_status(
                f"deskNode {launch_mode} beendet.",
                "success",
                PAGE_KEY,
            )
            studio.append_log(
                f"deskNode {launch_mode} erfolgreich beendet.",
                PAGE_KEY,
            )
            LOGGER.info(
                "deskNode process finished.",
                f"mode={launch_mode}; exit_code=0",
            )
            return

        studio.set_status(
            f"deskNode {launch_mode} mit Fehler beendet.",
            "error",
            PAGE_KEY,
        )
        studio.append_log(
            f"deskNode {launch_mode} beendet mit Code {exit_code}.",
            PAGE_KEY,
        )
        LOGGER.warning(
            "deskNode process finished with error.",
            f"mode={launch_mode}; exit_code={exit_code}",
        )

    def handle_process_error(_error) -> None:
        if bool(process.property("stop_requested")):
            return

        error_text = process.errorString().strip() or "Unbekannter QProcess-Fehler"

        if process.state() == QProcess.ProcessState.NotRunning:
            set_execute_button_running(button, False)

            if processes.get(launch_mode) is process:
                processes.pop(launch_mode, None)

        studio.set_status("deskNode-Prozess konnte nicht gestartet werden.", "error", PAGE_KEY)
        studio.append_log(
            f"deskNode {launch_mode} konnte nicht gestartet werden: {error_text}",
            PAGE_KEY,
        )
        LOGGER.warning(
            "deskNode process start error.",
            f"mode={launch_mode}; error={error_text}",
        )

    process.readyReadStandardOutput.connect(append_process_output)
    process.finished.connect(finish_process)
    process.errorOccurred.connect(handle_process_error)

    processes[launch_mode] = process
    set_execute_button_running(button, True)
    studio.set_status(
        f"deskNode {launch_mode} wird gestartet.",
        "running",
        PAGE_KEY,
    )
    studio.append_log(
        "Starte: "
        f"{python_executable()} {supervisor_script} {launch_mode}",
        PAGE_KEY,
    )
    LOGGER.info(
        "Starting deskNode process.",
        f"mode={launch_mode}; script={supervisor_script}",
    )
    process.start()
