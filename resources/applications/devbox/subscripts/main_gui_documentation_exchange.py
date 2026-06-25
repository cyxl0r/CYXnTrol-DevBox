from __future__ import annotations

from subscripts.main_gui_devbox_log import get_devbox_logger
LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")


import importlib.util
import os
import re
import shutil
import stat
import subprocess
import tempfile
import time
import unicodedata
import zipfile
from pathlib import Path, PurePosixPath


class DocumentationExchangeError(RuntimeError):
    pass


def document_product_key(product_name: str) -> str:
    normalized = unicodedata.normalize("NFKD", str(product_name))
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    result = re.sub(r"[^a-z0-9]+", "_", ascii_value.lower()).strip("_")
    if not result:
        raise DocumentationExchangeError("Der Produktname ergibt keinen gültigen Dokumentationsschlüssel.")
    return result


def validate_document_field_name(field_name: str) -> str:
    result = str(field_name).strip()
    if not re.fullmatch(r"[a-z][a-z0-9_]*", result):
        raise DocumentationExchangeError(
            "Dokumentfeld ist kein gültiger Dateiname: "
            f"{field_name!r}. Erlaubt sind Kleinbuchstaben, Ziffern und Unterstriche."
        )
    return result


def load_python_module(module_name: str, module_file: Path):
    spec = importlib.util.spec_from_file_location(module_name, module_file)
    if spec is None or spec.loader is None:
        raise DocumentationExchangeError(f"Modul konnte nicht geladen werden: {module_file}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def find_provider_file(project_root_path: Path, filename: str) -> Path:
    preferred_file = project_root_path / "platform" / "tools" / filename
    if preferred_file.is_file():
        return preferred_file

    files = sorted(
        (file for file in project_root_path.rglob(filename) if file.is_file()),
        key=lambda file: str(file).lower(),
    )
    if files:
        return files[0]
    raise DocumentationExchangeError(f"Provider-Datei nicht gefunden: {filename}")


def provider_timestamp(project_root_path: Path) -> str:
    provider_file = find_provider_file(project_root_path, "timestamp_provider.py")
    provider = load_python_module("devbox_documentation_timestamp_provider", provider_file)
    function = getattr(provider, "generate_combined_timestamp", None)
    if not callable(function):
        raise DocumentationExchangeError("timestamp_provider.py stellt generate_combined_timestamp nicht bereit.")

    try:
        value = function(variants=[4, 13], separator="_")
    except TypeError:
        value = function([4, 13], "_")
    except Exception as exc:
        raise DocumentationExchangeError(f"Zeitstempel konnte nicht erzeugt werden: {exc}") from exc

    value = str(value or "").strip()
    if not re.fullmatch(r"[A-Za-z0-9_-]+", value):
        raise DocumentationExchangeError("Zeitstempel enthält ungültige Zeichen.")
    return value


def provider_random_part(project_root_path: Path, length: int) -> str:
    provider_file = find_provider_file(project_root_path, "random_string_provider.py")
    provider = load_python_module("devbox_documentation_random_provider", provider_file)
    function = getattr(provider, "generate_string", None)
    if not callable(function):
        raise DocumentationExchangeError("random_string_provider.py stellt generate_string nicht bereit.")

    try:
        value = function(length=length, variant=1)
    except Exception as exc:
        raise DocumentationExchangeError(f"Zufallszeichenfolge konnte nicht erzeugt werden: {exc}") from exc

    value = str(value or "").strip()
    if len(value) != length or not value.isalnum():
        raise DocumentationExchangeError("Zufallszeichenfolge des Providers ist ungültig.")
    return value


def create_temp_workspace(project_root_path: Path) -> Path:
    parts = [
        provider_random_part(project_root_path, 6),
        provider_random_part(project_root_path, 5),
        provider_random_part(project_root_path, 7),
    ]
    workspace = Path(tempfile.gettempdir()) / "_".join(parts)
    try:
        workspace.mkdir(parents=True, exist_ok=False)
    except Exception as exc:
        raise DocumentationExchangeError(
            f"Temporärer Dokumentationsbereich konnte nicht erstellt werden: {workspace} | {exc}"
        ) from exc
    return workspace


def readonly_remove_handler(function, path, _exc_info) -> None:
    try:
        os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
        function(path)
    except Exception:
        pass


def remove_path(path: Path) -> bool:
    target = Path(path)
    for _ in range(12):
        if not target.exists():
            return True
        try:
            if target.is_dir() and not target.is_symlink():
                shutil.rmtree(target, onerror=readonly_remove_handler)
            else:
                os.chmod(target, stat.S_IWRITE | stat.S_IREAD)
                target.unlink()
        except Exception:
            time.sleep(0.2)
    return not target.exists()


def write_zip(source_dir: Path, target_zip: Path) -> None:
    if target_zip.exists() and not remove_path(target_zip):
        raise DocumentationExchangeError(f"Bestehende ZIP kann nicht überschrieben werden: {target_zip}")

    files = sorted(
        (file for file in source_dir.rglob("*") if file.is_file()),
        key=lambda file: file.relative_to(source_dir).as_posix().lower(),
    )
    if not files:
        raise DocumentationExchangeError("Der Dokumentations-Snapshot enthält keine Dateien.")

    try:
        with zipfile.ZipFile(
            target_zip,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
        ) as archive:
            for file in files:
                archive.write(file, file.relative_to(source_dir).as_posix())
    except Exception as exc:
        raise DocumentationExchangeError(f"ZIP-Erstellung fehlgeschlagen: {exc}") from exc

    if not target_zip.is_file() or target_zip.stat().st_size <= 0:
        raise DocumentationExchangeError(f"ZIP wurde nicht korrekt erzeugt: {target_zip}")


def output_snapshot_directory() -> Path:
    directory = Path(tempfile.gettempdir()) / "output of snapshot"

    while directory.exists():
        if remove_path(directory):
            break
        time.sleep(0.2)

    try:
        directory.mkdir(parents=True, exist_ok=False)
    except Exception as exc:
        raise DocumentationExchangeError(
            f"Snapshot-Ausgabeordner konnte nicht erstellt werden: {directory} | {exc}"
        ) from exc

    return directory


def open_explorer_and_select_file(file_path: Path) -> None:
    if not file_path.is_file():
        raise DocumentationExchangeError(f"Snapshot-Datei wurde nicht gefunden: {file_path}")
    try:
        subprocess.Popen(f'explorer.exe /select,"{file_path}"')
    except Exception:
        try:
            os.startfile(file_path.parent)
        except Exception as exc:
            raise DocumentationExchangeError(f"Explorer konnte nicht geöffnet werden: {exc}") from exc


def downloads_directory() -> Path:
    user_profile = os.environ.get("USERPROFILE", "").strip()
    base_path = Path(user_profile).expanduser() if user_profile else Path.home()
    return base_path / "Downloads"


def archive_member_path(name: str) -> PurePosixPath:
    path = PurePosixPath(name)
    if not name or path.is_absolute() or ".." in path.parts:
        raise DocumentationExchangeError(f"Unsicherer ZIP-Pfad: {name!r}")
    if any(part in {"", "."} for part in path.parts):
        raise DocumentationExchangeError(f"Ungültiger ZIP-Pfad: {name!r}")
    return path


def is_zip_symlink(info: zipfile.ZipInfo) -> bool:
    mode = (info.external_attr >> 16) & 0o170000
    return mode == stat.S_IFLNK
