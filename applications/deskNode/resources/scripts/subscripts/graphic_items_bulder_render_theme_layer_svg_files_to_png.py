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


def render_theme_layer_svg_files_to_png(runtime, theme_layer_directories: dict[str, dict[str, Path]], inkscape_executable_path: Path) -> int:
    if not theme_layer_directories:
        runtime.fail(runtime, 'Es wurden keine UX-Theme-Glow-Ordner zum PNG-Rendern übergeben.')
    rendered_png_count = 0
    for directories_for_theme in theme_layer_directories.values():
        for target_directory in directories_for_theme.values():
            if not target_directory.is_dir():
                runtime.fail(runtime, f'UX-Theme-Glow-Ordner existiert nicht für PNG-Rendering: {target_directory}')
            svg_files = [file_path for file_path in target_directory.glob('*.svg') if file_path.is_file()]
            svg_files.sort(key=lambda file_path: file_path.name.lower())
            for svg_file in svg_files:
                png_file = svg_file.with_suffix('.png')
                runtime.render_svg_to_png_with_inkscape(runtime, inkscape_executable_path, svg_file, png_file)
                rendered_png_count += 1
            print(f'Theme-Glow-PNGs gerendert: {target_directory.name} ({len(svg_files)} Dateien)')
    return rendered_png_count

def register(runtime):
    runtime.render_theme_layer_svg_files_to_png = render_theme_layer_svg_files_to_png
