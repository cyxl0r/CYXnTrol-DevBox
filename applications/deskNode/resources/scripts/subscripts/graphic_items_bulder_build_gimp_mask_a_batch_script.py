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


def build_gimp_mask_a_batch_script(runtime, mask_jobs: list[tuple[Path, Path]]) -> str:
    job_values = [(str(source_file.resolve()), str(target_file.resolve())) for source_file, target_file in mask_jobs]
    job_values_literal = repr(job_values)
    brightness_value = runtime.MASK_A_BRIGHTNESS / runtime.GIMP_BRIGHTNESS_CONTRAST_MAX_VALUE
    contrast_value = runtime.MASK_A_CONTRAST / runtime.GIMP_BRIGHTNESS_CONTRAST_MAX_VALUE
    return f'\nfrom gi.repository import Gimp, Gio\n\nMASK_JOBS = {job_values_literal}\nBRIGHTNESS_VALUE = {brightness_value!r}\nCONTRAST_VALUE = {contrast_value!r}\n\nfor source_path, target_path in MASK_JOBS:\n    source_file = Gio.file_new_for_path(source_path)\n    target_file = Gio.file_new_for_path(target_path)\n\n    image = Gimp.file_load(\n        Gimp.RunMode.NONINTERACTIVE,\n        source_file,\n    )\n\n    if image is None:\n        raise RuntimeError(\n            f"Bild konnte nicht geladen werden: {{source_path}}"\n        )\n\n    drawables = image.get_layers()\n\n    if not drawables:\n        raise RuntimeError(\n            f"Bild enthält keine bearbeitbare Ebene: {{source_path}}"\n        )\n\n    for drawable in drawables:\n        if not drawable.is_rgb():\n            raise RuntimeError(\n                "Ebene ist nicht im RGB-Format: "\n                f"{{source_path}}"\n            )\n\n        desaturate_success = drawable.desaturate(\n            Gimp.DesaturateMode.LUMA,\n        )\n\n        if desaturate_success is False:\n            raise RuntimeError(\n                "Sättigung konnte nicht auf 0 gesetzt werden: "\n                f"{{source_path}}"\n            )\n\n        brightness_contrast_success = (\n            drawable.brightness_contrast(\n                BRIGHTNESS_VALUE,\n                CONTRAST_VALUE,\n            )\n        )\n\n        if brightness_contrast_success is False:\n            raise RuntimeError(\n                "Helligkeit/Kontrast konnte nicht angewendet werden: "\n                f"{{source_path}}"\n            )\n\n    export_success = Gimp.file_save(\n        Gimp.RunMode.NONINTERACTIVE,\n        image,\n        target_file,\n        None,\n    )\n\n    if export_success is False:\n        raise RuntimeError(\n            f"PNG konnte nicht exportiert werden: {{target_path}}"\n        )\n\n    image.delete()\n\n    print(\n        "MASK_A_CREATED|"\n        + target_path\n    )\n'

def register(runtime):
    runtime.build_gimp_mask_a_batch_script = build_gimp_mask_a_batch_script
