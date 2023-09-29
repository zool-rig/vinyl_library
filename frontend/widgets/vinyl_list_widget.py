from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from frontend.widgets.abstract_vinyl_widget import AbstractVinylWidget


class VinylListWidget(AbstractVinylWidget):
    IMAGE_SIZE = (50, 50)
    MINIMUM_SIZE = (50, 80)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def load(self, image):
        super().load(image)
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.image_icon)
        self.layout.addWidget(self.name_lbl)
        self.name_lbl.setFont(QFont("Segoe UI,9,-1,5,400,0,0,0,0,0,0,0,0,0,0,1", 14))
        self.layout.addWidget(self.artist_lbl)
