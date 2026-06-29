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


def apply_solid_theme_color_to_svg(runtime, svg_file: Path, rgba_hex: str, inkscape_executable_path: Path) -> int:
    rgb_color, opacity_value = runtime.rgba_hex_to_svg_color_and_opacity(runtime, rgba_hex)
    tree, root = runtime.load_svg_tree(runtime, svg_file)
    paintable_elements = runtime.get_paintable_svg_elements(runtime, root)
    if not paintable_elements:
        runtime.fail(runtime, f'SVG enthält keine einfärbbaren Vektorformen: {svg_file}')
    for paintable_element in paintable_elements:
        runtime.clear_svg_fill_and_opacity(runtime, paintable_element)
        paintable_element.set('fill', rgb_color)
        paintable_element.set('fill-opacity', opacity_value)
        runtime.apply_common_svg_object_style(runtime, root, paintable_element)
    runtime.save_svg_tree(runtime, tree, svg_file)
    return runtime.apply_inkscape_compatible_blur_to_svg(runtime, svg_file, inkscape_executable_path)

def register(runtime):
    runtime.apply_solid_theme_color_to_svg = apply_solid_theme_color_to_svg
