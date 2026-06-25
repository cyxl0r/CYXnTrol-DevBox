#!/usr/bin/env python3
# -*- coding: utf-8 -*-

r"""
Schlanker Einstiegspunkt für den DevBox-Compiler.

Relative Lage im Projekt:
    <projektordner>\resources\applications\devbox\functions\compile_to_exe.py

Ausgelagerte Module:
    <projektordner>\resources\applications\devbox\subscripts\compile_to_exe_*.py

Provider:
    <projektordner>\platform\tools\random_string_provider.py
    <projektordner>\platform\tools\timestamp_provider.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _tool_file() -> Path:
    return Path(__file__).resolve()


def _project_root(tool_file: Path) -> Path:
    # compile_to_exe.py liegt unter:
    # <root>/resources/applications/devbox/functions/compile_to_exe.py
    try:
        return tool_file.parents[4]
    except IndexError:
        return tool_file.parent


def _prepare_import_paths() -> tuple[Path, Path, Path]:
    tool_file = _tool_file()
    project_root = _project_root(tool_file)
    devbox_dir = tool_file.parent.parent
    subscripts_dir = devbox_dir / "subscripts"
    provider_dir = project_root / "platform" / "tools"

    os.environ["CYXLABS_COMPILE_TO_EXE_TOOL_FILE"] = str(tool_file)
    os.environ["CYXLABS_COMPILE_TO_EXE_PROJECT_ROOT"] = str(project_root)
    os.environ["CYXLABS_COMPILE_TO_EXE_SUBSCRIPTS"] = str(subscripts_dir)
    os.environ["CYXLABS_COMPILE_TO_EXE_PROVIDER_DIR"] = str(provider_dir)

    for path in (subscripts_dir, provider_dir):
        text = str(path)
        if text not in sys.path:
            sys.path.insert(0, text)

    return project_root, subscripts_dir, provider_dir


def main() -> int:
    _prepare_import_paths()
    from compile_to_exe_runner import main as runner_main

    runner_main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
