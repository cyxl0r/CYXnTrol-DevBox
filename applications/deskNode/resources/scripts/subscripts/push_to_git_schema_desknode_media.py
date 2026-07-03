from __future__ import annotations

import re
import shutil
import unicodedata
from pathlib import Path


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tif", ".tiff", ".svg"}


def _safe_stem(file_path: Path) -> str:
    normalized = unicodedata.normalize("NFKD", file_path.stem)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    safe = re.sub(r"[^a-z0-9]+", "_", ascii_text).strip("_")
    return safe or "picture"


def _target_file(pictures_path: Path, source_file: Path, timestamp: str, index: int) -> Path:
    suffix = f"_{timestamp}" if index == 0 else f"_{timestamp}_{index:02d}"
    return pictures_path / f"{_safe_stem(source_file)}{suffix}{source_file.suffix.lower()}"


def copy_repository_images(image_paths: list[Path], pictures_path: Path, timestamp: str, reporter) -> list[Path]:
    pictures_path.mkdir(parents=True, exist_ok=True)
    copied: list[Path] = []
    for source_file in image_paths:
        if not source_file.is_file():
            reporter.warning("Optional image was skipped because it no longer exists.", source_file)
            continue
        if source_file.suffix.lower() not in IMAGE_EXTENSIONS:
            reporter.warning("Optional file was skipped because it is not an image.", source_file)
            continue
        index = 0
        target_file = _target_file(pictures_path, source_file, timestamp, index)
        while target_file.exists():
            index += 1
            target_file = _target_file(pictures_path, source_file, timestamp, index)
        shutil.copy2(source_file, target_file)
        copied.append(target_file)
        reporter.info("Repository image copied.", f"{source_file.name} -> {target_file.name}")
    return copied
