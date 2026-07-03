from __future__ import annotations

import argparse
import importlib.util
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType


PROJECT_ROOT_ENV = "_CYXLABS_DEVBOX_PROJECT_ROOT_PATH"
PRODUCT_SLUG = "desknode"


@dataclass(frozen=True)
class PushRequest:
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
    source_database_file: Path
    forms_file: Path
    timestamp: str


def parse_request(argv: list[str] | None = None) -> PushRequest:
    parser = argparse.ArgumentParser(
        description="Prepare and push the deskNode repository publication state."
    )
    parser.add_argument("--product-slug", default=PRODUCT_SLUG)
    parser.add_argument("--commit-text", default="")
    parser.add_argument("--image", action="append", default=[])
    arguments = parser.parse_args(argv)
    product_slug = str(arguments.product_slug or "").strip().casefold()
    if product_slug != PRODUCT_SLUG:
        raise ValueError("This schema only supports the deskNode product.")
    images = [Path(value).expanduser().resolve() for value in arguments.image]
    return PushRequest(
        commit_text=str(arguments.commit_text or "").strip(),
        image_paths=images,
    )


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


def _workspace_base() -> Path:
    configured = os.environ.get("CYXLABS_DESKNODE_PUBLISH_TEMP_ROOT", "").strip()
    if configured:
        base = Path(configured).expanduser()
    else:
        base = Path(tempfile.gettempdir()).resolve() / "cyx"
    base.mkdir(parents=True, exist_ok=True)
    return base.resolve()


def _create_workspace(base: Path, timestamp: str, random_provider) -> Path:
    compact_timestamp = "".join(character for character in timestamp if character.isalnum())[-14:]
    for _attempt in range(32):
        token = random_provider.generate_string(length=12, variant=1)
        candidate = base / f"n_{compact_timestamp}_{token}"
        try:
            candidate.mkdir(parents=False, exist_ok=False)
            return candidate
        except FileExistsError:
            continue
    raise RuntimeError("Could not allocate a unique deskNode publish workspace.")


def build_context() -> PushContext:
    project_root = find_project_root(Path(__file__).resolve())
    tools_path = project_root / "platform" / "tools"
    random_provider = _load_module(
        "desknode_push_random_string_provider",
        tools_path / "random_string_provider.py",
    )
    timestamp_provider = _load_module(
        "desknode_push_timestamp_provider",
        tools_path / "timestamp_provider.py",
    )
    timestamp = timestamp_provider.generate_combined_timestamp([4, 14])
    temp_path = _create_workspace(_workspace_base(), timestamp, random_provider)
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
        source_database_file=project_root / "resources" / "organization" / "devbox_db.r0b",
        forms_file=project_root / "resources" / "organization" / "doc_forms.r0b",
        timestamp=timestamp,
    )
