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


def get_svg_fill_value(runtime, element: ElementTree.Element) -> str | None:
    direct_fill = element.get('fill')
    if direct_fill:
        return direct_fill.strip().lower()
    style_value = element.get('style')
    if not style_value:
        return None
    for style_part in style_value.split(';'):
        if ':' not in style_part:
            continue
        property_name, property_value = style_part.split(':', 1)
        if property_name.strip().lower() == 'fill':
            return property_value.strip().lower()
    return None

def register(runtime):
    runtime.get_svg_fill_value = get_svg_fill_value
