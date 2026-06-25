from __future__ import annotations

from subscripts.main_gui_devbox_log import get_devbox_logger
LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")


import sys
from pathlib import Path

try:
    from PySide6.QtCore import (
        QEasingCurve,
        QPropertyAnimation,
        QRect,
        Qt,
        QTimer,
    )
    from PySide6.QtGui import QGuiApplication, QIcon, QPixmap
    from PySide6.QtWidgets import (
        QApplication,
        QFrame,
        QGraphicsOpacityEffect,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
    )
except Exception as exc:
    print("PySide6 konnte nicht geladen werden.")
    print("Diese isolierte DevBox-GUI benötigt PySide6.")
    print(f"Fehler: {type(exc).__name__}: {exc}")
    raise SystemExit(1)

from subscripts.main_gui_config import PAGE_KEYS, PROGRAM_NAME, TAB_KEYS, WORKSHOP_PROFILES
from subscripts.main_gui_pages import build_document_page, build_eventlab_page, build_profile_page, build_repository_page
from subscripts.main_gui_platform_page import build_platform_page
from subscripts.main_gui_manufacturer_setup_store import (
    FirstStartPreparationError,
    setup_required,
)
from subscripts.main_gui_manufacturer_wizard import ManufacturerFirstStartWizard
from subscripts.main_gui_structure_panel import StructureSettingsPanel, build_structure_settings_panel
from subscripts.main_gui_single_instance import DevBoxSingleInstance
from subscripts.main_gui_styles import style_sheet
from subscripts.main_gui_widgets import StudioRootWidget, StudioTopBar


