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


def get_glow_composite_source_files(runtime, qfying_file: Path, glow_layer1_path: Path, glow_layer2_path: Path, glow_state: str) -> tuple[Path, Path]:
    source_prefix = 'symbol_qfying_'
    if not qfying_file.name.startswith(source_prefix):
        runtime.fail(runtime, f'Quadrofying-PNG hat keinen erwarteten Dateinamenpräfix: {qfying_file.name}')
    normalized_glow_state = str(glow_state).strip().lower()
    if normalized_glow_state not in {'on', 'off'}:
        runtime.fail(runtime, f'Ungültiger Glow-State für Kompositionsquellen: {glow_state!r}')
    filename_tail = qfying_file.name.removeprefix(source_prefix)
    layer1_file = glow_layer1_path / f'symbol_glow-{normalized_glow_state}-layer1_{filename_tail}'
    layer2_file = glow_layer2_path / f'symbol_glow-{normalized_glow_state}-layer2_{filename_tail}'
    if not layer1_file.is_file():
        runtime.fail(runtime, f'Zugehörige Glow-{normalized_glow_state.title()}-Layer-1-PNG wurde nicht gefunden: {layer1_file}')
    if not layer2_file.is_file():
        runtime.fail(runtime, f'Zugehörige Glow-{normalized_glow_state.title()}-Layer-2-PNG wurde nicht gefunden: {layer2_file}')
    return (layer1_file, layer2_file)

def register(runtime):
    runtime.get_glow_composite_source_files = get_glow_composite_source_files
