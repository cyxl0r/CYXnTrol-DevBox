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


def create_final_version1_files(runtime, qfying_pngs: Path, final_path: Path) -> list[Path]:
    if not qfying_pngs.is_dir():
        runtime.fail(runtime, f'Quadrofying-PNG-Ordner wurde nicht gefunden: {qfying_pngs}')
    if not final_path.is_dir():
        runtime.fail(runtime, f'Final-Ordner wurde nicht gefunden: {final_path}')
    source_files = [file_path for file_path in qfying_pngs.glob('symbol_qfying_*.png') if file_path.is_file()]
    source_files.sort(key=lambda file_path: file_path.name.lower())
    if not source_files:
        runtime.fail(runtime, f'Keine symbol_qfying_*.png-Dateien gefunden: {qfying_pngs}')
    version1_files = []
    for source_file in source_files:
        target_filename = runtime.get_final_filename(runtime, source_file, 'symbol_qfying_', 'symbol_vers1_')
        target_file = final_path / target_filename
        try:
            shutil.copy2(source_file, target_file)
        except Exception as error:
            runtime.fail(runtime, f'Quadrofying-PNG konnte nicht als Final-Version 1 kopiert werden: {source_file} -> {target_file} | {error}')
        if not target_file.is_file():
            runtime.fail(runtime, f'Final-Version-1-PNG wurde nicht erzeugt: {target_file}')
        if target_file.stat().st_size <= 0:
            runtime.fail(runtime, f'Final-Version-1-PNG ist leer: {target_file}')
        version1_files.append(target_file)
        print(f'Final-Version 1 kopiert: {source_file.name} -> {target_file.name}')
    return version1_files

def register(runtime):
    runtime.create_final_version1_files = create_final_version1_files
