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


def finish_graphic_items(runtime, setup_result, build_result):
    canvas_size = runtime.TARGET_IMAGE_SIZE + runtime.HEADROOM_IMAGE_SIZE
    print()
    print("Erfolgreich bestimmt und verarbeitet:")
    print(f"rnd_str_prvdr:        {runtime.rnd_str_prvdr}")
    print(f"tmp_stmp_prvdr:       {runtime.tmp_stmp_prvdr}")
    print(f"target_image_size:    {runtime.TARGET_IMAGE_SIZE}px")
    print(f"headroom_image_size:  {runtime.HEADROOM_IMAGE_SIZE}px")
    print(f"quadrofying_size:     {canvas_size}px")
    print(f"mask_a_saturation:    {runtime.MASK_A_SATURATION}")
    print(f"mask_a_brightness:    {runtime.MASK_A_BRIGHTNESS}")
    print(f"mask_a_contrast:      {runtime.MASK_A_CONTRAST}")
    print(f"mask_b_brightness:    {runtime.MASK_B_BRIGHTNESS}")
    print(f"mask_b_contrast:      {runtime.MASK_B_CONTRAST}")
    print(f"trace_threshold:      {runtime.TRACE_BITMAP_THRESHOLD:.3f}")
    print(f"trace_invert:         {runtime.TRACE_BITMAP_INVERT}")
    print(f"trace_speckles:       {runtime.TRACE_BITMAP_SPECKLES}")
    print(f"trace_smooth_corners: {runtime.TRACE_BITMAP_SMOOTH_CORNERS:.2f}")
    print(f"trace_optimize:       {runtime.TRACE_BITMAP_OPTIMIZE:.3f}")
    print(f"trace_select_area:    {runtime.TRACE_BITMAP_SELECT_AREA}")
    print(f"project_root_path:    {setup_result['project_root_path']}")
    print(f"rnd_str_prvdr_file:   {setup_result['rnd_str_prvdr_file']}")
    print(f"tmp_stmp_prvdr_file:  {setup_result['tmp_stmp_prvdr_file']}")
    print(f"temp_path:            {setup_result['temp_path']}")
    print(f"source_images_path:   {runtime.source_images_path}")
    print(f"scaled_images_path:   {runtime.scaled_images_path}")
    print(f"step_one_pngs:        {runtime.step_one_pngs}")
    print(f"step_two_pngs:        {runtime.step_two_pngs}")
    print(f"qfying_pngs:          {runtime.qfying_pngs}")
    print(f"masks_svg_path:       {runtime.masks_svg_path}")
    print(f"final_path:           {runtime.final_path}")
    print(f"gimp_profile_path:    {runtime.gimp_batch_profile_path}")
    print(f"devbox_db:            {setup_result['devbox_db']}")
    print(f"manufacture_database: {runtime.manufacture_database}")
    print(f"graphic_items_database: {runtime.graphic_items_database}")
    print(f"items_archive_path:    {build_result['items_archive_path']}")
    print(f"manufacturer_name:    {runtime.manufacturer_name}")
    print(f"product_family:       {runtime.product_family}")
    print(f"product_name:         {runtime.product_name}")
    print(f"loc_db:               {runtime.loc_db}")
    print(f"inkscape_executable:  {runtime.inkscape_executable_path}")
    print(f"gimp_tool_key:        {runtime.gimp_tool_key}")
    print(f"gimp_executable:      {runtime.gimp_executable_path}")
    print(f"gimp_major_version:   {setup_result['gimp_major_version']}")
    print(f"mask_a_gimp_fix:      {build_result['mask_a_gimp_status']}")
    print(f"mask_b_gimp_fix:      {build_result['mask_b_gimp_status']}")
    print(f"Kopierte PNGs:        {len(build_result['copied_files'])}")
    print(f"Skalierte PNGs:       {len(build_result['scaled_files'])}")
    print(f"Quadrofied PNGs:      {len(build_result['qfying_files'])}")
    print(f"Mask-A PNGs:          {len(build_result['mask_a_files'])}")
    print(f"Mask-B PNGs:          {len(build_result['mask_b_files'])}")
    print(f"Masken-SVGs:          {len(build_result['mask_svg_files'])}")
    print(f"layer2_gradient_radius: {runtime.LAYER2_RADIAL_GRADIENT_RADIUS}")
    print(f"svg_object_opacity:   {runtime.SVG_OBJECT_OPACITY}")
    print(f"svg_blur_percent:     {runtime.SVG_BLUR_PERCENT}")
    print(f"UX-Theme-Datensätze:  {len(build_result['ux_themes'])}")
    print("UX-Theme-Ordner:      " + str(sum(len(paths) for paths in build_result['theme_layer_directories'].values())))
    print("Erzeugte Theme-SVGs:  " + str(build_result['created_theme_layer_svg_file_count']))
    print("Layer1-SVGs:          " + str(build_result['created_layer1_svg_file_count']))
    print("Layer2-SVGs:          " + str(build_result['created_layer2_svg_file_count']))
    print("Gerenderte Theme-PNGs: " + str(build_result['rendered_theme_layer_png_file_count']))
    print(f"Final-Version-1-PNGs: {len(build_result['final_version1_files'])}")
    print(f"Final-Version-2-PNGs: {len(build_result['final_version2_files'])}")
    print(f"Final-Version-3-PNGs: {len(build_result['final_version3_files'])}")
    print(f"Final-Version-4-PNGs: {len(build_result['final_version4_files'])}")
    print(f"Final-Version-5-PNGs: {len(build_result['final_version5_files'])}")
    print(f"Final-Version-6-PNGs: {len(build_result['final_version6_files'])}")
    print(f"Kopierte Masken-SVGs: {len(build_result['copied_mask_svg_files'])}")
    print(f"Kopierte Tree-Icon-SVGs: {len(build_result['copied_tree_icon_svg_files'])}")
    print(f"Archivierte Final-Dateien: {build_result['archived_final_file_count']}")
    print(f"items.zip Größe:       {build_result['items_archive_size']} Bytes")
    print(f"Final-Vers2-Deckkraft: {runtime.FINAL_VERSION2_OPACITY:.0%}")
    print(f"Final-Masken-Deckkraft: {runtime.FINAL_MASK_OVERLAY_OPACITY:.0%}")
    print(f"Final-Masken-Unschärfe: {runtime.FINAL_MASK_OVERLAY_BLUR_PERCENT:.0f}%")
    print(f"Final-Vers3-Themes:   {len(build_result['ux_themes'])} Glow-Off-Datensätze")
    print("Final-Vers3-Dateiname: symbol_vers3_<record_id>_<symbol>.png")
    print("Final-Vers4-Dateiname: symbol_vers4_<record_id>_<symbol>.png")
    print("Final-Vers5-Dateiname: symbol_vers5_<record_id>_<symbol>.png")
    print("Final-Vers6-Dateiname: symbol_vers6_<record_id>_<symbol>.png")
    print()
    print("Bestätigung: Alle Final-Dateien einschließlich der Masken- und Tree-Icon-SVGs wurden mit maximaler DEFLATE-Kompression in items.zip gepackt und als graphic_items.r0b installiert.")
    runtime.remove_directory_until_gone(
        runtime,
        setup_result["temp_path"],
    )
    print("Temporärer Arbeitsordner wurde vollständig entfernt. Skript beendet.")


def register(runtime):
    runtime.finish_graphic_items = finish_graphic_items
