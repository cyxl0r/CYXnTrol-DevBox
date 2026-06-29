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


def get_gimp_installation_root(runtime, gimp_executable_path: Path) -> Path:
    gimp_bin_path = gimp_executable_path.parent
    gimp_root_path = gimp_bin_path.parent
    if not gimp_bin_path.is_dir():
        runtime.fail(runtime, f'GIMP-bin-Ordner wurde nicht gefunden: {gimp_bin_path}')
    if not gimp_root_path.is_dir():
        runtime.fail(runtime, f'GIMP-Installationsordner wurde nicht gefunden: {gimp_root_path}')
    return gimp_root_path

def register(runtime):
    runtime.get_gimp_installation_root = get_gimp_installation_root
