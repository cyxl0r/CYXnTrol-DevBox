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


def get_product_name(runtime, devbox_db: Path, searched_product_name: str) -> str:
    try:
        with sqlite3.connect(devbox_db) as connection:
            cursor = connection.cursor()
            cursor.execute('\n                SELECT product_name\n                FROM product_credentials\n                WHERE product_name = ?\n                LIMIT 1\n                ', (searched_product_name,))
            row = cursor.fetchone()
    except sqlite3.Error as error:
        runtime.fail(runtime, f'product_credentials konnte nicht gelesen werden: {error}')
    if row is None:
        runtime.fail(runtime, f'Produkt wurde in product_credentials nicht gefunden: {searched_product_name}')
    product_name_value = row[0]
    if product_name_value is None:
        runtime.fail(runtime, 'product_name im gefundenen product_credentials-Datensatz ist leer.')
    product_name_value = str(product_name_value).strip()
    if not product_name_value:
        runtime.fail(runtime, 'product_name im gefundenen product_credentials-Datensatz ist leer.')
    return product_name_value

def register(runtime):
    runtime.get_product_name = get_product_name
