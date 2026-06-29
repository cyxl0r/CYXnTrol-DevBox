from __future__ import annotations
import sqlite3
from collections.abc import Callable
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)
from subscripts.main_gui_desknode_ux_apply import (
    apply_desknode_ux_settings,
    apply_preview_ux_settings,
)
from subscripts.main_gui_desknode_ux_defaults import (
    DEFAULT_SETTINGS,
    DEFAULT_THEME_NAME,
)
from subscripts.main_gui_desknode_ux_editor import build_editor
from subscripts.main_gui_desknode_ux_fonts import scan_project_fonts
from subscripts.main_gui_desknode_ux_preview import build_preview
from subscripts.main_gui_desknode_ux_storage import save_ux_settings
from subscripts.main_gui_desknode_version_refresh import (
    start_manufacturer_database_refresh,
)
from subscripts.main_gui_desknode_ux_theme_actions import (
    DeskNodeUxThemeActionsMixin,
)
from subscripts.main_gui_devbox_log import get_devbox_logger
LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")
PAGE_KEY = "desknode"
class DeskNodeUxDesignView(DeskNodeUxThemeActionsMixin, QWidget):
    def __init__(self, studio, return_to_execution: Callable[[], None]) -> None:
        super().__init__()
        self.studio = studio
        self.return_to_execution = return_to_execution
        self.color_inputs: dict[str, QLineEdit] = {}
        self.font_controls: dict[str, tuple] = {}
        self.number_controls: dict[str, QSpinBox] = {}
        self.outline_style_combo: QComboBox | None = None
        self.theme_combo = QComboBox()
        self.theme_combo.setObjectName("DeskNodeUxThemeCombo")
        self.save_button: QPushButton | None = None
        self.current_theme_name = DEFAULT_THEME_NAME
        self.notice = QLabel()
        self.notice.setObjectName("DeskNodeUxNotice")
        self.preview: QFrame | None = None
        self._build_ui()
        self.reload_settings()
    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 12, 10, 10)
        layout.setSpacing(12)
        layout.addLayout(self._build_toolbar())
        layout.addLayout(self.build_theme_row())
        self.notice.setWordWrap(True)
        layout.addWidget(self.notice)
        content = QHBoxLayout()
        content.setSpacing(14)
        content.addWidget(build_editor(self), stretch=3)
        self.preview = build_preview()
        content.addWidget(self.preview, stretch=2)
        layout.addLayout(content, stretch=1)
    def _build_toolbar(self) -> QHBoxLayout:
        row = QHBoxLayout()
        back_button = QPushButton("Zurück")
        back_button.setObjectName("DeskNodeUxBackButton")
        back_button.setMinimumWidth(145)
        back_button.clicked.connect(
            lambda _checked=False: self.return_to_execution()
        )
        row.addWidget(back_button)
        title = QLabel("Oberflächengestaltung: deskNode")
        title.setObjectName("DeskNodeUxTitle")
        row.addWidget(title)
        row.addStretch(1)

        for text, callback in (
            ("Standardwerte laden", self.load_defaults),
            ("Änderungen anwenden", self.apply_changes),
        ):
            button = QPushButton(text)
            button.setObjectName("DeskNodeUxActionButton")
            button.clicked.connect(
                lambda _checked=False, func=callback: func()
            )
            row.addWidget(button)

        self.save_button = QPushButton("Speichern")
        self.save_button.setObjectName("DeskNodeUxSaveButton")
        self.save_button.clicked.connect(
            lambda _checked=False: self.save_changes()
        )
        self.studio.desknode_ux_save_button = self.save_button
        row.addWidget(self.save_button)
        return row

    def reload_font_choices(self, show_notice: bool = True) -> None:
        font_files = scan_project_fonts(self.studio)
        for combo, *_rest in self.font_controls.values():
            selected_path = str(combo.currentData() or "")
            combo.blockSignals(True)
            combo.clear()
            combo.addItem("Systemstandard", "")
            for path in font_files:
                combo.addItem(path, path)
            index = combo.findData(selected_path)
            if selected_path and index < 0:
                combo.addItem(
                    f"Fehlende Schriftdatei: {selected_path}",
                    selected_path,
                )
                index = combo.count() - 1
            combo.setCurrentIndex(max(0, index))
            combo.blockSignals(False)
        if show_notice:
            self.notice.setText(f"{len(font_files)} Schriftdatei(en) gefunden.")
        self.update_preview()

    def _set_values(self, settings: dict) -> None:
        for key, field in self.color_inputs.items():
            field.blockSignals(True)
            field.setText(str(settings[key]))
            field.blockSignals(False)
            field.textChanged.emit(field.text())
        for key, field in self.number_controls.items():
            field.setValue(int(settings[key]))
        if self.outline_style_combo is not None:
            self.outline_style_combo.setCurrentText(
                str(settings["outline_style"])
            )
        for role, controls in self.font_controls.items():
            combo, color, size, bold, italic, underline = controls
            wanted_path = str(settings[f"{role}_font_path"])
            index = combo.findData(wanted_path)
            if wanted_path and index < 0:
                combo.addItem(
                    f"Fehlende Schriftdatei: {wanted_path}",
                    wanted_path,
                )
                index = combo.count() - 1
            combo.setCurrentIndex(max(0, index))
            color.setText(str(settings[f"{role}_font_rgba"]))
            size.setValue(int(settings[f"{role}_font_size"]))
            bold.setChecked(bool(int(settings[f"{role}_font_bold"])))
            italic.setChecked(bool(int(settings[f"{role}_font_italic"])))
            underline.setChecked(bool(int(settings[f"{role}_font_underline"])))

    def collect_settings(self) -> dict[str, object]:
        if self.outline_style_combo is None:
            return {}
        settings: dict[str, object] = {
            key: field.text()
            for key, field in self.color_inputs.items()
        }
        settings.update(
            {
                key: field.value()
                for key, field in self.number_controls.items()
            }
        )
        settings["outline_style"] = self.outline_style_combo.currentText()
        for role, controls in self.font_controls.items():
            combo, color, size, bold, italic, underline = controls
            settings.update(
                {
                    f"{role}_font_path": combo.currentData() or "",
                    f"{role}_font_rgba": color.text(),
                    f"{role}_font_size": size.value(),
                    f"{role}_font_bold": int(bold.isChecked()),
                    f"{role}_font_italic": int(italic.isChecked()),
                    f"{role}_font_underline": int(underline.isChecked()),
                }
            )
        return settings

    def update_preview(self) -> None:
        if self.preview is None:
            return
        try:
            apply_preview_ux_settings(
                self.studio,
                self.preview,
                self.collect_settings(),
            )
        except (TypeError, ValueError):
            return

    def reload_settings(self) -> None:
        try:
            requested_name = getattr(
                self.studio,
                "desknode_ux_theme_name",
                None,
            )
            self.refresh_theme_choices(requested_name)
            self.load_theme(
                self.current_theme_name,
                apply_to_execution=False,
            )
        except (OSError, RuntimeError, sqlite3.Error, ValueError) as error:
            self._set_values(dict(DEFAULT_SETTINGS))
            self.notice.setText(
                "Gespeicherte Werte konnten nicht geladen werden: "
                f"{error}"
            )
            self.update_preview()

    def load_defaults(self) -> None:
        self._set_values(dict(DEFAULT_SETTINGS))
        self.notice.setText(
            "Standardwerte geladen. Sie werden erst beim Speichern "
            "dauerhaft übernommen."
        )
        self.update_preview()

    def apply_changes(self) -> bool:
        try:
            settings = self.collect_settings()
            apply_desknode_ux_settings(self.studio, settings)
            self.update_preview()
        except (TypeError, ValueError) as error:
            self.notice.setText(
                f"Änderungen konnten nicht angewendet werden: {error}"
            )
            return False
        self.notice.setText(
            f"Änderungen für UX-Theme „{self.current_theme_name}“ "
            "wurden angewendet."
        )
        return True

    def save_changes(self) -> None:
        theme_name = self.current_theme_name

        try:
            settings = save_ux_settings(
                self.studio,
                self.collect_settings(),
                theme_name,
            )
        except (OSError, RuntimeError, sqlite3.Error, ValueError) as error:
            self.notice.setText(f"Speichern fehlgeschlagen: {error}")
            self.studio.set_status(
                "deskNode-Gestaltungsprofil konnte nicht gespeichert werden.",
                "error",
                PAGE_KEY,
            )
            return

        apply_desknode_ux_settings(self.studio, settings)
        self.update_preview()
        self.studio.append_log(
            f"UX-Theme gespeichert: {theme_name}.",
            PAGE_KEY,
        )
        LOGGER.info(
            "deskNode UX theme committed.",
            f"theme_name={theme_name}",
        )

        self.notice.setText(
            f"UX-Theme „{theme_name}“ wurde gespeichert. "
            "Herstellerdatenbank wird jetzt aktualisiert …"
        )

        started = start_manufacturer_database_refresh(
            self.studio,
            saved_subject=f"UX-Theme „{theme_name}“",
            controls_to_lock=("desknode_ux_save_button",),
            on_started=lambda: self.notice.setText(
                f"UX-Theme „{theme_name}“ ist gespeichert. "
                "create_manufacturer_db.py läuft …"
            ),
            on_finished=lambda succeeded, message: self.notice.setText(
                message if succeeded else f"UX-Theme gespeichert, aber {message}"
            ),
        )

        if not started:
            self.notice.setText(
                f"UX-Theme „{theme_name}“ wurde gespeichert, aber "
                "create_manufacturer_db.py konnte nicht gestartet werden. "
                "Details stehen im deskNode-Protokoll."
            )


def build_desknode_ux_design_view(
    studio,
    return_to_execution: Callable[[], None],
) -> DeskNodeUxDesignView:
    return DeskNodeUxDesignView(studio, return_to_execution)
