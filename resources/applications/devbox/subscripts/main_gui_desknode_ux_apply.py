from __future__ import annotations

from PySide6.QtGui import QFontDatabase

from subscripts.main_gui_desknode_ux_fonts import resolve_font_path


OUTLINE_QSS = {
    "durchgezogen": "solid",
    "gestrichelt": "dashed",
    "gepunktet": "dotted",
    "doppelt": "double",
    "keine": "none",
}


def rgba_to_qss(value: str) -> str:
    normalized = str(value or "00000000").lower()
    red = int(normalized[0:2], 16)
    green = int(normalized[2:4], 16)
    blue = int(normalized[4:6], 16)
    alpha = int(normalized[6:8], 16)
    return f"rgba({red}, {green}, {blue}, {alpha})"


def font_family(studio, relative_path: str, fallback: str) -> str:
    if not relative_path:
        return fallback

    cache = getattr(studio, "desknode_ux_font_cache", None)
    if not isinstance(cache, dict):
        cache = {}
        studio.desknode_ux_font_cache = cache

    if relative_path in cache:
        return cache[relative_path]

    font_path = resolve_font_path(studio, relative_path)
    if font_path is None:
        cache[relative_path] = fallback
        return fallback

    font_id = QFontDatabase.addApplicationFont(str(font_path))
    families = QFontDatabase.applicationFontFamilies(font_id)
    family = families[0] if families else fallback
    cache[relative_path] = family
    return family


def font_qss(studio, settings: dict, role: str, fallback: str) -> str:
    family = font_family(
        studio,
        str(settings[f"{role}_font_path"]),
        fallback,
    ).replace('"', "")
    size = int(settings[f"{role}_font_size"])
    color = rgba_to_qss(str(settings[f"{role}_font_rgba"]))
    weight = "700" if int(settings[f"{role}_font_bold"]) else "400"
    italic = "italic" if int(settings[f"{role}_font_italic"]) else "normal"
    underline = "underline" if int(settings[f"{role}_font_underline"]) else "none"
    return (
        f'font-family: "{family}"; font-size: {size}pt; '
        f"color: {color}; font-weight: {weight}; "
        f"font-style: {italic}; text-decoration: {underline};"
    )


