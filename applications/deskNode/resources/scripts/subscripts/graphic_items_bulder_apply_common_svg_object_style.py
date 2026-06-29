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


def apply_common_svg_object_style(runtime, root: ElementTree.Element, paintable_element: ElementTree.Element) -> None:
    runtime.validate_svg_object_styling_values(runtime)
    paintable_element.set('opacity', f'{runtime.SVG_OBJECT_OPACITY:.6f}'.rstrip('0').rstrip('.') or '0')
    paintable_element.attrib.pop('filter', None)

def register(runtime):
    runtime.apply_common_svg_object_style = apply_common_svg_object_style
