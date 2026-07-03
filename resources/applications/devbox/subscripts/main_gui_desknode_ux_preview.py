from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)


def build_preview() -> QFrame:
    preview = QFrame()
    preview.setObjectName("DeskNodeUxPreview")
    preview.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    layout = QVBoxLayout(preview)
    layout.setContentsMargins(18, 18, 18, 18)
    layout.setSpacing(12)

    title = QLabel("deskNode")
    title.setObjectName("HeaderLabel")
    layout.addWidget(title)

    location = QLabel("Wohnzimmer")
    location.setObjectName("DeskNodePreviewSection")
    layout.addWidget(location)

    structure_preview = QFrame()
    structure_preview.setObjectName("DeskNodePreviewStructure")
    structure_layout = QHBoxLayout(structure_preview)
    structure_layout.setContentsMargins(0, 0, 0, 0)
    structure_layout.setSpacing(0)

    normal_node = QFrame()
    normal_node.setObjectName("DeskNodePreviewStructureNode")
    normal_layout = QHBoxLayout(normal_node)
    normal_layout.setContentsMargins(12, 6, 12, 6)
    normal_label = QLabel("Dachgeschoss")
    normal_label.setObjectName("DeskNodePreviewStructureNodeLabel")
    normal_layout.addWidget(normal_label)

    connector = QFrame()
    connector.setObjectName("DeskNodePreviewStructureConnector")
    connector.setFixedHeight(4)
    connector.setMinimumWidth(18)

    selected_node = QFrame()
    selected_node.setObjectName("DeskNodePreviewStructureNodeSelected")
    selected_layout = QHBoxLayout(selected_node)
    selected_layout.setContentsMargins(12, 6, 12, 6)
    selected_label = QLabel("Treppenhaus")
    selected_label.setObjectName("DeskNodePreviewStructureNodeLabel")
    selected_layout.addWidget(selected_label)

    structure_layout.addWidget(normal_node)
    structure_layout.addWidget(connector)
    structure_layout.addWidget(selected_node)
    structure_layout.addStretch(1)
    layout.addWidget(structure_preview)

    device_panel = QFrame()
    device_panel.setObjectName("DeskNodePreviewDevicePanel")
    device_layout = QVBoxLayout(device_panel)
    device_layout.setContentsMargins(12, 10, 12, 10)
    device_layout.setSpacing(2)

    device_name = QLabel("Schreibtischlampe")
    device_name.setObjectName("DeskNodePreviewDeviceName")
    device_layout.addWidget(device_name)

    device_metric = QLabel("12,4 W · online")
    device_metric.setObjectName("DeskNodePreviewDeviceMetric")
    device_layout.addWidget(device_metric)
    layout.addWidget(device_panel)

    dialog = QFrame()
    dialog.setObjectName("DeskNodePreviewDialog")
    dialog_layout = QVBoxLayout(dialog)
    dialog_layout.setContentsMargins(14, 12, 14, 12)
    dialog_layout.setSpacing(9)

    dialog_title = QLabel("Gerät bearbeiten")
    dialog_title.setObjectName("DeskNodePreviewDialogTitle")
    dialog_layout.addWidget(dialog_title)

    name_input = QLineEdit("Schreibtischlampe")
    name_input.setObjectName("DeskNodePreviewInput")
    dialog_layout.addWidget(name_input)

    category_combo = QComboBox()
    category_combo.setObjectName("DeskNodePreviewCombo")
    category_combo.addItems(("Leuchte", "Computer und Peripherie", "Audio und Video"))
    dialog_layout.addWidget(category_combo)

    button_row = QHBoxLayout()
    button_row.setSpacing(8)
    save_button = QPushButton("Speichern")
    save_button.setObjectName("DeskNodePreviewDialogButton")
    cancel_button = QPushButton("Abbrechen")
    cancel_button.setObjectName("DeskNodePreviewDialogButton")
    button_row.addWidget(save_button)
    button_row.addWidget(cancel_button)
    dialog_layout.addLayout(button_row)
    layout.addWidget(dialog)

    menu = QFrame()
    menu.setObjectName("DeskNodePreviewContextMenu")
    menu_layout = QVBoxLayout(menu)
    menu_layout.setContentsMargins(8, 6, 8, 6)
    menu_item = QLabel("Gerät bearbeiten")
    menu_item.setObjectName("DeskNodePreviewContextMenuItem")
    menu_layout.addWidget(menu_item)
    layout.addWidget(menu)

    statusbar = QFrame()
    statusbar.setObjectName("DeskNodePreviewStatusbar")
    status_layout = QHBoxLayout(statusbar)
    status_layout.setContentsMargins(10, 6, 10, 6)
    status_layout.setSpacing(6)

    connection = QLabel("●  Verbindung:")
    connection.setObjectName("DeskNodePreviewStatusText")
    connection_state = QLabel("Online")
    connection_state.setObjectName("DeskNodePreviewStatusState")
    divider = QLabel("│")
    divider.setObjectName("DeskNodePreviewStatusDivider")
    system = QLabel("◈  System:")
    system.setObjectName("DeskNodePreviewStatusText")
    system_state = QLabel("OK")
    system_state.setObjectName("DeskNodePreviewStatusState")
    product = QLabel("◷  deskNode")
    product.setObjectName("DeskNodePreviewStatusText")

    status_layout.addWidget(connection)
    status_layout.addWidget(connection_state)
    status_layout.addWidget(divider)
    status_layout.addWidget(system)
    status_layout.addWidget(system_state)
    status_layout.addStretch(1)
    status_layout.addWidget(product)
    layout.addWidget(statusbar)
    layout.addStretch(1)
    return preview
