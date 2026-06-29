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


def create_directory(runtime, directory_path: Path, description: str) -> None:
    try:
        directory_path.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        runtime.fail(runtime, f'{description} existiert bereits: {directory_path}')
    except Exception as error:
        runtime.fail(runtime, f'{description} konnte nicht erstellt werden: {directory_path} | {error}')

def register(runtime):
    runtime.create_directory = create_directory
