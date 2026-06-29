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


def fail(runtime, message: str) -> None:
    print(f'FEHLER: {message}')
    sys.exit(1)

def register(runtime):
    runtime.fail = fail
