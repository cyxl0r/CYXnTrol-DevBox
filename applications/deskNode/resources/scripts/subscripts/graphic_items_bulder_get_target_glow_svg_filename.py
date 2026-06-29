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


def get_target_glow_svg_filename(runtime, source_file: Path, glow_state: str, layer_name: str) -> str:
    source_prefix = 'symbol_mask_'
    if not source_file.name.startswith(source_prefix):
        runtime.fail(runtime, f'Masken-SVG hat keinen erwarteten Dateinamenpräfix: {source_file.name}')
    if glow_state not in {'on', 'off'}:
        runtime.fail(runtime, f'Ungültiger Glow-Status für SVG-Dateinamen: {glow_state!r}')
    if layer_name not in {'layer1', 'layer2'}:
        runtime.fail(runtime, f'Ungültiger Layername für SVG-Dateinamen: {layer_name!r}')
    filename_tail = source_file.name.removeprefix(source_prefix)
    return f'symbol_glow-{glow_state}-{layer_name}_{filename_tail}'

def register(runtime):
    runtime.get_target_glow_svg_filename = get_target_glow_svg_filename
