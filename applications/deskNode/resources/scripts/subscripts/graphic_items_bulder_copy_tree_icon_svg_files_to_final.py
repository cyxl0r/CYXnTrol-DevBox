from __future__ import annotations

from pathlib import Path
import shutil


def copy_tree_icon_svg_files_to_final(
    runtime,
    project_root_path: Path,
    final_path: Path,
) -> list[Path]:
    source_directory = project_root_path / "resources" / "graphics"
    if not source_directory.is_dir():
        runtime.fail(
            runtime,
            f"Tree-Icon-Quellordner wurde nicht gefunden: {source_directory}",
        )
    if not final_path.is_dir():
        runtime.fail(runtime, f"Final-Ordner wurde nicht gefunden: {final_path}")
    source_files = [
        file_path
        for file_path in source_directory.glob("tree_ic_*.svg")
        if file_path.is_file()
    ]
    source_files.sort(key=lambda file_path: file_path.name.lower())
    if not source_files:
        runtime.fail(
            runtime,
            "Im Tree-Icon-Quellordner wurden keine Dateien gefunden: "
            f"{source_directory / 'tree_ic_*.svg'}",
        )
    copied_files = []
    for source_file in source_files:
        target_file = final_path / source_file.name
        if target_file.exists():
            runtime.remove_file_until_gone(runtime, target_file)
        try:
            shutil.copy2(source_file, target_file)
        except Exception as error:
            runtime.fail(
                runtime,
                "Tree-Icon-SVG konnte nicht in den Final-Ordner kopiert werden: "
                f"{source_file} -> {target_file} | {error}",
            )
        if not target_file.is_file():
            runtime.fail(runtime, f"Kopierte Tree-Icon-SVG existiert nicht: {target_file}")
        if target_file.stat().st_size <= 0:
            runtime.fail(runtime, f"Kopierte Tree-Icon-SVG ist leer: {target_file}")
        copied_files.append(target_file)
    return copied_files


def register(runtime):
    runtime.copy_tree_icon_svg_files_to_final = copy_tree_icon_svg_files_to_final
