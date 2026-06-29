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


def find_file_in_project(runtime, project_root_path: Path, filename: str) -> Path:
    try:
        for found_file in project_root_path.rglob(filename):
            if found_file.is_file():
                return found_file.resolve()
    except Exception as error:
        runtime.fail(runtime, f'Dateisuche fehlgeschlagen: {filename} | {error}')
    runtime.fail(runtime, f'Datei wurde nicht gefunden: {filename}')

def register(runtime):
    runtime.find_file_in_project = find_file_in_project
