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


def get_tool_location(runtime, database_path: Path, tool_key: str) -> Path:
    try:
        return runtime.read_tool_location(runtime, database_path, tool_key)
    except runtime.ToolLocationError as error:
        runtime.fail(runtime, str(error))

def register(runtime):
    runtime.get_tool_location = get_tool_location
