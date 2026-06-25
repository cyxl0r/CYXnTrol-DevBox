from __future__ import annotations

from collections.abc import Callable

from subscripts.main_gui_devbox_log import get_devbox_logger
LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")


from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QStackedLayout,
    QVBoxLayout,
)

from subscripts.main_gui_documentation_data import DocumentationDataForm
from subscripts.main_gui_global_app_structure import GlobalAppFolderStructureForm
from subscripts.main_gui_product_data import ProductDataForm
from subscripts.main_gui_roof_data import RoofDataForm


SectionFactory = Callable[[], QFrame]


class StructureSettingsPanel(QFrame):
    """Structure-workshop navigation with compact and full display modes."""

    def __init__(self, studio) -> None:
        super().__init__()
        self.studio = studio
        self.content_host: QFrame | None = None
        self.navigation_button_layout: QVBoxLayout | None = None
        self.workshop_button_layout: QHBoxLayout | None = None
        self.view_stack: QStackedLayout | None = None
        self.navigation_view: QFrame | None = None
        self.workshop_view: QFrame | None = None
        self.section_buttons: dict[str, QPushButton] = {}
        self.active_panel = ""
        self.display_mode = "navigation"
        self.section_definitions: list[tuple[str, str, SectionFactory]] = [
            (
                "roof",
                "Dach-Daten",
                lambda: RoofDataForm(self.studio.project_root_path),
            ),
            (
                "product",
                "Produkt-Daten",
                lambda: ProductDataForm(self.studio.project_root_path),
            ),
            (
                "documentation",
                "Dokumentationen",
                lambda: DocumentationDataForm(self.studio.project_root_path),
            ),
            (
                "global_app_structure",
                "Globale App-Ordnerstruktur",
                lambda: GlobalAppFolderStructureForm(self.studio.project_root_path),
            ),
        ]
        self.setObjectName("StructureSettingsPanel")
        self.setMinimumWidth(0)
        self.build_ui()

    def build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(0)

        self.view_stack = QStackedLayout()
        layout.addLayout(self.view_stack, 1)

        self.navigation_view = self.build_navigation_view()
        self.workshop_view = self.build_workshop_view()
        self.view_stack.addWidget(self.navigation_view)
        self.view_stack.addWidget(self.workshop_view)

        for section_key, title, _factory in self.section_definitions:
            button = QPushButton(title)
            button.setProperty("active", False)
            button.clicked.connect(
                lambda checked=False, key=section_key: self.handle_section_click(key)
            )
            self.section_buttons[section_key] = button

        self.show_navigation(reset_selection=True)

    def build_navigation_view(self) -> QFrame:
        view = QFrame()
        view.setObjectName("StructureNavigationView")
        view.setMinimumWidth(0)
        layout = QVBoxLayout(view)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setObjectName("StructureNavigationScroll")
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        content = QFrame()
        content.setObjectName("StructureNavigationContent")
        content.setMinimumWidth(0)
        self.navigation_button_layout = QVBoxLayout(content)
        self.navigation_button_layout.setContentsMargins(0, 0, 0, 0)
        self.navigation_button_layout.setSpacing(8)
        scroll_area.setWidget(content)
        layout.addWidget(scroll_area, 1)
        return view

    def build_workshop_view(self) -> QFrame:
        view = QFrame()
        view.setObjectName("StructureWorkshopView")
        view.setMinimumWidth(0)
        layout = QVBoxLayout(view)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.workshop_button_layout = QHBoxLayout()
        self.workshop_button_layout.setSpacing(7)
        layout.addLayout(self.workshop_button_layout)

        self.content_host = QFrame()
        self.content_host.setObjectName("StructureContentHost")
        host_layout = QVBoxLayout(self.content_host)
        host_layout.setContentsMargins(0, 0, 0, 0)
        host_layout.setSpacing(0)
        layout.addWidget(self.content_host, 1)
        self.set_placeholder()
        return view

    def compact_width_hint(self) -> int:
        button_widths = [
            button.sizeHint().width()
            for button in self.section_buttons.values()
        ]
        longest_button = max(button_widths, default=240)
        return max(276, min(344, longest_button + 24))

    def show_navigation(self, reset_selection: bool = False) -> None:
        if reset_selection:
            self.active_panel = ""
            self.set_placeholder()

        self.display_mode = "navigation"
        self.move_buttons_to_navigation()
        if self.view_stack is not None and self.navigation_view is not None:
            self.view_stack.setCurrentWidget(self.navigation_view)
        self.update_buttons()

    def show_workshop(self, section_key: str) -> None:
        self.display_mode = "workshop"
        self.move_buttons_to_workshop()
        if self.view_stack is not None and self.workshop_view is not None:
            self.view_stack.setCurrentWidget(self.workshop_view)
        self.show_panel(section_key)

    def handle_section_click(self, section_key: str) -> None:
        if self.display_mode == "navigation":
            self.studio.open_structure_workshop(section_key)
            return

        if self.active_panel == section_key:
            self.close_panel()
            return

        self.show_panel(section_key)

    def move_buttons_to_navigation(self) -> None:
        if self.navigation_button_layout is None:
            return

        detach_layout_items(self.navigation_button_layout)
        if self.workshop_button_layout is not None:
            detach_layout_items(self.workshop_button_layout)

        for button in self.section_buttons.values():
            button.setObjectName("StructureNavigationButton")
            self.navigation_button_layout.addWidget(button)
        self.navigation_button_layout.addStretch(1)

    def move_buttons_to_workshop(self) -> None:
        if self.workshop_button_layout is None:
            return

        if self.navigation_button_layout is not None:
            detach_layout_items(self.navigation_button_layout)
        detach_layout_items(self.workshop_button_layout)

        for button in self.section_buttons.values():
            button.setObjectName("StructureTinyButton")
            self.workshop_button_layout.addWidget(button)
        self.workshop_button_layout.addStretch(1)

    def show_panel(self, panel_name: str) -> None:
        section_factory = self.get_section_factory(panel_name)
        if section_factory is None or self.content_host is None:
            return

        clear_layout(self.content_host.layout())
        self.content_host.layout().addWidget(section_factory())
        self.active_panel = panel_name
        self.update_buttons()

    def get_section_factory(self, section_key: str) -> SectionFactory | None:
        for key, _title, factory in self.section_definitions:
            if key == section_key:
                return factory
        return None

    def close_panel(self) -> None:
        self.active_panel = ""
        self.set_placeholder()
        self.update_buttons()

    def set_placeholder(self) -> None:
        if self.content_host is None:
            return
        clear_layout(self.content_host.layout())
        placeholder = QLabel("Struktur-Werkstatt bereit.")
        placeholder.setObjectName("StructurePlaceholder")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_host.layout().addWidget(placeholder, 1)

    def update_buttons(self) -> None:
        for section_key, button in self.section_buttons.items():
            button.setProperty("active", self.active_panel == section_key)
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()


def detach_layout_items(layout) -> None:
    if layout is None:
        return
    while layout.count():
        layout.takeAt(0)


def clear_layout(layout) -> None:
    if layout is None:
        return
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        child_layout = item.layout()
        if widget is not None:
            widget.deleteLater()
        if child_layout is not None:
            clear_layout(child_layout)


def build_structure_settings_panel(studio) -> StructureSettingsPanel:
    return StructureSettingsPanel(studio)
