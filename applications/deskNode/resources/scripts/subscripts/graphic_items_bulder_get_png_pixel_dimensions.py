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


def get_png_pixel_dimensions(runtime, image_path: Path) -> tuple[int, int]:
    try:
        with image_path.open('rb') as file_handle:
            png_header = file_handle.read(24)
    except Exception as error:
        runtime.fail(runtime, f'PNG-Pixelgröße konnte nicht gelesen werden: {image_path} | {error}')
    if len(png_header) < 24:
        runtime.fail(runtime, f'PNG-Datei ist zu kurz für IHDR-Pixelmaße: {image_path}')
    png_signature = b'\x89PNG\r\n\x1a\n'
    if png_header[:8] != png_signature:
        runtime.fail(runtime, f'Datei ist keine gültige PNG-Datei: {image_path}')
    if png_header[12:16] != b'IHDR':
        runtime.fail(runtime, f'PNG-IHDR-Chunk wurde nicht an erwarteter Position gefunden: {image_path}')
    try:
        width, height = struct.unpack('>II', png_header[16:24])
    except struct.error as error:
        runtime.fail(runtime, f'PNG-Pixelmaße konnten nicht dekodiert werden: {image_path} | {error}')
    if width <= 0 or height <= 0:
        runtime.fail(runtime, f'PNG besitzt ungültige Pixelmaße: {image_path} | {width} x {height}')
    return (width, height)

def register(runtime):
    runtime.get_png_pixel_dimensions = get_png_pixel_dimensions
