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


def ensure_gimp_3_or_newer(runtime, gimp_executable_path: Path) -> int:
    gimp_major_version = runtime.get_gimp_major_version(runtime, gimp_executable_path)
    if gimp_major_version < 3:
        runtime.fail(runtime, f'Dieser Schritt benötigt GIMP 3 oder neuer, da er den Python-Batch-Interpreter python-fu-eval nutzt. Gefundene GIMP-Hauptversion: {gimp_major_version}')
    return gimp_major_version

def register(runtime):
    runtime.ensure_gimp_3_or_newer = ensure_gimp_3_or_newer
