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


def copy_mask_svg_files_to_final(runtime, masks_svg_path: Path, final_path: Path) -> list[Path]:
    if not masks_svg_path.is_dir():
        runtime.fail(runtime, f'Masken-SVG-Ordner wurde nicht gefunden: {masks_svg_path}')
    if not final_path.is_dir():
        runtime.fail(runtime, f'Final-Ordner wurde nicht gefunden: {final_path}')
    source_files = [file_path for file_path in masks_svg_path.glob('*.*') if file_path.is_file()]
    source_files.sort(key=lambda file_path: file_path.name.lower())
    if not source_files:
        runtime.fail(runtime, f'Im Masken-SVG-Ordner wurden keine Dateien gefunden: {masks_svg_path}')
    copied_files = []
    for source_file in source_files:
        target_file = final_path / source_file.name
        if target_file.exists():
            runtime.remove_file_until_gone(runtime, target_file)
        try:
            shutil.copy2(source_file, target_file)
        except Exception as error:
            runtime.fail(runtime, f'Masken-SVG konnte nicht in den Final-Ordner kopiert werden: {source_file} -> {target_file} | {error}')
        if not target_file.is_file():
            runtime.fail(runtime, f'Kopierte Masken-SVG existiert nicht: {target_file}')
        if target_file.stat().st_size <= 0:
            runtime.fail(runtime, f'Kopierte Masken-SVG ist leer: {target_file}')
        copied_files.append(target_file)
    return copied_files

def register(runtime):
    runtime.copy_mask_svg_files_to_final = copy_mask_svg_files_to_final
