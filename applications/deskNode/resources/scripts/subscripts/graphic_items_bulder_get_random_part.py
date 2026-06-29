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


def get_random_part(runtime, random_string_provider, length: int) -> str:
    try:
        return str(random_string_provider.generate_string(length=length, variant=1))
    except Exception as error:
        runtime.fail(runtime, f'Random-String konnte nicht erzeugt werden. Länge: {length} | {error}')

def register(runtime):
    runtime.get_random_part = get_random_part
