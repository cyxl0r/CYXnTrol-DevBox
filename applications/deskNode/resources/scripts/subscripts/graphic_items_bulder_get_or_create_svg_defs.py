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


def get_or_create_svg_defs(runtime, root: ElementTree.Element) -> ElementTree.Element:
    for child_element in list(root):
        if runtime.get_svg_local_name(runtime, child_element.tag) == 'defs':
            return child_element
    svg_namespace = 'http://www.w3.org/2000/svg'
    defs_element = ElementTree.Element(f'{{{svg_namespace}}}defs')
    root.insert(0, defs_element)
    return defs_element

def register(runtime):
    runtime.get_or_create_svg_defs = get_or_create_svg_defs
