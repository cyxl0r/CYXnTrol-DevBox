from pathlib import Path
import sys
import tempfile
import importlib.util
import shutil
import os
import zipfile
import stat
import subprocess


rnd_str_prvdr = "random_string_provider.py"
tmp_stmp_prvdr = "timestamp_provider.py"


current_file_path = Path(__file__).resolve()
i_am = current_file_path.stem
my_location_path = current_file_path.parent
searched_filnames = i_am.replace("to_ai_", "").replace("_snapshoter", "")

log_file = Path(tempfile.gettempdir()) / f"{i_am}_snapshot_error.log"


def log(message: str) -> None:
    try:
        with log_file.open("a", encoding="utf-8") as file:
            file.write(f"{message}\n")
    except Exception:
        pass


def fail(message: str) -> None:
    log(f"FEHLER: {message}")
    sys.exit(1)


def sanitize_filename_part(value: str) -> str:
    forbidden_chars = '<>:"/\\|?*'

    cleaned_value = str(value).strip()

    for forbidden_char in forbidden_chars:
        cleaned_value = cleaned_value.replace(forbidden_char, "-")

    cleaned_value = cleaned_value.replace(" ", "_")

    if not cleaned_value:
        fail("Leerer Dateinamen-Bestandteil erhalten.")

    return cleaned_value


def find_project_root(start_path: Path) -> Path:
    check_path = start_path

    while True:
        root_marker_file = check_path / ".root"

        if root_marker_file.is_file():
            try:
                marker_content = root_marker_file.read_text(encoding="utf-8").strip()
            except Exception:
                marker_content = ""

            if marker_content == "project-root":
                return check_path

        if check_path == check_path.parent:
            fail("Projektroot wurde nicht gefunden.")

        check_path = check_path.parent


def find_file_in_project(project_root_path: Path, filename: str) -> Path:
    try:
        for found_file in project_root_path.rglob(filename):
            if found_file.is_file():
                return found_file.resolve()
    except Exception as error:
        fail(f"Dateisuche fehlgeschlagen: {filename} | {error}")

    fail(f"Datei wurde nicht gefunden: {filename}")


