from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class CoverButton(QToolButton):
    def __init__(
        self, image: QImage = None, size: QSize = None, checkable: bool = False
    ):
        super().__init__()
        self._image = image
        if self._image:
            self.setIcon(QIcon(QPixmap.fromImage(image)))
        if size:
            self.setMinimumSize(size)
            self.setIconSize(size)
        self.setCheckable(checkable)
        self.setObjectName("CoverButton")

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, image):
        self._image = image
        self.setIcon(QPixmap.fromImage(image))
