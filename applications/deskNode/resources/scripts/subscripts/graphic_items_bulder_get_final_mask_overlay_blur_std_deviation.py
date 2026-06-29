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


def get_final_mask_overlay_blur_std_deviation(runtime, canvas_width: int, canvas_height: int) -> float:
    runtime.validate_final_mask_overlay_settings(runtime)
    return runtime.FINAL_MASK_OVERLAY_BLUR_PERCENT / 100 * ((canvas_width + canvas_height) / 8)

def register(runtime):
    runtime.get_final_mask_overlay_blur_std_deviation = get_final_mask_overlay_blur_std_deviation
