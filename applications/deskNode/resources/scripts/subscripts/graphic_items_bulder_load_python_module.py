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


def load_python_module(runtime, module_name: str, module_file: Path):
    try:
        spec = importlib.util.spec_from_file_location(module_name, module_file)
        if spec is None or spec.loader is None:
            raise ImportError(f'Spec/Loader ungültig: {module_file}')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as error:
        runtime.fail(runtime, f'Modul konnte nicht geladen werden: {module_file} | {error}')

def register(runtime):
    runtime.load_python_module = load_python_module
