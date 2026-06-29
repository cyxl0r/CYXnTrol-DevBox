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


def get_paintable_svg_elements(runtime, root: ElementTree.Element) -> list[ElementTree.Element]:
    paintable_element_names = {'path', 'polygon', 'polyline', 'rect', 'circle', 'ellipse'}
    paintable_elements = []

    def collect_elements(element: ElementTree.Element, inside_defs: bool) -> None:
        local_name = runtime.get_svg_local_name(runtime, element.tag)
        current_inside_defs = inside_defs or local_name == 'defs'
        if not current_inside_defs and local_name in paintable_element_names:
            paintable_elements.append(element)
        for child_element in list(element):
            collect_elements(child_element, current_inside_defs)
    collect_elements(root, False)
    return paintable_elements

def register(runtime):
    runtime.get_paintable_svg_elements = get_paintable_svg_elements
