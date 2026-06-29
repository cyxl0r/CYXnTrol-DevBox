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


def create_zip_archive_from_directory(runtime, source_directory: Path, archive_path: Path) -> tuple[int, int]:
    if not source_directory.is_dir():
        runtime.fail(runtime, f'ZIP-Quellordner wurde nicht gefunden: {source_directory}')
    if archive_path.exists():
        runtime.remove_file_until_gone(runtime, archive_path)
    archive_files = [file_path for file_path in source_directory.rglob('*') if file_path.is_file()]
    archive_files.sort(key=lambda file_path: str(file_path.relative_to(source_directory)).lower())
    if not archive_files:
        runtime.fail(runtime, f'Der Final-Ordner enthält keine Dateien zum Archivieren: {source_directory}')
    try:
        with zipfile.ZipFile(archive_path, mode='w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zip_archive:
            for archive_file in archive_files:
                zip_archive.write(archive_file, archive_file.relative_to(source_directory))
    except Exception as error:
        runtime.fail(runtime, f'Final-Ordner konnte nicht als ZIP-Archiv gepackt werden: {source_directory} -> {archive_path} | {error}')
    if not archive_path.is_file():
        runtime.fail(runtime, f'ZIP-Archiv wurde nicht erzeugt: {archive_path}')
    if archive_path.stat().st_size <= 0:
        runtime.fail(runtime, f'ZIP-Archiv ist leer: {archive_path}')
    if not zipfile.is_zipfile(archive_path):
        runtime.fail(runtime, f'Erzeugte Datei ist kein gültiges ZIP-Archiv: {archive_path}')
    return (len(archive_files), archive_path.stat().st_size)

def register(runtime):
    runtime.create_zip_archive_from_directory = create_zip_archive_from_directory
