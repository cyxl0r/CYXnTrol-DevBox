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


def validate_layer2_radial_gradient_radius(runtime) -> None:
    if not isinstance(runtime.LAYER2_RADIAL_GRADIENT_RADIUS, (int, float)):
        runtime.fail(runtime, 'LAYER2_RADIAL_GRADIENT_RADIUS muss eine Zahl sein.')
    if runtime.LAYER2_RADIAL_GRADIENT_RADIUS <= 0:
        runtime.fail(runtime, 'LAYER2_RADIAL_GRADIENT_RADIUS muss größer als 0 sein.')

def register(runtime):
    runtime.validate_layer2_radial_gradient_radius = validate_layer2_radial_gradient_radius
