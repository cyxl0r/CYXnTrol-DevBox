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


def validate_final_mask_overlay_settings(runtime) -> None:
    if not isinstance(runtime.FINAL_MASK_OVERLAY_OPACITY, (int, float)):
        runtime.fail(runtime, 'FINAL_MASK_OVERLAY_OPACITY muss eine Zahl sein.')
    if runtime.FINAL_MASK_OVERLAY_OPACITY < 0 or runtime.FINAL_MASK_OVERLAY_OPACITY > 1:
        runtime.fail(runtime, 'FINAL_MASK_OVERLAY_OPACITY muss zwischen 0 und 1 liegen.')
    if not isinstance(runtime.FINAL_MASK_OVERLAY_BLUR_PERCENT, (int, float)):
        runtime.fail(runtime, 'FINAL_MASK_OVERLAY_BLUR_PERCENT muss eine Zahl sein.')
    if runtime.FINAL_MASK_OVERLAY_BLUR_PERCENT < 0:
        runtime.fail(runtime, 'FINAL_MASK_OVERLAY_BLUR_PERCENT darf nicht kleiner als 0 sein.')

def register(runtime):
    runtime.validate_final_mask_overlay_settings = validate_final_mask_overlay_settings