class DevBoxGuiIsolatedWindow(QMainWindow):
    def __init__(self, base_dir: Path, project_root_path: Path) -> None:
        super().__init__()
        self.base_dir = Path(base_dir).resolve()
        self.project_root_path = Path(project_root_path).resolve()
        self.graphics_dir = self.project_root_path / "resources" / "graphics"
        self.layer1_path = self.graphics_dir / "devbox_background.png"
        self.layer2_left_path = self.graphics_dir / "devbox_logo_02.png"
        self.layer2_right_path = self.graphics_dir / "devbox_logo_01.png"
        self.icon_path = self.graphics_dir / "devbox.ico"

        self.pages: dict[str, dict[str, QLabel | QTextEdit]] = {}
        self.active_page_key = "platform"
        self.layer1_pixmap = QPixmap(str(self.layer1_path)) if self.layer1_path.exists() else QPixmap()
        self._layer1_anchor_geometry = None
        self._layer1_scaled_pixmap = QPixmap()
        self.root_widget: StudioRootWidget | None = None
        self.top_logo_bar: StudioTopBar | None = None
        self.structure_left_panel: QFrame | None = None
        self.structure_panel: StructureSettingsPanel | None = None
        self.right_shell: QFrame | None = None
        self.structure_settings_button: QPushButton | None = None
        self.repository_tab_index: int | None = None
        self.structure_settings_open = False
        self.structure_display_mode = "closed"
        self.structure_transition_running = False
        self.structure_normal_width = 1040
        self.structure_navigation_width = 288
        self.structure_full_width = self.structure_normal_width * 2
        self.structure_outer_spacing = 12
        self._structure_fade_animation: QPropertyAnimation | None = None
        self._structure_opacity_effect: QGraphicsOpacityEffect | None = None
        self._structure_normal_geometry: QRect | None = None
        self.first_start_required = False
        self.first_start_error = ""
        self.first_start_checked = False

        try:
            self.first_start_required = setup_required(self.project_root_path)
        except FirstStartPreparationError as exc:
            self.first_start_error = str(exc)
        except Exception as exc:
            self.first_start_error = f"{type(exc).__name__}: {exc}"

        self.setWindowTitle(PROGRAM_NAME)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        if self.icon_path.exists():
            self.setWindowIcon(QIcon(str(self.icon_path)))
        self.resize(self.structure_normal_width, 760)
        self.build_ui()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        if self.first_start_checked:
            return
        self.first_start_checked = True
        QTimer.singleShot(0, self.run_first_start_flow)

    def run_first_start_flow(self) -> None:
        if self.first_start_error:
            QMessageBox.critical(
                self,
                "DevBox konnte nicht eingerichtet werden",
                self.first_start_error,
            )
            self.close()
            return

        if not self.first_start_required:
            return

        wizard = ManufacturerFirstStartWizard(self.project_root_path, self)
        if not wizard.exec():
            self.close()
            return

        try:
            wizard.persist()
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Manufaktur-Ersteinrichtung",
                f"Speichern fehlgeschlagen: {type(exc).__name__}: {exc}",
            )
            self.close()
            return

        self.first_start_required = False
        QMessageBox.information(
            self,
            "DevBox eingerichtet",
            "Die Manufaktur-Grunddaten wurden gespeichert. DevBox ist jetzt bereit.",
        )

    def build_ui(self) -> None:
        root = StudioRootWidget(self)
        self.root_widget = root
        outer = QHBoxLayout(root)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(self.structure_outer_spacing)

        self.structure_left_panel = QFrame()
        self.structure_left_panel.setObjectName("StructureSettingsBlankPanel")
        self.structure_left_panel.setMinimumWidth(0)
        structure_left_layout = QVBoxLayout(self.structure_left_panel)
        structure_left_layout.setContentsMargins(0, 0, 0, 0)
        structure_left_layout.setSpacing(0)
        self.structure_panel = build_structure_settings_panel(self)
        structure_left_layout.addWidget(self.structure_panel)
        self.structure_left_panel.hide()
        self._structure_opacity_effect = QGraphicsOpacityEffect(
            self.structure_left_panel
        )
        self._structure_opacity_effect.setOpacity(1.0)
        self.structure_left_panel.setGraphicsEffect(self._structure_opacity_effect)
        outer.addWidget(self.structure_left_panel, stretch=1)

        self.right_shell = QFrame()
        self.right_shell.setObjectName("RightShell")
        shell_layout = QVBoxLayout(self.right_shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(12)
        outer.addWidget(self.right_shell, stretch=0)

        self.top_logo_bar = StudioTopBar(self)
        shell_layout.addWidget(self.top_logo_bar)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("MainTabs")
        self.tabs.currentChanged.connect(self.tab_changed)
        self.tabs.addTab(build_platform_page(self), "Entwicklungsplattform")
        self.tabs.addTab(
            build_profile_page(
                self,
                "workshop",
                "Werkstatt: DPM / EventLab / Tools",
                "Isolierte GUI-Vorschau: keine Worker-, Implementierungs-, Git- oder Daemon-Funktionen angebunden.",
                WORKSHOP_PROFILES,
            ),
            "(obsolet) DPM / EventLab / Tools",
        )
        self.tabs.addTab(build_document_page(self), "(obsolet) Doku-Snapshots")
        self.tabs.addTab(build_eventlab_page(self), "(obsolet) EventLab")
        self.repository_tab_index = self.tabs.addTab(
            build_repository_page(self),
            "Repositorys",
        )
        shell_layout.addWidget(self.tabs, stretch=1)

        self.setCentralWidget(root)
        self.setStyleSheet(style_sheet())
        if self.structure_panel is not None:
            self.structure_navigation_width = self.structure_panel.compact_width_hint()
        for key in PAGE_KEYS:
            self.set_status("GUI isoliert", "neutral", key)
            self.append_log("DevBox-GUI läuft als reine Vorschau ohne Backend-Funktionen.", key)

    def open_repository_page(self) -> None:
        """Activate the last main-GUI page used for repository maintenance."""
        if self.repository_tab_index is None:
            return
        self.tabs.setCurrentIndex(self.repository_tab_index)

    def register_structure_settings_button(self, button: QPushButton) -> None:
        self.structure_settings_button = button
        self.update_structure_settings_button()

    def toggle_structure_settings_panel(self) -> None:
        if self.structure_transition_running:
            return
        if self.structure_display_mode == "closed":
            self.open_structure_settings_panel()
            return
        self.close_structure_settings_panel()

    def open_structure_settings_panel(self) -> None:
        if self.structure_display_mode != "closed" or self.structure_transition_running:
            return
        if self.structure_left_panel is None or self.structure_panel is None:
            return

        LOGGER.info("Opening compact structure navigation.")
        self.capture_structure_normal_geometry()
        self.structure_transition_running = True
        self.structure_settings_open = True
        self.structure_display_mode = "navigation"
        self.prepare_structure_shell()
        self.structure_panel.show_navigation(reset_selection=True)
        self.structure_left_panel.setMaximumWidth(0)
        self.structure_left_panel.show()
        self.set_structure_opacity(0.0)
        self.update_structure_settings_button()

        self.apply_structure_layout(
            self.compact_structure_width(),
            self.structure_navigation_width,
        )
        self.fade_structure_panel(1.0, 180, self.finish_open_structure_navigation)

    def finish_open_structure_navigation(self) -> None:
        self.structure_transition_running = False
        self.update_structure_settings_button()

    def open_structure_workshop(self, section_key: str) -> None:
        if (
            self.structure_display_mode != "navigation"
            or self.structure_transition_running
            or self.structure_panel is None
        ):
            return

        LOGGER.info("Opening full structure workshop.", f"section={section_key}")
        self.structure_transition_running = True
        self.fade_structure_panel(
            0.0,
            110,
            lambda: self.expand_structure_workshop(section_key),
        )

    def expand_structure_workshop(self, section_key: str) -> None:
        self.apply_structure_layout(
            self.structure_full_width,
            self.full_structure_panel_width(),
        )
        self.finish_open_structure_workshop(section_key)

    def finish_open_structure_workshop(self, section_key: str) -> None:
        if self.structure_panel is not None:
            self.structure_panel.show_workshop(section_key)
        self.structure_display_mode = "workshop"
        self.fade_structure_panel(1.0, 190, self.finish_structure_transition)

    def close_structure_settings_panel(self) -> None:
        if self.structure_display_mode == "closed" or self.structure_transition_running:
            return

        LOGGER.info("Closing structure settings.")
        self.structure_transition_running = True
        self.fade_structure_panel(0.0, 110, self.collapse_structure_panel)

    def collapse_structure_panel(self) -> None:
        if self.structure_panel is not None:
            self.structure_panel.show_navigation(reset_selection=True)

        # Hide the complete workshop before restoring the outer geometry.
        # Otherwise a previously opened form can keep the central layout's
        # minimum width at the full-workshop size and block the shrink.
        if self.structure_left_panel is not None:
            self.structure_left_panel.hide()
            self.structure_left_panel.setMinimumWidth(0)
            self.structure_left_panel.setMaximumWidth(0)

        if self.right_shell is not None:
            self.right_shell.setMinimumWidth(0)
            self.right_shell.setMaximumWidth(16777215)

        self.restore_structure_normal_geometry()
        self.finish_close_structure_panel()

    def finish_close_structure_panel(self) -> None:
        if self.structure_left_panel is not None:
            self.structure_left_panel.hide()
            self.structure_left_panel.setMinimumWidth(0)
            self.structure_left_panel.setMaximumWidth(16777215)
        if self.right_shell is not None:
            self.right_shell.setMinimumWidth(0)
            self.right_shell.setMaximumWidth(16777215)
        self.set_structure_opacity(1.0)
        self.structure_settings_open = False
        self.structure_display_mode = "closed"
        self.finish_structure_transition()
        QTimer.singleShot(0, self.release_structure_normal_width_constraint)

    def finish_structure_transition(self) -> None:
        self.structure_transition_running = False
        self.update_structure_settings_button()
        if self.root_widget is not None:
            self.root_widget.update()

    def capture_structure_normal_geometry(self) -> None:
        """Remember the exact pre-workshop window geometry.

        The normal window may be adjusted by Qt once the initial layout has
        calculated its real minimum height. Restoring this captured geometry is
        therefore more reliable than restoring only a hard-coded width.
        """
        geometry = self.geometry()
        if geometry.width() <= 0 or geometry.height() <= 0:
            return

        self._structure_normal_geometry = QRect(geometry)
        self.structure_normal_width = geometry.width()
        self.structure_full_width = self.structure_normal_width * 2

    def restore_structure_normal_geometry(self) -> None:
        """Restore the original DevBox size after closing structure settings.

        A full workshop can leave large child forms inside the stacked layout.
        For one event-loop turn the top-level width is pinned to the remembered
        normal width. This ensures that Qt cannot retain the expanded minimum
        width while the hidden structure panel is being released.
        """
        target_geometry = self._structure_normal_geometry
        if target_geometry is None:
            self.apply_structure_layout(self.structure_normal_width, 0)
            return

        self.setUpdatesEnabled(False)
        try:
            self.setMinimumWidth(0)
            self.setMaximumWidth(target_geometry.width())
            self.setMinimumWidth(target_geometry.width())
            self.setGeometry(target_geometry)
        finally:
            self.setUpdatesEnabled(True)

        if self.root_widget is not None:
            self.root_widget.updateGeometry()
            self.root_widget.update()
        if self.top_logo_bar is not None:
            self.top_logo_bar.update_logos()

    def release_structure_normal_width_constraint(self) -> None:
        """Return the normal window to a resizable state after the restore."""
        if self.structure_display_mode != "closed":
            return

        self.setMinimumWidth(0)
        self.setMaximumWidth(16777215)

    def prepare_structure_shell(self) -> None:
        if self.right_shell is not None:
            self.right_shell.setFixedWidth(self.structure_normal_width - 32)
        if self.structure_left_panel is not None:
            self.structure_left_panel.setMinimumWidth(0)

    def compact_structure_width(self) -> int:
        return (
            self.structure_normal_width
            + self.structure_navigation_width
            + self.structure_outer_spacing
        )

    def full_structure_panel_width(self) -> int:
        return max(
            0,
            self.structure_full_width
            - self.structure_normal_width
            - self.structure_outer_spacing,
        )

    def apply_structure_layout(
        self,
        target_width: int,
        target_panel_width: int,
    ) -> None:
        """Apply a stable structure layout in one paint pass.

        The DevBox background is globally anchored to the virtual desktop.
        Animating the top-level window geometry forces a repaint for every
        animation frame and makes that projection visibly jitter. The window
        therefore moves directly to its final geometry; only the structure
        content itself is faded.
        """
        if self.structure_left_panel is None:
            return

        current_geometry = self.geometry()
        right_edge = current_geometry.x() + current_geometry.width()
        target_geometry = QRect(
            right_edge - target_width,
            current_geometry.y(),
            target_width,
            current_geometry.height(),
        )

        self.setUpdatesEnabled(False)
        try:
            if target_panel_width > 0:
                self.structure_left_panel.setMaximumWidth(target_panel_width)
                self.structure_left_panel.setMinimumWidth(target_panel_width)
                self.structure_left_panel.show()
            else:
                self.structure_left_panel.setMinimumWidth(0)
                self.structure_left_panel.setMaximumWidth(0)

            self.setGeometry(target_geometry)
            if self.root_widget is not None:
                self.root_widget.updateGeometry()
        finally:
            self.setUpdatesEnabled(True)

        if self.root_widget is not None:
            self.root_widget.update()
        if self.top_logo_bar is not None:
            self.top_logo_bar.update_logos()

    def fade_structure_panel(
        self,
        target_opacity: float,
        duration: int,
        on_finished=None,
    ) -> None:
        effect = self._structure_opacity_effect
        if effect is None:
            if on_finished is not None:
                on_finished()
            return

        if self._structure_fade_animation is not None:
            self._structure_fade_animation.stop()

        animation = QPropertyAnimation(effect, b"opacity", self)
        animation.setDuration(duration)
        animation.setStartValue(effect.opacity())
        animation.setEndValue(target_opacity)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        def finished() -> None:
            self._structure_fade_animation = None
            if on_finished is not None:
                on_finished()

        animation.finished.connect(finished)
        self._structure_fade_animation = animation
        animation.start()

    def set_structure_opacity(self, opacity: float) -> None:
        if self._structure_opacity_effect is not None:
            self._structure_opacity_effect.setOpacity(opacity)

    def update_structure_settings_button(self) -> None:
        button = self.structure_settings_button
        if button is None:
            return

        button.setProperty("active", self.structure_display_mode != "closed")
        button.style().unpolish(button)
        button.style().polish(button)
        button.update()

    def tab_changed(self, index: int) -> None:
        if 0 <= index < len(TAB_KEYS):
            self.active_page_key = TAB_KEYS[index]

    def page(self, page_key: str | None = None) -> dict[str, QLabel | QTextEdit]:
        return self.pages.get(page_key or self.active_page_key) or self.pages["workshop"]

    def set_status(self, text: str, state: str = "neutral", page_key: str | None = None) -> None:
        colors = {
            "neutral": ("#d8e0e8", "#3a4652"),
            "running": ("#72c7ff", "#2a6f9e"),
            "success": ("#39ff88", "#1f9b55"),
            "warning": ("#ffd84d", "#b88712"),
            "error": ("#ff4b5f", "#b52535"),
        }
        color, border = colors.get(state, colors["neutral"])
        status_label = self.page(page_key)["status"]
        assert isinstance(status_label, QLabel)
        status_label.setText(text)
        status_label.setStyleSheet(
            "background: #0d0f12; "
            f"color: {color}; "
            f"border: 2px solid {border}; "
            "border-radius: 8px; "
            "padding: 10px; "
            "font-weight: 900;"
        )

    def append_log(self, text: str, page_key: str | None = None) -> None:
        log = self.page(page_key)["log"]
        assert isinstance(log, QTextEdit)
        log.append(text.rstrip())
        log.verticalScrollBar().setValue(log.verticalScrollBar().maximum())

    def clear_log(self, page_key: str | None = None) -> None:
        log = self.page(page_key)["log"]
        assert isinstance(log, QTextEdit)
        log.clear()

    def copy_log_to_clipboard(self, page_key: str | None = None) -> None:
        log = self.page(page_key)["log"]
        assert isinstance(log, QTextEdit)
        QApplication.clipboard().setText(log.toPlainText())
        self.append_log("Log wurde in die Zwischenablage kopiert.", page_key)

    def preview_action(self, page_key: str, message: str) -> None:
        self.set_status("Nur GUI-Vorschau", "warning", page_key)
        self.append_log(message, page_key)
        QTimer.singleShot(900, lambda: self.set_status("GUI isoliert", "neutral", page_key))

    def rightmost_screen_geometry(self):
        screen_geometries = [screen.geometry() for screen in QGuiApplication.screens()]
        if not screen_geometries:
            screen = QGuiApplication.primaryScreen()
            return screen.geometry() if screen is not None else None

        return max(
            screen_geometries,
            key=lambda geometry: (geometry.x() + geometry.width(), geometry.y()),
        )

    def layer1_background_placement(self) -> tuple[QPixmap, int, int] | None:
        if self.layer1_pixmap.isNull():
            return None

        anchor_geometry = self.rightmost_screen_geometry()
        if anchor_geometry is None:
            return None

        if self._layer1_anchor_geometry != anchor_geometry:
            self._layer1_anchor_geometry = anchor_geometry
            self._layer1_scaled_pixmap = self.layer1_pixmap.scaledToHeight(
                max(1, anchor_geometry.height()),
                Qt.TransformationMode.SmoothTransformation,
            )

        if self._layer1_scaled_pixmap.isNull():
            return None

        global_left = anchor_geometry.x() + anchor_geometry.width() - self._layer1_scaled_pixmap.width()
        global_top = anchor_geometry.y() + (anchor_geometry.height() - self._layer1_scaled_pixmap.height()) // 2
        return self._layer1_scaled_pixmap, global_left, global_top

    def activate_existing_instance(self) -> None:
        """Restore and focus the already running DevBox window."""
        if self.isMinimized():
            self.showNormal()
        self.show()
        self.raise_()
        self.activateWindow()
        LOGGER.info("Existing DevBox window was raised and activated.")

    def moveEvent(self, event) -> None:
        super().moveEvent(event)
        if self.root_widget is not None:
            self.root_widget.update()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self.root_widget is not None:
            self.root_widget.update()
        if self.top_logo_bar is not None:
            self.top_logo_bar.update_logos()


def run_gui(base_dir: Path, project_root_path: Path) -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    project_root_path = Path(project_root_path).resolve()

    single_instance = DevBoxSingleInstance(project_root_path)
    if not single_instance.claim_or_activate():
        return 0

    icon_path = project_root_path / "resources" / "graphics" / "devbox.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    window = DevBoxGuiIsolatedWindow(base_dir, project_root_path)
    single_instance.attach_window(window)
    app.aboutToQuit.connect(single_instance.close)
    window.show()
    return app.exec()
