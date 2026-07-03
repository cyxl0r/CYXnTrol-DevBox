from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QRegularExpression, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QRegularExpressionValidator
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QWidget

from subscripts.main_gui_desknode_ux_color_dialog import pick_rgba_color
from subscripts.main_gui_desknode_ux_defaults import is_valid_rgba


class RgbaPreview(QWidget):
    """Clickable RGBA preview with a checkerboard transparency background."""

    clicked = Signal()

    def __init__(self, value: str = "00000000") -> None:
        super().__init__()
        self._rgba_value = "00000000"
        self._hovered = False
        self.setObjectName("DeskNodeUxColorPreview")
        self.setFixedSize(28, 28)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.set_rgba(value)

    def set_rgba(self, value: str) -> None:
        if not is_valid_rgba(value):
            return
        self._rgba_value = value.lower()
        self.update()

    def enterEvent(self, event) -> None:
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if (
            event.button() == Qt.MouseButton.LeftButton
            and self.rect().contains(event.position().toPoint())
        ):
            self.clicked.emit()
        super().mouseReleaseEvent(event)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(1, 1, -2, -2)
        tile_size = 5
        light = QColor(225, 232, 238)
        dark = QColor(166, 176, 184)
        for y in range(rect.top(), rect.bottom() + 1, tile_size):
            for x in range(rect.left(), rect.right() + 1, tile_size):
                use_light = ((x - rect.left()) // tile_size + (y - rect.top()) // tile_size) % 2 == 0
                painter.fillRect(x, y, tile_size, tile_size, light if use_light else dark)
        rgba = self._rgba_value
        color = QColor(
            int(rgba[0:2], 16),
            int(rgba[2:4], 16),
            int(rgba[4:6], 16),
            int(rgba[6:8], 16),
        )
        painter.fillRect(rect, color)
        border = QColor(119, 255, 247, 245) if self._hovered else QColor(228, 248, 255, 180)
        painter.setPen(border)
        painter.drawRect(rect)
        painter.end()


def refresh_widget_style(widget: QWidget) -> None:
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()


def build_rgba_input(
    value: str,
    changed: Callable[[], None] | None = None,
) -> tuple[QWidget, QLineEdit]:
    container = QWidget()
    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)

    input_field = QLineEdit(value.lower())
    input_field.setObjectName("DeskNodeUxColorInput")
    input_field.setMaxLength(8)
    input_field.setMinimumWidth(135)
    input_field.setAlignment(Qt.AlignmentFlag.AlignCenter)
    input_field.setValidator(
        QRegularExpressionValidator(
            QRegularExpression("[0-9A-Fa-f]{0,8}"),
            input_field,
        )
    )
    preview = RgbaPreview(value)
    preview.setToolTip(
        "Klicken, um Farbe und Deckkraft auszuwählen."
    )
    layout.addWidget(input_field)
    layout.addWidget(preview)
    layout.addStretch(1)

    def update_state() -> None:
        current_value = input_field.text().strip().lower()
        valid = is_valid_rgba(current_value)
        input_field.setProperty("invalid_rgba", not valid)
        refresh_widget_style(input_field)

        if valid:
            preview.set_rgba(current_value)

        if changed is not None:
            changed()

    def choose_color() -> None:
        current_value = input_field.text().strip().lower()
        if not is_valid_rgba(current_value):
            input_field.setFocus()
            return

        def apply_live_value(value: str) -> None:
            if input_field.text().strip().lower() != value:
                input_field.setText(value)

        selected_value = pick_rgba_color(
            container.window(),
            current_value,
            apply_live_value,
        )
        if selected_value is None:
            input_field.setText(current_value)
        elif input_field.text().strip().lower() != selected_value:
            input_field.setText(selected_value)

    input_field.textChanged.connect(lambda _text: update_state())
    preview.clicked.connect(choose_color)
    update_state()
    return container, input_field
