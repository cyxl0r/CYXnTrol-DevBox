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


def open_explorer(runtime, directory_path: Path) -> None:
    if not directory_path.is_dir():
        runtime.fail(runtime, f'Explorer-Zielordner existiert nicht: {directory_path}')
    try:
        subprocess.Popen(['explorer.exe', str(directory_path)])
    except Exception as error:
        runtime.fail(runtime, f'Explorer konnte nicht geöffnet werden: {directory_path} | {error}')

def register(runtime):
    runtime.open_explorer = open_explorer
