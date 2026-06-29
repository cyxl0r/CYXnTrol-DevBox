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


def apply_layer2_radial_gradient_to_svg(runtime, svg_file: Path, rgba_hex: str, inkscape_executable_path: Path) -> int:
    runtime.validate_layer2_radial_gradient_radius(runtime)
    rgb_color, outer_opacity = runtime.rgba_hex_to_svg_color_and_opacity(runtime, rgba_hex)
    tree, root = runtime.load_svg_tree(runtime, svg_file)
    paintable_elements = runtime.get_paintable_svg_elements(runtime, root)
    if not paintable_elements:
        runtime.fail(runtime, f'SVG enthält keine einfärbbaren Vektorformen: {svg_file}')
    svg_namespace = 'http://www.w3.org/2000/svg'
    defs_element = runtime.get_or_create_svg_defs(runtime, root)
    gradient_id = runtime.get_unused_svg_id(runtime, root, 'layer2_radial_glow')
    radial_gradient = ElementTree.SubElement(defs_element, f'{{{svg_namespace}}}radialGradient', {'id': gradient_id, 'gradientUnits': 'objectBoundingBox', 'cx': '0.5', 'cy': '0.5', 'fx': '0.5', 'fy': '0.5', 'r': f'{runtime.LAYER2_RADIAL_GRADIENT_RADIUS:.6f}'.rstrip('0').rstrip('.'), 'spreadMethod': 'pad'})
    ElementTree.SubElement(radial_gradient, f'{{{svg_namespace}}}stop', {'offset': '0%', 'stop-color': rgb_color, 'stop-opacity': '0'})
    ElementTree.SubElement(radial_gradient, f'{{{svg_namespace}}}stop', {'offset': '100%', 'stop-color': rgb_color, 'stop-opacity': outer_opacity})
    for paintable_element in paintable_elements:
        runtime.clear_svg_fill_and_opacity(runtime, paintable_element)
        paintable_element.set('fill', f'url(#{gradient_id})')
        runtime.apply_common_svg_object_style(runtime, root, paintable_element)
    runtime.save_svg_tree(runtime, tree, svg_file)
    return runtime.apply_inkscape_compatible_blur_to_svg(runtime, svg_file, inkscape_executable_path)

def register(runtime):
    runtime.apply_layer2_radial_gradient_to_svg = apply_layer2_radial_gradient_to_svg
