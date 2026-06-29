from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from subscripts.main_gui_desknode_graphic_pack import (
    start_graphic_items_pack_build,
)
from subscripts.main_gui_desknode_symbol_categories import CategoryEditor
from subscripts.main_gui_desknode_symbol_storage import ensure_symbol_tables
from subscripts.main_gui_desknode_symbol_devices import DeviceEditor
from subscripts.main_gui_devbox_log import get_devbox_logger
from subscripts.main_gui_pages import add_status_and_log


LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")

PAGE_KEY = "desknode_symbol_management"


def build_desknode_symbol_management_view(
    studio,
    return_to_execution: Callable[[], None],
) -> QWidget:
    """Build the compact deskNode consumer-device symbol workspace."""
    page = QWidget()
    page.setObjectName("DeskNodeSymbolManagementView")

    layout = QVBoxLayout(page)
    layout.setContentsMargins(10, 12, 10, 10)
    layout.setSpacing(12)

    toolbar = QHBoxLayout()
    toolbar.setSpacing(10)

    back_button = QPushButton("Zurück")
    back_button.setObjectName("DeskNodeSymbolBackButton")
    back_button.setMinimumWidth(145)
    back_button.clicked.connect(
        lambda _checked=False: return_to_execution()
    )
    toolbar.addWidget(back_button)

    title = QLabel("Symbolverwaltung: deskNode")
    title.setObjectName("DeskNodeSymbolTitle")
    toolbar.addWidget(title)
    toolbar.addStretch(1)

    build_button = QPushButton("Build Items-Graphic-Pack")
    build_button.setObjectName("DeskNodeGraphicPackButton")
    build_button.setMinimumWidth(235)
    studio.desknode_graphic_pack_button = build_button
    build_button.clicked.connect(
        lambda _checked=False: start_graphic_items_pack_build(
            studio=studio,
            button=build_button,
        )
    )
    toolbar.addWidget(build_button)
    layout.addLayout(toolbar)

    notice = QLabel(
        "Gerätekategorien und Verbrauchergeräte werden hier über ihre "
        "Auswahlmenüs verwaltet. Neue Verbrauchergeräte benötigen genau "
        "eine PNG-Quelle."
    )
    notice.setObjectName("DeskNodeSymbolNotice")
    notice.setWordWrap(True)
    layout.addWidget(notice)

    selector_panel = QFrame()
    selector_panel.setObjectName("DeskNodeSymbolPanel")
    selector_layout = QVBoxLayout(selector_panel)
    selector_layout.setContentsMargins(14, 14, 14, 14)
    selector_layout.setSpacing(14)

    category_editor = CategoryEditor(studio)
    device_editor = DeviceEditor(studio)
    selector_layout.addWidget(category_editor)
    selector_layout.addWidget(device_editor)
    layout.addWidget(selector_panel)
    layout.addStretch(1)

    category_editor.categories_changed.connect(device_editor.reload)
    studio.desknode_symbol_refresh_controls = (
        category_editor.record_combo,
        category_editor.new_button,
        category_editor.edit_button,
        category_editor.delete_button,
        device_editor.record_combo,
        device_editor.new_button,
        device_editor.edit_button,
        device_editor.delete_button,
        build_button,
    )

    def reload_data() -> None:
        try:
            ensure_symbol_tables(studio)
            category_editor.reload()
            device_editor.reload()
        except Exception as error:
            message = f"Symbolverwaltung konnte nicht geladen werden: {error}"
            studio.set_status(message, "error", PAGE_KEY)
            studio.append_log(message, PAGE_KEY)
            LOGGER.warning("Symbol management reload failed.", str(error))

    page.reload_data = reload_data
    page.category_editor = category_editor
    page.device_editor = device_editor

    add_status_and_log(studio, layout, PAGE_KEY)
    return page
