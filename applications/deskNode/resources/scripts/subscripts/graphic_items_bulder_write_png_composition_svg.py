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


def write_png_composition_svg(runtime, svg_file: Path, canvas_width: int, canvas_height: int, image_layers: list[tuple[Path, float]]) -> None:
    if canvas_width <= 0 or canvas_height <= 0:
        runtime.fail(runtime, f'PNG-Kompositionsfläche besitzt ungültige Pixelmaße: {canvas_width} x {canvas_height}')
    if not image_layers:
        runtime.fail(runtime, 'Für die PNG-Komposition wurden keine Bildlayer übergeben.')
    image_elements = []
    for image_file, opacity_value in image_layers:
        if not image_file.is_file():
            runtime.fail(runtime, f'PNG-Kompositionslayer wurde nicht gefunden: {image_file}')
        if opacity_value < 0 or opacity_value > 1:
            runtime.fail(runtime, f'PNG-Kompositionslayer enthält eine ungültige Deckkraft: {image_file} | {opacity_value}')
        image_width, image_height = runtime.get_png_pixel_dimensions(runtime, image_file)
        if image_width != canvas_width or image_height != canvas_height:
            runtime.fail(runtime, f'PNG-Kompositionslayer besitzt nicht die erwartete Canvas-Größe und würde skaliert werden müssen: {image_file} | Erwartet: {canvas_width} x {canvas_height} | Gefunden: {image_width} x {image_height}')
        image_uri = html.escape(image_file.resolve().as_uri(), quote=True)
        opacity_literal = f'{opacity_value:.6f}'.rstrip('0').rstrip('.') or '0'
        image_elements.append(f'    <image\n        x="0"\n        y="0"\n        width="{canvas_width}"\n        height="{canvas_height}"\n        opacity="{opacity_literal}"\n        href="{image_uri}"\n        xlink:href="{image_uri}" />')
    svg_content = f'<?xml version="1.0" encoding="UTF-8"?>\n<svg\n    xmlns="http://www.w3.org/2000/svg"\n    xmlns:xlink="http://www.w3.org/1999/xlink"\n    width="{canvas_width}px"\n    height="{canvas_height}px"\n    viewBox="0 0 {canvas_width} {canvas_height}">\n{chr(10).join(image_elements)}\n</svg>\n'
    try:
        svg_file.write_text(svg_content, encoding='utf-8')
    except Exception as error:
        runtime.fail(runtime, f'Temporäre PNG-Kompositions-SVG konnte nicht geschrieben werden: {svg_file} | {error}')
    if not svg_file.is_file():
        runtime.fail(runtime, f'Temporäre PNG-Kompositions-SVG wurde nicht erzeugt: {svg_file}')

def register(runtime):
    runtime.write_png_composition_svg = write_png_composition_svg
