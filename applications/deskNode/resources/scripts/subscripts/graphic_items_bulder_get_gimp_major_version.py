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


def get_gimp_major_version(runtime, gimp_executable_path: Path) -> int:
    try:
        result = subprocess.run([str(gimp_executable_path), '--version'], check=False, capture_output=True, text=True, encoding='utf-8', errors='replace')
    except Exception as error:
        runtime.fail(runtime, f'GIMP-Version konnte nicht abgefragt werden: {gimp_executable_path} | {error}')
    version_text = result.stdout + '\n' + result.stderr
    version_match = re.search('(\\d+)\\.(\\d+)(?:\\.\\d+)?', version_text)
    if version_match is None:
        runtime.fail(runtime, f'GIMP-Version konnte nicht ausgelesen werden. Ausgabe: {version_text.strip()!r}')
    return int(version_match.group(1))

def register(runtime):
    runtime.get_gimp_major_version = get_gimp_major_version
