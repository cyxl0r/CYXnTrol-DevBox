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
        sys.exit(1)

    current_path = parent_path
    os.chdir(current_path)


functions_path = (
    projekt_root_path
    / "resources"
    / "applications"
    / "devbox"
    / "functions"
)

create_devdbase_file = functions_path / "create_devdbase.py"
initializer_file = functions_path / "initialize_empty_application_projects.py"


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

    print(f"Running: {script_file}")

    process = subprocess.run(
        [str(get_python_executable()), str(script_file)],
        cwd=str(script_file.parent),
    )

    print(f"Finished: {script_file}")
    print(f"Return code: {process.returncode}")
    return int(process.returncode)


def main() -> int:
    print(f"projekt_root_path: {projekt_root_path}")

    database_return_code = run_script(create_devdbase_file)

    if database_return_code != 0:
        print("create_devdbase.py failed. Project initialization will not start.")
        return database_return_code

    initializer_return_code = run_script(initializer_file)

    if initializer_return_code != 0:
        print("initialize_empty_application_projects.py failed.")
        return initializer_return_code

    print("DevBox database update and empty-project initialization completed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
