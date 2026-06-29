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


def validate_final_version2_opacity(runtime) -> None:
    if not isinstance(runtime.FINAL_VERSION2_OPACITY, (int, float)):
        runtime.fail(runtime, 'FINAL_VERSION2_OPACITY muss eine Zahl sein.')
    if runtime.FINAL_VERSION2_OPACITY < 0 or runtime.FINAL_VERSION2_OPACITY > 1:
        runtime.fail(runtime, 'FINAL_VERSION2_OPACITY muss zwischen 0 und 1 liegen.')

def register(runtime):
    runtime.validate_final_version2_opacity = validate_final_version2_opacity
