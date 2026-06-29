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


def load_svg_tree(runtime, svg_file: Path) -> tuple[ElementTree.ElementTree, ElementTree.Element]:
    try:
        runtime.register_svg_namespaces(runtime)
        tree = ElementTree.parse(svg_file)
        root = tree.getroot()
    except Exception as error:
        runtime.fail(runtime, f'SVG konnte nicht gelesen werden: {svg_file} | {error}')
    return (tree, root)

def register(runtime):
    runtime.load_svg_tree = load_svg_tree
