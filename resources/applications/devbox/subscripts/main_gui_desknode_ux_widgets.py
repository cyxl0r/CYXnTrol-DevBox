from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QRegularExpression, Qt
from PySide6.QtGui import QColor, QPainter, QRegularExpressionValidator
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLineEdit, QWidget

from subscripts.main_gui_desknode_ux_defaults import is_valid_rgba


class RgbaPreview(QFrame):
    """Small checkerboard-backed color preview for an RGBA value."""

    def __init__(self, value: str = "00000000") -> None:
        super().__init__()
        self._rgba_value = "00000000"
        self.setObjectName("DeskNodeUxColorPreview")
        self.setFixedSize(28, 28)
        self.set_rgba(value)

    def set_rgba(self, value: str) -> None:
        if not is_valid_rgba(value):
            return
        self._rgba_value = value.lower()
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        size = 6
        light = QColor(214, 222, 225)
        dark = QColor(122, 136, 142)

        for y in range(0, self.height(), size):
            for x in range(0, self.width(), size):
                index = (x // size) + (y // size)
                painter.fillRect(
                    x,
                    y,
                    size,
                    size,
                    light if index % 2 == 0 else dark,
                )

        rgba = self._rgba_value
        color = QColor(
            int(rgba[0:2], 16),
            int(rgba[2:4], 16),
            int(rgba[4:6], 16),
            int(rgba[6:8], 16),
        )
        painter.fillRect(self.rect(), color)
        painter.setPen(QColor(228, 248, 255, 180))
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))
        painter.end()
        super().paintEvent(event)


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

    input_field.textChanged.connect(lambda _text: update_state())
    update_state()
    return container, input_field
