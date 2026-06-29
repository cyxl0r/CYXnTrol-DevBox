from __future__ import annotations

from pathlib import Path

from subscripts.main_gui_desknode_ux_defaults import normalize_font_path


FONT_SUFFIXES = {".ttf", ".otf"}


def project_root(studio) -> Path:
    return Path(studio.project_root_path)


def font_directory(studio) -> Path:
    return project_root(studio) / "resources" / "fonts"


def scan_project_fonts(studio) -> list[str]:
    """Return supported font files below <projectroot>/resources/fonts.

    Stored values are always relative to the project root, so the UX profile
    remains portable when the whole project is moved to another location.
    """
    root = font_directory(studio)
    if not root.is_dir():
        return []

    project_directory = project_root(studio)
    paths: list[str] = []

    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue
        if file_path.suffix.casefold() not in FONT_SUFFIXES:
            continue
        paths.append(
            file_path.relative_to(project_directory).as_posix()
        )

    return sorted(set(paths), key=str.casefold)


def resolve_font_path(studio, relative_path: object) -> Path | None:
    try:
        normalized = normalize_font_path(relative_path)
    except ValueError:
        return None

    if not normalized:
        return None

    root = project_root(studio).resolve()
    candidate = (root / normalized).resolve()

    try:
        candidate.relative_to(root)
    except ValueError:
        return None

    fonts_root = font_directory(studio).resolve()
    try:
        candidate.relative_to(fonts_root)
    except ValueError:
        return None

    if candidate.is_file() and candidate.suffix.casefold() in FONT_SUFFIXES:
        return candidate

    return None
