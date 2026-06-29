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


def get_script_fu_interpreter_config_file(runtime, gimp_root_path: Path) -> Path:
    return gimp_root_path / 'lib' / 'gimp' / '3.0' / 'interpreters' / 'gimp-script-fu-interpreter.interp'

def register(runtime):
    runtime.get_script_fu_interpreter_config_file = get_script_fu_interpreter_config_file
