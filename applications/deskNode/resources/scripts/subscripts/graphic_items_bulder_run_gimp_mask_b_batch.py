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


def run_gimp_mask_b_batch(runtime, gimp_executable_path: Path, gimp_batch_profile_path: Path, mask_jobs: list[tuple[Path, Path]]) -> str:
    if not mask_jobs:
        runtime.fail(runtime, 'Es wurden keine Mask-B-Bildaufträge übergeben.')
    batch_script = runtime.build_gimp_mask_b_batch_script(runtime, mask_jobs)
    command = [str(gimp_executable_path), '--no-interface', '--batch-interpreter=python-fu-eval', '--batch=-', '--quit']
    environment = runtime.build_gimp_batch_environment(runtime, gimp_batch_profile_path)
    with runtime.temporarily_repair_portable_script_fu_interpreter(runtime, gimp_executable_path) as portable_gimp_status:
        try:
            result = subprocess.run(command, input=batch_script, check=False, capture_output=True, text=True, encoding='utf-8', errors='replace', env=environment)
        except Exception as error:
            runtime.fail(runtime, f'GIMP konnte nicht im Batch-Modus gestartet werden: {gimp_executable_path} | {error}')
    if result.returncode != 0:
        runtime.fail(runtime, f'GIMP konnte die Mask-B-PNGs nicht erzeugen.\nExit-Code: {result.returncode}\nStandardausgabe:\n{result.stdout.strip()}\nFehlerausgabe:\n{result.stderr.strip()}')
    return portable_gimp_status

def register(runtime):
    runtime.run_gimp_mask_b_batch = run_gimp_mask_b_batch
