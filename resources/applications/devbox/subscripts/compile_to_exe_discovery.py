#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import os
import shutil
from pathlib import Path

from compile_to_exe_common import debug


def find_csc() -> Path | None:
    debug("Searching for csc.exe...")
    from_path = shutil.which("csc")
    if from_path:
        path = Path(from_path).resolve()
        debug(f"csc.exe found in PATH: {path}")
        return path

    windir = Path(os.environ.get("WINDIR", r"C:\Windows"))
    candidates = [
        windir / "Microsoft.NET" / "Framework64" / "v4.0.30319" / "csc.exe",
        windir / "Microsoft.NET" / "Framework" / "v4.0.30319" / "csc.exe",
    ]
    for candidate in candidates:
        debug(f"Checking csc.exe candidate: {candidate}")
        if candidate.exists():
            debug(f"csc.exe found: {candidate}")
            return candidate
    debug("csc.exe was not found.")
    return None


def find_signtool() -> Path | None:
    debug("Searching for signtool.exe...")
    from_path = shutil.which("signtool")
    if from_path:
        path = Path(from_path).resolve()
        debug(f"signtool.exe found in PATH: {path}")
        return path

    roots: list[Path] = []
    program_files_x86 = os.environ.get("ProgramFiles(x86)")
    program_files = os.environ.get("ProgramFiles")
    if program_files_x86:
        roots.append(Path(program_files_x86) / "Windows Kits" / "10" / "bin")
    if program_files:
        roots.append(Path(program_files) / "Windows Kits" / "10" / "bin")

    for root in roots:
        debug(f"Scanning signtool root: {root}")
        if not root.exists():
            continue
        candidates = sorted(root.glob("**/signtool.exe"), reverse=True)
        for candidate in candidates:
            text = str(candidate).lower()
            if "\\x64\\" in text or "/x64/" in text:
                debug(f"signtool.exe found: {candidate}")
                return candidate
        for candidate in candidates:
            debug(f"signtool.exe found: {candidate}")
            return candidate

    debug("signtool.exe was not found.")
    return None
