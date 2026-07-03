from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPen
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)


def _normalize_rgba(value: str) -> str:
    normalized = str(value or "").strip().lstrip("#").lower()
    if len(normalized) == 6:
        normalized += "ff"
    if len(normalized) != 8:
        return "000000ff"
    try:
        int(normalized, 16)
    except ValueError:
        return "000000ff"
    return normalized


class _SaturationValuePlane(QWidget):
    color_changed = Signal(int, int)

    def __init__(self) -> None:
        super().__init__()
        self._hue = 0
        self._saturation = 0
        self._value = 0
        self.setObjectName("DeskNodeUxColorPlane")
        self.setFixedSize(242, 174)
        self.setCursor(Qt.CursorShape.CrossCursor)

    def set_hsv(self, hue: int, saturation: int, value: int) -> None:
        self._hue = max(0, min(359, int(hue)))
        self._saturation = max(0, min(255, int(saturation)))
        self._value = max(0, min(255, int(value)))
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(1, 1, -2, -2)

        painter.fillRect(rect, QColor(255, 255, 255))
        hue_color = QColor.fromHsv(self._hue, 255, 255)
        saturation_gradient = QLinearGradient(rect.left(), rect.top(), rect.right(), rect.top())
        saturation_gradient.setColorAt(0.0, QColor(255, 255, 255))
        saturation_gradient.setColorAt(1.0, hue_color)
        painter.fillRect(rect, saturation_gradient)

        value_gradient = QLinearGradient(rect.left(), rect.top(), rect.left(), rect.bottom())
        value_gradient.setColorAt(0.0, QColor(0, 0, 0, 0))
        value_gradient.setColorAt(1.0, QColor(0, 0, 0, 255))
        painter.fillRect(rect, value_gradient)

        marker_x = rect.left() + round((self._saturation / 255) * rect.width())
        marker_y = rect.bottom() - round((self._value / 255) * rect.height())
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(0, 0, 0), 3))
        painter.drawEllipse(marker_x - 5, marker_y - 5, 10, 10)
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        painter.drawEllipse(marker_x - 5, marker_y - 5, 10, 10)
        painter.setPen(QPen(QColor(82, 196, 218, 230), 1))
        painter.drawRect(rect)
        painter.end()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._select_position(event.position().toPoint())
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if event.buttons() & Qt.MouseButton.LeftButton:
            self._select_position(event.position().toPoint())
        super().mouseMoveEvent(event)

    def _select_position(self, position) -> None:
        rect = self.rect().adjusted(1, 1, -2, -2)
        x = max(rect.left(), min(rect.right(), position.x()))
        y = max(rect.top(), min(rect.bottom(), position.y()))
        self._saturation = round(((x - rect.left()) / max(1, rect.width())) * 255)
        self._value = round(((rect.bottom() - y) / max(1, rect.height())) * 255)
        self.update()
        self.color_changed.emit(self._saturation, self._value)


class _HueStrip(QWidget):
    hue_changed = Signal(int)

    def __init__(self) -> None:
        super().__init__()
        self._hue = 0
        self.setObjectName("DeskNodeUxHueStrip")
        self.setFixedSize(22, 174)
        self.setCursor(Qt.CursorShape.CrossCursor)

    def set_hue(self, hue: int) -> None:
        self._hue = max(0, min(359, int(hue)))
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(3, 1, -4, -2)
        gradient = QLinearGradient(rect.left(), rect.top(), rect.left(), rect.bottom())
        gradient.setColorAt(0.0, QColor.fromHsv(0, 255, 255))
        gradient.setColorAt(1 / 6, QColor.fromHsv(300, 255, 255))
        gradient.setColorAt(2 / 6, QColor.fromHsv(240, 255, 255))
        gradient.setColorAt(3 / 6, QColor.fromHsv(180, 255, 255))
        gradient.setColorAt(4 / 6, QColor.fromHsv(120, 255, 255))
        gradient.setColorAt(5 / 6, QColor.fromHsv(60, 255, 255))
        gradient.setColorAt(1.0, QColor.fromHsv(0, 255, 255))
        painter.fillRect(rect, gradient)

        marker_y = rect.top() + round(((359 - self._hue) / 359) * rect.height())
        painter.setPen(QPen(QColor(0, 0, 0), 3))
        painter.drawLine(1, marker_y, self.width() - 2, marker_y)
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        painter.drawLine(1, marker_y, self.width() - 2, marker_y)
        painter.setPen(QPen(QColor(82, 196, 218, 230), 1))
        painter.drawRect(rect)
        painter.end()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._select_position(event.position().toPoint())
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if event.buttons() & Qt.MouseButton.LeftButton:
            self._select_position(event.position().toPoint())
        super().mouseMoveEvent(event)

    def _select_position(self, position) -> None:
        rect = self.rect().adjusted(3, 1, -4, -2)
        y = max(rect.top(), min(rect.bottom(), position.y()))
        self._hue = round(359 - ((y - rect.top()) / max(1, rect.height())) * 359)
        self.update()
        self.hue_changed.emit(self._hue)




