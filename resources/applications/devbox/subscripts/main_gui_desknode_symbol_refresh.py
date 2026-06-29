from __future__ import annotations

import sys
from collections.abc import Callable, Iterable
from pathlib import Path

from PySide6.QtCore import QProcess, QProcessEnvironment

from subscripts.main_gui_devbox_log import get_devbox_logger


LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")

PAGE_KEY = "desknode_symbol_management"
PRODUCT_DIRECTORY_NAME = "deskNode"
MANUFACTURER_DB_SCRIPT_NAME = "create_manufacturer_db.py"
PROJECT_ROOT_ENV_NAME = "_CYXLABS_DEVBOX_PROJECT_ROOT_PATH"
START_TIMEOUT_MS = 2500


RefreshFinishedCallback = Callable[[bool, str], None]


def manufacturer_database_script(studio) -> Path:
    return (
        Path(studio.project_root_path)
        / "applications"
        / PRODUCT_DIRECTORY_NAME
        / "resources"
        / "scripts"
        / MANUFACTURER_DB_SCRIPT_NAME
    )


def python_executable() -> Path:
    executable = Path(sys.executable).resolve()

    if executable.name.casefold() == "pythonw.exe":
        console_executable = executable.with_name("python.exe")

        if console_executable.is_file():
            return console_executable

    return executable


def set_controls_enabled(
    controls: Iterable[object],
    enabled: bool,
) -> None:
    for control in controls:
        if control is not None and hasattr(control, "setEnabled"):
            control.setEnabled(enabled)


def start_symbol_manufacturer_database_refresh(
    studio,
    saved_subject: str,
    controls_to_lock: Iterable[object] = (),
    on_finished: RefreshFinishedCallback | None = None,
) -> bool:
    """Run create_manufacturer_db.py after a committed symbol-catalog write."""
    script_file = manufacturer_database_script(studio)
    controls = tuple(controls_to_lock)

    if not script_file.is_file():
        message = (
            f"{saved_subject} wurde gespeichert, aber "
            f"create_manufacturer_db.py fehlt: {script_file}"
        )
        studio.set_status(
            "Symbolkatalog gespeichert, Herstellerdatenbank-Skript fehlt.",
            "error",
            PAGE_KEY,
        )
        studio.append_log(message, PAGE_KEY)
        LOGGER.warning("Symbol manufacturer refresh blocked.", message)

        if on_finished is not None:
            on_finished(False, message)

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
            "weil bereits eine Herstellerdatenbank-Aktualisierung läuft."
        )
        studio.set_status(
            f"{saved_subject} gespeichert. Herstellerdatenbank wird bereits aktualisiert.",
            "warning",
            PAGE_KEY,
        )
        studio.append_log(message, PAGE_KEY)

        if on_finished is not None:
            on_finished(False, message)

        return False

    process = QProcess(studio)
    process.setProperty("symbol_refresh_finished", False)
    process.setProcessChannelMode(
        QProcess.ProcessChannelMode.MergedChannels
    )

    environment = QProcessEnvironment.systemEnvironment()
    environment.insert(
        PROJECT_ROOT_ENV_NAME,
        str(studio.project_root_path),
    )
    process.setProcessEnvironment(environment)
    process.setProgram(str(python_executable()))
    process.setArguments([str(script_file)])
    process.setWorkingDirectory(str(script_file.parent))

    def append_process_output() -> None:
        output = bytes(process.readAllStandardOutput()).decode(
            "utf-8",
            "replace",
        ).rstrip()

        if output:
            studio.append_log(output, PAGE_KEY)

    def complete(
        succeeded: bool,
        message: str,
        status_kind: str,
    ) -> None:
        if bool(process.property("symbol_refresh_finished")):
            return

        process.setProperty("symbol_refresh_finished", True)
        append_process_output()
        set_controls_enabled(controls, True)

        if getattr(
            studio,
            "desknode_manufacturer_refresh_process",
            None,
        ) is process:
            studio.desknode_manufacturer_refresh_process = None

        studio.set_status(message, status_kind, PAGE_KEY)
        studio.append_log(message, PAGE_KEY)

        if on_finished is not None:
            on_finished(succeeded, message)

    def finish_process(exit_code: int, exit_status) -> None:
        if (
            exit_code == 0
            and exit_status == QProcess.ExitStatus.NormalExit
        ):
            message = (
                f"{saved_subject} gespeichert und "
                "Herstellerdatenbank aktualisiert."
            )
            complete(True, message, "success")
            LOGGER.info(
                "Symbol manufacturer refresh finished.",
                f"subject={saved_subject}; exit_code=0",
            )
            return

        message = (
            f"{saved_subject} gespeichert, aber Herstellerdatenbank "
            f"mit Fehler beendet (Code {exit_code})."
        )
        complete(False, message, "error")
        LOGGER.warning(
            "Symbol manufacturer refresh failed.",
            f"subject={saved_subject}; exit_code={exit_code}",
        )

    def handle_process_error(_error) -> None:
        error_text = (
            process.errorString().strip()
            or "Unbekannter QProcess-Fehler"
        )
        message = (
            f"{saved_subject} gespeichert, aber "
            "create_manufacturer_db.py konnte nicht gestartet werden: "
            f"{error_text}"
        )
        complete(False, message, "error")
        LOGGER.warning(
            "Symbol manufacturer refresh start error.",
            f"subject={saved_subject}; error={error_text}",
        )

    process.readyReadStandardOutput.connect(append_process_output)
    process.finished.connect(finish_process)
    process.errorOccurred.connect(handle_process_error)

    studio.desknode_manufacturer_refresh_process = process
    set_controls_enabled(controls, False)

    start_message = (
        "Starte Herstellerdatenbank-Aktualisierung: "
        f"{python_executable()} {script_file}"
    )
    studio.set_status(
        f"{saved_subject} gespeichert. Herstellerdatenbank wird aktualisiert.",
        "running",
        PAGE_KEY,
    )
    studio.append_log(start_message, PAGE_KEY)
    LOGGER.info(
        "Starting symbol manufacturer refresh.",
        f"subject={saved_subject}; script={script_file}",
    )

    process.start()

    if not process.waitForStarted(START_TIMEOUT_MS):
        handle_process_error(QProcess.ProcessError.FailedToStart)
        return False

    return True
