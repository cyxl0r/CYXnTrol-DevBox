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


def write_svg_style_properties(runtime, element: ElementTree.Element, style_properties: dict[str, str]) -> None:
    if not style_properties:
        element.attrib.pop('style', None)
        return
    serialized_style = ';'.join((f'{property_name}:{property_value}' for property_name, property_value in style_properties.items()))
    element.set('style', serialized_style)

def register(runtime):
    runtime.write_svg_style_properties = write_svg_style_properties
