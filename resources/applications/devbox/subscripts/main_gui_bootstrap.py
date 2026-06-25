from __future__ import annotations

from subscripts.main_gui_devbox_log import get_devbox_logger
LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")

import os
import sys
from pathlib import Path


ROOT_MARKER_NAME = ".root"
ROOT_MARKER_TEXT = "project-root"
PROJECT_ROOT_ENV_NAME = "_CYXLABS_DEVBOX_PROJECT_ROOT_PATH"


def is_project_root(project_root_path: Path) -> bool:
    root_file = Path(project_root_path).resolve() / ROOT_MARKER_NAME

    if not root_file.is_file():
        return False

    return root_file.read_text(encoding="utf-8").strip() == ROOT_MARKER_TEXT


def find_project_root_or_exit(home_path: Path) -> Path:
    environment_path = os.environ.get(PROJECT_ROOT_ENV_NAME, "").strip()

    if environment_path:
        candidate_path = Path(environment_path).expanduser().resolve()

        if is_project_root(candidate_path):
            os.chdir(candidate_path)
            return candidate_path

        print(f"Invalid project root environment path: {candidate_path}")

    home_path = Path(home_path).resolve()
    os.chdir(home_path)
    current_path = home_path

    while True:
        root_file = current_path / ROOT_MARKER_NAME

        if root_file.is_file():
            content = root_file.read_text(encoding="utf-8").strip()

            if content == ROOT_MARKER_TEXT:
                os.chdir(current_path)
                return current_path

        parent_path = current_path.parent

        if parent_path == current_path:
            print("No project root found.")
            sys.exit(0)

        current_path = parent_path
        os.chdir(current_path)
