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


def is_white_svg_fill(runtime, fill_value: str | None) -> bool:
    if fill_value is None:
        return False
    normalized_value = fill_value.strip().lower()
    if normalized_value in {'#fff', '#ffffff', 'white', 'rgb(255,255,255)', 'rgb(100%,100%,100%)'}:
        return True
    hex_match = re.fullmatch('#([0-9a-f]{6})', normalized_value)
    if hex_match is not None:
        rgb_value = hex_match.group(1)
        red_value = int(rgb_value[0:2], 16)
        green_value = int(rgb_value[2:4], 16)
        blue_value = int(rgb_value[4:6], 16)
        return red_value >= 250 and green_value >= 250 and (blue_value >= 250)
    return False

def register(runtime):
    runtime.is_white_svg_fill = is_white_svg_fill
