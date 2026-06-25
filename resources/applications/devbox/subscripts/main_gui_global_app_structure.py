from __future__ import annotations

from subscripts.main_gui_devbox_log import get_devbox_logger
LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")

from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
)
from subscripts.main_gui_global_app_structure_store import (
    APP_PLACEHOLDER,
    APPLICATIONS_FOLDER_NAME,
    MAX_LEVELS,
    SORT_ORDER_OFFSET,
    applications_folder_name,
    database_file,
    load_template_paths,
    make_row,
    sanitize_folder_name,
    save_template_rows,
    split_path,
)
def item_path_parts_raw(item: QTreeWidgetItem) -> list[str]:
    parts = []
    current = item
    while current is not None:
        value = current.data(0, Qt.UserRole + 1)
        if value:
            parts.append(str(value))
        current = current.parent()
    parts.reverse()
    return parts
class GlobalAppFolderStructureForm(QFrame):
    def __init__(self, project_root_path: Path) -> None:
        super().__init__()
        self.project_root_path = Path(project_root_path).resolve()
        self.database_file = database_file(self.project_root_path)
        self.applications_name = applications_folder_name(self.project_root_path)
        self.root_item: QTreeWidgetItem | None = None
        self.placeholder_item: QTreeWidgetItem | None = None
        self.path_preview: QLabel | None = None
        self.add_button: QPushButton | None = None
        self.rename_button: QPushButton | None = None
        self.delete_button: QPushButton | None = None
        self.setObjectName("GlobalAppFolderStructureForm")
        self.build_ui()
        self.reload_tree()
    def build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(9)
        title_row = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        title = QLabel("Globale App-Ordnerstruktur")
        title.setObjectName("StructureFormTitle")
        subtitle = QLabel(
            f"Vorlage für {self.applications_name}\\{APP_PLACEHOLDER}\\"
        )
        subtitle.setObjectName("GlobalAppStructureSubtitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        title_row.addLayout(title_box, 1)
        save_button = QPushButton("Speichern")
        save_button.setObjectName("StructureSaveButton")
        save_button.clicked.connect(self.save_tree)
        title_row.addWidget(save_button)
        layout.addLayout(title_row)
        toolbar = QHBoxLayout()
        toolbar.setSpacing(7)
        self.add_button = self.make_button("+ Ordner", "GlobalAppStructureButton")
        self.rename_button = self.make_button("Umbenennen", "GlobalAppStructureButton")
        self.delete_button = self.make_button("Löschen", "GlobalAppStructureDeleteButton")
        reload_button = self.make_button("Neu laden", "GlobalAppStructureButton")
        self.add_button.clicked.connect(self.add_child_folder)
        self.rename_button.clicked.connect(self.rename_folder)
        self.delete_button.clicked.connect(self.delete_folder)
        reload_button.clicked.connect(self.reload_tree)
        for button in (
            self.add_button,
            self.rename_button,
            self.delete_button,
            reload_button,
        ):
            toolbar.addWidget(button)
        toolbar.addStretch(1)
        layout.addLayout(toolbar)
        panel = QFrame()
        panel.setObjectName("GlobalAppStructureTreePanel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(10, 10, 10, 10)
        panel_layout.setSpacing(8)
        self.tree = QTreeWidget()
        self.tree.setObjectName("GlobalAppStructureTree")
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(18)
        self.tree.setAnimated(True)
        self.tree.setExpandsOnDoubleClick(True)
        self.tree.itemSelectionChanged.connect(self.update_selection_state)
        self.path_preview = QLabel("Pfad: —")
        self.path_preview.setObjectName("GlobalAppStructurePathPreview")
        self.path_preview.setTextInteractionFlags(Qt.TextSelectableByMouse)
        panel_layout.addWidget(self.tree, 1)
        panel_layout.addWidget(self.path_preview)
        layout.addWidget(panel, 1)
    def make_button(self, text: str, object_name: str) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName(object_name)
        button.setCursor(Qt.PointingHandCursor)
        return button
    def selected_item(self) -> QTreeWidgetItem | None:
        return self.tree.currentItem() or self.placeholder_item
    def selected_item_is_editable(self) -> bool:
        item = self.selected_item()
        return item is not None and item.data(0, Qt.UserRole) == "editable"
    def selected_item_allows_child_creation(self) -> bool:
        item = self.selected_item()
        if item is None:
            return False
        return item.data(0, Qt.UserRole) in {"editable", "add_child_only"}
    def update_selection_state(self) -> None:
        self.update_path_preview()
        allows_child_creation = self.selected_item_allows_child_creation()
        editable = self.selected_item_is_editable()
        if self.add_button is not None:
            self.add_button.setEnabled(allows_child_creation)
            self.add_button.setCursor(
                Qt.PointingHandCursor if allows_child_creation else Qt.ArrowCursor
            )
        for button in (self.rename_button, self.delete_button):
            if button is not None:
                button.setEnabled(editable)
                button.setCursor(
                    Qt.PointingHandCursor if editable else Qt.ArrowCursor
                )
    def update_path_preview(self) -> None:
        item = self.selected_item()
        if item is not None and self.path_preview is not None:
            self.path_preview.setText(
                "Pfad: " + " / ".join(item_path_parts_raw(item))
            )
    def reload_tree(self) -> None:
        self.tree.clear()
        self.root_item = self.make_item(
            f"📁 {self.applications_name}",
            self.applications_name,
            "locked",
        )
        self.placeholder_item = self.make_item(
            f"◆ {APP_PLACEHOLDER}",
            APP_PLACEHOLDER,
            "add_child_only",
        )
        self.root_item.addChild(self.placeholder_item)
        self.tree.addTopLevelItem(self.root_item)
        for relative_path in load_template_paths(self.database_file):
            parts = split_path(relative_path)
            if (
                len(parts) >= 3
                and parts[0].lower() == APPLICATIONS_FOLDER_NAME
                and parts[1] == APP_PLACEHOLDER
            ):
                self.ensure_path(parts[2:])
        self.root_item.setExpanded(True)
        self.placeholder_item.setExpanded(True)
        self.tree.setCurrentItem(self.placeholder_item)
        self.update_selection_state()
    def make_item(
        self,
        visible_text: str,
        raw_text: str,
        item_state: str,
    ) -> QTreeWidgetItem:
        item = QTreeWidgetItem([visible_text])
        item.setData(0, Qt.UserRole, item_state)
        item.setData(0, Qt.UserRole + 1, raw_text)
        return item
    def ensure_path(self, folder_parts: list[str]) -> QTreeWidgetItem | None:
        parent = self.placeholder_item
        if parent is None:
            return None
        for folder_name in folder_parts:
            child = self.find_child(parent, folder_name)
            if child is None:
                child = self.make_item(f"📁 {folder_name}", folder_name, "editable")
                parent.addChild(child)
            parent = child
        return parent
    def find_child(
        self,
        parent_item: QTreeWidgetItem,
        raw_text: str,
    ) -> QTreeWidgetItem | None:
        for index in range(parent_item.childCount()):
            child = parent_item.child(index)
            if child.data(0, Qt.UserRole + 1) == raw_text:
                return child
        return None
    def add_child_folder(self) -> None:
        parent = self.selected_item()
        if parent is None or not self.selected_item_allows_child_creation():
            return
        if len(item_path_parts_raw(parent)) >= MAX_LEVELS:
            QMessageBox.warning(self, "Tiefe", f"Maximal {MAX_LEVELS} Ebenen.")
            return
        folder_name, ok = QInputDialog.getText(self, "Unterordner", "Ordnername:")
        folder_name = sanitize_folder_name(folder_name) if ok else ""
        if not folder_name:
            return
        if self.find_child(parent, folder_name) is not None:
            QMessageBox.warning(self, "Vorhanden", "Dieser Ordner existiert bereits.")
            return
        child = self.make_item(f"📁 {folder_name}", folder_name, "editable")
        parent.addChild(child)
        parent.setExpanded(True)
        self.tree.setCurrentItem(child)
    def rename_folder(self) -> None:
        item = self.tree.currentItem()
        if item is None or not self.selected_item_is_editable():
            return
        folder_name, ok = QInputDialog.getText(
            self,
            "Umbenennen",
            "Neuer Name:",
            text=item.data(0, Qt.UserRole + 1),
        )
        folder_name = sanitize_folder_name(folder_name) if ok else ""
        if folder_name:
            item.setData(0, Qt.UserRole + 1, folder_name)
            item.setText(0, f"📁 {folder_name}")
            self.update_selection_state()
    def delete_folder(self) -> None:
        item = self.tree.currentItem()
        if item is None or not self.selected_item_is_editable():
            return
        if QMessageBox.question(
            self,
            "Löschen",
            "Ordner inklusive Unterordner entfernen?",
        ) != QMessageBox.Yes:
            return
        parent = item.parent()
        if parent is not None:
            parent.removeChild(item)
            self.update_selection_state()
    def collect_rows(self) -> list[dict[str, object]]:
        rows = []
        sort_order = SORT_ORDER_OFFSET
        rows.append(
            make_row(
                self.applications_name,
                sort_order,
                "application_template_root",
                [self.applications_name, APP_PLACEHOLDER],
            )
        )
        sort_order += 1
        def walk(parent_item: QTreeWidgetItem) -> None:
            nonlocal sort_order
            for index in range(parent_item.childCount()):
                child = parent_item.child(index)
                rows.append(
                    make_row(
                        self.applications_name,
                        sort_order,
                        "application_template_subfolder",
                        item_path_parts_raw(child),
                    )
                )
                sort_order += 1
                walk(child)
        if self.placeholder_item is not None:
            walk(self.placeholder_item)
        return rows
    def save_tree(self) -> None:
        try:
            save_template_rows(self.database_file, self.collect_rows())
        except Exception as exc:
            QMessageBox.warning(self, "Fehler", str(exc))
            return
        QMessageBox.information(self, "Gespeichert", "Vorlage wurde gespeichert.")
