from typing import Tuple, Optional, List
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from random import choice
from copy import copy
import os


class MosaicImageGenerator(object):
    class CoverSizeModes:
        AUTO = 0
        CUSTOM = 1

    def __init__(
        self,
        cover_count: int,
        image_size: Tuple[int, int],
        cover_size: Optional[int],
        cover_size_mode: int,
        cover_images: List[QImage]
    ):
        super().__init__()
        self.cover_count = cover_count
        self.image_size = image_size
        self._cover_size = cover_size
        self.cover_size_mode = cover_size_mode
        self.cover_images = cover_images

    def set_cover_count(self, value: int) -> None:
        self.cover_count = value

    def set_image_size(self, value: Tuple[int, int]) -> None:
        self.image_size = value

    def set_cover_size(self, value: Optional[int]) -> None:
        self.cover_size = value

    def set_cover_size_mode(self, value: int) -> None:
        self.cover_size_mode = value

    @property
    def cover_size(self) -> int:
        return self._cover_size if self.cover_size_mode == self.CoverSizeModes.CUSTOM else self.calculate_cover_size()

    @cover_size.setter
    def cover_size(self, value: Optional[int]):
        self._cover_size = value

    def calculate_cover_size(self) -> int:
        cover_size = max(self.image_size)
        max_width, max_height = self.image_size
        row_count = 1
        while (cover_size * self.cover_count) / row_count > max_width:
            while cover_size * row_count < max_height:
                row_count += 1
            cover_size -= 1
        return cover_size

    def generate(self) -> QPixmap:
        pixmap = QPixmap(*self.image_size)
        painter = QPainter(pixmap)
        painter.fillRect(QRect(0, 0, *self.image_size), Qt.black)

        pos_x = 0
        pos_y = 0
        cover_size = self.cover_size
        cover_images = copy(self.cover_images)
        for i in range(self.cover_count):
            cover = choice(cover_images)
            cover_images.remove(cover)
            cover_pixmap = QPixmap(cover).scaledToWidth(
                self.cover_size or 50,
                Qt.SmoothTransformation
            )
            painter.drawPixmap(QPoint(pos_x, pos_y), cover_pixmap)
            pos_x += cover_size
            if pos_x + cover_size >= self.image_size[0] + 1:
                pos_x = 0
                pos_y += cover_size

        painter.end()
        return pixmap

    @staticmethod
    def save(pixmap: QPixmap, output_path: str) -> None:
        directory = os.path.split(output_path)[0]
        if not os.path.isdir(directory):
            os.makedirs(directory)
        pixmap.save(output_path)
