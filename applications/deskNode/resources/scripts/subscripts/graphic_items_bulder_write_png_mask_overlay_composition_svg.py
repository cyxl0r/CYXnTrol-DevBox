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


def write_png_mask_overlay_composition_svg(runtime, svg_file: Path, canvas_width: int, canvas_height: int, base_image_file: Path, mask_image_file: Path) -> None:
    if canvas_width <= 0 or canvas_height <= 0:
        runtime.fail(runtime, f'PNG-Maskenkompositionsfläche besitzt ungültige Pixelmaße: {canvas_width} x {canvas_height}')
    for required_file in (base_image_file, mask_image_file):
        if not required_file.is_file():
            runtime.fail(runtime, f'PNG-Maskenkompositionsquelle wurde nicht gefunden: {required_file}')
    for required_file in (base_image_file, mask_image_file):
        image_width, image_height = runtime.get_png_pixel_dimensions(runtime, required_file)
        if image_width != canvas_width or image_height != canvas_height:
            runtime.fail(runtime, f'PNG-Maskenkompositionsquelle besitzt nicht die erwartete Canvas-Größe und würde skaliert werden müssen: {required_file} | Erwartet: {canvas_width} x {canvas_height} | Gefunden: {image_width} x {image_height}')
    runtime.validate_final_mask_overlay_settings(runtime)
    base_image_uri = html.escape(base_image_file.resolve().as_uri(), quote=True)
    mask_image_uri = html.escape(mask_image_file.resolve().as_uri(), quote=True)
    mask_opacity_literal = f'{runtime.FINAL_MASK_OVERLAY_OPACITY:.6f}'.rstrip('0').rstrip('.') or '0'
    std_deviation = runtime.get_final_mask_overlay_blur_std_deviation(runtime, canvas_width, canvas_height)
    std_deviation_literal = f'{std_deviation:.6f}'.rstrip('0').rstrip('.') or '0'
    filter_padding = max(std_deviation * 3.0, 1.0)
    filter_x = -filter_padding
    filter_y = -filter_padding
    filter_width = canvas_width + filter_padding * 2.0
    filter_height = canvas_height + filter_padding * 2.0
    filter_x_literal = f'{filter_x:.6f}'.rstrip('0').rstrip('.') or '0'
    filter_y_literal = f'{filter_y:.6f}'.rstrip('0').rstrip('.') or '0'
    filter_width_literal = f'{filter_width:.6f}'.rstrip('0').rstrip('.') or '0'
    filter_height_literal = f'{filter_height:.6f}'.rstrip('0').rstrip('.') or '0'
    svg_content = f'<?xml version="1.0" encoding="UTF-8"?>\n<svg\n    xmlns="http://www.w3.org/2000/svg"\n    xmlns:xlink="http://www.w3.org/1999/xlink"\n    xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"\n    width="{canvas_width}px"\n    height="{canvas_height}px"\n    viewBox="0 0 {canvas_width} {canvas_height}">\n    <defs>\n        <filter\n            id="mask_overlay_blur"\n            x="{filter_x_literal}"\n            y="{filter_y_literal}"\n            width="{filter_width_literal}"\n            height="{filter_height_literal}"\n            filterUnits="userSpaceOnUse"\n            primitiveUnits="userSpaceOnUse"\n            style="color-interpolation-filters:sRGB"\n            inkscape:label="Blur">\n            <feGaussianBlur stdDeviation="{std_deviation_literal}" />\n        </filter>\n    </defs>\n    <image\n        x="0"\n        y="0"\n        width="{canvas_width}"\n        height="{canvas_height}"\n        opacity="1"\n        href="{base_image_uri}"\n        xlink:href="{base_image_uri}" />\n    <image\n        x="0"\n        y="0"\n        width="{canvas_width}"\n        height="{canvas_height}"\n        opacity="{mask_opacity_literal}"\n        filter="url(#mask_overlay_blur)"\n        href="{mask_image_uri}"\n        xlink:href="{mask_image_uri}" />\n</svg>\n'
    try:
        svg_file.write_text(svg_content, encoding='utf-8')
    except Exception as error:
        runtime.fail(runtime, f'Temporäre PNG-Maskenkompositions-SVG konnte nicht geschrieben werden: {svg_file} | {error}')
    if not svg_file.is_file():
        runtime.fail(runtime, f'Temporäre PNG-Maskenkompositions-SVG wurde nicht erzeugt: {svg_file}')

def register(runtime):
    runtime.write_png_mask_overlay_composition_svg = write_png_mask_overlay_composition_svg
