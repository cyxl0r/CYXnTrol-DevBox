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


def ensure_inkscape_object_trace_action(runtime, inkscape_executable_path: Path) -> None:
    action_list_output = runtime.get_inkscape_action_list(runtime, inkscape_executable_path)
    if 'object-trace' not in action_list_output:
        runtime.fail(runtime, "Die verwendete Inkscape-Version unterstützt die CLI-Aktion 'object-trace' nicht. Für diesen SVG-Maskenschritt wird Inkscape 1.4 oder neuer benötigt.")

def register(runtime):
    runtime.ensure_inkscape_object_trace_action = ensure_inkscape_object_trace_action
