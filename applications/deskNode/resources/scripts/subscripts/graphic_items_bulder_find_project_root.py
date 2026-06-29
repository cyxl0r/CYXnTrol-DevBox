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


def find_project_root(runtime, start_path: Path) -> Path:
    check_path = start_path.resolve()
    while True:
        root_marker_file = check_path / '.root'
        if root_marker_file.is_file():
            try:
                marker_content = root_marker_file.read_text(encoding='utf-8').strip()
            except Exception:
                marker_content = ''
            if marker_content == 'project-root':
                return check_path
        if check_path == check_path.parent:
            runtime.fail(runtime, 'Projektroot wurde nicht gefunden.')
        check_path = check_path.parent

def register(runtime):
    runtime.find_project_root = find_project_root
