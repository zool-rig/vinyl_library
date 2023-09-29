# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QHBoxLayout

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
        self.layout.addSpacing(10)
        self.layout.addWidget(self.name_lbl)
        self.layout.addStretch()
        self.layout.addWidget(self.artist_lbl)
        self.name_lbl.setWordWrap(True)
        self.artist_lbl.setWordWrap(True)
