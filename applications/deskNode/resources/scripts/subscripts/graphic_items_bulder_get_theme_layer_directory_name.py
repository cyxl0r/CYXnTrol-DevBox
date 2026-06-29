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


def get_theme_layer_directory_name(runtime, record_id: str, glow_state: str, layer_name: str) -> str:
    if glow_state not in {'on', 'off'}:
        runtime.fail(runtime, f'Ungültiger Glow-Status für Zielordner: {glow_state!r}')
    if layer_name not in {'layer1', 'layer2'}:
        runtime.fail(runtime, f'Ungültiger Layername für Zielordner: {layer_name!r}')
    return f'glow_{glow_state}_{record_id}_{layer_name}'

def register(runtime):
    runtime.get_theme_layer_directory_name = get_theme_layer_directory_name
