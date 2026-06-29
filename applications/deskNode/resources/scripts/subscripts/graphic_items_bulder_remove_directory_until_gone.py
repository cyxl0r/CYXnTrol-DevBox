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


def remove_directory_until_gone(runtime, directory_path: Path) -> None:
    if directory_path.exists() and (not directory_path.is_dir()):
        runtime.fail(runtime, f'Der zu löschende Pfad ist kein Ordner: {directory_path}')
    while directory_path.exists():
        try:
            shutil.rmtree(directory_path, onerror=lambda _function, failed_path, _exception: runtime.make_writable_for_removal(runtime, failed_path) or _function(failed_path))
        except FileNotFoundError:
            pass
        except Exception as error:
            print(f'Ordner konnte noch nicht gelöscht werden: {directory_path} | {error}')
        if directory_path.exists():
            time.sleep(0.2)

def register(runtime):
    runtime.remove_directory_until_gone = remove_directory_until_gone
