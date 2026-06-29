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


def build_gimp_mask_b_batch_script(runtime, mask_jobs: list[tuple[Path, Path]]) -> str:
    job_values = [(str(source_file.resolve()), str(target_file.resolve())) for source_file, target_file in mask_jobs]
    job_values_literal = repr(job_values)
    brightness_value = runtime.MASK_B_BRIGHTNESS / runtime.GIMP_BRIGHTNESS_CONTRAST_MAX_VALUE
    contrast_value = runtime.MASK_B_CONTRAST / runtime.GIMP_BRIGHTNESS_CONTRAST_MAX_VALUE
    return f'\nfrom gi.repository import Gimp, Gio\n\nMASK_JOBS = {job_values_literal}\nBRIGHTNESS_VALUE = {brightness_value!r}\nCONTRAST_VALUE = {contrast_value!r}\n\n\ndef run_brightness_contrast_pdb(\n    drawable,\n    brightness_value,\n    contrast_value,\n    operation_name,\n):\n    procedure = Gimp.get_pdb().lookup_procedure(\n        "gimp-drawable-brightness-contrast",\n    )\n\n    if procedure is None:\n        raise RuntimeError(\n            "GIMP-PDB-Prozedur nicht gefunden: "\n            "gimp-drawable-brightness-contrast"\n        )\n\n    config = procedure.create_config()\n    config.set_property("drawable", drawable)\n    config.set_property("brightness", brightness_value)\n    config.set_property("contrast", contrast_value)\n\n    result = procedure.run(config)\n    status = result.index(0)\n\n    if status != Gimp.PDBStatusType.SUCCESS:\n        raise RuntimeError(\n            "GIMP-PDB-Prozedur fehlgeschlagen: "\n            f"{{operation_name}} | Status: {{status}}"\n        )\n\n    update_success = drawable.update(\n        0,\n        0,\n        drawable.get_width(),\n        drawable.get_height(),\n    )\n\n    if update_success is False:\n        raise RuntimeError(\n            "GIMP konnte die geänderte Ebene nicht aktualisieren: "\n            f"{{operation_name}}"\n        )\n\n\nfor source_path, target_path in MASK_JOBS:\n    source_file = Gio.file_new_for_path(source_path)\n    target_file = Gio.file_new_for_path(target_path)\n\n    image = Gimp.file_load(\n        Gimp.RunMode.NONINTERACTIVE,\n        source_file,\n    )\n\n    if image is None:\n        raise RuntimeError(\n            f"Bild konnte nicht geladen werden: {{source_path}}"\n        )\n\n    drawables = image.get_layers()\n\n    if not drawables:\n        raise RuntimeError(\n            f"Bild enthält keine bearbeitbare Ebene: {{source_path}}"\n        )\n\n    for drawable in drawables:\n        if not drawable.is_rgb():\n            raise RuntimeError(\n                "Ebene ist nicht im RGB-Format: "\n                f"{{source_path}}"\n            )\n\n        run_brightness_contrast_pdb(\n            drawable,\n            BRIGHTNESS_VALUE,\n            0.0,\n            "Mask-B | Helligkeit -127",\n        )\n\n        run_brightness_contrast_pdb(\n            drawable,\n            0.0,\n            CONTRAST_VALUE,\n            "Mask-B | Kontrast 127",\n        )\n\n    Gimp.displays_flush()\n\n    export_success = Gimp.file_save(\n        Gimp.RunMode.NONINTERACTIVE,\n        image,\n        target_file,\n        None,\n    )\n\n    if export_success is False:\n        raise RuntimeError(\n            f"PNG konnte nicht exportiert werden: {{target_path}}"\n        )\n\n    image.delete()\n\n    print(\n        "MASK_B_CREATED|"\n        + target_path\n    )\n'

def register(runtime):
    runtime.build_gimp_mask_b_batch_script = build_gimp_mask_b_batch_script
