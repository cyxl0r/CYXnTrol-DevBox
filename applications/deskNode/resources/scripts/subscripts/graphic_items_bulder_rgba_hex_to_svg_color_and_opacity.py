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


def rgba_hex_to_svg_color_and_opacity(runtime, rgba_hex: str) -> tuple[str, str]:
    if re.fullmatch('[0-9a-f]{8}', rgba_hex) is None:
        runtime.fail(runtime, f'RGBA-Hexwert konnte nicht in SVG-Farbe umgewandelt werden: {rgba_hex!r}')
    rgb_color = f'#{rgba_hex[0:6]}'
    alpha_value = int(rgba_hex[6:8], 16) / 255
    opacity_value = f'{alpha_value:.6f}'.rstrip('0').rstrip('.')
    if not opacity_value:
        opacity_value = '0'
    return (rgb_color, opacity_value)

def register(runtime):
    runtime.rgba_hex_to_svg_color_and_opacity = rgba_hex_to_svg_color_and_opacity
