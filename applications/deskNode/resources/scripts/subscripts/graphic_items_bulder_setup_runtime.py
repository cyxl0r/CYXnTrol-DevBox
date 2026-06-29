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


def setup_runtime(runtime, current_file_path):
    my_location_path = current_file_path.parent
    project_root_path = runtime.find_project_root(
        runtime,
        my_location_path.parent,
    )
    rnd_str_prvdr_file = runtime.find_file_in_project(
        runtime,
        project_root_path,
        runtime.rnd_str_prvdr,
    )
    tmp_stmp_prvdr_file = runtime.find_file_in_project(
        runtime,
        project_root_path,
        runtime.tmp_stmp_prvdr,
    )
    random_string_provider = runtime.load_python_module(
        runtime,
        "random_string_provider",
        rnd_str_prvdr_file,
    )
    random_part_6 = runtime.get_random_part(
        runtime,
        random_string_provider,
        6,
    )
    random_part_5 = runtime.get_random_part(
        runtime,
        random_string_provider,
        5,
    )
    random_part_7 = runtime.get_random_part(
        runtime,
        random_string_provider,
        7,
    )
    temp_path = Path(tempfile.gettempdir()) / (
        f"{random_part_6}_{random_part_5}_{random_part_7}"
    )
    runtime.create_directory(
        runtime,
        temp_path,
        "Temporärer Arbeitsordner",
    )
    runtime.source_images_path = temp_path / "source_pngs"
    runtime.scaled_images_path = temp_path / "scaled_pngs"
    runtime.step_one_pngs = temp_path / "m_step1_pngs"
    runtime.step_two_pngs = temp_path / "m_step2_pngs"
    runtime.qfying_pngs = temp_path / "quadrofying_pngs"
    runtime.masks_svg_path = temp_path / "svg_masks"
    runtime.final_path = temp_path / "final"
    runtime.gimp_batch_profile_path = temp_path / "gimp_batch_profile"
    for directory_path, description in (
        (runtime.source_images_path, "Quellbildordner"),
        (runtime.scaled_images_path, "Skalierter-Bildordner"),
        (runtime.step_one_pngs, "Schritt-1-Bildordner"),
        (runtime.step_two_pngs, "Schritt-2-Bildordner"),
        (runtime.qfying_pngs, "Quadrofying-Bildordner"),
        (runtime.masks_svg_path, "Masken-SVG-Ordner"),
        (runtime.final_path, "Final-Bildordner"),
        (runtime.gimp_batch_profile_path, "Temporärer GIMP-Konfigurationsordner"),
    ):
        runtime.create_directory(
            runtime,
            directory_path,
            description,
        )
    devbox_db = (
        project_root_path
        / "resources"
        / "organization"
        / "devbox_db.r0b"
    )
    if not devbox_db.is_file():
        runtime.fail(
            runtime,
            "DevBox-Datenbank wurde nicht gefunden: "
            f"{devbox_db}",
        )
    runtime.manufacture_database = (
        project_root_path
        / "applications"
        / "deskNode"
        / "data"
        / "mnfctr_db.r0b"
    )
    if not runtime.manufacture_database.is_file():
        runtime.fail(
            runtime,
            "Herstellerdatenbank wurde nicht gefunden: "
            f"{runtime.manufacture_database}",
        )
    runtime.graphic_items_database = (
        project_root_path
        / "applications"
        / "deskNode"
        / "data"
        / "graphic_items.r0b"
    )
    (
        runtime.manufacturer_name,
        runtime.product_family,
    ) = runtime.get_manufacturer_credentials(
        runtime,
        devbox_db,
    )
    runtime.product_name = runtime.get_product_name(
        runtime,
        devbox_db,
        "deskNode",
    )
    appdata_path = runtime.get_appdata_path(runtime)
    runtime.loc_db = (
        appdata_path
        / runtime.manufacturer_name
        / runtime.product_family
        / "devbox"
        / "locdata.r0b"
    )
    if not runtime.loc_db.is_file():
        runtime.fail(
            runtime,
            "Lokale Datenbank wurde nicht gefunden: "
            f"{runtime.loc_db}",
        )
    runtime.inkscape_executable_path = runtime.get_tool_location(
        runtime,
        runtime.loc_db,
        "inkscape",
    )
    (
        runtime.gimp_tool_key,
        runtime.gimp_executable_path,
    ) = runtime.get_first_available_tool_location(
        runtime,
        runtime.loc_db,
        (
            "gimp_console",
            "gimp_console_3_0",
            "gimp_console_3",
            "gimp",
        ),
    )
    gimp_major_version = runtime.ensure_gimp_3_or_newer(
        runtime,
        runtime.gimp_executable_path,
    )
    return {
        "project_root_path": project_root_path,
        "rnd_str_prvdr_file": rnd_str_prvdr_file,
        "tmp_stmp_prvdr_file": tmp_stmp_prvdr_file,
        "temp_path": temp_path,
        "devbox_db": devbox_db,
        "gimp_major_version": gimp_major_version,
    }


def register(runtime):
    runtime.setup_runtime = setup_runtime
