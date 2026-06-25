from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

from subscripts.main_gui_devbox_log import get_devbox_logger


MODULE_LOGGER = get_devbox_logger(__file__)
MODULE_LOGGER.info("Module loaded.")


def _remove_pycache(root_dir: Path) -> None:
    directories = sorted(
        (item for item in root_dir.rglob("__pycache__") if item.is_dir()),
        key=lambda item: len(item.parts),
        reverse=True,
    )
    for directory in directories:
        shutil.rmtree(directory, ignore_errors=True)


def _clear_font_files(root_dir: Path, reporter) -> None:
    fonts_directory = root_dir / "resources" / "fonts"
    if not fonts_directory.is_dir():
        return
    for file_path in fonts_directory.rglob("*"):
        if file_path.is_file():
            try:
                file_path.unlink()
            except OSError as error:
                reporter.warning("Could not remove font file from publish root.", error)


def _replace_installers_with_dummies(root_dir: Path, reporter) -> None:
    installers_directory = root_dir / "resources" / "third_party_installers"
    if not installers_directory.is_dir():
        return
    installer_names = [item.name for item in installers_directory.iterdir() if item.is_file()]
    for file_path in installers_directory.iterdir():
        if file_path.is_file():
            try:
                file_path.unlink()
            except OSError as error:
                reporter.warning("Could not remove third-party installer.", error)
    for file_name in installer_names:
        (installers_directory / file_name).write_text("Dummy.EXE", encoding="utf-8")


def _remove_devbox_executable(root_dir: Path, reporter) -> None:
    executable = root_dir / "resources" / "applications" / "devbox" / "devbox.exe"
    if executable.is_file():
        try:
            executable.unlink()
        except OSError as error:
            reporter.warning("Could not remove DevBox executable from publish root.", error)


def _extract_document_forms(context) -> None:
    if not context.forms_file.is_file():
        raise FileNotFoundError(f"Document forms archive not found: {context.forms_file}")
    context.docs_path.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(context.forms_file, "r") as archive:
        archive.extractall(context.docs_path)


def prepare_publish_root(context, reporter) -> None:
    reporter.info("Creating prepared DevBox publish root.")
    shutil.copytree(
        context.project_root,
        context.root_dir,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", ".git"),
    )
    _remove_pycache(context.root_dir)

    root_applications = context.root_dir / "applications"
    if root_applications.is_dir():
        shutil.rmtree(root_applications, ignore_errors=True)
    root_applications.mkdir(parents=True, exist_ok=True)

    _clear_font_files(context.root_dir, reporter)
    _replace_installers_with_dummies(context.root_dir, reporter)
    _remove_devbox_executable(context.root_dir, reporter)
    _extract_document_forms(context)
    context.assets_path.mkdir(parents=True, exist_ok=True)
    context.documents_path.mkdir(parents=True, exist_ok=True)
    context.pictures_path.mkdir(parents=True, exist_ok=True)
    reporter.info("Prepared DevBox publish root created.", str(context.root_dir))
