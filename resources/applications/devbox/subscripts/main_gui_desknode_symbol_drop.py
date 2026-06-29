from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QMouseEvent
from PySide6.QtWidgets import QFileDialog, QFrame, QLabel, QVBoxLayout


class PngDropField(QFrame):
    file_changed = Signal(object)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._source_file: Path | None = None
        self.setObjectName("DeskNodeSymbolPngDrop")
        self.setAcceptDrops(True)
        self.setMinimumHeight(74)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(9, 7, 9, 7)
        layout.setSpacing(2)

        self.title = QLabel("PNG hier ablegen oder anklicken")
        self.title.setObjectName("DeskNodeSymbolPngDropTitle")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title)

        self.detail = QLabel("Genau eine .png-Datei")
        self.detail.setObjectName("DeskNodeSymbolPngDropDetail")
        self.detail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.detail)

        self._refresh()

    @property
    def source_file(self) -> Path | None:
        return self._source_file

    def clear_file(self) -> None:
        self._source_file = None
        self._refresh()
        self.file_changed.emit(None)

    def set_file(self, source_file: Path | None) -> None:
        if source_file is None:
            self.clear_file()
            return

        source_file = Path(source_file).resolve()

        if not source_file.is_file() or source_file.suffix.casefold() != ".png":
            self.detail.setText("Ungültig: genau eine PNG-Datei erforderlich")
            self.setProperty("invalid", True)
            self._refresh()
            return

        self._source_file = source_file
        self.setProperty("invalid", False)
        self._refresh()
        self.file_changed.emit(source_file)

    def _refresh(self) -> None:
        has_file = self._source_file is not None
        self.setProperty("has_file", has_file)

        if has_file:
            self.title.setText(self._source_file.name)
            self.detail.setText("Neue PNG wird beim Speichern übernommen")
        elif not bool(self.property("invalid")):
            self.title.setText("PNG hier ablegen oder anklicken")
            self.detail.setText("Genau eine .png-Datei")

        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        mime_data = event.mimeData()
        urls = mime_data.urls() if mime_data.hasUrls() else []

        if len(urls) == 1 and urls[0].isLocalFile():
            path = Path(urls[0].toLocalFile())

            if path.suffix.casefold() == ".png":
                event.acceptProposedAction()
                return

        event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        urls = event.mimeData().urls()

        if len(urls) != 1 or not urls[0].isLocalFile():
            event.ignore()
            return

        self.set_file(Path(urls[0].toLocalFile()))
        event.acceptProposedAction()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            file_name, _selected_filter = QFileDialog.getOpenFileName(
                self,
                "PNG-Quelle auswählen",
                "",
                "PNG-Dateien (*.png)",
            )

            if file_name:
                self.set_file(Path(file_name))

            event.accept()
            return

        super().mousePressEvent(event)
