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


def get_first_available_tool_location(runtime, database_path: Path, tool_keys: tuple[str, ...]) -> tuple[str, Path]:
    errors = []
    for tool_key in tool_keys:
        try:
            executable_path = runtime.read_tool_location(runtime, database_path, tool_key)
            return (tool_key, executable_path)
        except runtime.ToolLocationError as error:
            errors.append(str(error))
    runtime.fail(runtime, 'Kein nutzbarer GIMP-Pfad wurde in loc_db gefunden.\n' + '\n'.join(errors))

def register(runtime):
    runtime.get_first_available_tool_location = get_first_available_tool_location
