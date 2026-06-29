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


def build_graphic_items(runtime, setup_result):
    copied_files = runtime.copy_source_images(
        runtime,
        setup_result["project_root_path"],
        runtime.source_images_path,
    )
    unwanted_source_file = runtime.source_images_path / "symbol_source.png"
    if unwanted_source_file.exists():
        runtime.remove_file_until_gone(
            runtime,
            unwanted_source_file,
        )
    scaled_files = runtime.scale_source_images(
        runtime,
        runtime.source_images_path,
        runtime.scaled_images_path,
        runtime.inkscape_executable_path,
    )
    qfying_files = runtime.quadrofiy_scaled_images(
        runtime,
        runtime.scaled_images_path,
        runtime.qfying_pngs,
        runtime.inkscape_executable_path,
    )
    mask_a_files, mask_a_gimp_status = runtime.create_mask_a_images(
        runtime,
        runtime.qfying_pngs,
        runtime.step_one_pngs,
        runtime.gimp_executable_path,
        runtime.gimp_batch_profile_path,
    )
    mask_b_files, mask_b_gimp_status = runtime.create_mask_b_images(
        runtime,
        runtime.step_one_pngs,
        runtime.step_two_pngs,
        runtime.gimp_executable_path,
        runtime.gimp_batch_profile_path,
    )
    mask_svg_files = runtime.create_mask_svg_files(
        runtime,
        runtime.step_two_pngs,
        runtime.masks_svg_path,
        runtime.inkscape_executable_path,
    )
    ux_themes = runtime.get_ux_themes(
        runtime,
        runtime.manufacture_database,
    )
    theme_layer_directories = runtime.create_theme_layer_directories(
        runtime,
        setup_result["temp_path"],
        ux_themes,
    )
    (
        created_theme_layer_svg_file_count,
        created_layer1_svg_file_count,
        created_layer2_svg_file_count,
    ) = runtime.create_colored_theme_layer_svg_files(
        runtime,
        runtime.masks_svg_path,
        ux_themes,
        theme_layer_directories,
        runtime.inkscape_executable_path,
    )
    rendered_theme_layer_png_file_count = runtime.render_theme_layer_svg_files_to_png(
        runtime,
        theme_layer_directories,
        runtime.inkscape_executable_path,
    )
    final_version1_files = runtime.create_final_version1_files(
        runtime,
        runtime.qfying_pngs,
        runtime.final_path,
    )
    final_version2_files = runtime.create_final_version2_files(
        runtime,
        final_version1_files,
        runtime.final_path,
        runtime.inkscape_executable_path,
    )
    final_version3_files = runtime.create_final_version3_files(
        runtime,
        qfying_files,
        ux_themes,
        theme_layer_directories,
        runtime.final_path,
        runtime.inkscape_executable_path,
    )
    final_version4_files = runtime.create_final_version4_files(
        runtime,
        qfying_files,
        ux_themes,
        theme_layer_directories,
        runtime.final_path,
        runtime.inkscape_executable_path,
    )
    final_version5_files = runtime.create_final_version5_files(
        runtime,
        qfying_files,
        ux_themes,
        runtime.final_path,
        runtime.step_two_pngs,
        runtime.inkscape_executable_path,
    )
    final_version6_files = runtime.create_final_version6_files(
        runtime,
        qfying_files,
        ux_themes,
        runtime.final_path,
        runtime.step_two_pngs,
        runtime.inkscape_executable_path,
    )
    copied_mask_svg_files = runtime.copy_mask_svg_files_to_final(
        runtime,
        runtime.masks_svg_path,
        runtime.final_path,
    )
    items_archive_path = setup_result["temp_path"] / "items.zip"
    (
        archived_final_file_count,
        items_archive_size,
    ) = runtime.create_zip_archive_from_directory(
        runtime,
        runtime.final_path,
        items_archive_path,
    )
    runtime.install_graphic_items_archive(
        runtime,
        items_archive_path,
        runtime.graphic_items_database,
    )
    return {
        "copied_files": copied_files,
        "scaled_files": scaled_files,
        "qfying_files": qfying_files,
        "mask_a_files": mask_a_files,
        "mask_b_files": mask_b_files,
        "mask_a_gimp_status": mask_a_gimp_status,
        "mask_b_gimp_status": mask_b_gimp_status,
        "mask_svg_files": mask_svg_files,
        "ux_themes": ux_themes,
        "theme_layer_directories": theme_layer_directories,
        "created_theme_layer_svg_file_count": created_theme_layer_svg_file_count,
        "created_layer1_svg_file_count": created_layer1_svg_file_count,
        "created_layer2_svg_file_count": created_layer2_svg_file_count,
        "rendered_theme_layer_png_file_count": rendered_theme_layer_png_file_count,
        "final_version1_files": final_version1_files,
        "final_version2_files": final_version2_files,
        "final_version3_files": final_version3_files,
        "final_version4_files": final_version4_files,
        "final_version5_files": final_version5_files,
        "final_version6_files": final_version6_files,
        "copied_mask_svg_files": copied_mask_svg_files,
        "items_archive_path": items_archive_path,
        "archived_final_file_count": archived_final_file_count,
        "items_archive_size": items_archive_size,
    }


def register(runtime):
    runtime.build_graphic_items = build_graphic_items
