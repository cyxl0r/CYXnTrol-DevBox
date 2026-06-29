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


def read_tool_location(runtime, database_path: Path, tool_key: str) -> Path:
    try:
        with sqlite3.connect(database_path) as connection:
            cursor = connection.cursor()
            cursor.execute('\n                SELECT\n                    executable_name,\n                    executable_path,\n                    status\n                FROM tool_locations\n                WHERE tool_key = ?\n                LIMIT 1\n                ', (tool_key,))
            row = cursor.fetchone()
    except sqlite3.Error as error:
        raise runtime.ToolLocationError(f'Tool-Pfad konnte aus loc_db nicht gelesen werden. Tool: {tool_key} | {error}') from error
    if row is None:
        raise runtime.ToolLocationError(f'Tool wurde in loc_db nicht gefunden: {tool_key}')
    executable_name = row[0]
    executable_path_value = row[1]
    tool_status = row[2]
    if executable_name is None:
        raise runtime.ToolLocationError(f'executable_name ist in loc_db leer. Tool: {tool_key}')
    if executable_path_value is None:
        raise runtime.ToolLocationError(f'executable_path ist in loc_db leer. Tool: {tool_key}')
    if tool_status is None:
        raise runtime.ToolLocationError(f'status ist in loc_db leer. Tool: {tool_key}')
    executable_name = str(executable_name).strip()
    executable_path_value = str(executable_path_value).strip()
    tool_status = str(tool_status).strip().lower()
    if not executable_name:
        raise runtime.ToolLocationError(f'executable_name ist in loc_db leer. Tool: {tool_key}')
    if not executable_path_value:
        raise runtime.ToolLocationError(f'executable_path ist in loc_db leer. Tool: {tool_key}')
    if tool_status != 'found':
        raise runtime.ToolLocationError(f'Tool wurde laut loc_db nicht gefunden. Tool: {tool_key} | Status: {tool_status}')
    executable_path = Path(executable_path_value)
    if not executable_path.is_file():
        raise runtime.ToolLocationError(f'Die eingetragene Programmdatei existiert nicht. Tool: {tool_key} | Pfad: {executable_path}')
    if executable_path.name.lower() != executable_name.lower():
        raise runtime.ToolLocationError(f'Der Dateiname stimmt nicht mit executable_name überein. Tool: {tool_key} | Erwartet: {executable_name} | Gefunden: {executable_path.name}')
    return executable_path

def register(runtime):
    runtime.read_tool_location = read_tool_location
