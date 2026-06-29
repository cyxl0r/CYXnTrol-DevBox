from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QProcess, QProcessEnvironment
from PySide6.QtWidgets import QPushButton

from subscripts.main_gui_devbox_log import get_devbox_logger


LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")

PAGE_KEY = "desknode_symbol_management"
PRODUCT_DIRECTORY_NAME = "deskNode"
GRAPHIC_PACK_SCRIPT_NAME = "graphic_items_bulder.py"
PROJECT_ROOT_ENV_NAME = "_CYXLABS_DEVBOX_PROJECT_ROOT_PATH"


def graphic_pack_builder_script(studio) -> Path:
    return (
        Path(studio.project_root_path)
        / "applications"
        / PRODUCT_DIRECTORY_NAME
        / "resources"
        / "scripts"
        / GRAPHIC_PACK_SCRIPT_NAME
    )


def python_executable() -> Path:
    executable = Path(sys.executable).resolve()

    if executable.name.casefold() == "pythonw.exe":
        console_executable = executable.with_name("python.exe")

        if console_executable.is_file():
            return console_executable

    return executable


def refresh_build_button(button: QPushButton, is_running: bool) -> None:
    button.setProperty("running", is_running)
    button.setEnabled(not is_running)
    button.style().unpolish(button)
    button.style().polish(button)
    button.update()


def start_graphic_items_pack_build(
    studio,
    button: QPushButton,
) -> None:
    existing_process = getattr(
        studio,
        "desknode_graphic_pack_process",
        None,
    )

    if (
        existing_process is not None
        and existing_process.state() != QProcess.ProcessState.NotRunning
    ):
        studio.set_status(
            "Grafikpaket-Build läuft bereits.",
            "warning",
            PAGE_KEY,
        )
        studio.append_log(
            "Grafikpaket-Build wurde nicht doppelt gestartet.",
            PAGE_KEY,
        )
        return

    script_file = graphic_pack_builder_script(studio)

    if not script_file.is_file():
        message = f"Grafikpaket-Skript nicht gefunden: {script_file}"
        studio.set_status(
            "Grafikpaket-Skript nicht gefunden.",
            "error",
            PAGE_KEY,
        )
        studio.append_log(message, PAGE_KEY)
        LOGGER.warning("Graphic pack build blocked.", message)
        return

    process = QProcess(studio)
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

    def finish_process(exit_code: int, exit_status) -> None:
        append_process_output()
        refresh_build_button(button, False)

        if getattr(
            studio,
            "desknode_graphic_pack_process",
            None,
        ) is process:
            studio.desknode_graphic_pack_process = None

        if (
            exit_code == 0
            and exit_status == QProcess.ExitStatus.NormalExit
        ):
            message = "Items-Graphic-Pack erfolgreich erstellt."
            studio.set_status(message, "success", PAGE_KEY)
            studio.append_log(message, PAGE_KEY)
            LOGGER.info(
                "Graphic pack build finished.",
                "exit_code=0",
            )
            return

        message = (
            "Items-Graphic-Pack mit Fehler beendet "
            f"(Code {exit_code})."
        )
        studio.set_status(message, "error", PAGE_KEY)
        studio.append_log(message, PAGE_KEY)
        LOGGER.warning(
            "Graphic pack build failed.",
            f"exit_code={exit_code}",
        )

    def handle_process_error(_error) -> None:
        append_process_output()
        refresh_build_button(button, False)

        if getattr(
            studio,
            "desknode_graphic_pack_process",
            None,
        ) is process:
            studio.desknode_graphic_pack_process = None

        error_text = (
            process.errorString().strip()
            or "Unbekannter QProcess-Fehler"
        )
        message = (
            "Items-Graphic-Pack konnte nicht gestartet werden: "
            f"{error_text}"
        )
        studio.set_status(message, "error", PAGE_KEY)
        studio.append_log(message, PAGE_KEY)
        LOGGER.warning(
            "Graphic pack build start error.",
            error_text,
        )

    process.readyReadStandardOutput.connect(append_process_output)
    process.finished.connect(finish_process)
    process.errorOccurred.connect(handle_process_error)

    studio.desknode_graphic_pack_process = process
    refresh_build_button(button, True)
    studio.set_status(
        "Items-Graphic-Pack wird erstellt.",
        "running",
        PAGE_KEY,
    )
    studio.append_log(
        "Starte Items-Graphic-Pack: "
        f"{python_executable()} {script_file}",
        PAGE_KEY,
    )
    LOGGER.info(
        "Starting graphic pack build.",
        f"script={script_file}",
    )
    process.start()
