from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from frontend.widgets.abstract_vinyl_widget import AbstractVinylWidget


class VinylMosaicWidget(AbstractVinylWidget):
    IMAGE_SIZE = (150, 150)
    MINIMUM_SIZE = (150, 180)

    def load(self, image):
        super().load(image)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.image_icon)
        self.layout.addWidget(self.name_lbl)
        self.layout.addWidget(self.artist_lbl)
