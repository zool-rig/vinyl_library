from typing import Tuple

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QSpinBox,
)


class SizeSpinbox(QWidget):
    size_changed = Signal(int, int)

    def __init__(self):
        super().__init__()
        self._layout = QHBoxLayout(self)
        self._width_spn = QSpinBox()
        self._height_spn = QSpinBox()

        self._layout.addWidget(self._width_spn)
        self._layout.addWidget(self._height_spn)

        self._width_spn.valueChanged.connect(
            lambda w: self.size_changed.emit(w, self._height_spn.value())
        )
        self._height_spn.valueChanged.connect(
            lambda h: self.size_changed.emit(self._width_spn.value(), h)
        )

    def get_output_width(self) -> int:
        return self._width_spn.value()

    def set_output_width(self, value: int) -> None:
        self._width_spn.setValue(value)

    @property
    def output_width(self) -> int:
        return self.get_output_width()

    @output_width.setter
    def output_width(self, value: int) -> None:
        self.set_output_width(value)

    def get_output_height(self) -> int:
        return self._height_spn.value()

    def set_output_height(self, value: int) -> None:
        self._height_spn.setValue(value)

    @property
    def output_height(self) -> int:
        return self.get_output_height()

    @output_height.setter
    def output_height(self, value: int) -> None:
        self.set_output_height(value)

    def get_output_size(self) -> Tuple[int, int]:
        return self.output_width, self.output_height

    def set_output_size(self, value: Tuple[int, int]) -> None:
        self.output_width, self.output_height = value

    @property
    def output_size(self) -> Tuple[int, int]:
        return self.get_output_size()

    @output_size.setter
    def output_size(self, value: Tuple[int, int]) -> None:
        self.set_output_size(value)

    def get_width_range(self) -> Tuple[int, int]:
        return self._width_spn.minimum(), self._width_spn.maximum()

    def set_width_range(self, min_: int, max_: int) -> None:
        self._width_spn.setRange(min_, max_)

    @property
    def width_range(self) -> Tuple[int, int]:
        return self.get_width_range()

    @width_range.setter
    def width_range(self, value: Tuple[int, int]) -> None:
        self.set_width_range(*value)

    def get_height_range(self) -> Tuple[int, int]:
        return self._height_spn.minimum(), self._height_spn.maximum()

    def set_height_range(self, min_: int, max_: int) -> None:
        self._height_spn.setRange(min_, max_)

    @property
    def height_range(self) -> Tuple[int, int]:
        return self.get_height_range()

    @height_range.setter
    def height_range(self, value: Tuple[int, int]) -> None:
        self.set_height_range(*value)

    def get_ranges(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        return self.width_range, self.height_range

    def set_ranges(self, min_w: int, max_w: int, min_h: int, max_h: int) -> None:
        self.set_width_range(min_w, max_w)
        self.set_height_range(min_h, max_h)

    @property
    def ranges(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        return self.get_ranges()

    @ranges.setter
    def ranges(self, value: Tuple[Tuple[int, int], Tuple[int, int]]) -> None:
        w_range, h_range = value
        min_w, max_w = w_range
        min_h, max_h = h_range
        self.set_ranges(min_w, max_w, min_h, max_h)
