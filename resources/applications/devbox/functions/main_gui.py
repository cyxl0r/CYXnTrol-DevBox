from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
PROJECT_CODE_ROOT = SCRIPT_PATH.parent.parent

if str(PROJECT_CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_CODE_ROOT))

from subscripts.main_gui_devbox_log import get_devbox_logger
LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")

from subscripts.main_gui_bootstrap import find_project_root_or_exit


home_path = SCRIPT_PATH.parent
projekt_root_path = find_project_root_or_exit(home_path)

from subscripts.main_gui_window import run_gui


if __name__ == "__main__":
    LOGGER.info("GUI entry started.")

    try:
        exit_code = run_gui(home_path, projekt_root_path)
    except Exception as error:
        LOGGER.exception("GUI entry failed.", error)
        raise

    LOGGER.info("GUI entry finished.", f"return_code={exit_code}")
    raise SystemExit(exit_code)
