# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QVBoxLayout

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
        self.name_lbl.setWordWrap(True)
        self.artist_lbl.setWordWrap(True)
