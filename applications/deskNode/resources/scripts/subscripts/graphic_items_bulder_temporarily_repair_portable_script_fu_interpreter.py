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


@contextmanager
def temporarily_repair_portable_script_fu_interpreter(runtime, gimp_executable_path: Path):
    gimp_root_path = runtime.get_gimp_installation_root(runtime, gimp_executable_path)
    interpreter_config_file = runtime.get_script_fu_interpreter_config_file(runtime, gimp_root_path)
    if not interpreter_config_file.is_file():
        yield 'Script-Fu-Interpreterdatei nicht vorhanden; keine Anpassung nötig.'
        return
    actual_interpreter_path = runtime.find_portable_script_fu_interpreter(runtime, gimp_root_path)
    if actual_interpreter_path is None:
        yield 'Kein portabler Script-Fu-Interpreter gefunden; keine Anpassung durchgeführt.'
        return
    try:
        original_content = interpreter_config_file.read_text(encoding='utf-8', errors='surrogateescape')
    except Exception as error:
        runtime.fail(runtime, f'Script-Fu-Interpreterdatei konnte nicht gelesen werden: {interpreter_config_file} | {error}')
    portable_interpreter_path = str(actual_interpreter_path.resolve())
    old_interpreter_path_pattern = re.compile('(?i)(?:[a-z]:)?[^\\"\\r\\n]*?gimp-script-fu-interpreter(?:-\\d+(?:\\.\\d+)*)?\\.exe')
    patched_content, replacements = old_interpreter_path_pattern.subn(lambda _match: portable_interpreter_path, original_content)
    if replacements == 0:
        yield 'Script-Fu-Interpreterdatei enthält keinen ersetzbaren EXE-Pfad; keine Anpassung durchgeführt.'
        return
    if patched_content == original_content:
        yield 'Script-Fu-Interpreterdatei verweist bereits auf den portablen Interpreter.'
        return
    try:
        interpreter_config_file.write_text(patched_content, encoding='utf-8', errors='surrogateescape')
    except Exception as error:
        runtime.fail(runtime, f'Script-Fu-Interpreterdatei konnte nicht temporär angepasst werden: {interpreter_config_file} | {error}')
    try:
        yield f'Script-Fu-Interpreterdatei wurde temporär auf {actual_interpreter_path.name} umgebogen.'
    finally:
        try:
            interpreter_config_file.write_text(original_content, encoding='utf-8', errors='surrogateescape')
        except Exception as error:
            runtime.fail(runtime, f'Die originale Script-Fu-Interpreterdatei konnte nicht wiederhergestellt werden: {interpreter_config_file} | {error}')

def register(runtime):
    runtime.temporarily_repair_portable_script_fu_interpreter = temporarily_repair_portable_script_fu_interpreter
