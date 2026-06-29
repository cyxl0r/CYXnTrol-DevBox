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


def render_png_composition_svg_with_inkscape(runtime, inkscape_executable_path: Path, source_svg_file: Path, target_png_file: Path, canvas_width: int, canvas_height: int) -> None:
    command = [str(inkscape_executable_path), str(source_svg_file), '--export-type=png', '--export-area-page', '--export-background-opacity=0', f'--export-width={canvas_width}', f'--export-height={canvas_height}', f'--export-filename={target_png_file}']
    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True, encoding='utf-8', errors='replace')
    except Exception as error:
        runtime.fail(runtime, f'Inkscape konnte nicht zum PNG-Kompositionsrendering gestartet werden: {source_svg_file} | {error}')
    if result.returncode != 0:
        runtime.fail(runtime, f'Inkscape konnte PNG-Komposition nicht rendern.\nQuell-SVG: {source_svg_file}\nZiel-PNG: {target_png_file}\nExit-Code: {result.returncode}\nStandardausgabe:\n{result.stdout.strip()}\nFehlerausgabe:\n{result.stderr.strip()}')
    if not target_png_file.is_file():
        runtime.fail(runtime, f'PNG-Komposition wurde nicht erzeugt: {target_png_file}')
    if target_png_file.stat().st_size <= 0:
        runtime.fail(runtime, f'PNG-Komposition ist leer: {target_png_file}')
    target_width, target_height = runtime.get_png_pixel_dimensions(runtime, target_png_file)
    if target_width != canvas_width or target_height != canvas_height:
        runtime.fail(runtime, f'PNG-Komposition besitzt nicht die erwartete Zielgröße: {target_png_file} | Erwartet: {canvas_width} x {canvas_height} | Gefunden: {target_width} x {target_height}')

def register(runtime):
    runtime.render_png_composition_svg_with_inkscape = render_png_composition_svg_with_inkscape
