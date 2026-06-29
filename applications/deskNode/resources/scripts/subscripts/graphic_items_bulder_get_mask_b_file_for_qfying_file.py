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


def get_mask_b_file_for_qfying_file(runtime, qfying_file: Path, step_two_pngs: Path) -> Path:
    source_prefix = 'symbol_qfying_'
    if not qfying_file.name.startswith(source_prefix):
        runtime.fail(runtime, f'Quadrofying-PNG hat keinen erwarteten Dateinamenpräfix: {qfying_file.name}')
    filename_tail = qfying_file.name.removeprefix(source_prefix)
    mask_b_file = step_two_pngs / f'symbol_maskB_{filename_tail}'
    if not mask_b_file.is_file():
        runtime.fail(runtime, f'Zugehörige Mask-B-PNG wurde nicht gefunden: {mask_b_file}')
    return mask_b_file

def register(runtime):
    runtime.get_mask_b_file_for_qfying_file = get_mask_b_file_for_qfying_file
