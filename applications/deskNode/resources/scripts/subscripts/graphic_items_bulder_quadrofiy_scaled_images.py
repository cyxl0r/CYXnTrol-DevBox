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


def quadrofiy_scaled_images(runtime, scaled_images_path: Path, qfying_pngs: Path, inkscape_executable_path: Path) -> list[Path]:
    scaled_files = [file_path for file_path in scaled_images_path.glob('symbol_scaled_*.png') if file_path.is_file()]
    scaled_files.sort(key=lambda file_path: file_path.name.lower())
    if not scaled_files:
        runtime.fail(runtime, f'Keine symbol_scaled_*.png-Dateien gefunden: {scaled_images_path}')
    qfying_files = []
    for scaled_file in scaled_files:
        image_width, image_height = runtime.get_png_pixel_dimensions(runtime, scaled_file)
        qfying_filename = scaled_file.name.replace('symbol_scaled_', 'symbol_qfying_', 1)
        qfying_file = qfying_pngs / qfying_filename
        temporary_svg_file = qfying_pngs / f'{qfying_file.stem}_temporary.svg'
        if temporary_svg_file.exists():
            runtime.remove_file_until_gone(runtime, temporary_svg_file)
        canvas_size = runtime.create_centered_png_svg(runtime, temporary_svg_file, scaled_file, image_width, image_height)
        runtime.export_svg_to_png_with_inkscape(runtime, inkscape_executable_path, temporary_svg_file, qfying_file, canvas_size)
        runtime.remove_file_until_gone(runtime, temporary_svg_file)
        qfying_files.append(qfying_file)
        print(f'Quadrofied: {scaled_file.name} ({image_width:.0f} x {image_height:.0f}) -> {qfying_file.name} ({canvas_size} x {canvas_size})')
    return qfying_files

def register(runtime):
    runtime.quadrofiy_scaled_images = quadrofiy_scaled_images
