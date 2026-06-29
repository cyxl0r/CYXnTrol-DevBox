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


def create_trace_source_svg(runtime, svg_file: Path, source_file: Path, image_width: float, image_height: float) -> int:
    canvas_size = runtime.TARGET_IMAGE_SIZE + runtime.HEADROOM_IMAGE_SIZE
    horizontal_position = (canvas_size - image_width) / 2
    vertical_position = (canvas_size - image_height) / 2
    source_uri = html.escape(source_file.resolve().as_uri(), quote=True)
    svg_content = f'<?xml version="1.0" encoding="UTF-8"?>\n<svg\n    xmlns="http://www.w3.org/2000/svg"\n    xmlns:xlink="http://www.w3.org/1999/xlink"\n    width="{canvas_size}px"\n    height="{canvas_size}px"\n    viewBox="0 0 {canvas_size} {canvas_size}">\n    <image\n        id="source_mask_image"\n        x="{horizontal_position}"\n        y="{vertical_position}"\n        width="{image_width}"\n        height="{image_height}"\n        href="{source_uri}"\n        xlink:href="{source_uri}" />\n</svg>\n'
    try:
        svg_file.write_text(svg_content, encoding='utf-8')
    except Exception as error:
        runtime.fail(runtime, f'Temporäre SVG-Quelldatei konnte nicht geschrieben werden: {svg_file} | {error}')
    if not svg_file.is_file():
        runtime.fail(runtime, f'Temporäre SVG-Quelldatei existiert nicht: {svg_file}')
    return canvas_size

def register(runtime):
    runtime.create_trace_source_svg = create_trace_source_svg
