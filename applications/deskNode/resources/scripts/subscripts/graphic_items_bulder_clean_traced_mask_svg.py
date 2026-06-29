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


def clean_traced_mask_svg(runtime, target_svg_file: Path) -> int:
    try:
        ElementTree.register_namespace('', 'http://www.w3.org/2000/svg')
        ElementTree.register_namespace('xlink', 'http://www.w3.org/1999/xlink')
        ElementTree.register_namespace('inkscape', 'http://www.inkscape.org/namespaces/inkscape')
        tree = ElementTree.parse(target_svg_file)
        root = tree.getroot()
    except Exception as error:
        runtime.fail(runtime, f'Nachgezeichnete SVG konnte nicht gelesen werden: {target_svg_file} | {error}')
    removed_element_count = 0
    for parent_element in root.iter():
        for child_element in list(parent_element):
            child_local_name = runtime.get_svg_local_name(runtime, child_element.tag)
            if child_local_name == 'image':
                parent_element.remove(child_element)
                removed_element_count += 1
                continue
            if child_local_name != 'path':
                continue
            fill_value = runtime.get_svg_fill_value(runtime, child_element)
            if runtime.is_white_svg_fill(runtime, fill_value):
                parent_element.remove(child_element)
                removed_element_count += 1
    remaining_image_elements = [element for element in root.iter() if runtime.get_svg_local_name(runtime, element.tag) == 'image']
    if remaining_image_elements:
        runtime.fail(runtime, f'Die Quell-PNG konnte nicht vollständig aus der Masken-SVG entfernt werden: {target_svg_file}')
    remaining_path_elements = [element for element in root.iter() if runtime.get_svg_local_name(runtime, element.tag) == 'path']
    if not remaining_path_elements:
        runtime.fail(runtime, f'Nach dem Bitmap-Nachzeichnen sind keine Vektorpfade übrig geblieben: {target_svg_file}')
    try:
        tree.write(target_svg_file, encoding='utf-8', xml_declaration=True)
    except Exception as error:
        runtime.fail(runtime, f'Bereinigte Masken-SVG konnte nicht gespeichert werden: {target_svg_file} | {error}')
    return removed_element_count

def register(runtime):
    runtime.clean_traced_mask_svg = clean_traced_mask_svg
