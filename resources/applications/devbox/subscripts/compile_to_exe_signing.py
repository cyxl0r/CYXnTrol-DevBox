#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from compile_to_exe_common import debug, debug_header, fail
from compile_to_exe_discovery import find_signtool


def sign_executable(
    output_exe: Path,
    signtool_path: Path | None,
    cert_path: Path | None,
    cert_password: str | None,
    timestamp_url: str | None,
) -> None:
    debug_header("Code signing")
    resolved_signtool = signtool_path or find_signtool()
    if resolved_signtool is None:
        fail("Signing is enabled, but signtool.exe could not be found.")

    command = [str(resolved_signtool), "sign", "/fd", "SHA256"]
    if cert_path is not None:
        command.extend(["/f", str(cert_path)])
    if cert_password is not None:
        command.extend(["/p", cert_password])
    if timestamp_url:
        command.extend(["/tr", timestamp_url, "/td", "SHA256"])
    if cert_path is None:
        command.append("/a")
    command.append(str(output_exe))

    safe_command: list[str] = []
    skip_next = False
    for item in command:
        if skip_next:
            skip_next = False
            continue
        if item == "/p":
            safe_command.extend(["/p", "***"])
            skip_next = True
        else:
            safe_command.append(item)

    debug("signtool command:")
    debug("  " + subprocess.list2cmdline(safe_command))
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.stdout.strip():
        debug("signtool stdout:")
        print(result.stdout.strip(), flush=True)
    if result.stderr.strip():
        debug("signtool stderr:")
        print(result.stderr.strip(), file=sys.stderr, flush=True)

    debug(f"signtool exit code: {result.returncode}")
    if result.returncode != 0:
        fail(f"Code signing failed with exit code {result.returncode}.")
    debug("Code signing completed successfully.")
