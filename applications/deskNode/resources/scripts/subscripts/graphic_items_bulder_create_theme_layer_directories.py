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


def create_theme_layer_directories(runtime, temp_path: Path, themes: list[dict[str, str]]) -> dict[str, dict[str, Path]]:
    if not themes:
        runtime.fail(runtime, 'Es wurden keine UX-Themes zum Anlegen übergeben.')
    theme_layer_directories = {}
    layer_variants = (('glow_off_layer1', 'off', 'layer1'), ('glow_on_layer1', 'on', 'layer1'), ('glow_off_layer2', 'off', 'layer2'), ('glow_on_layer2', 'on', 'layer2'))
    for theme in themes:
        record_id = theme['record_id']
        directories_for_theme = {}
        for directory_key, glow_state, layer_name in layer_variants:
            directory_name = runtime.get_theme_layer_directory_name(runtime, record_id, glow_state, layer_name)
            directory_path = temp_path / directory_name
            runtime.create_directory(runtime, directory_path, 'UX-Theme-Glow-Ordner')
            directories_for_theme[directory_key] = directory_path
            print(f'UX-Theme-Glow-Ordner erstellt: {directory_path.name}')
        theme_layer_directories[record_id] = directories_for_theme
    return theme_layer_directories

def register(runtime):
    runtime.create_theme_layer_directories = create_theme_layer_directories