def desk_node_style_sheet(
    studio,
    settings: dict,
    root_selector: str,
) -> str:
    default_outline = rgba_to_qss(settings["outline_default_rgba"])
    hover_outline = rgba_to_qss(settings["outline_hover_rgba"])
    running_outline = rgba_to_qss(settings["outline_running_rgba"])
    running_hover_outline = rgba_to_qss(settings["outline_running_hover_rgba"])
    disabled_outline = rgba_to_qss(settings["outline_disabled_rgba"])
    outline_style = OUTLINE_QSS[str(settings["outline_style"])]
    default_width = int(settings["outline_default_width"])
    running_width = int(settings["outline_running_width"])
    panel_radius = int(settings["panel_radius"])
    button_radius = int(settings["button_radius"])
    input_radius = int(settings["input_radius"])
    page = rgba_to_qss(settings["page_background_rgba"])
    panel = rgba_to_qss(settings["panel_rgba"])
    input_color = rgba_to_qss(settings["input_rgba"])
    button = rgba_to_qss(settings["button_rgba"])
    button_hover = rgba_to_qss(settings["button_hover_rgba"])
    button_pressed = rgba_to_qss(settings["button_pressed_rgba"])
    button_running = rgba_to_qss(settings["button_running_rgba"])
    button_running_hover = rgba_to_qss(settings["button_running_hover_rgba"])
    button_disabled = rgba_to_qss(settings["button_disabled_rgba"])
    status = rgba_to_qss(settings["status_rgba"])
    log = rgba_to_qss(settings["log_rgba"])
    path = rgba_to_qss(settings["path_rgba"])

    return f"""
        {root_selector} {{ background: {page}; }}
        {root_selector} QLabel#HeaderLabel {{ {font_qss(studio, settings, 'headline', 'Segoe UI') } }}
        {root_selector} QLabel#Subtitle,
        {root_selector} QLabel#PathLabel {{ {font_qss(studio, settings, 'body', 'Segoe UI') } }}
        {root_selector} QLabel#PathLabel {{ background: {path}; border: {default_width}px {outline_style} {default_outline}; border-radius: {input_radius}px; padding: 7px; }}
        {root_selector} QFrame#DeskNodeVersionPanel {{ background: {panel}; border: {default_width}px {outline_style} {default_outline}; border-radius: {panel_radius}px; }}
        {root_selector} QPushButton#DeskNodeExecuteButton,
        {root_selector} QPushButton#DeskNodeVersionButton,
        {root_selector} QPushButton#DeskNodeUxDesignButton,
        {root_selector} QPushButton#DeskNodeUxBackButton {{ {font_qss(studio, settings, 'button', 'Segoe UI') } background: {button}; border: {default_width}px {outline_style} {default_outline}; border-radius: {button_radius}px; padding-left: 16px; padding-right: 16px; }}
        {root_selector} QPushButton#DeskNodeExecuteButton:hover,
        {root_selector} QPushButton#DeskNodeVersionButton:hover,
        {root_selector} QPushButton#DeskNodeUxDesignButton:hover,
        {root_selector} QPushButton#DeskNodeUxBackButton:hover {{ background: {button_hover}; border-color: {hover_outline}; }}
        {root_selector} QPushButton#DeskNodeExecuteButton:pressed,
        {root_selector} QPushButton#DeskNodeVersionButton:pressed,
        {root_selector} QPushButton#DeskNodeUxDesignButton:pressed,
        {root_selector} QPushButton#DeskNodeUxBackButton:pressed {{ background: {button_pressed}; }}
        {root_selector} QPushButton#DeskNodeExecuteButton[running="true"] {{ background: {button_running}; border: {running_width}px {outline_style} {running_outline}; }}
        {root_selector} QPushButton#DeskNodeExecuteButton[running="true"]:hover {{ background: {button_running_hover}; border-color: {running_hover_outline}; }}
        {root_selector} QPushButton#DeskNodeExecuteButton:disabled,
        {root_selector} QPushButton#DeskNodeVersionButton:disabled {{ background: {button_disabled}; border-color: {disabled_outline}; }}
        {root_selector} QLineEdit#DeskNodeVersionInput {{ {font_qss(studio, settings, 'input', 'Segoe UI') } background: {input_color}; border: {default_width}px {outline_style} {default_outline}; border-radius: {input_radius}px; padding: 4px 9px; }}
        {root_selector} QLabel#StatusPanel {{ {font_qss(studio, settings, 'status', 'Segoe UI') } background: {status}; border: {default_width}px {outline_style} {default_outline}; border-radius: {panel_radius}px; padding: 8px; }}
        {root_selector} QTextEdit#LogBox {{ {font_qss(studio, settings, 'log', 'Consolas') } background: {log}; border: {default_width}px {outline_style} {default_outline}; border-radius: {panel_radius}px; }}
        {root_selector} QLabel#DeskNodePreviewSection {{ {font_qss(studio, settings, 'section', 'Segoe UI') } }}
    """


def apply_desknode_ux_settings(studio, settings: dict) -> None:
    execution_view = getattr(studio, "desknode_execution_view", None)

    if execution_view is not None:
        execution_view.setStyleSheet(
            desk_node_style_sheet(
                studio,
                settings,
                "QWidget#DeskNodeExecutionView",
            )
        )

    studio.desknode_ux_settings = dict(settings)


def apply_preview_ux_settings(studio, preview, settings: dict) -> None:
    preview.setStyleSheet(
        desk_node_style_sheet(
            studio,
            settings,
            "QFrame#DeskNodeUxPreview",
        )
    )
