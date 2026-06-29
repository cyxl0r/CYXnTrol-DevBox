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


def main(runtime, current_file_path):
    setup_result = runtime.setup_runtime(
        runtime,
        current_file_path,
    )
    build_result = runtime.build_graphic_items(
        runtime,
        setup_result,
    )
    runtime.finish_graphic_items(
        runtime,
        setup_result,
        build_result,
    )


def register(runtime):
    runtime.main = main
