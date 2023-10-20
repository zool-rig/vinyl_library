# -*- coding: utf-8 -*-
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QPushButton,
    QScrollArea,
    QWidget,
)

from frontend.widgets import HSplitter, VinylListWidget


class ShuffleVinylsDialog(QDialog):
    DEFAULT_COUNT = 10

    def __init__(self, parent):
        super().__init__(parent)

        # Layouts
        self.main_v_layout = None
        self.count_h_layout = None
        self.scroll_area_v_layout = None

        # Widgets
        self.count_lbl = None
        self.count_spn = None
        self.shuffle_btn = None
        self.scroll_area = None
        self.scroll_area_widget = None
        self.vinyl_widgets = list()

    def init_ui(self):
        self.init_layouts()
        self.init_widgets()
        self.set_layouts()
        self.set_connections()
        self.set_default()

    def init_layouts(self):
        self.main_v_layout = QVBoxLayout(self)
        self.count_h_layout = QHBoxLayout()
        self.scroll_area_v_layout = QVBoxLayout()

    def init_widgets(self):
        self.count_lbl = QLabel("Count :")
        self.count_spn = QSpinBox()
        self.shuffle_btn = QPushButton("Shuffle")
        self.scroll_area = QScrollArea()
        self.scroll_area_widget = QWidget()

    def set_layouts(self):
        self.main_v_layout.addLayout(self.count_h_layout)
        self.count_h_layout.addWidget(self.count_lbl)
        self.count_h_layout.addWidget(self.count_spn)
        self.main_v_layout.addWidget(self.shuffle_btn)
        self.main_v_layout.addWidget(HSplitter())
        self.main_v_layout.addWidget(self.scroll_area)
        self.scroll_area.setWidget(self.scroll_area_widget)
        self.scroll_area_widget.setLayout(self.scroll_area_v_layout)

    def set_connections(self):
        self.shuffle_btn.clicked.connect(self.shuffle)

    def set_default(self):
        self.setWindowTitle("Shuffle Vinyls")
        self.main_v_layout.setAlignment(Qt.AlignTop)
        self.count_h_layout.setAlignment(Qt.AlignCenter)
        self.scroll_area_v_layout.setAlignment(Qt.AlignTop)
        self.count_spn.setRange(1, (32**2) - 1)
        self.count_spn.setValue(self.DEFAULT_COUNT)
        self.scroll_area.setWidgetResizable(True)

    def exec(self):
        self.init_ui()
        super().exec()

    def showEvent(self, arg__1):
        self.setGeometry(self.pos().x() - 300, self.pos().y() - 400, 600, 800)

    def clear(self):
        for widget in self.vinyl_widgets:
            widget.deleteLater()
        self.vinyl_widgets = list()

    def shuffle(self):
        self.clear()
        vinyls = self.parent().api.shuffle_vinyls(self.count_spn.value())
        for vinyl in vinyls:
            widget = VinylListWidget(vinyl)
            widget.load(self.parent().api.get_image(widget.vinyl.cover_file_name))
            self.scroll_area_v_layout.addWidget(widget)
            self.vinyl_widgets.append(widget)
