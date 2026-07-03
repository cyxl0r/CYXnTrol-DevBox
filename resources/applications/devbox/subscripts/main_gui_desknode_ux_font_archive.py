from __future__ import annotations

import importlib.util
import os
import shutil
import stat
import tempfile
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from subscripts.main_gui_desknode_ux_defaults import normalize_font_path
from subscripts.main_gui_desknode_ux_fonts import font_directory, project_root, resolve_font_path
from subscripts.main_gui_devbox_log import get_devbox_logger


LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")


class DeskNodeUxFontArchiveError(RuntimeError):
    pass


@dataclass(frozen=True)
class DeskNodeUxFontArchiveResult:
    family_names: tuple[str, ...]
    archived_file_count: int
    archive_path: Path


def _load_random_string_provider(root: Path):
    provider_file = root / "platform" / "tools" / "random_string_provider.py"
    if not provider_file.is_file():
        raise DeskNodeUxFontArchiveError(
            "random_string_provider.py wurde nicht gefunden: "
            f"{provider_file}"
        )

    spec = importlib.util.spec_from_file_location(
        "devbox_desknode_ux_random_string_provider",
        provider_file,
    )
    if spec is None or spec.loader is None:
        raise DeskNodeUxFontArchiveError(
            "random_string_provider.py konnte nicht geladen werden: "
            f"{provider_file}"
        )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    generator = getattr(module, "generate_string", None)
    if not callable(generator):
        raise DeskNodeUxFontArchiveError(
            "random_string_provider.py stellt generate_string nicht bereit."
        )
    return generator


def _generate_temp_directory(root: Path) -> Path:
    generator = _load_random_string_provider(root)

    while True:
        try:
            folder_name = str(generator(length=64, variant=1)).strip()
        except Exception as error:
            raise DeskNodeUxFontArchiveError(
                "Die Zufallszeichenfolge für das Schriftarchiv konnte nicht "
                f"erzeugt werden: {error}"
            ) from error

        if len(folder_name) != 64 or not folder_name.isalnum():
            raise DeskNodeUxFontArchiveError(
                "random_string_provider.py lieferte keine gültige 64-stellige "
                "alphanumerische Zeichenfolge."
            )

        temp_path = Path(tempfile.gettempdir()) / folder_name
        try:
            temp_path.mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            continue
        except OSError as error:
            raise DeskNodeUxFontArchiveError(
                "Temporärer Schriftarchiv-Ordner konnte nicht erstellt werden: "
                f"{temp_path} | {error}"
            ) from error
        return temp_path


def _remove_readonly(function, path, _exception_info) -> None:
    try:
        os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
        function(path)
    except OSError:
        return


def _remove_until_gone(path: Path) -> None:
    target = Path(path)

    while target.exists():
        try:
            if target.is_dir() and not target.is_symlink():
                shutil.rmtree(target, onerror=_remove_readonly)
            else:
                os.chmod(target, stat.S_IWRITE | stat.S_IREAD)
                target.unlink()
        except OSError:
            pass

        if target.exists():
            time.sleep(0.1)


def _selected_font_family_directories(
    studio,
    settings: dict[str, object],
) -> tuple[Path, ...]:
    fonts_root = font_directory(studio).resolve()
    selected_paths = sorted(
        {
            normalize_font_path(value)
            for key, value in settings.items()
            if key.endswith("_font_path") and str(value or "").strip()
        },
        key=str.casefold,
    )

    family_directories: dict[str, Path] = {}

    for selected_path in selected_paths:
        font_file = resolve_font_path(studio, selected_path)
        if font_file is None:
            raise DeskNodeUxFontArchiveError(
                "Die ausgewählte Schriftdatei ist ungültig oder liegt nicht "
                "innerhalb von resources/fonts: "
                f"{selected_path}"
            )

        relative_font_file = font_file.resolve().relative_to(fonts_root)
        if len(relative_font_file.parts) < 2:
            raise DeskNodeUxFontArchiveError(
                "Ausgewählte Schriftdateien müssen in einem eigenen "
                "Schrift-Mutterverzeichnis unter resources/fonts liegen: "
                f"{selected_path}"
            )

        family_name = relative_font_file.parts[0]
        family_directory = (fonts_root / family_name).resolve()

        try:
            family_directory.relative_to(fonts_root)
        except ValueError as error:
            raise DeskNodeUxFontArchiveError(
                "Das Schrift-Mutterverzeichnis liegt außerhalb von "
                "resources/fonts: "
                f"{family_directory}"
            ) from error

        if not family_directory.is_dir():
            raise DeskNodeUxFontArchiveError(
                "Das Schrift-Mutterverzeichnis wurde nicht gefunden: "
                f"{family_directory}"
            )

        family_directories[family_name.casefold()] = family_directory

    return tuple(
        family_directories[key]
        for key in sorted(family_directories, key=str.casefold)
    )


