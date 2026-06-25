#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path

from compile_to_exe_common import debug, debug_header, fail, generate_build_timestamp, generate_random_part, tool_file


def create_temp_structure() -> tuple[Path, Path, Path]:
    random_part = generate_random_part()
    own_stem = tool_file().stem
    temp_path = Path(tempfile.gettempdir()) / f"_{own_stem}_{random_part}"
    work_dir = temp_path / "work_dir"
    final_compile = temp_path / "final_compile"

    debug(f"Temp root will be: {temp_path}")
    debug(f"Work directory will be: {work_dir}")
    debug(f"Final compile directory will be: {final_compile}")
    if temp_path.exists():
        fail(f"Temporary path already exists, refusing to reuse it: {temp_path}")
    work_dir.mkdir(parents=True, exist_ok=False)
    final_compile.mkdir(parents=True, exist_ok=False)
    debug("Temporary build directories created.")
    return temp_path, work_dir, final_compile


def copy_file_to_directory(source: Path, target_directory: Path, label: str) -> Path:
    target = target_directory / source.name
    debug(f"Cloning {label}:")
    debug(f"  Source: {source}")
    debug(f"  Target: {target}")
    if target.exists():
        timestamp = generate_build_timestamp()
        target = target_directory / f"{source.stem}_{timestamp}{source.suffix}"
        debug(f"  Name collision detected. New target: {target}")
    shutil.copy2(source, target)
    debug(f"  Clone completed: {target}")
    return target


def remove_python_sources_from_final_compile(final_compile: Path) -> None:
    debug_header("Final package source cleanup")
    debug("Ensuring that no .py files are delivered, saved, or zipped from final_compile.")
    removed = 0
    for path in sorted(final_compile.rglob("*.py")):
        if path.is_file():
            debug(f"Removing Python source from final package: {path.relative_to(final_compile)}")
            path.unlink()
            removed += 1
    debug("No .py files found in final_compile." if removed == 0 else f"Removed .py files from final_compile: {removed}")


def create_zip_from_directory(source_dir: Path, zip_file: Path) -> None:
    debug_header("ZIP compression")
    debug(f"Source directory: {source_dir}")
    debug(f"ZIP path:         {zip_file}")
    debug("Compression:      ZIP_DEFLATED, compresslevel=9")
    with zipfile.ZipFile(zip_file, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(source_dir.rglob("*")):
            if path.is_file():
                relative = path.relative_to(source_dir)
                debug(f"Adding to ZIP: {relative}")
                archive.write(path, relative)
    debug(f"ZIP created: {zip_file}")
    debug(f"ZIP size: {zip_file.stat().st_size} bytes")


def ask_save_as_zip(default_filename: str) -> Path | None:
    debug_header("Save As dialog")
    debug("Opening graphical Save As dialog...")
    try:
        import tkinter as tk
        from tkinter import filedialog
    except Exception as exc:
        debug(f"tkinter is not available: {exc!r}")
        return ask_save_as_zip_console(default_filename)

    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        selected = filedialog.asksaveasfilename(
            title="ZIP speichern unter",
            defaultextension=".zip",
            initialfile=default_filename,
            filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")],
        )
        root.destroy()
        if not selected:
            debug("Save As dialog was cancelled.")
            return None
        target = Path(selected).expanduser().resolve()
        if target.suffix.lower() != ".zip":
            target = target.with_suffix(".zip")
        debug(f"Selected ZIP target: {target}")
        return target
    except Exception as exc:
        debug(f"Save As dialog failed: {exc!r}")
        return ask_save_as_zip_console(default_filename)


def ask_save_as_zip_console(default_filename: str) -> Path | None:
    debug("Falling back to console-based target path input.")
    print(f"Enter ZIP target path or press ENTER to cancel. Default filename suggestion: {default_filename}", flush=True)
    value = input("> ").strip()
    if not value:
        debug("Console target input cancelled.")
        return None
    target = Path(value).expanduser().resolve()
    if target.suffix.lower() != ".zip":
        target = target.with_suffix(".zip")
    debug(f"Console-selected ZIP target: {target}")
    return target


def robust_remove_tree(path: Path) -> None:
    debug_header("Cleanup")
    debug(f"Removing temporary directory: {path}")

    def onerror(function, failed_path, exc_info):
        failed = Path(failed_path)
        debug(f"Cleanup issue at: {failed}")
        debug(f"Trying to make writable and retry: {failed}")
        try:
            failed.chmod(0o700)
            function(failed_path)
        except Exception as exc:
            debug(f"Cleanup retry failed for {failed}: {exc!r}")

    if not path.exists():
        debug("Temporary directory does not exist anymore.")
        return
    shutil.rmtree(path, onerror=onerror)
    debug("Temporary directory could not be removed completely." if path.exists() else "Temporary directory removed successfully.")


def copy_zip_to_target(temp_zip: Path, target_zip: Path) -> None:
    debug_header("Final copy")
    debug(f"Temporary ZIP: {temp_zip}")
    debug(f"Target ZIP:    {target_zip}")
    target_zip.parent.mkdir(parents=True, exist_ok=True)
    if target_zip.exists():
        debug("Target ZIP already exists and will be overwritten.")
    shutil.copy2(temp_zip, target_zip)
    debug("Final ZIP copied successfully.")
    debug(f"Final ZIP size: {target_zip.stat().st_size} bytes")


def copy_directory_contents_to_target(source_dir: Path, target_dir: Path) -> None:
    debug_header("Final folder export")
    debug(f"Source directory: {source_dir}")
    debug(f"Target directory: {target_dir}")
    target_dir.mkdir(parents=True, exist_ok=True)
    for source_path in sorted(source_dir.rglob("*")):
        relative = source_path.relative_to(source_dir)
        target_path = target_dir / relative
        if source_path.is_dir():
            target_path.mkdir(parents=True, exist_ok=True)
        elif source_path.is_file():
            target_path.parent.mkdir(parents=True, exist_ok=True)
            debug(("Overwriting existing file: " if target_path.exists() else "Copying file: ") + str(target_path))
            shutil.copy2(source_path, target_path)
    debug("Final folder export completed successfully.")


def export_final_compile(final_compile: Path, temp_path: Path, launcher_stem: str, export_mode: str, export_target: Path | None) -> Path:
    debug_header("Export selection")
    debug(f"Export mode:   {export_mode}")
    debug(f"Export target: {export_target if export_target else 'dialog'}")
    if export_mode == "direct_folder":
        if export_target is None:
            fail("Internal error: direct folder export selected without target path.")
        copy_directory_contents_to_target(final_compile, export_target)
        return export_target

    build_timestamp = generate_build_timestamp()
    temp_zip = temp_path / f"{launcher_stem}_{build_timestamp}.zip"
    create_zip_from_directory(final_compile, temp_zip)

    if export_mode == "direct_zip":
        if export_target is None:
            fail("Internal error: direct ZIP export selected without target path.")
        copy_zip_to_target(temp_zip, export_target)
        return export_target

    if export_mode == "dialog_zip":
        target_zip = ask_save_as_zip(f"{launcher_stem}.zip")
        if target_zip is None:
            fail("No ZIP target selected. Build result was not exported.", exit_code=2)
        copy_zip_to_target(temp_zip, target_zip)
        return target_zip

    fail(f"Unsupported export mode: {export_mode}")
