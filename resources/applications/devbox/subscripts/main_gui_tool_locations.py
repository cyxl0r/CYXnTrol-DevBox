from __future__ import annotations

from subscripts.main_gui_devbox_log import get_devbox_logger
LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")


import os
import sqlite3
import subprocess
from pathlib import Path


APPDATA_FOLDER_PARTS = ("CYXLabs", "CYXnTrol", "DevBox")
LOCDATA_FILE_NAME = "locdata.r0b"


def get_appdata_directory() -> Path:
    appdata_value = os.environ.get("APPDATA", "").strip()

    if appdata_value:
        return Path(appdata_value).expanduser()

    local_appdata_value = os.environ.get("LOCALAPPDATA", "").strip()

    if local_appdata_value:
        return Path(local_appdata_value).expanduser()

    return Path.home() / "AppData" / "Roaming"


def get_locdata_file() -> Path:
    return get_appdata_directory().joinpath(
        *APPDATA_FOLDER_PARTS,
        LOCDATA_FILE_NAME,
    )


def get_registered_tool_path(
    tool_key: str,
    executable_name: str,
) -> Path | None:
    locdata_file = get_locdata_file()

    if not locdata_file.is_file():
        return None

    connection: sqlite3.Connection | None = None

    try:
        connection = sqlite3.connect(locdata_file, timeout=2.0)
        row = connection.execute(
            """
            SELECT executable_path, status
            FROM tool_locations
            WHERE tool_key = ?
              AND executable_name = ?
            LIMIT 1
            """,
            (tool_key, executable_name),
        ).fetchone()
    except sqlite3.Error as error:
        LOGGER.warning(
            "Could not read registered application path.",
            f"{tool_key}: {error}",
        )
        return None
    finally:
        if connection is not None:
            connection.close()

    if row is None:
        return None

    executable_path = Path(str(row[0] or "")).expanduser()
    status = str(row[1] or "").strip().lower()

    if (
        status != "found"
        or executable_path.name.lower() != executable_name.lower()
        or not executable_path.is_file()
    ):
        return None

    return executable_path


def start_registered_tool(
    executable_path: Path,
    executable_name: str,
) -> tuple[bool, str]:
    executable_path = Path(executable_path).resolve()

    if (
        executable_path.name.lower() != executable_name.lower()
        or not executable_path.is_file()
    ):
        return (
            False,
            f"Anwendung nicht verfügbar: {executable_name}",
        )

    try:
        subprocess.Popen(
            [str(executable_path)],
            cwd=str(executable_path.parent),
        )
        LOGGER.info(
            "Registered application started.",
            str(executable_path),
        )
        return True, ""
    except OSError as error:
        details = (
            f"{executable_path}: "
            f"{type(error).__name__}: {error}"
        )
        LOGGER.error(
            "Could not start registered application.",
            details,
        )
        return (
            False,
            "Anwendung konnte nicht gestartet werden: "
            f"{type(error).__name__}: {error}",
        )
