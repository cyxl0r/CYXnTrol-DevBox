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


def create_final_version2_files(runtime, version1_files: list[Path], final_path: Path, inkscape_executable_path: Path) -> list[Path]:
    runtime.validate_final_version2_opacity(runtime)
    if not version1_files:
        runtime.fail(runtime, 'Es wurden keine Final-Version-1-PNGs zum Erzeugen von Version 2 übergeben.')
    version2_files = []
    for version1_file in version1_files:
        canvas_width, canvas_height = runtime.get_png_pixel_dimensions(runtime, version1_file)
        target_filename = runtime.get_final_filename(runtime, version1_file, 'symbol_vers1_', 'symbol_vers2_')
        target_file = final_path / target_filename
        temporary_svg_file = final_path / f'__opacity_{target_file.stem}.svg'
        if temporary_svg_file.exists():
            runtime.remove_file_until_gone(runtime, temporary_svg_file)
        runtime.write_png_composition_svg(runtime, temporary_svg_file, canvas_width, canvas_height, [(version1_file, runtime.FINAL_VERSION2_OPACITY)])
        runtime.render_png_composition_svg_with_inkscape(runtime, inkscape_executable_path, temporary_svg_file, target_file, canvas_width, canvas_height)
        runtime.remove_file_until_gone(runtime, temporary_svg_file)
        version2_files.append(target_file)
        print(f'Final-Version 2 gerendert: {version1_file.name} -> {target_file.name} (Deckkraft: {runtime.FINAL_VERSION2_OPACITY:.0%})')
    return version2_files

def register(runtime):
    runtime.create_final_version2_files = create_final_version2_files
