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


def create_final_version3_files(runtime, qfying_files: list[Path], ux_themes: list[dict[str, str]], theme_layer_directories: dict[str, dict[str, Path]], final_path: Path, inkscape_executable_path: Path) -> list[Path]:
    if not qfying_files:
        runtime.fail(runtime, 'Es wurden keine Quadrofying-PNGs zum Erzeugen von Version 3 übergeben.')
    if not ux_themes:
        runtime.fail(runtime, 'Es wurden keine UX-Themes zum Erzeugen von Final-Version 3 übergeben.')
    if not theme_layer_directories:
        runtime.fail(runtime, 'Es wurden keine UX-Theme-Glow-Ordner zum Erzeugen von Final-Version 3 übergeben.')
    if not final_path.is_dir():
        runtime.fail(runtime, f'Final-Ordner wurde nicht gefunden: {final_path}')
    version3_files = []
    for theme in ux_themes:
        record_id = theme['record_id']
        if record_id not in theme_layer_directories:
            runtime.fail(runtime, f'Es fehlen Zielordner für UX-Theme bei Final-Version 3: {record_id!r}')
        directories_for_theme = theme_layer_directories[record_id]
        try:
            glow_off_layer1_path = directories_for_theme['glow_off_layer1']
            glow_off_layer2_path = directories_for_theme['glow_off_layer2']
        except KeyError as error:
            runtime.fail(runtime, f'Für Final-Version 3 fehlen Glow-Off-Layer-Ordner: Theme: {record_id!r} | {error}')
        for required_directory in (glow_off_layer1_path, glow_off_layer2_path):
            if not required_directory.is_dir():
                runtime.fail(runtime, f'Für Final-Version 3 benötigter Glow-Off-Ordner wurde nicht gefunden: {required_directory}')
        for qfying_file in qfying_files:
            canvas_width, canvas_height = runtime.get_png_pixel_dimensions(runtime, qfying_file)
            glow_layer1_file, glow_layer2_file = runtime.get_glow_composite_source_files(runtime, qfying_file, glow_off_layer1_path, glow_off_layer2_path, 'off')
            target_filename = runtime.get_final_version3_filename(runtime, qfying_file, record_id)
            target_file = final_path / target_filename
            temporary_svg_file = final_path / f'__composite_{target_file.stem}.svg'
            if temporary_svg_file.exists():
                runtime.remove_file_until_gone(runtime, temporary_svg_file)
            if target_file.exists():
                runtime.remove_file_until_gone(runtime, target_file)
            runtime.write_png_composition_svg(runtime, temporary_svg_file, canvas_width, canvas_height, [(glow_layer1_file, 1.0), (qfying_file, 1.0), (glow_layer2_file, 1.0)])
            runtime.render_png_composition_svg_with_inkscape(runtime, inkscape_executable_path, temporary_svg_file, target_file, canvas_width, canvas_height)
            runtime.remove_file_until_gone(runtime, temporary_svg_file)
            version3_files.append(target_file)
            print(f'Final-Version 3 gerendert: Theme {record_id} | {glow_layer1_file.name} + {qfying_file.name} + {glow_layer2_file.name} -> {target_file.name}')
    return version3_files

def register(runtime):
    runtime.create_final_version3_files = create_final_version3_files
