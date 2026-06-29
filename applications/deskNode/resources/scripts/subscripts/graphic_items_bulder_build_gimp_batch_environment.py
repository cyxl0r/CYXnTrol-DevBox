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


def build_gimp_batch_environment(runtime, gimp_batch_profile_path: Path) -> dict[str, str]:
    if not gimp_batch_profile_path.is_dir():
        runtime.fail(runtime, f'Temporärer GIMP-Konfigurationsordner existiert nicht: {gimp_batch_profile_path}')
    environment = os.environ.copy()
    environment['GIMP3_DIRECTORY'] = str(gimp_batch_profile_path.resolve())
    return environment

def register(runtime):
    runtime.build_gimp_batch_environment = build_gimp_batch_environment
