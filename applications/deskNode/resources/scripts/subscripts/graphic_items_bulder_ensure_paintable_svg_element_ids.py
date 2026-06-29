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


def ensure_paintable_svg_element_ids(runtime, root: ElementTree.Element, paintable_elements: list[ElementTree.Element]) -> list[str]:
    object_ids = []
    for paintable_element in paintable_elements:
        object_id = paintable_element.get('id')
        if not object_id:
            object_id = runtime.get_unused_svg_id(runtime, root, 'theme_glow_object')
            paintable_element.set('id', object_id)
        object_ids.append(object_id)
    return object_ids

def register(runtime):
    runtime.ensure_paintable_svg_element_ids = ensure_paintable_svg_element_ids
