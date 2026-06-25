#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from compile_to_exe_common import debug, debug_header, fail


def cs_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\r", "\\r").replace("\n", "\\n")
    return '"' + escaped + '"'


def create_csharp_source(local_script_name: str, original_script_path: str, python_path: str) -> str:
    return f"""
using System;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Windows.Forms;

internal static class Program
{{
    private static string LocalScriptName = {cs_string(local_script_name)};
    private static string OriginalScriptPath = {cs_string(original_script_path)};
    private static string ConfiguredPythonPath = {cs_string(python_path)};

    [STAThread]
    private static int Main(string[] args)
    {{
        try
        {{
            string exeDir = AppDomain.CurrentDomain.BaseDirectory;
            string localScriptPath = Path.GetFullPath(Path.Combine(exeDir, LocalScriptName));
            string scriptPath = File.Exists(localScriptPath) ? localScriptPath : OriginalScriptPath;
            string pythonPath = ResolvePythonPath(exeDir, ConfiguredPythonPath);

            if (!File.Exists(scriptPath))
            {{
                MessageBox.Show(
                    "Python launcher script was not found.\\n\\nLocal path:\\n" + localScriptPath + "\\n\\nFallback path:\\n" + OriginalScriptPath,
                    "Launcher error",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error
                );
                return 2;
            }}

            ProcessStartInfo psi = new ProcessStartInfo();
            psi.FileName = pythonPath;
            psi.WorkingDirectory = Path.GetDirectoryName(scriptPath);
            psi.UseShellExecute = false;
            psi.CreateNoWindow = true;
            psi.Arguments = QuoteArgument(scriptPath) + BuildForwardedArguments(args);
            Process.Start(psi);
            return 0;
        }}
        catch (Exception ex)
        {{
            MessageBox.Show(ex.ToString(), "Launcher error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            return 1;
        }}
    }}

    private static string ResolvePythonPath(string exeDir, string configuredPythonPath)
    {{
        if (String.IsNullOrWhiteSpace(configuredPythonPath))
            return "python.exe";
        if (configuredPythonPath.Equals("python.exe", StringComparison.OrdinalIgnoreCase))
            return "python.exe";
        if (configuredPythonPath.Equals("pythonw.exe", StringComparison.OrdinalIgnoreCase))
            throw new InvalidOperationException("pythonw.exe is forbidden by this launcher.");
        if (Path.IsPathRooted(configuredPythonPath))
            return configuredPythonPath;
        return Path.GetFullPath(Path.Combine(exeDir, configuredPythonPath));
    }}

    private static string BuildForwardedArguments(string[] args)
    {{
        if (args == null || args.Length == 0)
            return "";
        StringBuilder builder = new StringBuilder();
        foreach (string arg in args)
        {{
            builder.Append(" ");
            builder.Append(QuoteArgument(arg));
        }}
        return builder.ToString();
    }}

    private static string QuoteArgument(string arg)
    {{
        if (arg == null || arg.Length == 0)
            return "\\\"\\\"";
        bool needsQuotes = false;
        foreach (char c in arg)
        {{
            if (Char.IsWhiteSpace(c) || c == '\"')
            {{
                needsQuotes = true;
                break;
            }}
        }}
        if (!needsQuotes)
            return arg;
        StringBuilder builder = new StringBuilder();
        builder.Append('\"');
        int backslashCount = 0;
        foreach (char c in arg)
        {{
            if (c == '\\\\')
            {{
                backslashCount++;
            }}
            else if (c == '\"')
            {{
                builder.Append(new string('\\\\', backslashCount * 2 + 1));
                builder.Append('\"');
                backslashCount = 0;
            }}
            else
            {{
                builder.Append(new string('\\\\', backslashCount));
                builder.Append(c);
                backslashCount = 0;
            }}
        }}
        builder.Append(new string('\\\\', backslashCount * 2));
        builder.Append('\"');
        return builder.ToString();
    }}
}}
""".strip()


def compile_csharp(csc_path: Path, source_file: Path, output_exe: Path, icon_path: Path | None) -> None:
    debug_header("C# compilation")
    debug(f"Compiler: {csc_path}")
    debug(f"Source:   {source_file}")
    debug(f"Output:   {output_exe}")

    command = [
        str(csc_path),
        "/nologo",
        "/target:winexe",
        "/platform:anycpu",
        "/optimize+",
        "/reference:System.Windows.Forms.dll",
        f"/out:{str(output_exe)}",
    ]
    if icon_path is not None:
        command.append(f"/win32icon:{str(icon_path)}")
        debug(f"Icon:     {icon_path}")
    else:
        debug("Icon:     none")
    command.append(str(source_file))

    debug("Compiler command:")
    debug("  " + subprocess.list2cmdline(command))
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.stdout.strip():
        debug("Compiler stdout:")
        print(result.stdout.strip(), flush=True)
    if result.stderr.strip():
        debug("Compiler stderr:")
        print(result.stderr.strip(), file=sys.stderr, flush=True)

    debug(f"Compiler exit code: {result.returncode}")
    if result.returncode != 0:
        fail(f"C# compilation failed with exit code {result.returncode}.")
    if not output_exe.exists():
        fail(f"Compiler reported success, but output EXE does not exist: {output_exe}")
    debug(f"Compilation successful: {output_exe}")
    debug(f"EXE size: {output_exe.stat().st_size} bytes")
