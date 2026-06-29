from __future__ import annotations

import sqlite3

from PySide6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPushButton,
)

from subscripts.main_gui_desknode_ux_apply import (
    apply_desknode_ux_settings,
)
from subscripts.main_gui_desknode_ux_storage import (
    create_ux_theme,
    delete_ux_theme,
    list_ux_theme_names,
    load_ux_settings,
    rename_ux_theme,
)


class DeskNodeUxThemeActionsMixin:
    def build_theme_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)
        row.addWidget(QLabel("UX-Theme"))
        self.theme_combo.setMinimumWidth(250)
        self.theme_combo.currentTextChanged.connect(self._on_theme_selected)
        row.addWidget(self.theme_combo)

        buttons = (
            ("+", self.create_theme, "Neues UX-Theme anlegen"),
            ("−", self.delete_theme, "Aktuelles UX-Theme löschen"),
            ("Duplizieren", self.duplicate_theme, "Aktuelles UX-Theme duplizieren"),
            ("Umbenennen", self.rename_theme, "Aktuelles UX-Theme umbenennen"),
        )
        for text, callback, tooltip in buttons:
            button = QPushButton(text)
            button.setObjectName("DeskNodeUxActionButton")
            button.setToolTip(tooltip)
            if text in {"+", "−"}:
                button.setFixedWidth(40)
            button.clicked.connect(
                lambda _checked=False, func=callback: func()
            )
            row.addWidget(button)
        row.addStretch(1)
        return row

    def refresh_theme_choices(self, selected_name: str | None = None) -> None:
        theme_names = list_ux_theme_names(self.studio)
        selected_name = selected_name or self.current_theme_name
        self.theme_combo.blockSignals(True)
        self.theme_combo.clear()
        self.theme_combo.addItems(theme_names)
        index = self.theme_combo.findText(selected_name)
        self.theme_combo.setCurrentIndex(max(0, index))
        self.theme_combo.blockSignals(False)
        self.current_theme_name = self.theme_combo.currentText()

    def theme_name_prompt(
        self,
        title: str,
        label: str,
        initial_value: str = "",
    ) -> str | None:
        value, accepted = QInputDialog.getText(
            self,
            title,
            label,
            text=initial_value,
        )
        return value if accepted else None

    def _on_theme_selected(self, theme_name: str) -> None:
        if not theme_name:
            return
        try:
            self.load_theme(theme_name, apply_to_execution=True)
        except (OSError, RuntimeError, sqlite3.Error, ValueError) as error:
            self.notice.setText(f"UX-Theme konnte nicht geladen werden: {error}")

    def load_theme(
        self,
        theme_name: str,
        apply_to_execution: bool,
    ) -> None:
        settings = load_ux_settings(self.studio, theme_name)
        self.current_theme_name = theme_name
        self.studio.desknode_ux_theme_name = theme_name
        self.reload_font_choices(show_notice=False)
        self._set_values(settings)
        self.update_preview()
        if apply_to_execution:
            apply_desknode_ux_settings(self.studio, settings)
        self.notice.setText(f"UX-Theme „{theme_name}“ geladen.")

    def create_theme(self) -> None:
        name = self.theme_name_prompt(
            "Neues UX-Theme",
            "Name des neuen UX-Themes:",
        )
        if name is None:
            return
        try:
            created_name = create_ux_theme(self.studio, name)
            self.refresh_theme_choices(created_name)
            self.load_theme(created_name, apply_to_execution=True)
            self.notice.setText(f"UX-Theme „{created_name}“ wurde angelegt.")
        except (OSError, RuntimeError, sqlite3.Error, ValueError) as error:
            self.notice.setText(f"UX-Theme konnte nicht angelegt werden: {error}")

    def duplicate_theme(self) -> None:
        name = self.theme_name_prompt(
            "UX-Theme duplizieren",
            "Name der Kopie:",
            f"{self.current_theme_name} Kopie",
        )
        if name is None:
            return
        try:
            created_name = create_ux_theme(
                self.studio,
                name,
                self.collect_settings(),
            )
            self.refresh_theme_choices(created_name)
            self.load_theme(created_name, apply_to_execution=True)
            self.notice.setText(f"UX-Theme „{created_name}“ wurde dupliziert.")
        except (OSError, RuntimeError, sqlite3.Error, ValueError) as error:
            self.notice.setText(f"UX-Theme konnte nicht dupliziert werden: {error}")

    def rename_theme(self) -> None:
        old_name = self.current_theme_name
        name = self.theme_name_prompt(
            "UX-Theme umbenennen",
            "Neuer Name des UX-Themes:",
            old_name,
        )
        if name is None:
            return
        try:
            renamed_name = rename_ux_theme(self.studio, old_name, name)
            self.refresh_theme_choices(renamed_name)
            self.current_theme_name = renamed_name
            self.studio.desknode_ux_theme_name = renamed_name
            self.notice.setText(f"UX-Theme wurde in „{renamed_name}“ umbenannt.")
        except (OSError, RuntimeError, sqlite3.Error, ValueError) as error:
            self.notice.setText(f"UX-Theme konnte nicht umbenannt werden: {error}")

    def delete_theme(self) -> None:
        theme_name = self.current_theme_name
        answer = QMessageBox.question(
            self,
            "UX-Theme löschen",
            f"Soll das UX-Theme „{theme_name}“ wirklich gelöscht werden?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            next_theme = delete_ux_theme(self.studio, theme_name)
            self.refresh_theme_choices(next_theme)
            self.load_theme(next_theme, apply_to_execution=True)
            self.notice.setText(f"UX-Theme „{theme_name}“ wurde gelöscht.")
        except (OSError, RuntimeError, sqlite3.Error, ValueError) as error:
            self.notice.setText(f"UX-Theme konnte nicht gelöscht werden: {error}")
