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


def get_svg_local_name(runtime, element_tag: str) -> str:
    if '}' in element_tag:
        return element_tag.rsplit('}', 1)[1]
    return element_tag

def register(runtime):
    runtime.get_svg_local_name = get_svg_local_name
