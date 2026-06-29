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


def get_inkscape_action_list(runtime, inkscape_executable_path: Path) -> str:
    action_list_commands = ('--action-list', '--actions-list')
    command_errors = []
    for action_list_command in action_list_commands:
        try:
            result = subprocess.run([str(inkscape_executable_path), action_list_command], check=False, capture_output=True, text=True, encoding='utf-8', errors='replace')
        except Exception as error:
            command_errors.append(f'{action_list_command}: {error}')
            continue
        action_list_output = result.stdout + '\n' + result.stderr
        if result.returncode == 0 and action_list_output.strip():
            return action_list_output
        command_errors.append(f'{action_list_command}: Exit-Code {result.returncode}')
    runtime.fail(runtime, 'Inkscape-Aktionsliste konnte nicht abgefragt werden.\n' + '\n'.join(command_errors))

def register(runtime):
    runtime.get_inkscape_action_list = get_inkscape_action_list
