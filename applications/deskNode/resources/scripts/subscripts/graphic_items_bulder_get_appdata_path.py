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


def get_appdata_path(runtime) -> Path:
    appdata_value = os.environ.get('APPDATA')
    if not appdata_value:
        runtime.fail(runtime, 'Die Umgebungsvariable APPDATA ist nicht gesetzt.')
    appdata_path = Path(appdata_value)
    if not appdata_path.is_dir():
        runtime.fail(runtime, f'APPDATA-Pfad existiert nicht: {appdata_path}')
    return appdata_path

def register(runtime):
    runtime.get_appdata_path = get_appdata_path
