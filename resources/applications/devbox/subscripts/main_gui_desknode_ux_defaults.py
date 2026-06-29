from __future__ import annotations

import re
from pathlib import Path

TABLE_NAME = "ux-deskNode"
PRODUCT_DIRECTORY_NAME = "deskNode"
DEFAULT_THEME_NAME = "Standard"
RGBA_PATTERN = re.compile(r"^[0-9a-fA-F]{8}$")
OUTLINE_STYLES = (
    "durchgezogen",
    "gestrichelt",
    "gepunktet",
    "doppelt",
    "keine",
)

COLOR_DEFAULTS = {
    "page_background_rgba": "02080c58",
    "panel_rgba": "030a0eaa",
    "input_rgba": "01070bcd",
    "button_rgba": "0082a0aa",
    "button_hover_rgba": "00a5becd",
    "button_pressed_rgba": "006e86dd",
    "button_running_rgba": "991723cd",
    "button_running_hover_rgba": "c01f2de1",
    "button_disabled_rgba": "0306088c",
    "outline_default_rgba": "00e4ffff",
    "outline_hover_rgba": "77fff7f5",
    "outline_running_rgba": "ff5d6df5",
    "outline_running_hover_rgba": "ffabb4fa",
    "outline_disabled_rgba": "2c3e4696",
    "status_rgba": "00000091",
    "log_rgba": "000000b2",
    "path_rgba": "00000096",
    "glow_on_rgba": "00e4ffff",
    "glow_off_rgba": "2c3e4696",
    "non_off_rgba": "00000000",
}

FONT_ROLES = (
    "headline",
    "section",
    "body",
    "button",
    "input",
    "status",
    "log",
)

FONT_DEFAULTS = {
    "headline": ("", "ffffffff", 13, 1, 0, 0),
    "section": ("", "d9f0f7ff", 10, 1, 0, 0),
    "body": ("", "b8d5ddff", 10, 0, 0, 0),
    "button": ("", "ffffffff", 10, 1, 0, 0),
    "input": ("", "eef8ffff", 10, 0, 0, 0),
    "status": ("", "d8e0e8ff", 17, 1, 0, 0),
    "log": ("", "d8e0e8ff", 9, 0, 0, 0),
}

SHAPE_DEFAULTS = {
    "panel_radius": 8,
    "button_radius": 8,
    "input_radius": 7,
    "outline_default_width": 1,
    "outline_running_width": 1,
    "outline_style": "durchgezogen",
}

DEFAULT_SETTINGS: dict[str, str | int] = {
    **COLOR_DEFAULTS,
    **SHAPE_DEFAULTS,
}

for _role, _values in FONT_DEFAULTS.items():
    _path, _rgba, _size, _bold, _italic, _underline = _values
    DEFAULT_SETTINGS.update(
        {
            f"{_role}_font_path": _path,
            f"{_role}_font_rgba": _rgba,
            f"{_role}_font_size": _size,
            f"{_role}_font_bold": _bold,
            f"{_role}_font_italic": _italic,
            f"{_role}_font_underline": _underline,
        }
    )


def is_valid_rgba(value: object) -> bool:
    return bool(RGBA_PATTERN.fullmatch(str(value or "").strip()))


def normalize_rgba(value: object) -> str:
    normalized = str(value or "").strip().lower()
    if not is_valid_rgba(normalized):
        raise ValueError("RGBA-Werte benötigen genau acht Hex-Zeichen.")
    return normalized


def normalize_font_path(value: object) -> str:
    path_text = str(value or "").strip().replace("\\", "/")
    if not path_text:
        return ""
    candidate = Path(path_text)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError("Schriftpfade müssen relativ zum Projektroot sein.")
    return candidate.as_posix()


def normalize_theme_name(value: object) -> str:
    theme_name = str(value or "").strip()
    if not theme_name:
        raise ValueError("Ein UX-Theme benötigt einen Namen.")
    if len(theme_name) > 80:
        raise ValueError("UX-Theme-Namen dürfen maximal 80 Zeichen lang sein.")
    if any(character in "\r\n\t" for character in theme_name):
        raise ValueError("UX-Theme-Namen dürfen keine Zeilenumbrüche enthalten.")
    return theme_name


def normalize_settings(values: dict[str, object]) -> dict[str, str | int]:
    normalized: dict[str, str | int] = {}
    for key, default_value in DEFAULT_SETTINGS.items():
        value = values.get(key, default_value)
        if key.endswith("_rgba"):
            normalized[key] = normalize_rgba(value)
        elif key.endswith("_font_path"):
            normalized[key] = normalize_font_path(value)
        elif key.endswith(("_font_bold", "_font_italic", "_font_underline")):
            normalized[key] = int(bool(value))
        elif key.endswith("_font_size"):
            number = int(value)
            if not 6 <= number <= 72:
                raise ValueError("Schriftgrößen müssen zwischen 6 und 72 liegen.")
            normalized[key] = number
        elif key.endswith("_radius"):
            number = int(value)
            if not 0 <= number <= 64:
                raise ValueError("Eckenradien müssen zwischen 0 und 64 liegen.")
            normalized[key] = number
        elif key.endswith("_width"):
            number = int(value)
            if not 0 <= number <= 12:
                raise ValueError("Konturstärken müssen zwischen 0 und 12 liegen.")
            normalized[key] = number
        elif key == "outline_style":
            style = str(value or "").strip().lower()
            if style not in OUTLINE_STYLES:
                raise ValueError("Ungültige Konturart.")
            normalized[key] = style
        else:
            normalized[key] = value
    return normalized
