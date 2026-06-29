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


def run_inkscape_bitmap_trace(runtime, inkscape_executable_path: Path, source_svg_file: Path, target_svg_file: Path) -> None:
    runtime.validate_trace_bitmap_settings(runtime)
    trace_settings = ','.join((str(runtime.TRACE_BITMAP_COLOR_SCANS), str(runtime.TRACE_BITMAP_SMOOTH).lower(), str(runtime.TRACE_BITMAP_STACK).lower(), str(runtime.TRACE_BITMAP_REMOVE_BACKGROUND).lower(), str(runtime.TRACE_BITMAP_SPECKLES), f'{runtime.TRACE_BITMAP_SMOOTH_CORNERS:.2f}', f'{runtime.TRACE_BITMAP_OPTIMIZE:.3f}'))
    target_svg_action_path = target_svg_file.resolve().as_posix()
    actions = ';'.join(('select-clear', 'select-by-id:source_mask_image', f'object-trace:{trace_settings}', 'select-clear', 'select-by-id:source_mask_image', 'delete-selection', 'export-plain-svg', f'export-filename:{target_svg_action_path}', 'export-do'))
    command = [str(inkscape_executable_path), str(source_svg_file), f'--actions={actions}']
    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True, encoding='utf-8', errors='replace')
    except Exception as error:
        runtime.fail(runtime, f'Inkscape konnte nicht zum Bitmap-Nachzeichnen gestartet werden: {source_svg_file} | {error}')
    if result.returncode != 0:
        runtime.fail(runtime, f'Inkscape konnte die Masken-SVG nicht nachzeichnen.\nQuell-SVG: {source_svg_file}\nExit-Code: {result.returncode}\nStandardausgabe:\n{result.stdout.strip()}\nFehlerausgabe:\n{result.stderr.strip()}')
    if not target_svg_file.is_file():
        runtime.fail(runtime, f'Inkscape hat keine nachgezeichnete SVG erzeugt: {target_svg_file}')
    if target_svg_file.stat().st_size <= 0:
        runtime.fail(runtime, f'Die nachgezeichnete SVG ist leer: {target_svg_file}')

def register(runtime):
    runtime.run_inkscape_bitmap_trace = run_inkscape_bitmap_trace