def _copy_font_families(
    family_directories: tuple[Path, ...],
    temp_copy_path: Path,
) -> int:
    copied_file_count = 0

    for source_directory in family_directories:
        target_directory = temp_copy_path / source_directory.name
        try:
            shutil.copytree(
                source_directory,
                target_directory,
                symlinks=True,
                copy_function=shutil.copy2,
            )
        except (OSError, shutil.Error) as error:
            raise DeskNodeUxFontArchiveError(
                "Schrift-Mutterverzeichnis konnte nicht vollständig kopiert "
                f"werden: {source_directory} | {error}"
            ) from error
        copied_file_count += sum(
            1
            for item in target_directory.rglob("*")
            if item.is_file()
        )

    return copied_file_count


def _create_zip_archive(temp_copy_path: Path) -> Path:
    archive_path = temp_copy_path / "schriftarchiv.zip"
    source_files = sorted(
        (
            item
            for item in temp_copy_path.rglob("*")
            if item.is_file() and item != archive_path
        ),
        key=lambda item: item.relative_to(temp_copy_path).as_posix().casefold(),
    )

    try:
        with zipfile.ZipFile(
            archive_path,
            mode="w",
            compression=zipfile.ZIP_LZMA,
        ) as archive:
            for source_file in source_files:
                archive.write(
                    source_file,
                    source_file.relative_to(temp_copy_path).as_posix(),
                )
    except (OSError, RuntimeError, NotImplementedError, zipfile.BadZipFile) as error:
        raise DeskNodeUxFontArchiveError(
            f"Schriftarchiv konnte nicht erstellt werden: {error}"
        ) from error

    if not archive_path.is_file() or archive_path.stat().st_size <= 0:
        raise DeskNodeUxFontArchiveError(
            "Schriftarchiv wurde nicht korrekt erstellt: "
            f"{archive_path}"
        )

    return archive_path


def _replace_target_archive(
    archive_path: Path,
    root: Path,
) -> Path:
    target_path = root / "applications" / "deskNode" / "data" / "fonts.r0b"
    target_path.parent.mkdir(parents=True, exist_ok=True)

    if target_path.exists():
        _remove_until_gone(target_path)

    try:
        shutil.copy2(archive_path, target_path)
    except OSError as error:
        raise DeskNodeUxFontArchiveError(
            "Schriftarchiv konnte nicht nach fonts.r0b kopiert werden: "
            f"{target_path} | {error}"
        ) from error

    if not target_path.is_file() or target_path.stat().st_size != archive_path.stat().st_size:
        raise DeskNodeUxFontArchiveError(
            "fonts.r0b wurde nicht korrekt kopiert: "
            f"{target_path}"
        )

    return target_path


def rebuild_desknode_font_archive(
    studio,
    settings: dict[str, object],
    progress: Callable[[str], None] | None = None,
) -> DeskNodeUxFontArchiveResult:
    """Bundle all currently selected non-system font families into fonts.r0b.

    Every non-empty ``*_font_path`` value is resolved dynamically. Each first
    directory below ``resources/fonts`` is copied once in full, including all
    cuts, licences, readmes and other bundled files. Empty paths represent
    ``Systemstandard`` and are deliberately skipped.
    """
    root = project_root(studio).resolve()
    temp_copy_path = _generate_temp_directory(root)

    try:
        if progress is not None:
            progress("Schriftarchiv wird vorbereitet …")

        family_directories = _selected_font_family_directories(studio, settings)

        if progress is not None:
            progress("Ausgewählte Schriftfamilien werden kopiert …")

        archived_file_count = _copy_font_families(
            family_directories,
            temp_copy_path,
        )

        if progress is not None:
            progress("Schriftarchiv wird mit maximaler Kompression erstellt …")

        archive_path = _create_zip_archive(temp_copy_path)

        if progress is not None:
            progress("fonts.r0b wird ersetzt …")

        target_path = _replace_target_archive(archive_path, root)
        result = DeskNodeUxFontArchiveResult(
            family_names=tuple(directory.name for directory in family_directories),
            archived_file_count=archived_file_count,
            archive_path=target_path,
        )
        LOGGER.info(
            "deskNode font archive rebuilt.",
            f"families={result.family_names}; files={result.archived_file_count}; "
            f"target={result.archive_path}",
        )
        return result
    finally:
        _remove_until_gone(temp_copy_path)
