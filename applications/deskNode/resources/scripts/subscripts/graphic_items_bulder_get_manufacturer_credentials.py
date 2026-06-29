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


def get_manufacturer_credentials(runtime, devbox_db: Path) -> tuple[str, str]:
    try:
        with sqlite3.connect(devbox_db) as connection:
            cursor = connection.cursor()
            cursor.execute('\n                SELECT\n                    manufacturer_name,\n                    product_family\n                FROM manufacturer_credentials\n                ORDER BY rowid ASC\n                LIMIT 1 OFFSET 1\n                ')
            row = cursor.fetchone()
    except sqlite3.Error as error:
        runtime.fail(runtime, f'manufacturer_credentials konnte nicht gelesen werden: {error}')
    if row is None:
        runtime.fail(runtime, 'In manufacturer_credentials existiert kein zweiter Datensatz.')
    manufacturer_name_value = row[0]
    product_family_value = row[1]
    if manufacturer_name_value is None:
        runtime.fail(runtime, 'manufacturer_name im zweiten manufacturer_credentials-Datensatz ist leer.')
    if product_family_value is None:
        runtime.fail(runtime, 'product_family im zweiten manufacturer_credentials-Datensatz ist leer.')
    manufacturer_name_value = str(manufacturer_name_value).strip()
    product_family_value = str(product_family_value).strip()
    if not manufacturer_name_value:
        runtime.fail(runtime, 'manufacturer_name im zweiten manufacturer_credentials-Datensatz ist leer.')
    if not product_family_value:
        runtime.fail(runtime, 'product_family im zweiten manufacturer_credentials-Datensatz ist leer.')
    return (manufacturer_name_value, product_family_value)

def register(runtime):
    runtime.get_manufacturer_credentials = get_manufacturer_credentials
