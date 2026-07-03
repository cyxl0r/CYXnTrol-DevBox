from pathlib import Path
import ctypes
import importlib.util
import os
import shutil
import stat
import sys
import time
import zipfile


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


def load_module_from_path(module_name: str, module_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, module_path)

    if spec is None or spec.loader is None:
        print(f"Could not load module: {module_path}")
        sys.exit(0)

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


random_string_provider_path = (
    projekt_root_path
    / "platform"
    / "tools"
    / "random_string_provider.py"
)

timestamp_provider_path = (
    projekt_root_path
    / "platform"
    / "tools"
    / "timestamp_provider.py"
)

if not random_string_provider_path.is_file():
    print("Random string provider not found.")
    sys.exit(0)

if not timestamp_provider_path.is_file():
    print("Timestamp provider not found.")
    sys.exit(0)

random_string_provider = load_module_from_path(
    "random_string_provider",
    random_string_provider_path,
)

timestamp_provider = load_module_from_path(
    "timestamp_provider",
    timestamp_provider_path,
)

random_value = random_string_provider.generate_string(
    length=64,
    variant=1,
)

timestamp_value = timestamp_provider.generate_combined_timestamp(
    variants=[4, 13],
    separator="_",
)

temp_path = Path(os.environ["TEMP"]) / f"{random_value}_{timestamp_value}"

finished_path = Path(os.environ["TEMP"]) / "output of snapshot"
finished_file = finished_path / "project_platform_proof_of_concept.zip"


def make_writable(path: str) -> None:
    try:
        os.chmod(path, stat.S_IWRITE)
    except Exception:
        pass


def remove_dir_until_gone(folder_path: Path) -> None:
    while folder_path.exists():
        try:
            shutil.rmtree(
                folder_path,
                onerror=lambda func, path, exc_info: (
                    make_writable(path),
                    func(path),
                ),
            )
        except Exception:
            time.sleep(0.25)
            continue

        if folder_path.exists():
            time.sleep(0.25)


def remove_file_until_gone(file_path: Path) -> None:
    while file_path.exists():
        try:
            make_writable(str(file_path))
            file_path.unlink()
        except FileNotFoundError:
            pass
        except Exception:
            time.sleep(0.25)
            continue

        if file_path.exists():
            time.sleep(0.25)


def remove_pycache_dirs(root_path: Path) -> None:
    pycache_dirs = [
        path
        for path in root_path.rglob("__pycache__")
        if path.is_dir()
    ]

    pycache_dirs.sort(
        key=lambda path: len(path.parts),
        reverse=True,
    )

    for pycache_dir in pycache_dirs:
        remove_dir_until_gone(pycache_dir)


def remove_png_and_graphic_items_files(root_path: Path) -> None:
    file_paths = [
        path
        for path in root_path.rglob("*")
        if path.is_file()
    ]

    for file_path in file_paths:
        if (
            file_path.suffix.lower() == ".png"
            or file_path.name.lower() == "graphic_items.r0b"
        ):
            try:
                file_path.unlink()
            except Exception as exc:
                print(f"Could not remove file: {file_path}")
                print(f"Reason: {type(exc).__name__}: {exc}")


def replace_large_files(
    root_path: Path,
    dummy_file_path: Path,
    max_file_size: int,
) -> None:
    for file_path in root_path.rglob("*"):
        if not file_path.is_file():
            continue

        try:
            file_size = file_path.stat().st_size
        except Exception:
            continue

        if file_size > max_file_size:
            try:
                file_path.unlink()
                shutil.copy2(dummy_file_path, file_path)
            except Exception as exc:
                print(f"Could not replace large file: {file_path}")
                print(f"Reason: {type(exc).__name__}: {exc}")


def zip_folder(source_folder: Path, zip_file_path: Path) -> None:
    with zipfile.ZipFile(
        zip_file_path,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as zip_file:
        for file_path in source_folder.rglob("*"):
            if file_path.is_file():
                archive_name = file_path.relative_to(source_folder)
                zip_file.write(file_path, archive_name)


def open_explorer_and_select_file(file_path: Path) -> None:
    file_path = file_path.resolve()

    if not file_path.is_file():
        print(f"Finished file not found: {file_path}")

        if file_path.parent.is_dir():
            os.startfile(str(file_path.parent))

        return

    ctypes.windll.shell32.ShellExecuteW(
        None,
        "open",
        "explorer.exe",
        f'/select,"{file_path}"',
        None,
        1,
    )


temp_path.mkdir(parents=True, exist_ok=False)

rootfiles_path = temp_path / "rootfiles"
rootfiles_path.mkdir(parents=True, exist_ok=False)

shutil.copytree(
    projekt_root_path,
    rootfiles_path,
    dirs_exist_ok=True,
)

remove_pycache_dirs(rootfiles_path)

remove_png_and_graphic_items_files(rootfiles_path)

dummy_file_path = temp_path / "dummy.file"
dummy_file_path.write_text(
    "dummy",
    encoding="utf-8",
)

max_file_size = 2 * 1024 * 1024

replace_large_files(
    root_path=rootfiles_path,
    dummy_file_path=dummy_file_path,
    max_file_size=max_file_size,
)

devbox_bat_path = (
    rootfiles_path
    / "resources"
    / "applications"
    / "devbox"
    / "devbox.bat"
)

devbox_exe_path = (
    rootfiles_path
    / "resources"
    / "applications"
    / "devbox"
    / "devbox.exe"
)

remove_file_until_gone(devbox_bat_path)

remove_file_until_gone(devbox_exe_path)

zip_file_path = temp_path / "zip.file"

zip_folder(
    source_folder=rootfiles_path,
    zip_file_path=zip_file_path,
)

if finished_path.exists():
    remove_dir_until_gone(finished_path)

finished_path.mkdir(parents=True, exist_ok=False)

shutil.copy2(
    zip_file_path,
    finished_file,
)

remove_dir_until_gone(temp_path)

open_explorer_and_select_file(finished_file)

sys.exit(0)