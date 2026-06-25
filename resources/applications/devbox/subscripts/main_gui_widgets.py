from __future__ import annotations

from subscripts.main_gui_devbox_log import get_devbox_logger
LOGGER = get_devbox_logger(__file__)
LOGGER.info("Module loaded.")


from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import QFileDialog, QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout

from subscripts.main_gui_config import (
    COLOR_DESIRED_OFF,
    COLOR_DESIRED_ON,
    COLOR_LIVE_OFF,
    COLOR_LIVE_ON,
    COLOR_PENDING,
)

if TYPE_CHECKING:
    from subscripts.main_gui_window import DevBoxGuiIsolatedWindow


class StudioRootWidget(QFrame):
    def __init__(self, studio: "DevBoxGuiIsolatedWindow") -> None:
        super().__init__()
        self.studio = studio
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.GlobalColor.black)

        placement = self.studio.layer1_background_placement()
        if placement is not None:
            scaled, global_left, global_top = placement
            global_top_left = self.mapToGlobal(QPoint(0, 0))
            draw_x = global_left - global_top_left.x()
            draw_y = global_top - global_top_left.y()
            painter.drawPixmap(draw_x, draw_y, scaled)

        super().paintEvent(event)


class StudioTopBar(QFrame):
    def __init__(self, studio: "DevBoxGuiIsolatedWindow") -> None:
        super().__init__()
        self.studio = studio
        self.drag_offset: QPoint | None = None
        self.setObjectName("TopLogoBar")
        self.setMinimumHeight(76)
        self.setMaximumHeight(96)
        self.setCursor(Qt.CursorShape.SizeAllCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(10)

        self.left_logo_label = QLabel()
        self.left_logo_label.setObjectName("TopLogoLabel")
        self.left_logo_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.left_logo_label, stretch=0)

        layout.addStretch(1)

        self.right_logo_label = QLabel()
        self.right_logo_label.setObjectName("TopLogoLabel")
        self.right_logo_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.right_logo_label, stretch=0)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.update_logos()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.update_logos()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_offset = event.globalPosition().toPoint() - self.studio.frameGeometry().topLeft()
            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self.drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.studio.move(event.globalPosition().toPoint() - self.drag_offset)
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        self.drag_offset = None
        super().mouseReleaseEvent(event)

    def update_logos(self) -> None:
        target_height = max(1, self.height() - 20)
        self.apply_logo(self.left_logo_label, self.studio.layer2_left_path, target_height)
        self.apply_logo(self.right_logo_label, self.studio.layer2_right_path, target_height)

    @staticmethod
    def apply_logo(label: QLabel, path: Path, target_height: int) -> None:
        if path.exists():
            pixmap = QPixmap(str(path))
            if not pixmap.isNull():
                label.setPixmap(pixmap.scaledToHeight(target_height, Qt.TransformationMode.SmoothTransformation))
                return
        label.clear()


class RepositoryImageDropBox(QFrame):
    """Optional image picker used by the repository page.

    The widget only collects image paths for now. Copying and normalization are
    intentionally left to the later push schema so the GUI remains separate
    from the DevBox repository process.
    """

    files_changed = Signal(list)
    IMAGE_SUFFIXES = {
        ".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tif", ".tiff",
    }

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("RepositoryImageDropBox")
        self.setMinimumSize(176, 142)
        self.setAcceptDrops(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._image_files: list[Path] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(4)

        crosshair = QLabel("⌖")
        crosshair.setAlignment(Qt.AlignmentFlag.AlignCenter)
        crosshair.setObjectName("RepositoryImageCrosshair")
        layout.addWidget(crosshair, stretch=1)

        self.info_label = QLabel("Bilder\nhierherziehen\noder anklicken")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setWordWrap(True)
        self.info_label.setObjectName("Subtitle")
        layout.addWidget(self.info_label)

        self.count_label = QLabel("0 Datei(en)")
        self.count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.count_label.setObjectName("SubtitleSmall")
        layout.addWidget(self.count_label)

        self.setToolTip("Bilddateien hinzufügen (optional)")
        self.setAccessibleName("Optionale Bilddateien für das Repository")

    def image_files(self) -> list[Path]:
        return list(self._image_files)

    def clear_files(self) -> None:
        self.set_image_files([])

    def set_image_files(self, file_paths: list[Path]) -> None:
        normalized: list[Path] = []
        seen: set[str] = set()

        for file_path in file_paths:
            path = Path(file_path).expanduser()
            if not path.is_file() or path.suffix.lower() not in self.IMAGE_SUFFIXES:
                continue
            key = str(path.resolve()).casefold()
            if key in seen:
                continue
            seen.add(key)
            normalized.append(path.resolve())

        self._image_files = normalized
        count = len(self._image_files)
        self.count_label.setText(f"{count} Datei(en)")
        self.files_changed.emit(self.image_files())

    def dragEnterEvent(self, event) -> None:
        mime_data = event.mimeData()
        if not mime_data.hasUrls():
            event.ignore()
            return

        for url in mime_data.urls():
            if url.isLocalFile() and Path(url.toLocalFile()).suffix.lower() in self.IMAGE_SUFFIXES:
                event.acceptProposedAction()
                return
        event.ignore()

    def dropEvent(self, event) -> None:
        paths = [
            Path(url.toLocalFile())
            for url in event.mimeData().urls()
            if url.isLocalFile()
        ]
        self.set_image_files([*self._image_files, *paths])
        event.acceptProposedAction()

    def mousePressEvent(self, event) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return

        selected_files, _ = QFileDialog.getOpenFileNames(
            self,
            "Bilddateien auswählen",
            "",
            "Bilddateien (*.png *.jpg *.jpeg *.webp *.bmp *.gif *.tif *.tiff)",
        )
        if selected_files:
            self.set_image_files([
                *self._image_files,
                *(Path(item) for item in selected_files),
            ])
        event.accept()


# Compatibility alias for older callers until all historical references have
# been removed from external snapshots.
GitPublisherImageDropBox = RepositoryImageDropBox


class DemoDeviceCard(QPushButton):
    def __init__(self, name: str, model: str, power: float, desired_on: bool, live_on: bool) -> None:
        super().__init__()
        self.setMinimumHeight(84)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setText(f"{name}\n{power:.1f} W")
        self.setToolTip(f"Demo-Gerät: {model}")

        border_color = COLOR_LIVE_ON if live_on else COLOR_LIVE_OFF
        bg_color = COLOR_DESIRED_ON if desired_on else COLOR_DESIRED_OFF
        if desired_on != live_on:
            border_color = COLOR_PENDING

        self.setStyleSheet(
            f"QPushButton {{ background: {bg_color}; color: #ffffff; "
            f"border: 2px solid {border_color}; border-radius: 12px; "
            "font-weight: 900; font-size: 11pt; padding: 8px; }}"
            "QPushButton:hover { border-width: 3px; }"
        )
