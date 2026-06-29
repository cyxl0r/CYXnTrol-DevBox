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


def clear_svg_fill_and_opacity(runtime, element: ElementTree.Element) -> None:
    for attribute_name in ('fill', 'fill-opacity', 'opacity'):
        element.attrib.pop(attribute_name, None)
    style_properties = runtime.get_svg_style_properties(runtime, element)
    for property_name in ('fill', 'fill-opacity', 'opacity'):
        style_properties.pop(property_name, None)
    runtime.write_svg_style_properties(runtime, element, style_properties)

def register(runtime):
    runtime.clear_svg_fill_and_opacity = clear_svg_fill_and_opacity
