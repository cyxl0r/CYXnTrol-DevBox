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


def create_final_version6_files(runtime, qfying_files: list[Path], ux_themes: list[dict[str, str]], final_path: Path, step_two_pngs: Path, inkscape_executable_path: Path) -> list[Path]:
    if not qfying_files:
        runtime.fail(runtime, 'Es wurden keine Quadrofying-PNGs zum Erzeugen von Version 6 übergeben.')
    if not ux_themes:
        runtime.fail(runtime, 'Es wurden keine UX-Themes zum Erzeugen von Final-Version 6 übergeben.')
    if not final_path.is_dir():
        runtime.fail(runtime, f'Final-Ordner wurde nicht gefunden: {final_path}')
    if not step_two_pngs.is_dir():
        runtime.fail(runtime, f'Mask-B-Ordner wurde nicht gefunden: {step_two_pngs}')
    version6_files = []
    for theme in ux_themes:
        record_id = theme['record_id']
        for qfying_file in qfying_files:
            base_file = final_path / runtime.get_final_version4_filename(runtime, qfying_file, record_id)
            if not base_file.is_file():
                runtime.fail(runtime, f'Für Final-Version 6 wurde die benötigte Vers4-PNG nicht gefunden: {base_file}')
            mask_b_file = runtime.get_mask_b_file_for_qfying_file(runtime, qfying_file, step_two_pngs)
            canvas_width, canvas_height = runtime.get_png_pixel_dimensions(runtime, base_file)
            target_filename = runtime.get_final_version6_filename(runtime, qfying_file, record_id)
            target_file = final_path / target_filename
            temporary_svg_file = final_path / f'__mask_overlay_{target_file.stem}.svg'
            if temporary_svg_file.exists():
                runtime.remove_file_until_gone(runtime, temporary_svg_file)
            if target_file.exists():
                runtime.remove_file_until_gone(runtime, target_file)
            runtime.write_png_mask_overlay_composition_svg(runtime, temporary_svg_file, canvas_width, canvas_height, base_file, mask_b_file)
            runtime.render_png_composition_svg_with_inkscape(runtime, inkscape_executable_path, temporary_svg_file, target_file, canvas_width, canvas_height)
            runtime.remove_file_until_gone(runtime, temporary_svg_file)
            version6_files.append(target_file)
            print(f'Final-Version 6 gerendert: Theme {record_id} | {base_file.name} + {mask_b_file.name} -> {target_file.name} (Masken-Deckkraft: {runtime.FINAL_MASK_OVERLAY_OPACITY:.0%}, Masken-Unschärfe: {runtime.FINAL_MASK_OVERLAY_BLUR_PERCENT:.0f}%)')
    return version6_files

def register(runtime):
    runtime.create_final_version6_files = create_final_version6_files
