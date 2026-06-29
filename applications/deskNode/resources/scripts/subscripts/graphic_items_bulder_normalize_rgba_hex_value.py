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


def normalize_rgba_hex_value(runtime, rgba_value, column_name: str, record_id: str) -> str:
    if rgba_value is None:
        runtime.fail(runtime, f'ux_themes.{column_name} ist leer. record_id: {record_id!r}')
    normalized_value = str(rgba_value).strip()
    if normalized_value.startswith('#'):
        normalized_value = normalized_value[1:]
    if re.fullmatch('[0-9a-fA-F]{8}', normalized_value) is None:
        runtime.fail(runtime, f'ux_themes.{column_name} enthält keinen gültigen RGBA-Hexwert im Format RRGGBBAA. record_id: {record_id!r} | Wert: {rgba_value!r}')
    return normalized_value.lower()

def register(runtime):
    runtime.normalize_rgba_hex_value = normalize_rgba_hex_value
