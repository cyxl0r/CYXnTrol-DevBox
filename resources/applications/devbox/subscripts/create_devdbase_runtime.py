from pathlib import Path
import os
import shutil
import stat
import time


def make_writable(path: str) -> None:
    try:
        os.chmod(path, stat.S_IWRITE)
    except Exception:
        pass


def remove_dir_until_gone(folder_path: Path) -> None:
    while folder_path.exists():
        try:
            shutil.rmtree(
                folder_path,
                onerror=lambda func, path, exc_info: (
                    make_writable(path),
                    func(path),
                ),
            )
        except Exception:
            time.sleep(0.25)
            continue

        if folder_path.exists():
            time.sleep(0.25)
