from __future__ import annotations

import argparse
import importlib.util
import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

from subscripts.main_gui_devbox_log import get_devbox_logger


MODULE_LOGGER = get_devbox_logger(__file__)
MODULE_LOGGER.info("Module loaded.")
PROJECT_ROOT_ENV = "_CYXLABS_DEVBOX_PROJECT_ROOT_PATH"


@dataclass(frozen=True)
class PushRequest:
    product_slug: str
    commit_text: str
    image_paths: list[Path]


@dataclass(frozen=True)
class PushContext:
    project_root: Path
    temp_path: Path
    root_dir: Path
    repository_path: Path
    docs_path: Path
    assets_path: Path
    documents_path: Path
    pictures_path: Path
    database_file: Path
    source_database_file: Path
    forms_file: Path
    timestamp: str


def parse_request(argv: list[str] | None = None) -> PushRequest:
    parser = argparse.ArgumentParser(
        description="Prepare and push the DevBox repository publication state."
    )
    parser.add_argument("--product-slug", default="devbox")
    parser.add_argument("--commit-text", default="")
    parser.add_argument("--image", action="append", default=[])
    arguments = parser.parse_args(argv)
    product_slug = str(arguments.product_slug or "").strip().lower()
    if product_slug != "devbox":
        raise ValueError("This schema only supports the DevBox product.")
    images = [Path(value).expanduser().resolve() for value in arguments.image]
    return PushRequest(product_slug, str(arguments.commit_text or "").strip(), images)


def _load_module(name: str, module_file: Path) -> ModuleType:
    specification = importlib.util.spec_from_file_location(name, module_file)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"Provider could not be loaded: {module_file}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def _valid_root(path: Path) -> bool:
    root_file = path / ".root"
    try:
        return root_file.is_file() and root_file.read_text(encoding="utf-8").strip() == "project-root"
    except OSError:
        return False


def find_project_root(start_path: Path) -> Path:
    configured_root = os.environ.get(PROJECT_ROOT_ENV, "").strip()
    if configured_root:
        candidate = Path(configured_root).expanduser().resolve()
        if _valid_root(candidate):
            return candidate
    current_path = start_path.resolve()
    while True:
        if _valid_root(current_path):
            return current_path
        if current_path.parent == current_path:
            raise FileNotFoundError("No project root (.root = project-root) was found.")
        current_path = current_path.parent


def _get_publish_workspace_base() -> Path:
    configured_base = os.environ.get(
        "CYXLABS_DEVBOX_PUBLISH_TEMP_ROOT",
        "",
    ).strip()

    if configured_base:
        workspace_base = Path(configured_base).expanduser()
    else:
        system_temp_path = Path(tempfile.gettempdir()).resolve()
        workspace_base = Path(system_temp_path.anchor) / "cyx"

    try:
        workspace_base.mkdir(
            parents=True,
            exist_ok=True,
        )
    except OSError as error:
        raise RuntimeError(
            "Could not create the short DevBox publish workspace base: "
            f"{workspace_base}"
        ) from error

    return workspace_base.resolve()


def _create_short_publish_workspace(
    workspace_base: Path,
    timestamp: str,
    random_provider,
) -> Path:
    compact_timestamp = "".join(
        character
        for character in timestamp
        if character.isalnum()
    )[-14:]

    for _attempt in range(32):
        random_part = random_provider.generate_string(
            length=12,
            variant=1,
        )
        workspace_path = workspace_base / (
            f"p_{compact_timestamp}_{random_part}"
        )

        try:
            workspace_path.mkdir(
                parents=False,
                exist_ok=False,
            )
            return workspace_path

        except FileExistsError:
            continue

        except OSError as error:
            raise RuntimeError(
                "Could not create the short DevBox publish workspace: "
                f"{workspace_path}"
            ) from error

    raise RuntimeError(
        "Could not allocate a unique short DevBox publish workspace."
    )


def build_context(request: PushRequest) -> PushContext:
    project_root = find_project_root(Path(__file__).resolve())
    tools_path = project_root / "platform" / "tools"
    random_provider = _load_module(
        "devbox_push_random_string_provider",
        tools_path / "random_string_provider.py",
    )
    timestamp_provider = _load_module(
        "devbox_push_timestamp_provider",
        tools_path / "timestamp_provider.py",
    )
    timestamp = timestamp_provider.generate_combined_timestamp([4, 14])
    workspace_base = _get_publish_workspace_base()
    temp_path = _create_short_publish_workspace(
        workspace_base=workspace_base,
        timestamp=timestamp,
        random_provider=random_provider,
    )
    root_dir = temp_path / "root_dir"
    assets_path = root_dir / "assets"
    return PushContext(
        project_root=project_root,
        temp_path=temp_path,
        root_dir=root_dir,
        repository_path=temp_path / "repository_work",
        docs_path=temp_path / "docs",
        assets_path=assets_path,
        documents_path=assets_path / "documents",
        pictures_path=assets_path / "pictures",
        database_file=root_dir / "resources" / "organization" / "devbox_db.r0b",
        source_database_file=project_root / "resources" / "organization" / "devbox_db.r0b",
        forms_file=root_dir / "resources" / "organization" / "doc_forms.r0b",
        timestamp=timestamp,
    )
