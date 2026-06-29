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


def get_final_version4_filename(runtime, qfying_file: Path, record_id: str) -> str:
    return runtime.get_final_composite_filename(runtime, qfying_file, record_id, 4)

def register(runtime):
    runtime.get_final_version4_filename = get_final_version4_filename
