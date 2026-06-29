from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

from subscripts.main_gui_devbox_log import get_devbox_logger


MODULE_LOGGER = get_devbox_logger(__file__)
MODULE_LOGGER.info("Module loaded.")


def _remove_pycache(root_dir: Path) -> None:
    directories = sorted(
        (
            item
            for item in root_dir.rglob("__pycache__")
            if item.is_dir()
        ),
        key=lambda item: len(item.parts),
        reverse=True,
    )

    for directory in directories:
        shutil.rmtree(
            directory,
            ignore_errors=True,
        )


def _clear_font_files(
    root_dir: Path,
    reporter,
) -> None:
    fonts_directory = (
        root_dir
        / "resources"
        / "fonts"
    )

    if not fonts_directory.is_dir():
        return

    for file_path in fonts_directory.rglob("*"):
        if not file_path.is_file():
            continue

        try:
            file_path.unlink()

        except OSError as error:
            reporter.warning(
                "Could not remove font file from publish root.",
                error,
            )


def _replace_installers_with_dummies(
    root_dir: Path,
    reporter,
) -> None:
    installers_directory = (
        root_dir
        / "resources"
        / "third_party_installers"
    )

    if not installers_directory.is_dir():
        return

    installer_names = [
        item.name
        for item in installers_directory.iterdir()
        if item.is_file()
    ]

    for file_path in installers_directory.iterdir():
        if not file_path.is_file():
            continue

        try:
            file_path.unlink()

        except OSError as error:
            reporter.warning(
                "Could not remove third-party installer.",
                error,
            )

    for file_name in installer_names:
        dummy_file = installers_directory / file_name

        dummy_file.write_text(
            "Dummy.EXE",
            encoding="utf-8",
        )


def _remove_devbox_executable(
    root_dir: Path,
    reporter,
) -> None:
    executable = (
        root_dir
        / "resources"
        / "applications"
        / "devbox"
        / "devbox.exe"
    )

    if not executable.is_file():
        return

    try:
        executable.unlink()

    except OSError as error:
        reporter.warning(
            "Could not remove DevBox executable from publish root.",
            error,
        )


def _extract_document_forms(
    context,
) -> None:
    if not context.forms_file.is_file():
        raise FileNotFoundError(
            "Document forms archive not found: "
            f"{context.forms_file}"
        )

    context.docs_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    with zipfile.ZipFile(
        context.forms_file,
        "r",
    ) as archive:
        archive.extractall(context.docs_path)


def _count_files(
    directory_path: Path,
) -> int:
    return sum(
        1
        for item in directory_path.rglob("*")
        if item.is_file()
    )


def _copy_desknode_resource_scripts(
    context,
    reporter,
) -> None:
    source_scripts_path = (
        context.project_root
        / "applications"
        / "deskNode"
        / "resources"
        / "scripts"
    )

    target_scripts_path = (
        context.root_dir
        / "applications"
        / "deskNode"
        / "resources"
        / "scripts"
    )

    if not source_scripts_path.is_dir():
        raise FileNotFoundError(
            "deskNode resource scripts directory not found: "
            f"{source_scripts_path}"
        )

    if target_scripts_path.exists():
        shutil.rmtree(
            target_scripts_path,
            ignore_errors=True,
        )

    shutil.copytree(
        source_scripts_path,
        target_scripts_path,
        ignore=shutil.ignore_patterns(
            "__pycache__",
            "*.pyc",
            "*.pyo",
        ),
    )

    _remove_pycache(target_scripts_path)

    copied_file_count = _count_files(
        target_scripts_path,
    )

    reporter.info(
        "deskNode resource scripts copied to publish root.",
        (
            f"source={source_scripts_path}; "
            f"target={target_scripts_path}; "
            f"files={copied_file_count}"
        ),
    )


def _prepare_repository_applications(
    context,
    reporter,
) -> None:
    root_applications = (
        context.root_dir
        / "applications"
    )

    if root_applications.is_dir():
        shutil.rmtree(
            root_applications,
            ignore_errors=True,
        )

    root_applications.mkdir(
        parents=True,
        exist_ok=True,
    )

    _copy_desknode_resource_scripts(
        context=context,
        reporter=reporter,
    )


def prepare_publish_root(
    context,
    reporter,
) -> None:
    reporter.info(
        "Creating prepared DevBox publish root."
    )

    shutil.copytree(
        context.project_root,
        context.root_dir,
        ignore=shutil.ignore_patterns(
            "__pycache__",
            "*.pyc",
            "*.pyo",
            ".git",
        ),
    )

    _remove_pycache(
        context.root_dir,
    )

    _prepare_repository_applications(
        context=context,
        reporter=reporter,
    )

    _clear_font_files(
        context.root_dir,
        reporter,
    )

    _replace_installers_with_dummies(
        context.root_dir,
        reporter,
    )

    _remove_devbox_executable(
        context.root_dir,
        reporter,
    )

    _extract_document_forms(
        context,
    )

    context.assets_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    context.documents_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    context.pictures_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    reporter.info(
        "Prepared DevBox publish root created.",
        str(context.root_dir),
    )

