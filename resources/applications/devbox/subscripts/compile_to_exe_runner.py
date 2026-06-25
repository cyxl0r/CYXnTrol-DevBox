#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import os
import sys
from pathlib import Path

import compile_to_exe_common as common
from compile_to_exe_arguments import parse_arguments, resolve_main_inputs, resolve_output_inputs, resolve_signing_inputs
from compile_to_exe_csharp import compile_csharp, create_csharp_source
from compile_to_exe_discovery import find_csc
from compile_to_exe_files import (
    copy_file_to_directory,
    create_temp_structure,
    export_final_compile,
    remove_python_sources_from_final_compile,
    robust_remove_tree,
)
from compile_to_exe_signing import sign_executable


def main() -> None:
    common.setup_logging()

    common.debug_header("Startup")
    common.debug(f"Log file:                             {common.log_file}")
    common.debug(f"Python executable running this tool: {sys.executable}")
    common.debug(f"Current working directory:          {Path.cwd()}")
    common.debug(f"Tool path:                          {common.tool_file()}")
    common.debug(f"Project root:                       {common.project_root()}")
    common.debug(f"Provider dir:                       {common.provider_dir()}")

    if os.name != "nt":
        common.fail("This tool currently supports Windows only.")

    args = parse_arguments()

    common.debug_header("Argument resolution")
    launcher_script, icon_path, python_exe = resolve_main_inputs(args)
    cert_path, signtool_path, cert_password = resolve_signing_inputs(args)
    export_mode, export_target = resolve_output_inputs(args)

    common.debug(f"Launcher script: {launcher_script}")
    common.debug(f"Icon path:       {icon_path if icon_path else 'none'}")
    common.debug(f"Python path:     {python_exe}")
    common.debug(f"Signing enabled: {args.sign}")
    common.debug(f"Certificate:     {cert_path if cert_path else 'none'}")
    common.debug(f"Timestamp URL:   {args.timestamp_url if args.sign else 'not used'}")
    common.debug(f"Output mode:     {export_mode}")
    common.debug(f"Output target:   {export_target if export_target else 'dialog'}")
    common.debug(f"Keep temp:       {args.keep_temp}")

    temp_path: Path | None = None

    try:
        common.debug_header("Temporary build setup")
        temp_path, work_dir, final_compile = create_temp_structure()
        cloned_launcher = copy_file_to_directory(launcher_script, work_dir, "launcher script")

        cloned_icon: Path | None = None
        if icon_path is not None:
            cloned_icon = copy_file_to_directory(icon_path, work_dir, "icon")

        cloned_cert: Path | None = None
        if cert_path is not None:
            cloned_cert = copy_file_to_directory(cert_path, work_dir, "certificate")

        common.debug_header("C# source generation")
        csharp_file = work_dir / f"{launcher_script.stem}_generated_launcher.cs"
        csharp_code = create_csharp_source(
            local_script_name=cloned_launcher.name,
            original_script_path=str(launcher_script),
            python_path=python_exe,
        )
        csharp_file.write_text(csharp_code, encoding="utf-8")
        common.debug(f"C# source generated: {csharp_file}")
        common.debug(f"C# source size: {csharp_file.stat().st_size} bytes")

        csc_path = find_csc()
        if csc_path is None:
            common.fail("csc.exe was not found. Install .NET Framework Developer Pack or Visual Studio Build Tools.")

        output_exe = final_compile / f"{launcher_script.stem}.exe"
        compile_csharp(csc_path=csc_path, source_file=csharp_file, output_exe=output_exe, icon_path=cloned_icon)

        common.debug_header("Final package file staging")
        common.debug("Launcher .py is intentionally not copied into final_compile.")
        common.debug("Only the generated EXE and future required runtime attachments are exported.")

        if args.sign:
            sign_executable(
                output_exe=output_exe,
                signtool_path=signtool_path,
                cert_path=cloned_cert,
                cert_password=cert_password,
                timestamp_url=args.timestamp_url,
            )
        else:
            common.debug_header("Code signing")
            common.debug("Signing skipped because --sign is not set.")

        remove_python_sources_from_final_compile(final_compile)
        final_export = export_final_compile(
            final_compile=final_compile,
            temp_path=temp_path,
            launcher_stem=launcher_script.stem,
            export_mode=export_mode,
            export_target=export_target,
        )

        common.debug_header("Done")
        common.debug("Build completed successfully.")
        common.debug(f"Final export: {final_export}")
        common.debug(f"Log file:     {common.log_file}")

    finally:
        if temp_path is not None:
            if getattr(args, "keep_temp", False):
                common.debug_header("Cleanup")
                common.debug(f"--keep-temp is set. Temporary directory preserved: {temp_path}")
            else:
                robust_remove_tree(temp_path)
