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


def render_svg_to_png_with_inkscape(runtime, inkscape_executable_path: Path, svg_file: Path, png_file: Path) -> None:
    command = [str(inkscape_executable_path), str(svg_file), '--export-type=png', '--export-area-page', '--export-background-opacity=0', f'--export-filename={png_file}']
    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True, encoding='utf-8', errors='replace')
    except Exception as error:
        runtime.fail(runtime, f'Inkscape konnte nicht zum Rendern der Theme-SVG als PNG gestartet werden: {svg_file} | {error}')
    if result.returncode != 0:
        runtime.fail(runtime, f'Inkscape konnte Theme-SVG nicht als PNG rendern: {svg_file}\nExit-Code: {result.returncode}\nFehlerausgabe: {result.stderr.strip()}')
    if not png_file.is_file():
        runtime.fail(runtime, f'Gerenderte Theme-PNG wurde nicht erzeugt: {png_file}')
    if png_file.stat().st_size <= 0:
        runtime.fail(runtime, f'Gerenderte Theme-PNG ist leer: {png_file}')

def register(runtime):
    runtime.render_svg_to_png_with_inkscape = render_svg_to_png_with_inkscape
