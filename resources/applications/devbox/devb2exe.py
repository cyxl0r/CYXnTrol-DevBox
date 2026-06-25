from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile

home_path = Path(__file__).resolve().parent
os.chdir(home_path)

current_path = home_path
projekt_root_path = None

while True:
    root_file = current_path / ".root"

    if root_file.is_file():
        content = root_file.read_text(encoding="utf-8").strip()

        if content == "project-root":
            projekt_root_path = current_path
            break

    parent_path = current_path.parent

    if parent_path == current_path:
        print("No project root found.")
        sys.exit(0)

    current_path = parent_path
    os.chdir(current_path)

compiler_script = (
    projekt_root_path
    / "resources"
    / "applications"
    / "devbox"
    / "functions"
    / "compile_to_exe.py"
)

launcher_script = (
    projekt_root_path
    / "resources"
    / "applications"
    / "devbox"
    / "functions"
    / "devbox_launcher.py"
)

icon_file = projekt_root_path / "resources" / "graphics" / "devbox.ico"
target_exe = home_path / "devbox.exe"
staging_exe = home_path / ".devbox_build_staging.exe"

python_exe = Path(sys.executable).resolve()

if python_exe.name.lower() == "pythonw.exe":
    python_exe = python_exe.with_name("python.exe")

if not python_exe.is_file() or python_exe.name.lower() != "python.exe":
    print(f"python.exe was not found: {python_exe}")
    sys.exit(1)

if not compiler_script.is_file():
    print(f"Compiler script not found: {compiler_script}")
    sys.exit(1)

if not launcher_script.is_file():
    print(f"DevBox launcher script not found: {launcher_script}")
    sys.exit(1)

if not icon_file.is_file():
    print(f"DevBox icon not found: {icon_file}")
    sys.exit(1)

temporary_output_path = Path(
    tempfile.mkdtemp(prefix="_devbox_compile_output_")
)

try:
    command = [
        str(python_exe),
        str(compiler_script),
        str(launcher_script),
        "--icon",
        str(icon_file),
        "--python",
        str(python_exe),
        "--output",
        str(temporary_output_path),
        "--output-mode",
        "folder",
    ]

    result = subprocess.run(
        command,
        cwd=str(projekt_root_path),
    )

    if result.returncode != 0:
        sys.exit(result.returncode)

    compiled_exe = temporary_output_path / "devbox_launcher.exe"

    if not compiled_exe.is_file():
        print(f"Compiled executable not found: {compiled_exe}")
        sys.exit(1)

    if staging_exe.exists():
        staging_exe.unlink()

    shutil.copy2(compiled_exe, staging_exe)
    os.replace(staging_exe, target_exe)

    print(f"DevBox executable created: {target_exe}")

finally:
    if staging_exe.exists():
        staging_exe.unlink()

    shutil.rmtree(temporary_output_path, ignore_errors=True)