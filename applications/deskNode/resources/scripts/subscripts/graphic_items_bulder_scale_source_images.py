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


def scale_source_images(runtime, source_images_path: Path, scaled_images_path: Path, inkscape_executable_path: Path) -> list[Path]:
    source_files = [file_path for file_path in source_images_path.glob('*.png') if file_path.is_file()]
    source_files.sort(key=lambda file_path: file_path.name.lower())
    if not source_files:
        runtime.fail(runtime, f'Keine PNG-Dateien zum Skalieren gefunden: {source_images_path}')
    scaled_files = []
    for source_file in source_files:
        if 'symbol_source_' not in source_file.name:
            runtime.fail(runtime, f"Dateiname enthält nicht die erwartete Zeichenfolge 'symbol_source_': {source_file.name}")
        target_filename = source_file.name.replace('symbol_source_', 'symbol_scaled_', 1)
        target_file = scaled_images_path / target_filename
        source_width, source_height = runtime.get_inkscape_image_dimensions(runtime, inkscape_executable_path, source_file)
        runtime.scale_png_with_inkscape(runtime, inkscape_executable_path, source_file, target_file, source_width, source_height)
        scaled_files.append(target_file)
        print(f'Skaliert: {source_file.name} ({source_width:.0f} x {source_height:.0f}) -> {target_file.name}')
    return scaled_files

def register(runtime):
    runtime.scale_source_images = scale_source_images
