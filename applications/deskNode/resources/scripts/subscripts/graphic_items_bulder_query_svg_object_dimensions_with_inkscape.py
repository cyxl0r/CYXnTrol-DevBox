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


def query_svg_object_dimensions_with_inkscape(runtime, inkscape_executable_path: Path, svg_file: Path, object_ids: list[str]) -> dict[str, tuple[float, float]]:
    if not object_ids:
        runtime.fail(runtime, f'Es wurden keine SVG-Objekt-IDs zur Dimensionsabfrage übergeben: {svg_file}')
    command = [str(inkscape_executable_path), str(svg_file), '--query-all']
    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True, encoding='utf-8', errors='replace')
    except Exception as error:
        runtime.fail(runtime, f'Inkscape konnte nicht zur Objekt-Dimensionsabfrage gestartet werden: {svg_file} | {error}')
    if result.returncode != 0:
        runtime.fail(runtime, f'Inkscape konnte SVG-Objektdimensionen nicht abfragen: {svg_file}\nExit-Code: {result.returncode}\nFehlerausgabe: {result.stderr.strip()}')
    requested_object_ids = set(object_ids)
    object_dimensions = {}
    for output_line in result.stdout.splitlines():
        parts = output_line.strip().split(',')
        if len(parts) != 5:
            continue
        object_id = parts[0].strip()
        if object_id not in requested_object_ids:
            continue
        try:
            width = float(parts[3].strip().replace(',', '.'))
            height = float(parts[4].strip().replace(',', '.'))
        except ValueError:
            continue
        if width <= 0 or height <= 0:
            runtime.fail(runtime, f'Inkscape lieferte ungültige Objektmaße für Unschärfe: SVG: {svg_file} | ID: {object_id} | Breite: {width} | Höhe: {height}')
        object_dimensions[object_id] = (width, height)
    missing_object_ids = [object_id for object_id in object_ids if object_id not in object_dimensions]
    if missing_object_ids:
        runtime.fail(runtime, f'Inkscape lieferte nicht für alle SVG-Objekte Maße. SVG: {svg_file} | Fehlende IDs: {missing_object_ids}')
    return object_dimensions

def register(runtime):
    runtime.query_svg_object_dimensions_with_inkscape = query_svg_object_dimensions_with_inkscape
