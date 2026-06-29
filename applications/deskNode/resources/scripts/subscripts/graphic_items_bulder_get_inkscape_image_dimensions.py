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


def get_inkscape_image_dimensions(runtime, inkscape_executable_path: Path, image_path: Path) -> tuple[float, float]:
    width = runtime.get_inkscape_image_dimension(runtime, inkscape_executable_path, image_path, 'width')
    height = runtime.get_inkscape_image_dimension(runtime, inkscape_executable_path, image_path, 'height')
    return (width, height)

def register(runtime):
    runtime.get_inkscape_image_dimensions = get_inkscape_image_dimensions
