from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from frontend.widgets.abstract_vinyl_widget import AbstractVinylWidget


class VinylListWidget(AbstractVinylWidget):
    IMAGE_SIZE = (50, 50)
    MINIMUM_SIZE = (50, 80)

    def load(self, image):
        super().load(image)
        self.layout = QHBoxLayout(self)
        self.layout.setAlignment(Qt.AlignLeft)
        self.layout.addWidget(self.image_icon)
        self.layout.addWidget(self.name_lbl)
        self.layout.addStretch()
        self.layout.addWidget(self.artist_lbl)
        self.layout.addStretch()
        self.layout.addStretch()
        self.layout.addStretch()
        self.layout.addStretch()

