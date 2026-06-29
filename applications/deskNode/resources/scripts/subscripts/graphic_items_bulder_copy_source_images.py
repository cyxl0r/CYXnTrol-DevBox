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


def copy_source_images(runtime, project_root_path: Path, source_images_path: Path) -> list[Path]:
    graphics_path = project_root_path / 'resources' / 'graphics'
    if not graphics_path.is_dir():
        runtime.fail(runtime, f'Grafikordner wurde nicht gefunden: {graphics_path}')
    source_files = [file_path for file_path in graphics_path.glob('symbol_source_*.png') if file_path.is_file()]
    source_files.sort(key=lambda file_path: file_path.name.lower())
    if not source_files:
        runtime.fail(runtime, f'Es wurden keine symbol_source_*.png-Dateien gefunden: {graphics_path}')
    copied_files = []
    for source_file in source_files:
        target_file = source_images_path / source_file.name
        try:
            shutil.copy2(source_file, target_file)
        except Exception as error:
            runtime.fail(runtime, f'Grafik konnte nicht kopiert werden: {source_file} -> {target_file} | {error}')
        if not target_file.is_file():
            runtime.fail(runtime, f'Kopierte Grafik existiert nicht: {target_file}')
        copied_files.append(target_file)
    return copied_files

def register(runtime):
    runtime.copy_source_images = copy_source_images
