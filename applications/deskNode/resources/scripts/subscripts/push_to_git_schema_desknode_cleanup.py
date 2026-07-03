from __future__ import annotations

import os
import shutil
import stat
import time
from pathlib import Path


def _remove_readonly(function, path, _exception_info) -> None:
    os.chmod(path, stat.S_IWRITE)
    function(path)


def cleanup_workspace(temp_path: Path, reporter) -> bool:
    for attempt in range(6):
        try:
            if temp_path.exists():
                shutil.rmtree(temp_path, onerror=_remove_readonly)
            if not temp_path.exists():
                return True
        except OSError as error:
            if attempt == 5:
                reporter.warning("Could not remove temporary deskNode publish workspace.", error)
                return False
        time.sleep(0.4 * (attempt + 1))
    return not temp_path.exists()
