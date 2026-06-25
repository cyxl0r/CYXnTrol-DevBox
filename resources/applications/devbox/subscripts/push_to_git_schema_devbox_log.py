from __future__ import annotations

from datetime import datetime
from pathlib import Path

from subscripts.main_gui_devbox_log import get_devbox_logger


MODULE_LOGGER = get_devbox_logger(__file__)
MODULE_LOGGER.info("Module loaded.")


class ProcessReporter:
    """Writes a traceable console and AppData SQLite log for this process."""

    def __init__(self, source_file: str | Path) -> None:
        self._logger = get_devbox_logger(source_file)

    @staticmethod
    def _console_line(level: str, message: object, details: object = "") -> str:
        timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
        text = f"[{timestamp}] [{level}] {message}"
        if details:
            text = f"{text}\n{details}"
        return text

    def log(self, level: str, message: object, details: object = "") -> None:
        normalized_level = str(level or "INFO").upper()
        print(self._console_line(normalized_level, message, details), flush=True)
        self._logger.log(normalized_level, message, details)

    def info(self, message: object, details: object = "") -> None:
        self.log("INFO", message, details)

    def warning(self, message: object, details: object = "") -> None:
        self.log("WARNING", message, details)

    def error(self, message: object, details: object = "") -> None:
        self.log("ERROR", message, details)

    def exception(self, message: object, error: BaseException) -> None:
        self._logger.exception(message, error)
        self.error(message, f"{type(error).__name__}: {error}")
