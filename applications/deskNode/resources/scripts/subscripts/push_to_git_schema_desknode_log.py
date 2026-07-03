from __future__ import annotations

from datetime import datetime
from pathlib import Path


class ProcessReporter:
    """Small console reporter captured by the DevBox repository view."""

    def __init__(self, source_file: str | Path) -> None:
        self.source_file = Path(source_file).name

    @staticmethod
    def _format(level: str, message: object, details: object = "") -> str:
        timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
        line = f"[{timestamp}] [{level}] {message}"
        if details:
            line = f"{line}\n{details}"
        return line

    def log(self, level: str, message: object, details: object = "") -> None:
        print(self._format(str(level).upper(), message, details), flush=True)

    def info(self, message: object, details: object = "") -> None:
        self.log("INFO", message, details)

    def warning(self, message: object, details: object = "") -> None:
        self.log("WARNING", message, details)

    def error(self, message: object, details: object = "") -> None:
        self.log("ERROR", message, details)

    def exception(self, message: object, error: BaseException) -> None:
        self.error(message, f"{type(error).__name__}: {error}")
