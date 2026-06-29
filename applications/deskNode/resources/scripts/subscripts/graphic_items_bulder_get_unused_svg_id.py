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


def get_unused_svg_id(runtime, root: ElementTree.Element, preferred_id: str) -> str:
    existing_ids = {element.get('id') for element in root.iter() if element.get('id')}
    if preferred_id not in existing_ids:
        return preferred_id
    suffix = 1
    while True:
        candidate_id = f'{preferred_id}_{suffix}'
        if candidate_id not in existing_ids:
            return candidate_id
        suffix += 1

def register(runtime):
    runtime.get_unused_svg_id = get_unused_svg_id
