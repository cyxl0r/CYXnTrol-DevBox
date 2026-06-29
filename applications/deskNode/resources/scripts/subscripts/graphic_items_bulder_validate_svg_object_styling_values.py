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


def validate_svg_object_styling_values(runtime) -> None:
    if not isinstance(runtime.SVG_OBJECT_OPACITY, (int, float)):
        runtime.fail(runtime, 'SVG_OBJECT_OPACITY muss eine Zahl sein.')
    if runtime.SVG_OBJECT_OPACITY < 0 or runtime.SVG_OBJECT_OPACITY > 1:
        runtime.fail(runtime, 'SVG_OBJECT_OPACITY muss zwischen 0 und 1 liegen.')
    if not isinstance(runtime.SVG_BLUR_PERCENT, (int, float)):
        runtime.fail(runtime, 'SVG_BLUR_PERCENT muss eine Zahl sein.')
    if runtime.SVG_BLUR_PERCENT < 0:
        runtime.fail(runtime, 'SVG_BLUR_PERCENT darf nicht kleiner als 0 sein.')

def register(runtime):
    runtime.validate_svg_object_styling_values = validate_svg_object_styling_values
