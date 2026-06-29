from __future__ import annotations

import sys
from collections.abc import Callable, Iterable
from pathlib import Path

from PySide6.QtCore import QProcess, QProcessEnvironment

from subscripts.main_gui_desknode_version_data import PRODUCT_NAME
from subscripts.main_gui_devbox_log import get_devbox_logger


LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")

PAGE_KEY = "desknode"
PROJECT_ROOT_ENV_NAME = "_CYXLABS_DEVBOX_PROJECT_ROOT_PATH"
MANUFACTURER_DB_SCRIPT = "create_manufacturer_db.py"
START_TIMEOUT_MS = 2500


RefreshFinishedCallback = Callable[[bool, str], None]
RefreshStartedCallback = Callable[[], None]


def manufacturer_database_script(studio) -> Path:
    return (
        Path(studio.project_root_path)
        / "applications"
        / PRODUCT_NAME
        / "resources"
        / "scripts"
        / MANUFACTURER_DB_SCRIPT
    )


def python_executable() -> Path:
    executable = Path(sys.executable).resolve()

    if executable.name.casefold() == "pythonw.exe":
        console_executable = executable.with_name("python.exe")

        if console_executable.is_file():
            return console_executable

    return executable


def set_controls_enabled(
    studio,
    attribute_names: Iterable[str],
    enabled: bool,
) -> None:
    for attribute_name in attribute_names:
        widget = getattr(studio, attribute_name, None)

        if widget is not None:
            widget.setEnabled(enabled)


def call_finished_callback(
    callback: RefreshFinishedCallback | None,
    succeeded: bool,
    message: str,
) -> None:
    if callback is not None:
        callback(succeeded, message)


def start_manufacturer_database_refresh(
    studio,
    saved_subject: str = "Version",
    controls_to_lock: tuple[str, ...] = (),
    on_started: RefreshStartedCallback | None = None,
    on_finished: RefreshFinishedCallback | None = None,
) -> bool:
    """Start create_manufacturer_db.py after one committed deskNode change.

    The caller must only invoke this function after its SQLite transaction has
    completed successfully. The function keeps the QProcess on ``studio`` so
    the process remains alive for the complete manufacturer-database rebuild.
    """
    script_file = manufacturer_database_script(studio)
    subject_text = f"{saved_subject} gespeichert"

    if not script_file.is_file():
        message = (
            f"{subject_text}, aber create_manufacturer_db.py wurde "
            f"nicht gefunden: {script_file}"
        )
        studio.set_status(
            f"{subject_text}, Herstellerdatenbank-Skript fehlt.",
            "error",
            PAGE_KEY,
        )
        studio.append_log(message, PAGE_KEY)
        call_finished_callback(on_finished, False, message)
        return False

    existing_process = getattr(
        studio,
        "desknode_manufacturer_refresh_process",
        None,
    )

    if (
        existing_process is not None
        and existing_process.state() != QProcess.ProcessState.NotRunning
    ):
        message = (
            "create_manufacturer_db.py wurde nicht erneut gestartet, "
            "weil bereits eine Aktualisierung läuft."
        )
        studio.set_status(
            f"{subject_text}. Herstellerdatenbank wird bereits erzeugt.",
            "warning",
            PAGE_KEY,
        )
        studio.append_log(message, PAGE_KEY)
        call_finished_callback(on_finished, False, message)
        return False

    process = QProcess(studio)
    process.setProperty("refresh_finished", False)

    environment = QProcessEnvironment.systemEnvironment()
    environment.insert(
        PROJECT_ROOT_ENV_NAME,
        str(studio.project_root_path),
    )
    process.setProcessEnvironment(environment)
    process.setProgram(str(python_executable()))
    process.setArguments([str(script_file)])
    process.setWorkingDirectory(str(script_file.parent))
    process.setProcessChannelMode(
        QProcess.ProcessChannelMode.MergedChannels
    )

    def append_process_output() -> None:
        output = bytes(process.readAllStandardOutput()).decode(
            "utf-8",
            "replace",
        ).rstrip()

        if output:
            studio.append_log(output, PAGE_KEY)

    def complete_refresh(
        succeeded: bool,
        message: str,
        status_kind: str,
    ) -> None:
        if bool(process.property("refresh_finished")):
            return

        process.setProperty("refresh_finished", True)
        append_process_output()
        set_controls_enabled(studio, controls_to_lock, True)

        if getattr(
            studio,
            "desknode_manufacturer_refresh_process",
            None,
        ) is process:
            studio.desknode_manufacturer_refresh_process = None

        studio.set_status(message, status_kind, PAGE_KEY)
        studio.append_log(message, PAGE_KEY)
        call_finished_callback(on_finished, succeeded, message)

    def finish_process(exit_code: int, exit_status) -> None:
        if (
            exit_code == 0
            and exit_status == QProcess.ExitStatus.NormalExit
        ):
            message = (
                f"{subject_text} und Herstellerdatenbank aktualisiert."
            )
            complete_refresh(True, message, "success")
            LOGGER.info(
                "Manufacturer database refresh finished.",
                f"source={saved_subject}; exit_code=0",
            )
            return

        message = (
            f"{subject_text}, Herstellerdatenbank mit Fehler beendet "
            f"(Code {exit_code})."
        )
        complete_refresh(False, message, "error")
        LOGGER.warning(
            "Manufacturer database refresh failed.",
            f"source={saved_subject}; exit_code={exit_code}",
        )

    def handle_process_error(_error) -> None:
        error_text = (
            process.errorString().strip()
            or "Unbekannter QProcess-Fehler"
        )
        message = (
            f"{subject_text}, Herstellerdatenbank-Skript konnte "
            f"nicht gestartet werden: {error_text}"
        )
        complete_refresh(False, message, "error")
        LOGGER.warning(
            "Manufacturer database refresh could not start.",
            f"source={saved_subject}; error={error_text}",
        )

    process.readyReadStandardOutput.connect(append_process_output)
    process.finished.connect(finish_process)
    process.errorOccurred.connect(handle_process_error)

    studio.desknode_manufacturer_refresh_process = process
    set_controls_enabled(studio, controls_to_lock, False)

    launch_text = (
        "Starte Herstellerdatenbank-Aktualisierung: "
        f"{python_executable()} {script_file}"
    )
    studio.set_status(
        f"{subject_text}. Herstellerdatenbank wird aktualisiert.",
        "running",
        PAGE_KEY,
    )
    studio.append_log(launch_text, PAGE_KEY)
    LOGGER.info(
        "Starting manufacturer database refresh.",
        f"source={saved_subject}; script={script_file}",
    )

    process.start()

    if not process.waitForStarted(START_TIMEOUT_MS):
        handle_process_error(QProcess.ProcessError.FailedToStart)
        return False

    if on_started is not None:
        on_started()

    return True
