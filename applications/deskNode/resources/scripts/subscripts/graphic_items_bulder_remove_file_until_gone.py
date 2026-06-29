from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import html
import importlib.util
import os
import re
import shutil
import sqlite3
import stat
import struct
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ElementTree
import zipfile


def remove_file_until_gone(runtime, file_path: Path) -> None:
    while file_path.exists():
        try:
            if file_path.is_file() or file_path.is_symlink():
                try:
                    os.chmod(file_path, 438)
                except Exception:
                    pass
                file_path.unlink()
            else:
                runtime.fail(runtime, f'Der zu löschende Pfad ist keine Datei: {file_path}')
        except Exception as error:
            print(f'Datei konnte noch nicht gelöscht werden: {file_path} | {error}')
        if file_path.exists():
            time.sleep(0.2)

def register(runtime):
    runtime.remove_file_until_gone = remove_file_until_gone
