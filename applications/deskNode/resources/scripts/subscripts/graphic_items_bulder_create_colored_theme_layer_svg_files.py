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


def create_colored_theme_layer_svg_files(runtime, masks_svg_path: Path, themes: list[dict[str, str]], theme_layer_directories: dict[str, dict[str, Path]], inkscape_executable_path: Path) -> tuple[int, int, int]:
    if not masks_svg_path.is_dir():
        runtime.fail(runtime, f'Masken-SVG-Ordner wurde nicht gefunden: {masks_svg_path}')
    if not themes:
        runtime.fail(runtime, 'Es wurden keine UX-Themes zum Verarbeiten übergeben.')
    if not theme_layer_directories:
        runtime.fail(runtime, 'Es wurden keine UX-Theme-Glow-Ordner zum Verarbeiten übergeben.')
    source_files = [file_path for file_path in masks_svg_path.glob('symbol_mask_*.svg') if file_path.is_file()]
    source_files.sort(key=lambda file_path: file_path.name.lower())
    if not source_files:
        runtime.fail(runtime, f'Es wurden keine symbol_mask_*.svg-Dateien gefunden: {masks_svg_path}')
    layer_variants = (('glow_off_layer1', 'off', 'layer1', 'glow_off_rgba'), ('glow_on_layer1', 'on', 'layer1', 'glow_on_rgba'), ('glow_off_layer2', 'off', 'layer2', 'glow_off_rgba'), ('glow_on_layer2', 'on', 'layer2', 'glow_on_rgba'))
    created_file_count = 0
    layer1_file_count = 0
    layer2_file_count = 0
    for theme in themes:
        record_id = theme['record_id']
        if record_id not in theme_layer_directories:
            runtime.fail(runtime, f'Es fehlen Zielordner für UX-Theme: {record_id!r}')
        directories_for_theme = theme_layer_directories[record_id]
        for directory_key, glow_state, layer_name, rgba_column_name in layer_variants:
            if directory_key not in directories_for_theme:
                runtime.fail(runtime, f'Ein benötigter UX-Theme-Glow-Ordner fehlt: Theme: {record_id!r} | Schlüssel: {directory_key}')
            target_directory = directories_for_theme[directory_key]
            if not target_directory.is_dir():
                runtime.fail(runtime, f'UX-Theme-Glow-Zielordner existiert nicht: {target_directory}')
            rgba_hex = theme[rgba_column_name]
            colored_shape_count = 0
            for source_file in source_files:
                target_filename = runtime.get_target_glow_svg_filename(runtime, source_file, glow_state, layer_name)
                target_file = target_directory / target_filename
                try:
                    shutil.copy2(source_file, target_file)
                except Exception as error:
                    runtime.fail(runtime, f'Masken-SVG konnte nicht in den UX-Theme-Glow-Ordner kopiert werden: {source_file} -> {target_file} | {error}')
                if not target_file.is_file():
                    runtime.fail(runtime, f'Kopierte Masken-SVG existiert nicht: {target_file}')
                if target_file.stat().st_size <= 0:
                    runtime.fail(runtime, f'Kopierte Masken-SVG ist leer: {target_file}')
                if layer_name == 'layer1':
                    colored_shape_count += runtime.apply_solid_theme_color_to_svg(runtime, target_file, rgba_hex, inkscape_executable_path)
                    layer1_file_count += 1
                else:
                    colored_shape_count += runtime.apply_layer2_radial_gradient_to_svg(runtime, target_file, rgba_hex, inkscape_executable_path)
                    layer2_file_count += 1
                created_file_count += 1
            print(f'Theme-Glow-SVGs erzeugt: {target_directory.name} ({len(source_files)} Dateien, {colored_shape_count} Vektorformen, RGBA: {rgba_hex})')
    return (created_file_count, layer1_file_count, layer2_file_count)

def register(runtime):
    runtime.create_colored_theme_layer_svg_files = create_colored_theme_layer_svg_files
