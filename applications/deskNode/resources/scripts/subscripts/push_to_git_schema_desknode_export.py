from __future__ import annotations

import shutil
import zipfile
from pathlib import Path


REQUIRED_RUNTIME_FILES = (
    "lan.r0b",
    "mnfctr_db.r0b",
    "fonts.r0b",
    "graphic_items.r0b",
)
ZIP_RUNTIME_ARCHIVES = (
    "fonts.r0b",
    "graphic_items.r0b",
)


def _remove_pycache(root_dir: Path) -> int:
    directories = sorted(
        (path for path in root_dir.rglob("__pycache__") if path.is_dir()),
        key=lambda path: len(path.parts),
        reverse=True,
    )
    for directory in directories:
        shutil.rmtree(directory, ignore_errors=True)
    return len(directories)


def _validate_runtime_payload(source_root: Path) -> None:
    data_path = source_root / "data"
    missing = [name for name in REQUIRED_RUNTIME_FILES if not (data_path / name).is_file()]
    if missing:
        raise FileNotFoundError(
            "deskNode publish was stopped because required runtime data is missing: "
            + ", ".join(str(data_path / name) for name in missing)
        )
    invalid_archives = [
        name for name in ZIP_RUNTIME_ARCHIVES
        if not zipfile.is_zipfile(data_path / name)
    ]
    if invalid_archives:
        raise RuntimeError(
            "deskNode publish was stopped because runtime archives are invalid: "
            + ", ".join(str(data_path / name) for name in invalid_archives)
        )


def _extract_document_forms(context) -> None:
    if not context.forms_file.is_file():
        raise FileNotFoundError(f"Document forms archive not found: {context.forms_file}")
    context.docs_path.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(context.forms_file, "r") as archive:
        archive.extractall(context.docs_path)


def prepare_publish_root(context, reporter) -> None:
    source_root = context.project_root / "applications" / "deskNode"
    if not source_root.is_dir():
        raise FileNotFoundError(f"deskNode source directory not found: {source_root}")
    _validate_runtime_payload(source_root)

    shutil.copytree(
        source_root,
        context.root_dir,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", ".git"),
    )
    reporter.info("deskNode content copied to publish root.", str(context.root_dir))

    resources_path = context.root_dir / "resources"
    if resources_path.exists():
        shutil.rmtree(resources_path, ignore_errors=True)
        reporter.info("deskNode resources directory removed from publish root.")

    removed_cache_count = _remove_pycache(context.root_dir)
    reporter.info("Publish root Python cache cleanup finished.", f"removed={removed_cache_count}")

    _extract_document_forms(context)
    context.assets_path.mkdir(parents=True, exist_ok=True)
    context.documents_path.mkdir(parents=True, exist_ok=True)
    context.pictures_path.mkdir(parents=True, exist_ok=True)
    reporter.info("deskNode repository asset structure created.")
