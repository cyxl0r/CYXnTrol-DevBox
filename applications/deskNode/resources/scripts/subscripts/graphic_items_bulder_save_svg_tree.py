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


def save_svg_tree(runtime, tree: ElementTree.ElementTree, svg_file: Path) -> None:
    try:
        tree.write(svg_file, encoding='utf-8', xml_declaration=True)
    except Exception as error:
        runtime.fail(runtime, f'SVG konnte nicht gespeichert werden: {svg_file} | {error}')

def register(runtime):
    runtime.save_svg_tree = save_svg_tree
