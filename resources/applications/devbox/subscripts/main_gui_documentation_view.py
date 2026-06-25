from __future__ import annotations

from subscripts.main_gui_devbox_log import get_devbox_logger
LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")


from PySide6.QtWidgets import QFrame, QFormLayout, QLabel, QTextEdit


LABELS_DE = {
    "short_description": "Kurzbeschreibung",
    "long_description": "Ausführliche Beschreibung",
    "purpose": "Zweck",
    "context": "Kontext",
    "core_idea": "Kernidee",
    "features_and_goals": "Funktionen und Ziele",
    "architecture_overview": "Architekturüberblick",
    "status": "Projektstatus",
    "installation_and_start": "Installation und Start",
    "configuration": "Konfiguration",
    "technology": "Technologie",
    "repository_note": "Repository-Hinweis",
}

LABELS_EN = {
    "short_description": "Short Description",
    "long_description": "Long Description",
    "purpose": "Purpose",
    "context": "Context",
    "core_idea": "Core Idea",
    "features_and_goals": "Features and Goals",
    "architecture_overview": "Architecture Overview",
    "status": "Status",
    "installation_and_start": "Installation and Start",
    "configuration": "Configuration",
    "technology": "Technology",
    "repository_note": "Repository Note",
}


def document_label(column_name: str, labels: dict[str, str]) -> str:
    if column_name in labels:
        return labels[column_name]
    return str(column_name).replace("_", " ").strip().capitalize()


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


def build_language_group(
    title: str,
    labels: dict[str, str],
    values: dict[str, object],
    field_store: dict[str, QTextEdit],
    field_order: list[str],
    enabled: bool,
    value_to_text,
) -> QFrame:
    box = QFrame()
    box.setObjectName("RoofDataGroup")
    form_layout = QFormLayout(box)
    form_layout.setContentsMargins(10, 8, 10, 10)
    form_layout.setSpacing(8)
    group_label = QLabel(title)
    group_label.setObjectName("RoofDataGroupTitle")
    form_layout.addRow(group_label)

    for column_name in field_order:
        editor = QTextEdit()
        editor.setObjectName("DocumentationTextInput")
        editor.setAcceptRichText(False)
        editor.setMinimumHeight(92)
        editor.setPlainText(value_to_text(values.get(column_name)))
        editor.setEnabled(enabled)
        field_store[column_name] = editor
        form_layout.addRow(document_label(column_name, labels), editor)

    return box
