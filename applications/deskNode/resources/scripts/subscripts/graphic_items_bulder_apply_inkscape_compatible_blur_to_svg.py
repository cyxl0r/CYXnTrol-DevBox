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


def apply_inkscape_compatible_blur_to_svg(runtime, svg_file: Path, inkscape_executable_path: Path) -> int:
    tree, root = runtime.load_svg_tree(runtime, svg_file)
    paintable_elements = runtime.get_paintable_svg_elements(runtime, root)
    if not paintable_elements:
        runtime.fail(runtime, f'SVG enthält keine Vektorformen für die Unschärfe: {svg_file}')
    for paintable_element in paintable_elements:
        paintable_element.attrib.pop('filter', None)
    object_ids = runtime.ensure_paintable_svg_element_ids(runtime, root, paintable_elements)
    runtime.save_svg_tree(runtime, tree, svg_file)
    object_dimensions = runtime.query_svg_object_dimensions_with_inkscape(runtime, inkscape_executable_path, svg_file, object_ids)
    tree, root = runtime.load_svg_tree(runtime, svg_file)
    paintable_elements = runtime.get_paintable_svg_elements(runtime, root)
    paintable_elements_by_id = {paintable_element.get('id'): paintable_element for paintable_element in paintable_elements if paintable_element.get('id')}
    defs_element = runtime.get_or_create_svg_defs(runtime, root)
    svg_namespace = 'http://www.w3.org/2000/svg'
    inkscape_namespace = 'http://www.inkscape.org/namespaces/inkscape'
    filter_margin = runtime.get_inkscape_blur_filter_margin(runtime)
    filter_region_position = f'{-filter_margin:.6f}'.rstrip('0').rstrip('.')
    filter_region_size = f'{1 + 2 * filter_margin:.6f}'.rstrip('0').rstrip('.')
    for object_id in object_ids:
        if object_id not in paintable_elements_by_id:
            runtime.fail(runtime, f'SVG-Objekt konnte nach der Dimensionsabfrage nicht mehr gefunden werden: {svg_file} | ID: {object_id}')
        object_width, object_height = object_dimensions[object_id]
        std_deviation = runtime.get_inkscape_blur_std_deviation(runtime, object_width, object_height)
        std_deviation_literal = f'{std_deviation:.6f}'.rstrip('0').rstrip('.')
        filter_id = runtime.get_unused_svg_id(runtime, root, 'inkscape_blur')
        filter_element = ElementTree.SubElement(defs_element, f'{{{svg_namespace}}}filter', {'id': filter_id, 'x': filter_region_position, 'y': filter_region_position, 'width': filter_region_size, 'height': filter_region_size, 'style': 'color-interpolation-filters:sRGB', f'{{{inkscape_namespace}}}label': 'Blur'})
        ElementTree.SubElement(filter_element, f'{{{svg_namespace}}}feGaussianBlur', {'stdDeviation': std_deviation_literal or '0'})
        paintable_elements_by_id[object_id].set('filter', f'url(#{filter_id})')
    runtime.save_svg_tree(runtime, tree, svg_file)
    return len(object_ids)

def register(runtime):
    runtime.apply_inkscape_compatible_blur_to_svg = apply_inkscape_compatible_blur_to_svg
