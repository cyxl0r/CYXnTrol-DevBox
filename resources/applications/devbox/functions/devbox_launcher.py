from __future__ import annotations

import ctypes
import importlib.util
import os
import re
import shutil
import sqlite3
import stat
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from types import ModuleType
from typing import Any


home_path = Path(__file__).resolve().parent
os.chdir(home_path)

current_path = home_path
projekt_root_path = None

while True:
    root_file = current_path / ".root"

    if root_file.is_file():
        content = root_file.read_text(encoding="utf-8").strip()

        if content == "project-root":
            projekt_root_path = current_path
            break

    parent_path = current_path.parent

    if parent_path == current_path:
        print("No project root found.")
        sys.exit(0)

    current_path = parent_path
    os.chdir(current_path)


rnd_prv = projekt_root_path / "platform" / "tools" / "random_string_provider.py"
tme_prv = projekt_root_path / "platform" / "tools" / "timestamp_provider.py"
crt_db = (
    projekt_root_path
    / "resources"
    / "applications"
    / "devbox"
    / "functions"
    / "create_devdbase.py"
)
initializer_script = (
    projekt_root_path
    / "resources"
    / "applications"
    / "devbox"
    / "functions"
    / "initialize_empty_application_projects.py"
)

database_file = projekt_root_path / "resources" / "organization" / "devbox_db.r0b"
devbox_source_path = projekt_root_path / "resources" / "applications" / "devbox"
devbox_log_module_file = (
    devbox_source_path
    / "subscripts"
    / "main_gui_devbox_log.py"
)
project_root_env_name = "_CYXLABS_DEVBOX_PROJECT_ROOT_PATH"
logfile_env_name = "_CYXLABS_DEVBOX_LOGFILE_PATH"
appdata_folder_parts = ("CYXLabs", "CYXnTrol", "DevBox")
logfile_name = "logfile.r0b"
locdata_name = "locdata.r0b"


TOOL_DEFINITIONS = (
    ("inkscape", "inkscape.exe"),
    ("gimp_console", "gimp-console.exe"),
    ("gimp_console_3_0", "gimp-console-3.0.exe"),
    ("gimp_console_3", "gimp-console-3.exe"),
    ("gimp", "gimp.exe"),
)


def load_module(module_name: str, module_file: Path) -> ModuleType:
    if not module_file.is_file():
        raise FileNotFoundError(f"Provider not found: {module_file}")

    specification = importlib.util.spec_from_file_location(module_name, module_file)

    if specification is None or specification.loader is None:
        raise ImportError(f"Provider could not be loaded: {module_file}")

    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def get_python_executable() -> Path:
    executable_path = Path(sys.executable).resolve()

    if executable_path.name.lower() == "pythonw.exe":
        python_executable = executable_path.with_name("python.exe")

        if python_executable.is_file():
            return python_executable

    return executable_path


def get_timestamp() -> str:
    return datetime.now().astimezone().isoformat(timespec="milliseconds")


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def resolve_appdata_directory() -> Path:
    appdata_value = os.environ.get("APPDATA", "").strip()

    if appdata_value:
        return Path(appdata_value).expanduser()

    local_appdata_value = os.environ.get("LOCALAPPDATA", "").strip()

    if local_appdata_value:
        return Path(local_appdata_value).expanduser()

    return Path.home() / "AppData" / "Roaming"


def ensure_runtime_paths() -> tuple[Path, Path, Path]:
    runtime_directory = resolve_appdata_directory().joinpath(*appdata_folder_parts)
    runtime_directory.mkdir(parents=True, exist_ok=True)

    logfile_path = runtime_directory / logfile_name
    locdata_path = runtime_directory / locdata_name

    for database_path in (logfile_path, locdata_path):
        connection = sqlite3.connect(database_path)

        try:
            connection.execute("PRAGMA journal_mode = WAL")
            connection.execute("PRAGMA busy_timeout = 5000")
            connection.commit()
        finally:
            connection.close()

    return runtime_directory, logfile_path, locdata_path


def load_launcher_logger() -> Any | None:
    if not devbox_log_module_file.is_file():
        print(f"DevBox logger module not found: {devbox_log_module_file}")
        return None

    try:
        return load_module("devbox_launcher_logger", devbox_log_module_file)
    except Exception as error:
        print(f"DevBox logger module could not be loaded: {error}")
        return None


def log_message(
    logger: Any | None,
    level: str,
    message: str,
    details: str = "",
) -> None:
    if logger is None:
        print(f"[{level}] {message}")
        if details:
            print(details)
        return

    try:
        logger.log(level, message, details)
    except Exception:
        print(f"[{level}] {message}")
        if details:
            print(details)


def create_script_logger(
    logger_module: Any | None,
    script_file: Path,
) -> Any | None:
    if logger_module is None:
        return None

    try:
        return logger_module.get_devbox_logger(script_file)
    except Exception:
        return None