def load_python_module(module_name: str, module_file: Path):
    try:
        spec = importlib.util.spec_from_file_location(module_name, module_file)

        if spec is None or spec.loader is None:
            raise ImportError(f"Spec/Loader ungültig: {module_file}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    except Exception as error:
        fail(f"Modul konnte nicht geladen werden: {module_file} | {error}")


def get_random_part(random_string_provider, length: int) -> str:
    try:
        return str(random_string_provider.generate_string(length=length, variant=1))
    except Exception as error:
        fail(f"Random-String konnte nicht erzeugt werden. Länge: {length} | {error}")


def get_timestamp_from_provider(timestamp_provider) -> str:
    timestamp_function = getattr(
        timestamp_provider,
        "generate_combined_timestamp",
        None,
    )

    if not callable(timestamp_function):
        fail(
            "Timestamp-Provider stellt keine Funktion "
            "'generate_combined_timestamp' bereit."
        )

    try:
        timestamp_value = timestamp_function(
            variants=[4, 13],
            separator="_",
        )
    except TypeError:
        try:
            timestamp_value = timestamp_function(
                [4, 13],
                "_",
            )
        except Exception as error:
            fail(f"Zeitstempel konnte nicht beim Provider bestellt werden: {error}")
    except Exception as error:
        fail(f"Zeitstempel konnte nicht beim Provider bestellt werden: {error}")

    if timestamp_value is None:
        fail("Timestamp-Provider hat keinen Zeitstempel zurückgegeben.")

    timestamp_part = sanitize_filename_part(timestamp_value)

    if not timestamp_part:
        fail("Timestamp-Provider hat einen leeren Zeitstempel zurückgegeben.")

    return timestamp_part


def remove_readonly_handler(function, path, exc_info):
    try:
        os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
        function(path)
    except Exception:
        pass


def ensure_removed_dir(dir_path: Path) -> None:
    while dir_path.exists():
        try:
            if dir_path.is_dir():
                shutil.rmtree(dir_path, onerror=remove_readonly_handler)
            else:
                dir_path.unlink()
        except Exception as error:
            log(f"Ordner konnte noch nicht gelöscht werden: {dir_path} | {error}")

        if dir_path.exists():
            time.sleep(0.2)


def ensure_removed_file(file_path: Path) -> None:
    while file_path.exists():
        try:
            if file_path.is_file() or file_path.is_symlink():
                try:
                    os.chmod(file_path, stat.S_IWRITE | stat.S_IREAD)
                except Exception:
                    pass

                file_path.unlink()

            elif file_path.is_dir():
                shutil.rmtree(file_path, onerror=remove_readonly_handler)

        except Exception as error:
            log(f"Datei konnte noch nicht gelöscht werden: {file_path} | {error}")

        if file_path.exists():
            time.sleep(0.2)


def zip_directory_max_ratio(source_dir: Path, target_zip_file: Path) -> None:
    try:
        if target_zip_file.exists():
            ensure_removed_file(target_zip_file)

        files_to_zip = [
            found_file
            for found_file in source_dir.rglob("*")
            if found_file.is_file()
        ]

        files_to_zip.sort(
            key=lambda file_path: str(file_path.relative_to(source_dir)).lower()
        )

        with zipfile.ZipFile(
            target_zip_file,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
        ) as zip_file:
            for found_file in files_to_zip:
                relative_file_path = found_file.relative_to(source_dir)
                zip_file.write(
                    found_file,
                    relative_file_path.as_posix(),
                )

        if not target_zip_file.is_file():
            fail(f"Temporäres ZIP wurde nicht erzeugt: {target_zip_file}")

        if target_zip_file.stat().st_size <= 0:
            fail(f"Temporäres ZIP ist leer: {target_zip_file}")

    except Exception as error:
        fail(f"ZIP-Erstellung fehlgeschlagen: {target_zip_file} | {error}")


def open_explorer_and_select_file(file_path: Path) -> None:
    try:
        if not file_path.is_file():
            fail(f"Explorer-Zieldatei existiert nicht: {file_path}")

        command = f'explorer.exe /select,"{file_path}"'
        subprocess.Popen(command)

    except Exception as error:
        log(f"Explorer-Auswahl fehlgeschlagen: {error}")

        try:
            os.startfile(file_path.parent)
        except Exception as second_error:
            fail(f"Explorer konnte nicht geöffnet werden: {second_error}")


def main() -> None:
    log("Snapshot startet.")

    projekt_root_path = find_project_root(my_location_path.parent)

    rnd_str_prvdr_file = find_file_in_project(
        projekt_root_path,
        rnd_str_prvdr,
    )

    tmp_stmp_prvdr_file = find_file_in_project(
        projekt_root_path,
        tmp_stmp_prvdr,
    )

    random_string_provider = load_python_module(
        "random_string_provider",
        rnd_str_prvdr_file,
    )

    timestamp_provider = load_python_module(
        "timestamp_provider",
        tmp_stmp_prvdr_file,
    )

    random_part_6 = get_random_part(random_string_provider, 6)
    random_part_5 = get_random_part(random_string_provider, 5)
    random_part_7 = get_random_part(random_string_provider, 7)

    temp_path = Path(tempfile.gettempdir()) / (
        f"{random_part_6}_{random_part_5}_{random_part_7}"
    )

    try:
        temp_path.mkdir(parents=True, exist_ok=False)
    except Exception as error:
        fail(
            f"Temp-Arbeitsordner konnte nicht erstellt werden: "
            f"{temp_path} | {error}"
        )

    search_pattern = f"*{searched_filnames}*.py"

    try:
        for source_file in projekt_root_path.rglob(search_pattern):
            if not source_file.is_file():
                continue

            relative_file_path = source_file.relative_to(projekt_root_path)
            target_file = temp_path / relative_file_path

            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, target_file)

    except Exception as error:
        fail(f"Snapshot-Dateien konnten nicht kopiert werden: {error}")

    try:
        os.chdir(temp_path)

        exact_i_am_filename = f"{i_am}.py"

        for file_to_delete in temp_path.rglob(exact_i_am_filename):
            if file_to_delete.is_file():
                file_to_delete.unlink()

    except Exception as error:
        fail(f"Eigenes Snapshot-Skript konnte nicht entfernt werden: {error}")

    try:
        os.chdir(temp_path)

        pycache_dirs = [
            found_dir
            for found_dir in temp_path.rglob("__pycache__")
            if found_dir.is_dir()
        ]

        for pycache_dir in pycache_dirs:
            shutil.rmtree(pycache_dir, onerror=remove_readonly_handler)

    except Exception as error:
        fail(f"__pycache__ konnte nicht entfernt werden: {error}")

    old_dir_file = temp_path / "old_dir.md"

    try:
        files_for_snapshot = [
            found_file
            for found_file in temp_path.rglob("*")
            if found_file.is_file()
            and found_file.resolve() != old_dir_file.resolve()
        ]

        files_for_snapshot.sort(
            key=lambda file_path: str(file_path.relative_to(temp_path)).lower()
        )

        old_dir_lines = [
            "# old_dir",
            "",
            "Root: `<project-root>`",
            "",
            "```text",
            "<project-root>/",
        ]

        for found_file in files_for_snapshot:
            relative_file_path = found_file.relative_to(temp_path)
            old_dir_lines.append(f"    {relative_file_path.as_posix()}")

        old_dir_lines.extend(
            [
                "```",
                "",
            ]
        )

        old_dir_file.write_text(
            "\n".join(old_dir_lines),
            encoding="utf-8",
        )

    except Exception as error:
        fail(f"old_dir.md konnte nicht geschrieben werden: {error}")

    chatgpt_order_file = temp_path / "chatgpt_order.md"

    try:
        chatgpt_order_text = """# ChatGPT Order

Hello ChatGPT,

this is the current snapshot.

Please carry out the changes, modifications, and extensions exactly as previously discussed.

If any files appear to be obsolete, briefly ask whether it is acceptable to delete them before removing them.

Remove this instruction.

Ignore `old_dir.md`. I need this file again exactly as it is, unchanged and unedited.

Package your new version together with `old_dir.md` into a ZIP archive.

Use the filename of the ZIP archive I sent you as the basis for the new ZIP filename.

Update the timestamp in the filename and replace the string `snapshot` with `implement_it`.
"""

        chatgpt_order_file.write_text(
            chatgpt_order_text,
            encoding="utf-8",
        )

    except Exception as error:
        fail(f"chatgpt_order.md konnte nicht geschrieben werden: {error}")

    temp_zip_file = Path(tempfile.gettempdir()) / f"{random_part_6}.{random_part_7}"

    zip_directory_max_ratio(
        temp_path,
        temp_zip_file,
    )

    output_dir = Path(tempfile.gettempdir()) / "output of snapshot"

    if output_dir.exists():
        ensure_removed_dir(output_dir)

    try:
        output_dir.mkdir(parents=True, exist_ok=False)
    except Exception as error:
        fail(f"Output-Ordner konnte nicht erstellt werden: {output_dir} | {error}")

    timestamp_part = get_timestamp_from_provider(timestamp_provider)

    final_zip_file = output_dir / f"{searched_filnames}_snapshot_{timestamp_part}.zip"

    try:
        shutil.copy2(
            temp_zip_file,
            final_zip_file,
        )
    except Exception as error:
        fail(f"Temporäres ZIP konnte nicht in den Output-Ordner kopiert werden: {error}")

    if not final_zip_file.is_file():
        fail(f"Finales ZIP existiert nach Kopieren nicht: {final_zip_file}")

    if final_zip_file.stat().st_size <= 0:
        fail(f"Finales ZIP ist leer: {final_zip_file}")

    ensure_removed_file(temp_zip_file)

    open_explorer_and_select_file(final_zip_file)

    log(f"Snapshot erfolgreich erstellt: {final_zip_file}")


if __name__ == "__main__":
    main()