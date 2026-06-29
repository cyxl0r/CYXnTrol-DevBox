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


def export_svg_to_png_with_inkscape(runtime, inkscape_executable_path: Path, svg_file: Path, target_file: Path, canvas_size: int) -> None:
    command = [str(inkscape_executable_path), str(svg_file), '--export-type=png', '--export-area-page', '--export-background-opacity=0', f'--export-width={canvas_size}', f'--export-height={canvas_size}', f'--export-filename={target_file}']
    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True, encoding='utf-8', errors='replace')
    except Exception as error:
        runtime.fail(runtime, f'Inkscape konnte nicht zum Quadrofying gestartet werden: {svg_file} | {error}')
    if result.returncode != 0:
        runtime.fail(runtime, f'Inkscape konnte keine quadratische PNG erzeugen: {svg_file}\nExit-Code: {result.returncode}\nFehlerausgabe: {result.stderr.strip()}')
    if not target_file.is_file():
        runtime.fail(runtime, f'Quadrofied PNG wurde nicht erzeugt: {target_file}')
    if target_file.stat().st_size <= 0:
        runtime.fail(runtime, f'Quadrofied PNG ist leer: {target_file}')

def register(runtime):
    runtime.export_svg_to_png_with_inkscape = export_svg_to_png_with_inkscape
