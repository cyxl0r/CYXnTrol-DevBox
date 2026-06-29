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


def create_mask_svg_files(runtime, step_two_pngs: Path, masks_svg_path: Path, inkscape_executable_path: Path) -> list[Path]:
    runtime.ensure_inkscape_object_trace_action(runtime, inkscape_executable_path)
    mask_b_files = [file_path for file_path in step_two_pngs.glob('symbol_maskB_*.png') if file_path.is_file()]
    mask_b_files.sort(key=lambda file_path: file_path.name.lower())
    if not mask_b_files:
        runtime.fail(runtime, f'Keine symbol_maskB_*.png-Dateien gefunden: {step_two_pngs}')
    mask_svg_files = []
    for mask_b_file in mask_b_files:
        image_width, image_height = runtime.get_inkscape_image_dimensions(runtime, inkscape_executable_path, mask_b_file)
        mask_svg_filename = mask_b_file.name.replace('symbol_maskB_', 'symbol_mask_', 1)
        mask_svg_file = masks_svg_path / Path(mask_svg_filename).with_suffix('.svg')
        temporary_source_svg_file = masks_svg_path / f'__trace_source_{mask_svg_file.stem}.svg'
        if temporary_source_svg_file.exists():
            runtime.remove_file_until_gone(runtime, temporary_source_svg_file)
        if mask_svg_file.exists():
            runtime.remove_file_until_gone(runtime, mask_svg_file)
        canvas_size = runtime.create_trace_source_svg(runtime, temporary_source_svg_file, mask_b_file, image_width, image_height)
        runtime.run_inkscape_bitmap_trace(runtime, inkscape_executable_path, temporary_source_svg_file, mask_svg_file)
        removed_element_count = runtime.clean_traced_mask_svg(runtime, mask_svg_file)
        runtime.remove_file_until_gone(runtime, temporary_source_svg_file)
        if not mask_svg_file.is_file():
            runtime.fail(runtime, f'Die fertige Masken-SVG existiert nicht: {mask_svg_file}')
        if mask_svg_file.stat().st_size <= 0:
            runtime.fail(runtime, f'Die fertige Masken-SVG ist leer: {mask_svg_file}')
        mask_svg_files.append(mask_svg_file)
        print(f'Masken-SVG erzeugt: {mask_b_file.name} -> {mask_svg_file.name} ({canvas_size} x {canvas_size}px, entfernte Objekte: {removed_element_count})')
    return mask_svg_files

def register(runtime):
    runtime.create_mask_svg_files = create_mask_svg_files
