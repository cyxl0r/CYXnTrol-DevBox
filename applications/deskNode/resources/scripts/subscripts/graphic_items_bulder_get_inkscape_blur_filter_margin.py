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


def get_inkscape_blur_filter_margin(runtime) -> float:
    runtime.validate_svg_object_styling_values(runtime)
    return runtime.SVG_BLUR_PERCENT / 100 * 1.2

def register(runtime):
    runtime.get_inkscape_blur_filter_margin = get_inkscape_blur_filter_margin
