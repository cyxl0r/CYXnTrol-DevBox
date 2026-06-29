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


def register_svg_namespaces(runtime) -> None:
    ElementTree.register_namespace('', 'http://www.w3.org/2000/svg')
    ElementTree.register_namespace('xlink', 'http://www.w3.org/1999/xlink')
    ElementTree.register_namespace('inkscape', 'http://www.inkscape.org/namespaces/inkscape')

def register(runtime):
    runtime.register_svg_namespaces = register_svg_namespaces
