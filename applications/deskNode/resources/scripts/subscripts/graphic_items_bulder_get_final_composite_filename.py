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


def get_final_composite_filename(runtime, qfying_file: Path, record_id: str, version_number: int) -> str:
    source_prefix = 'symbol_qfying_'
    if not qfying_file.name.startswith(source_prefix):
        runtime.fail(runtime, f'Quadrofying-PNG hat keinen erwarteten Dateinamenpräfix: {qfying_file.name}')
    normalized_record_id = str(record_id).strip()
    if not normalized_record_id:
        runtime.fail(runtime, f'Final-Version-{version_number}-Dateiname kann nicht erzeugt werden: record_id ist leer.')
    filename_tail = qfying_file.name.removeprefix(source_prefix)
    return f'symbol_vers{version_number}_{normalized_record_id}_{filename_tail}'

def register(runtime):
    runtime.get_final_composite_filename = get_final_composite_filename