def ensure_locdata_schema(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS tool_locations (
            tool_key TEXT PRIMARY KEY,
            executable_name TEXT NOT NULL UNIQUE,
            executable_path TEXT,
            search_source TEXT,
            last_checked TEXT NOT NULL,
            last_found TEXT,
            status TEXT NOT NULL
        )
        """
    )

    current_timestamp = get_timestamp()

    for tool_key, executable_name in TOOL_DEFINITIONS:
        connection.execute(
            """
            INSERT INTO tool_locations (
                tool_key,
                executable_name,
                executable_path,
                search_source,
                last_checked,
                last_found,
                status
            )
            VALUES (?, ?, NULL, NULL, ?, NULL, ?)
            ON CONFLICT(tool_key) DO UPDATE SET
                executable_name = excluded.executable_name
            """,
            (
                tool_key,
                executable_name,
                current_timestamp,
                "missing",
            ),
        )


def is_valid_tool_path(executable_path: str, executable_name: str) -> bool:
    if not executable_path:
        return False

    path_value = Path(executable_path).expanduser()

    return (
        path_value.is_file()
        and path_value.name.lower() == executable_name.lower()
    )


def find_executables(
    search_root: Path,
    executable_names: set[str],
) -> dict[str, Path]:
    if not search_root.is_dir() or not executable_names:
        return {}

    normalized_targets = {
        executable_name.lower()
        for executable_name in executable_names
    }
    found_paths: dict[str, Path] = {}

    def on_error(error: OSError) -> None:
        return None

    for directory_path, _directory_names, file_names in os.walk(
        search_root,
        topdown=True,
        onerror=on_error,
        followlinks=False,
    ):
        remaining_targets = normalized_targets.difference(found_paths)

        if not remaining_targets:
            break

        for file_name in file_names:
            normalized_file_name = file_name.lower()

            if normalized_file_name not in remaining_targets:
                continue

            candidate_path = Path(directory_path) / file_name

            if candidate_path.is_file():
                found_paths[normalized_file_name] = candidate_path

                if normalized_targets.issubset(found_paths):
                    break

    return found_paths


def update_tool_location(
    connection: sqlite3.Connection,
    tool_key: str,
    executable_path: Path | None,
    search_source: str | None,
    status: str,
) -> None:
    current_timestamp = get_timestamp()
    path_value = str(executable_path) if executable_path is not None else None
    last_found = current_timestamp if executable_path is not None else None

    connection.execute(
        """
        UPDATE tool_locations
        SET executable_path = ?,
            search_source = ?,
            last_checked = ?,
            last_found = COALESCE(?, last_found),
            status = ?
        WHERE tool_key = ?
        """,
        (
            path_value,
            search_source,
            current_timestamp,
            last_found,
            status,
            tool_key,
        ),
    )


def show_missing_tools_warning() -> None:
    title = "DevBox – Externe Werkzeuge nicht gefunden"
    message = (
        "Inkscape und GIMP konnten weder unter %ProgramFiles% noch "
        "unter %TEMP% gefunden werden.\n\n"
        "Funktionen der DevBox, die diese Programme benötigen, stehen "
        "möglicherweise nicht zur Verfügung."
    )

    if os.name == "nt":
        try:
            ctypes.windll.user32.MessageBoxW(
                None,
                message,
                title,
                0x00000030,
            )
            return
        except Exception:
            pass

    print(f"WARNING: {title}\n{message}")


def verify_or_locate_external_tools(
    locdata_path: Path,
    launcher_logger: Any | None,
) -> None:
    connection = sqlite3.connect(locdata_path, timeout=5.0)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA busy_timeout = 5000")

    try:
        ensure_locdata_schema(connection)
        connection.commit()

        rows = connection.execute(
            """
            SELECT tool_key, executable_name, executable_path
            FROM tool_locations
            ORDER BY tool_key ASC
            """
        ).fetchall()

        missing_names: set[str] = set()
        tool_rows: dict[str, sqlite3.Row] = {}
        valid_tool_count = 0

        for row in rows:
            tool_key = str(row["tool_key"])
            executable_name = str(row["executable_name"])
            executable_path = str(row["executable_path"] or "")
            tool_rows[executable_name.lower()] = row

            if is_valid_tool_path(executable_path, executable_name):
                valid_tool_count += 1
                update_tool_location(
                    connection,
                    tool_key,
                    Path(executable_path),
                    "stored_path",
                    "found",
                )
                log_message(
                    launcher_logger,
                    "INFO",
                    f"Verified external tool: {executable_name}",
                    executable_path,
                )
            else:
                missing_names.add(executable_name)
                update_tool_location(
                    connection,
                    tool_key,
                    None,
                    None,
                    "missing",
                )
                log_message(
                    launcher_logger,
                    "WARNING",
                    f"External tool path missing or invalid: {executable_name}",
                    executable_path,
                )

        connection.commit()

        found_paths: dict[str, tuple[Path, str]] = {}
        program_files_value = os.environ.get("ProgramFiles", "").strip()

        if missing_names and program_files_value:
            program_files_path = Path(program_files_value).expanduser()
            log_message(
                launcher_logger,
                "INFO",
                "Searching external tools in Program Files.",
                str(program_files_path),
            )

            for executable_name, executable_path in find_executables(
                program_files_path,
                missing_names,
            ).items():
                found_paths[executable_name] = (
                    executable_path,
                    "programfiles",
                )

        remaining_names = {
            executable_name
            for executable_name in missing_names
            if executable_name.lower() not in found_paths
        }

        if remaining_names:
            temp_search_path = Path(tempfile.gettempdir())
            log_message(
                launcher_logger,
                "INFO",
                "Searching external tools in TEMP.",
                str(temp_search_path),
            )

            for executable_name, executable_path in find_executables(
                temp_search_path,
                remaining_names,
            ).items():
                found_paths[executable_name] = (
                    executable_path,
                    "temp",
                )

        for executable_name, row in tool_rows.items():
            if executable_name not in missing_names:
                continue

            tool_key = str(row["tool_key"])
            found_item = found_paths.get(executable_name)

            if found_item is None:
                update_tool_location(
                    connection,
                    tool_key,
                    None,
                    None,
                    "missing",
                )
                continue

            executable_path, search_source = found_item
            valid_tool_count += 1
            update_tool_location(
                connection,
                tool_key,
                executable_path,
                search_source,
                "found",
            )
            log_message(
                launcher_logger,
                "INFO",
                f"External tool found: {row['executable_name']}",
                str(executable_path),
            )

        connection.commit()

        if valid_tool_count == 0:
            log_message(
                launcher_logger,
                "WARNING",
                "No configured Inkscape or GIMP executable was found.",
            )
            show_missing_tools_warning()
    except Exception as error:
        log_message(
            launcher_logger,
            "ERROR",
            "External tool verification failed.",
            f"{type(error).__name__}: {error}",
        )
        print(f"External tool verification failed: {type(error).__name__}: {error}")
    finally:
        connection.close()


def copy_gui_sources(temp_path: Path) -> Path:
    """Copy the isolated GUI entry and its subscripts into the temp workspace.

    ``main_gui.py`` lives in ``functions`` while its importable sibling package
    lives in ``subscripts``. Only the GUI entry file is copied from ``functions``
    so unrelated DevBox function scripts are not duplicated into the temporary
    GUI workspace.
    """
    source_gui_file = devbox_source_path / "functions" / "main_gui.py"
    source_subscripts_path = devbox_source_path / "subscripts"
    target_gui_file = temp_path / "functions" / "main_gui.py"
    target_subscripts_path = temp_path / "subscripts"

    if not source_gui_file.is_file():
        raise FileNotFoundError(f"GUI entry file not found: {source_gui_file}")

    if not source_subscripts_path.is_dir():
        raise FileNotFoundError(
            f"GUI subscripts directory not found: {source_subscripts_path}"
        )

    target_gui_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_gui_file, target_gui_file)
    shutil.copytree(
        source_subscripts_path,
        target_subscripts_path,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
    )

    if not target_gui_file.is_file():
        raise FileNotFoundError(
            f"Temporary GUI entry file not found: {target_gui_file}"
        )

    return target_gui_file


def run_process_with_log(
    command: list[str],
    cwd: Path,
    script_logger: Any | None,
    process_label: str,
    environment: dict[str, str] | None = None,
) -> int:
    log_message(
        script_logger,
        "INFO",
        f"Starting process: {process_label}",
        " ".join(command),
    )

    process = subprocess.Popen(
        command,
        cwd=str(cwd),
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )

    if process.stdout is not None:
        for output_line in process.stdout:
            normalized_line = output_line.rstrip()

            if normalized_line:
                print(normalized_line)
                log_message(
                    script_logger,
                    "INFO",
                    "Console output.",
                    normalized_line,
                )

    return_code = int(process.wait())
    log_message(
        script_logger,
        "INFO" if return_code == 0 else "ERROR",
        f"Process finished: {process_label}",
        f"return_code={return_code}",
    )
    return return_code


def run_create_database(
    logger_module: Any | None,
) -> int:
    script_logger = create_script_logger(logger_module, crt_db)

    if not crt_db.is_file():
        message = f"Database creator not found: {crt_db}"
        print(message)
        log_message(script_logger, "ERROR", message)
        return 1

    print(f"Running database creator: {crt_db}")
    return run_process_with_log(
        [str(get_python_executable()), str(crt_db)],
        crt_db.parent,
        script_logger,
        "create_devdbase.py",
    )


def run_empty_project_initializer(
    logger_module: Any | None,
) -> int:
    script_logger = create_script_logger(logger_module, initializer_script)

    if not initializer_script.is_file():
        message = f"Project initializer not found: {initializer_script}"
        print(message)
        log_message(script_logger, "ERROR", message)
        return 1

    print(f"Running empty-project initializer: {initializer_script}")
    return run_process_with_log(
        [str(get_python_executable()), str(initializer_script)],
        initializer_script.parent,
        script_logger,
        "initialize_empty_application_projects.py",
    )


def run_gui(
    gui_file: Path,
    logger_module: Any | None,
    logfile_path: Path,
) -> int:
    environment = os.environ.copy()
    environment[project_root_env_name] = str(projekt_root_path)
    environment[logfile_env_name] = str(logfile_path)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONUNBUFFERED"] = "1"
    script_logger = create_script_logger(logger_module, gui_file)

    print(f"Starting temporary GUI: {gui_file}")
    return run_process_with_log(
        [str(get_python_executable()), str(gui_file)],
        projekt_root_path,
        script_logger,
        "main_gui.py",
        environment,
    )


def remove_readonly(function, path, exception_info) -> None:
    try:
        os.chmod(path, stat.S_IWRITE)
        function(path)
    except Exception:
        raise exception_info[1]


def remove_temp_path(temp_path: Path) -> bool:
    for retry_index in range(6):
        try:
            if temp_path.exists():
                shutil.rmtree(temp_path, onerror=remove_readonly)
            return True
        except OSError as exc:
            if retry_index == 5:
                print(f"Temporary GUI cleanup failed: {exc}")
                return False
            time.sleep(0.4 * (retry_index + 1))

    return False


def main() -> int:
    temp_path: Path | None = None
    logger_module: Any | None = None
    launcher_logger: Any | None = None

    try:
        runtime_directory, logfile_path, locdata_path = ensure_runtime_paths()
        os.environ[logfile_env_name] = str(logfile_path)
        logger_module = load_launcher_logger()
        launcher_logger = create_script_logger(logger_module, Path(__file__))
        log_message(
            launcher_logger,
            "INFO",
            "DevBox launcher started.",
            f"runtime_directory={runtime_directory}",
        )
        log_message(
            launcher_logger,
            "INFO",
            "Runtime databases are ready.",
            f"logfile={logfile_path}; locdata={locdata_path}",
        )

        verify_or_locate_external_tools(locdata_path, launcher_logger)

        random_provider = load_module("devbox_random_string_provider", rnd_prv)
        timestamp_provider = load_module("devbox_timestamp_provider", tme_prv)

        timestamp = timestamp_provider.generate_combined_timestamp([4, 14])
        random_string = random_provider.generate_string(length=128, variant=1)
        temp_path = Path(tempfile.gettempdir()) / f"{timestamp}_{random_string}"

        temp_path.mkdir(parents=True, exist_ok=False)
        print(f"Temporary GUI path: {temp_path}")
        log_message(launcher_logger, "INFO", "Temporary GUI path created.", str(temp_path))

        gui_file = copy_gui_sources(temp_path)
        log_message(launcher_logger, "INFO", "Temporary GUI sources copied.", str(gui_file))

        if not database_file.is_file():
            return_code = run_create_database(logger_module)

            if return_code != 0:
                message = "Database creation failed. GUI will not be started."
                print(message)
                log_message(launcher_logger, "ERROR", message)
                return return_code

        if not database_file.is_file():
            message = f"Database was not created: {database_file}"
            print(message)
            log_message(launcher_logger, "ERROR", message)
            return 1

        initializer_return_code = run_empty_project_initializer(logger_module)

        if initializer_return_code != 0:
            message = "Empty application project initialization failed. GUI will not be started."
            print(message)
            log_message(launcher_logger, "ERROR", message)
            return initializer_return_code

        return_code = run_gui(gui_file, logger_module, logfile_path)
        log_message(
            launcher_logger,
            "INFO" if return_code == 0 else "ERROR",
            "DevBox GUI process finished.",
            f"return_code={return_code}",
        )
        return return_code

    except Exception as exc:
        message = f"DevBox launcher failed: {type(exc).__name__}: {exc}"
        print(message)
        log_message(launcher_logger, "ERROR", message)
        return 1

    finally:
        if temp_path is not None:
            cleanup_successful = remove_temp_path(temp_path)
            log_message(
                launcher_logger,
                "INFO" if cleanup_successful else "WARNING",
                "Temporary GUI cleanup completed."
                if cleanup_successful
                else "Temporary GUI cleanup failed.",
                str(temp_path),
            )


if __name__ == "__main__":
    sys.exit(main())
