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


def create_mask_b_images(runtime, step_one_pngs: Path, step_two_pngs: Path, gimp_executable_path: Path, gimp_batch_profile_path: Path) -> tuple[list[Path], str]:
    mask_a_files = [file_path for file_path in step_one_pngs.glob('symbol_maskA_*.png') if file_path.is_file()]
    mask_a_files.sort(key=lambda file_path: file_path.name.lower())
    if not mask_a_files:
        runtime.fail(runtime, f'Keine symbol_maskA_*.png-Dateien gefunden: {step_one_pngs}')
    mask_jobs = []
    mask_files = []
    for mask_a_file in mask_a_files:
        mask_filename = mask_a_file.name.replace('symbol_maskA_', 'symbol_maskB_', 1)
        mask_file = step_two_pngs / mask_filename
        mask_jobs.append((mask_a_file, mask_file))
        mask_files.append(mask_file)
    portable_gimp_status = runtime.run_gimp_mask_b_batch(runtime, gimp_executable_path, gimp_batch_profile_path, mask_jobs)
    for mask_file in mask_files:
        if not mask_file.is_file():
            runtime.fail(runtime, f'GIMP hat die erwartete Mask-B-PNG nicht erzeugt: {mask_file}')
        if mask_file.stat().st_size <= 0:
            runtime.fail(runtime, f'GIMP hat eine leere Mask-B-PNG erzeugt: {mask_file}')
    for source_file, mask_file in mask_jobs:
        print(f'Mask-B erzeugt: {source_file.name} -> {mask_file.name}')
    return (mask_files, portable_gimp_status)

def register(runtime):
    runtime.create_mask_b_images = create_mask_b_images