class _AlphaPreview(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._rgba = "000000ff"
        self.setObjectName("DeskNodeUxColorDialogPreview")
        self.setFixedSize(38, 28)

    def set_rgba(self, rgba: str) -> None:
        self._rgba = _normalize_rgba(rgba)
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(1, 1, -2, -2)
        tile = 6
        light = QColor(225, 232, 238)
        dark = QColor(166, 176, 184)
        for y in range(rect.top(), rect.bottom() + 1, tile):
            for x in range(rect.left(), rect.right() + 1, tile):
                use_light = ((x - rect.left()) // tile + (y - rect.top()) // tile) % 2 == 0
                painter.fillRect(x, y, tile, tile, light if use_light else dark)
        color = QColor(
            int(self._rgba[0:2], 16),
            int(self._rgba[2:4], 16),
            int(self._rgba[4:6], 16),
            int(self._rgba[6:8], 16),
        )
        painter.fillRect(rect, color)
        painter.setPen(QPen(QColor(228, 248, 255, 200), 1))
        painter.drawRect(rect)
        painter.end()

class DeskNodeUxColorDialog(QDialog):
    color_changed = Signal(str)

    def __init__(self, rgba_value: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        normalized = _normalize_rgba(rgba_value)
        self._alpha_int = int(normalized[6:8], 16)
        self._color = QColor(
            int(normalized[0:2], 16),
            int(normalized[2:4], 16),
            int(normalized[4:6], 16),
        )
        self._hue = self._color.hsvHue()
        if self._hue < 0:
            self._hue = 0
        self._saturation = self._color.hsvSaturation()
        self._value = self._color.value()

        self.setObjectName("DeskNodeUxColorDialog")
        self.setWindowTitle("Farbe auswählen")
        self.setModal(True)
        self.setMinimumWidth(360)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        title = QLabel("Farbe auswählen")
        title.setObjectName("DeskNodeUxColorDialogTitle")
        layout.addWidget(title)

        hint = QLabel("Die Auswahl ändert Farbton und Deckkraft. Änderungen werden sofort in der Vorschau sichtbar.")
        hint.setObjectName("DeskNodeUxColorDialogHint")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        picker_row = QHBoxLayout()
        picker_row.setSpacing(10)
        self._plane = _SaturationValuePlane()
        self._hue_strip = _HueStrip()
        picker_row.addWidget(self._plane)
        picker_row.addWidget(self._hue_strip)
        picker_row.addStretch(1)
        layout.addLayout(picker_row)

        value_row = QHBoxLayout()
        value_row.setSpacing(10)
        value_label = QLabel("Hex")
        value_label.setObjectName("DeskNodeUxColorDialogFieldLabel")
        self._hex_input = QLineEdit()
        self._hex_input.setObjectName("DeskNodeUxColorDialogHex")
        self._hex_input.setMaxLength(7)
        self._hex_input.setPlaceholderText("#RRGGBB")
        self._preview = _AlphaPreview()
        self._preview.setObjectName("DeskNodeUxColorDialogPreview")
        self._preview.setFixedSize(38, 28)
        value_row.addWidget(value_label)
        value_row.addWidget(self._hex_input, 1)
        value_row.addWidget(self._preview)
        layout.addLayout(value_row)

        alpha_row = QHBoxLayout()
        alpha_row.setSpacing(10)
        alpha_label = QLabel("Deckkraft")
        alpha_label.setObjectName("DeskNodeUxColorDialogFieldLabel")
        self._alpha_slider = QSlider(Qt.Orientation.Horizontal)
        self._alpha_slider.setObjectName("DeskNodeUxColorDialogAlphaSlider")
        self._alpha_slider.setRange(0, 100)
        self._alpha_slider.setSingleStep(1)
        self._alpha_slider.setPageStep(5)
        self._alpha_slider.setValue(round((self._alpha_int / 255) * 100))
        self._alpha_value_label = QLabel("")
        self._alpha_value_label.setObjectName("DeskNodeUxColorDialogAlpha")
        self._alpha_value_label.setMinimumWidth(44)
        self._alpha_value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        alpha_row.addWidget(alpha_label)
        alpha_row.addWidget(self._alpha_slider, 1)
        alpha_row.addWidget(self._alpha_value_label)
        layout.addLayout(alpha_row)

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        cancel_button = QPushButton("Abbrechen")
        cancel_button.setObjectName("DeskNodeUxColorDialogCancelButton")
        apply_button = QPushButton("Übernehmen")
        apply_button.setObjectName("DeskNodeUxColorDialogApplyButton")
        cancel_button.clicked.connect(self.reject)
        apply_button.clicked.connect(self.accept)
        button_row.addWidget(cancel_button)
        button_row.addWidget(apply_button)
        layout.addLayout(button_row)

        self._plane.color_changed.connect(self._set_saturation_value)
        self._hue_strip.hue_changed.connect(self._set_hue)
        self._hex_input.editingFinished.connect(self._apply_hex_value)
        self._hex_input.returnPressed.connect(self.accept)
        self._alpha_slider.valueChanged.connect(self._set_alpha_percent)
        self._sync_widgets()

    def selected_rgba(self) -> str:
        return (
            f"{self._color.red():02x}{self._color.green():02x}"
            f"{self._color.blue():02x}{self._alpha_int:02x}"
        )

    def _set_hue(self, hue: int) -> None:
        self._hue = max(0, min(359, int(hue)))
        self._color = QColor.fromHsv(self._hue, self._saturation, self._value)
        self._sync_widgets()

    def _set_saturation_value(self, saturation: int, value: int) -> None:
        self._saturation = max(0, min(255, int(saturation)))
        self._value = max(0, min(255, int(value)))
        self._color = QColor.fromHsv(self._hue, self._saturation, self._value)
        self._sync_widgets()

    def _set_alpha_percent(self, percent: int) -> None:
        percent = max(0, min(100, int(percent)))
        self._alpha_int = round((percent / 100) * 255)
        self._sync_widgets()

    def _apply_hex_value(self) -> None:
        raw = self._hex_input.text().strip().lstrip("#")
        if len(raw) != 6:
            self._sync_widgets()
            return
        try:
            color = QColor(
                int(raw[0:2], 16),
                int(raw[2:4], 16),
                int(raw[4:6], 16),
            )
        except ValueError:
            self._sync_widgets()
            return
        self._color = color
        hue = color.hsvHue()
        if hue >= 0:
            self._hue = hue
        self._saturation = color.hsvSaturation()
        self._value = color.value()
        self._sync_widgets()

    def _sync_widgets(self) -> None:
        self._plane.set_hsv(self._hue, self._saturation, self._value)
        self._hue_strip.set_hue(self._hue)
        hex_value = f"#{self._color.red():02X}{self._color.green():02X}{self._color.blue():02X}"
        self._hex_input.blockSignals(True)
        self._hex_input.setText(hex_value)
        self._hex_input.blockSignals(False)
        alpha_percent = round((self._alpha_int / 255) * 100)
        self._alpha_slider.blockSignals(True)
        self._alpha_slider.setValue(alpha_percent)
        self._alpha_slider.blockSignals(False)
        self._alpha_value_label.setText(f"{alpha_percent} %")
        self._preview.set_rgba(self.selected_rgba())
        self.color_changed.emit(self.selected_rgba())


def pick_rgba_color(
    parent: QWidget | None,
    rgba_value: str,
    changed=None,
) -> str | None:
    dialog = DeskNodeUxColorDialog(rgba_value, parent)
    if changed is not None:
        dialog.color_changed.connect(changed)
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return None
    return dialog.selected_rgba()
