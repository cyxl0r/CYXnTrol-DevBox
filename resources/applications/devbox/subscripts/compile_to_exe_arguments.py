#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import getpass
import os
from pathlib import Path

from compile_to_exe_common import APP_NAME, debug, ensure_directory_writable, fail, normalize_path


def looks_like_icon(value: str) -> bool:
    return Path(value).suffix.lower() == ".ico"


def looks_like_python_exe(value: str) -> bool:
    return Path(value).name.lower() == "python.exe"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog=APP_NAME,
        description="Build a small native Windows launcher EXE for a Python launcher script.",
    )
    parser.add_argument("launcher_script", help="Required path to the Python launcher script.")
    parser.add_argument("optional_1", nargs="?", help="Optional .ico path or python.exe path.")
    parser.add_argument("optional_2", nargs="?", help="Optional python.exe path when optional_1 is an icon.")
    parser.add_argument("--icon", dest="icon_path", help="Optional .ico path.")
    parser.add_argument("--python", dest="python_exe", help="Optional python.exe path. pythonw.exe is forbidden.")
    parser.add_argument("--output", dest="output_path", help="Optional output path. If set, Save As is skipped.")
    parser.add_argument(
        "--output-mode",
        dest="output_mode",
        choices=["zip", "folder"],
        default=None,
        help="Output mode for --output. Default with --output is zip.",
    )
    parser.add_argument("--sign", action="store_true", help="Enable code signing after compilation.")
    parser.add_argument("--cert", dest="cert_path", help="Optional PFX certificate path for signtool.")
    parser.add_argument(
        "--timestamp-url",
        dest="timestamp_url",
        default="http://timestamp.digicert.com",
        help="Timestamp server URL for signtool.",
    )
    parser.add_argument("--signtool", dest="signtool_path", help="Optional path to signtool.exe.")
    parser.add_argument("--cert-password-env", dest="cert_password_env", help="Env var containing the PFX password.")
    parser.add_argument("--ask-cert-password", action="store_true", help="Ask interactively for the PFX password.")
    parser.add_argument("--keep-temp", action="store_true", help="Do not delete the temporary build directory.")
    return parser.parse_args()


def resolve_main_inputs(args: argparse.Namespace) -> tuple[Path, Path | None, str]:
    launcher_script = normalize_path(args.launcher_script)
    if not launcher_script.exists():
        fail(f"Launcher script not found: {launcher_script}")
    if not launcher_script.is_file():
        fail(f"Launcher script is not a file: {launcher_script}")
    if launcher_script.suffix.lower() != ".py":
        fail(f"Launcher script must be a .py file: {launcher_script}")

    icon_path: Path | None = normalize_path(args.icon_path) if args.icon_path else None
    python_exe = str(normalize_path(args.python_exe)) if args.python_exe else "python.exe"

    if args.optional_1:
        optional_1 = args.optional_1
        if looks_like_icon(optional_1):
            if icon_path is not None:
                fail("Icon was provided more than once.")
            icon_path = normalize_path(optional_1)
        elif looks_like_python_exe(optional_1):
            if args.python_exe:
                fail("Python executable was provided more than once.")
            python_exe = str(normalize_path(optional_1))
        else:
            fail("Second positional parameter must be either an .ico file or python.exe. pythonw.exe is forbidden.")

    if args.optional_2:
        if not looks_like_python_exe(args.optional_2):
            fail("Third positional parameter must be python.exe. pythonw.exe is forbidden.")
        if args.python_exe:
            fail("Python executable was provided more than once.")
        python_exe = str(normalize_path(args.optional_2))

    if icon_path is not None:
        if not icon_path.exists():
            fail(f"Icon not found: {icon_path}")
        if not icon_path.is_file():
            fail(f"Icon is not a file: {icon_path}")
        if icon_path.suffix.lower() != ".ico":
            fail(f"Icon must have .ico extension: {icon_path}")

    if python_exe.lower() != "python.exe":
        python_path = Path(python_exe)
        if not python_path.exists():
            fail(f"Python executable not found: {python_path}")
        if not python_path.is_file():
            fail(f"Python executable is not a file: {python_path}")
        if python_path.name.lower() != "python.exe":
            fail(f"Python executable must be python.exe. pythonw.exe is forbidden: {python_path}")

    return launcher_script, icon_path, python_exe


def resolve_signing_inputs(args: argparse.Namespace) -> tuple[Path | None, Path | None, str | None]:
    cert_path: Path | None = None
    signtool_path: Path | None = None
    cert_password: str | None = None

    if not args.sign:
        if args.cert_path or args.signtool_path or args.cert_password_env or args.ask_cert_password:
            fail("Signing options were provided, but --sign is not set.")
        return cert_path, signtool_path, cert_password

    if args.cert_path:
        cert_path = normalize_path(args.cert_path)
        if not cert_path.exists():
            fail(f"Certificate file not found: {cert_path}")
        if not cert_path.is_file():
            fail(f"Certificate path is not a file: {cert_path}")

    if args.signtool_path:
        signtool_path = normalize_path(args.signtool_path)
        if not signtool_path.exists():
            fail(f"signtool.exe not found: {signtool_path}")
        if not signtool_path.is_file():
            fail(f"signtool path is not a file: {signtool_path}")

    if args.cert_password_env:
        cert_password = os.environ.get(args.cert_password_env)
        if cert_password is None:
            fail(f"Environment variable not found or empty: {args.cert_password_env}")
        debug(f"Certificate password loaded from environment variable: {args.cert_password_env}")

    if args.ask_cert_password:
        if cert_password is not None:
            fail("Certificate password requested from both environment and interactive prompt.")
        cert_password = getpass.getpass("Certificate password: ")
        debug("Certificate password received from interactive prompt.")

    return cert_path, signtool_path, cert_password


def normalize_zip_output_path(path: Path) -> Path:
    if path.suffix.lower() == ".zip":
        return path
    if path.suffix:
        return Path(str(path) + ".zip")
    return path.with_suffix(".zip")


def resolve_output_inputs(args: argparse.Namespace) -> tuple[str, Path | None]:
    if args.output_path is None:
        if args.output_mode is not None:
            fail("--output-mode was provided, but --output is not set.")
        debug("No explicit output path provided. Save As dialog will be used.")
        return "dialog_zip", None

    mode = args.output_mode or "zip"
    raw_output = normalize_path(args.output_path)
    if mode == "zip":
        target_zip = normalize_zip_output_path(raw_output)
        if target_zip.exists() and target_zip.is_dir():
            fail(f"ZIP output path points to an existing directory: {target_zip}")
        ensure_directory_writable(target_zip.parent, "ZIP output parent")
        debug(f"Explicit ZIP output path resolved: {target_zip}")
        return "direct_zip", target_zip

    if mode == "folder":
        target_dir = raw_output
        if target_dir.exists() and not target_dir.is_dir():
            fail(f"Folder output path exists but is not a directory: {target_dir}")
        ensure_directory_writable(target_dir, "folder output")
        debug(f"Explicit folder output path resolved: {target_dir}")
        return "direct_folder", target_dir

    fail(f"Unsupported output mode: {mode}")
