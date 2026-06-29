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


def find_portable_script_fu_interpreter(runtime, gimp_root_path: Path) -> Path | None:
    gimp_bin_path = gimp_root_path / 'bin'
    if not gimp_bin_path.is_dir():
        return None
    candidate_files = [candidate_file for candidate_file in gimp_bin_path.glob('gimp-script-fu-interpreter*.exe') if candidate_file.is_file()]
    candidate_files.sort(key=lambda candidate_file: candidate_file.name.lower())
    if not candidate_files:
        return None
    return candidate_files[0].resolve()

def register(runtime):
    runtime.find_portable_script_fu_interpreter = find_portable_script_fu_interpreter
