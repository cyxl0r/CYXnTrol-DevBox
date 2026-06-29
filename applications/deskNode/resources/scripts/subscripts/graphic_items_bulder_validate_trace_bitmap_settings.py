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


def validate_trace_bitmap_settings(runtime) -> None:
    if runtime.TRACE_BITMAP_THRESHOLD != 0.45:
        runtime.fail(runtime, 'TRACE_BITMAP_THRESHOLD muss für diesen Ablauf auf 0.450 gesetzt sein.')
    if runtime.TRACE_BITMAP_INVERT is not False:
        runtime.fail(runtime, 'TRACE_BITMAP_INVERT muss für diesen Ablauf auf False gesetzt sein.')
    if runtime.TRACE_BITMAP_SELECT_AREA is not False:
        runtime.fail(runtime, 'TRACE_BITMAP_SELECT_AREA muss für diesen Ablauf auf False gesetzt sein.')
    if runtime.TRACE_BITMAP_SPECKLES < 0:
        runtime.fail(runtime, 'TRACE_BITMAP_SPECKLES darf nicht negativ sein.')
    if runtime.TRACE_BITMAP_SMOOTH_CORNERS < 0:
        runtime.fail(runtime, 'TRACE_BITMAP_SMOOTH_CORNERS darf nicht negativ sein.')
    if runtime.TRACE_BITMAP_OPTIMIZE < 0:
        runtime.fail(runtime, 'TRACE_BITMAP_OPTIMIZE darf nicht negativ sein.')

def register(runtime):
    runtime.validate_trace_bitmap_settings = validate_trace_bitmap_settings
