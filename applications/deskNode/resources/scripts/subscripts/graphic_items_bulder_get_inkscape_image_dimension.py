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


def get_inkscape_image_dimension(runtime, inkscape_executable_path: Path, image_path: Path, dimension: str) -> float:
    if dimension not in {'width', 'height'}:
        runtime.fail(runtime, f'Ungültige Inkscape-Bilddimension: {dimension}')
    command = [str(inkscape_executable_path), str(image_path), f'--query-{dimension}']
    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True, encoding='utf-8', errors='replace')
    except Exception as error:
        runtime.fail(runtime, f'Inkscape konnte nicht zur Dimensionsabfrage gestartet werden: {image_path} | {error}')
    if result.returncode != 0:
        runtime.fail(runtime, f'Inkscape konnte die Bilddimension nicht abfragen: {image_path}\nExit-Code: {result.returncode}\nFehlerausgabe: {result.stderr.strip()}')
    raw_value = result.stdout.strip().replace(',', '.')
    try:
        value = float(raw_value)
    except ValueError:
        runtime.fail(runtime, f'Inkscape lieferte keine lesbare Bilddimension: {image_path} | Dimension: {dimension} | Wert: {raw_value!r}')
    if value <= 0:
        runtime.fail(runtime, f'Inkscape lieferte eine ungültige Bilddimension: {image_path} | Dimension: {dimension} | Wert: {value}')
    return value

def register(runtime):
    runtime.get_inkscape_image_dimension = get_inkscape_image_dimension
