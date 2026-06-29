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


def get_final_filename(runtime, source_file: Path, source_prefix: str, final_prefix: str) -> str:
    if not source_file.name.startswith(source_prefix):
        runtime.fail(runtime, f'Quelldatei hat keinen erwarteten Dateinamenpräfix: {source_file.name} | Erwartet: {source_prefix}')
    return final_prefix + source_file.name.removeprefix(source_prefix)

def register(runtime):
    runtime.get_final_filename = get_final_filename
