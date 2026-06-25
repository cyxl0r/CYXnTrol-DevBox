from pathlib import Path
import os
import subprocess
import sys


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


create_devdbase_file = (
    projekt_root_path
    / "resources"
    / "applications"
    / "devbox"
    / "functions"
    / "create_devdbase.py"
)

folder_builder_file = (
    projekt_root_path
    / "resources"
    / "applications"
    / "devbox"
    / "functions"
    / "folder_builder.py"
)


def get_python_executable() -> Path:
    executable_path = Path(sys.executable)

    if executable_path.name.lower() == "pythonw.exe":
        python_exe = executable_path.with_name("python.exe")

        if python_exe.is_file():
            return python_exe

    return executable_path


def run_script(script_file: Path) -> int:
    if not script_file.is_file():
        print(f"Script not found: {script_file}")
        return 1

    python_executable = get_python_executable()

    print(f"Running: {script_file}")

    process = subprocess.run(
        [
            str(python_executable),
            str(script_file),
        ],
        cwd=str(script_file.parent),
    )

    print(f"Finished: {script_file}")
    print(f"Return code: {process.returncode}")

    return int(process.returncode)


def main() -> int:
    print(f"projekt_root_path: {projekt_root_path}")

    first_return_code = run_script(create_devdbase_file)

    if first_return_code != 0:
        print("create_devdbase.py failed. folder_builder.py will not be started.")
        return first_return_code

    second_return_code = run_script(folder_builder_file)

    if second_return_code != 0:
        print("folder_builder.py failed.")
        return second_return_code

    print("DevBox database and folder structure update completed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())