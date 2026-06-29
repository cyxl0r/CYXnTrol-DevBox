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


def install_graphic_items_archive(runtime, archive_path: Path, graphic_items_database: Path) -> None:
    if not archive_path.is_file():
        runtime.fail(runtime, f'Zu installierendes Items-Archiv wurde nicht gefunden: {archive_path}')
    target_directory = graphic_items_database.parent
    if not target_directory.is_dir():
        runtime.fail(runtime, f'Zielordner für graphic_items.r0b wurde nicht gefunden: {target_directory}')
    if graphic_items_database.exists():
        runtime.remove_file_until_gone(runtime, graphic_items_database)
    try:
        shutil.copy2(archive_path, graphic_items_database)
    except Exception as error:
        runtime.fail(runtime, f'Items-Archiv konnte nicht als graphic_items.r0b installiert werden: {archive_path} -> {graphic_items_database} | {error}')
    if not graphic_items_database.is_file():
        runtime.fail(runtime, f'graphic_items.r0b wurde nicht installiert: {graphic_items_database}')
    if graphic_items_database.stat().st_size != archive_path.stat().st_size:
        runtime.fail(runtime, f'graphic_items.r0b besitzt nicht dieselbe Größe wie das Items-Archiv: Archiv: {archive_path.stat().st_size} | Ziel: {graphic_items_database.stat().st_size}')
    if not zipfile.is_zipfile(graphic_items_database):
        runtime.fail(runtime, f'Die installierte graphic_items.r0b ist kein gültiges ZIP-Archiv: {graphic_items_database}')

def register(runtime):
    runtime.install_graphic_items_archive = install_graphic_items_archive
