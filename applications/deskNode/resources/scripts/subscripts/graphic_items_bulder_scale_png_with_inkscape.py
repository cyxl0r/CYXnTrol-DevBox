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


def scale_png_with_inkscape(runtime, inkscape_executable_path: Path, source_file: Path, target_file: Path, source_width: float, source_height: float) -> None:
    command = [str(inkscape_executable_path), str(source_file), '--export-type=png', '--export-area-page', '--export-background-opacity=0', f'--export-filename={target_file}']
    if source_width > source_height:
        command.append(f'--export-width={runtime.TARGET_IMAGE_SIZE}')
    elif source_height > source_width:
        command.append(f'--export-height={runtime.TARGET_IMAGE_SIZE}')
    else:
        command.append(f'--export-width={runtime.TARGET_IMAGE_SIZE}')
        command.append(f'--export-height={runtime.TARGET_IMAGE_SIZE}')
    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True, encoding='utf-8', errors='replace')
    except Exception as error:
        runtime.fail(runtime, f'Inkscape konnte nicht zum Skalieren gestartet werden: {source_file} | {error}')
    if result.returncode != 0:
        runtime.fail(runtime, f'Inkscape konnte PNG nicht skalieren: {source_file}\nExit-Code: {result.returncode}\nFehlerausgabe: {result.stderr.strip()}')
    if not target_file.is_file():
        runtime.fail(runtime, f'Skalierte PNG wurde nicht erzeugt: {target_file}')
    if target_file.stat().st_size <= 0:
        runtime.fail(runtime, f'Skalierte PNG ist leer: {target_file}')

def register(runtime):
    runtime.scale_png_with_inkscape = scale_png_with_inkscape
