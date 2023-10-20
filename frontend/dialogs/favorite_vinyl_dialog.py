from copy import copy

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
)

from frontend.lib.favorite_vinyl_generator import FavoriteVinylGenerator
from frontend.lib.vinyl import Vinyl
from frontend.widgets import HSplitter, VinylListWidget, CoverButton


class FavoriteVinylDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.generator = FavoriteVinylGenerator(copy(self.parent().api.vinyls))
        self.left_vinyl = None
        self.right_vinyl = None

        # Layouts
        self.main_v_layout = None
        self.top_h_layout = None
        self.mid_h_layout = None
        self.left_v_layout = None
        self.right_v_layout = None
        self.bot_h_layout = None

        # Widgets
        self.current_info_lbl = None
        self.current_vinyl_widget = None
        self.h_splitter = None
        self.new_info_lbl = None
        self.round_lbl = None
        self.left_vinyl_btn = None
        self.left_vinyl_lbl = None
        self.left_artist_lbl = None
        self.right_vinyl_btn = None
        self.right_vinyl_lbl = None
        self.right_artist_lbl = None
        self.skip_btn = None

    def init_ui(self):
        self.init_layouts()
        self.init_widgets()
        self.set_layouts()
        self.set_connections()
        self.set_default()
        self.next()

    def init_layouts(self):
        self.main_v_layout = QVBoxLayout(self)
        self.top_h_layout = QHBoxLayout()
        self.mid_h_layout = QHBoxLayout()
        self.left_v_layout = QVBoxLayout()
        self.right_v_layout = QVBoxLayout()
        self.bot_h_layout = QHBoxLayout()

    def init_widgets(self):
        if self.parent().user_data.get("favorite_vinyl"):
            self.current_info_lbl = QLabel("Your last favorite vinyl is :")
            current_favorite_vinyl = Vinyl.from_json(
                self.parent().user_data["favorite_vinyl"]
            )
            self.current_vinyl_widget = VinylListWidget(current_favorite_vinyl)
            self.current_vinyl_widget.load(
                self.parent().api.get_image(current_favorite_vinyl.cover_file_name)
            )
            self.h_splitter = HSplitter()
        self.new_info_lbl = QLabel("Select your favorite vinyl between :")
        self.round_lbl = QLabel(
            f"Round : {self.generator.round}/{self.generator.round_count}"
        )
        self.left_vinyl_btn = CoverButton(size=QSize(200, 200))
        self.left_vinyl_lbl = QLabel()
        self.left_artist_lbl = QLabel()
        self.right_vinyl_btn = CoverButton(size=QSize(200, 200))
        self.right_vinyl_lbl = QLabel()
        self.right_artist_lbl = QLabel()
        self.skip_btn = QPushButton("I can't choose !")

    def set_layouts(self):
        if self.current_info_lbl:
            self.main_v_layout.addWidget(self.current_info_lbl)
        if self.current_vinyl_widget:
            self.main_v_layout.addWidget(self.current_vinyl_widget)
        if self.h_splitter:
            self.main_v_layout.addWidget(self.h_splitter)
        self.main_v_layout.addLayout(self.top_h_layout)
        self.top_h_layout.addWidget(self.new_info_lbl)
        self.top_h_layout.addStretch()
        self.top_h_layout.addWidget(self.round_lbl)
        self.main_v_layout.addLayout(self.mid_h_layout)
        self.mid_h_layout.addLayout(self.left_v_layout)
        self.left_v_layout.addWidget(self.left_vinyl_btn)
        self.left_v_layout.addWidget(self.left_vinyl_lbl)
        self.left_v_layout.addWidget(self.left_artist_lbl)
        self.mid_h_layout.addLayout(self.right_v_layout)
        self.right_v_layout.addWidget(self.right_vinyl_btn)
        self.right_v_layout.addWidget(self.right_vinyl_lbl)
        self.right_v_layout.addWidget(self.right_artist_lbl)
        self.main_v_layout.addStretch()
        self.main_v_layout.addLayout(self.bot_h_layout)
        self.bot_h_layout.addWidget(self.skip_btn)

    def set_connections(self):
        self.left_vinyl_btn.clicked.connect(
            lambda: self.vinyl_selected(self.left_vinyl)
        )
        self.right_vinyl_btn.clicked.connect(
            lambda: self.vinyl_selected(self.right_vinyl)
        )
        self.skip_btn.clicked.connect(lambda: self.next(next_round=False))

    def set_default(self):
        self.setWindowTitle("Define your favorite vinyl")
        for layout, alignment in (
            (self.main_v_layout, Qt.AlignTop),
            (self.top_h_layout, Qt.AlignCenter),
            (self.bot_h_layout, Qt.AlignRight),
        ):
            layout.setAlignment(alignment)
        if self.current_info_lbl:
            self.current_info_lbl.setFont(
                QFont("Segoe UI,9,-1,5,400,0,0,0,0,0,0,0,0,0,0,1", 16)
            )
        self.new_info_lbl.setFont(
            QFont("Segoe UI,9,-1,5,400,0,0,0,0,0,0,0,0,0,0,1", 16)
        )
        self.left_vinyl_lbl.setFont(
            QFont("Segoe UI,9,-1,5,400,0,0,0,0,0,0,0,0,0,0,1", 14)
        )
        self.left_vinyl_lbl.setWordWrap(True)
        self.left_artist_lbl.setWordWrap(True)
        self.right_vinyl_lbl.setFont(
            QFont("Segoe UI,9,-1,5,400,0,0,0,0,0,0,0,0,0,0,1", 14)
        )
        self.right_vinyl_lbl.setWordWrap(True)
        self.right_artist_lbl.setWordWrap(True)

    def exec(self):
        self.init_ui()
        return super().exec()

    def next(self, next_round=True):
        if self.generator.is_last_round():
            self.new_info_lbl.setText("Your favorite vinyl is :")
            to_hide = [
                self.round_lbl,
                self.skip_btn,
                self.left_vinyl_btn
                if self.generator.favorite_vinyl != self.left_vinyl
                else self.right_vinyl_btn,
                self.left_vinyl_lbl
                if self.generator.favorite_vinyl != self.left_vinyl
                else self.right_vinyl_lbl,
                self.left_artist_lbl
                if self.generator.favorite_vinyl != self.left_vinyl
                else self.right_artist_lbl,
            ]
            if self.current_info_lbl:
                to_hide.append(self.current_info_lbl)
            if self.current_vinyl_widget:
                to_hide.append(self.current_vinyl_widget)
            if self.h_splitter:
                to_hide.append(self.h_splitter)
            for widget in to_hide:
                widget.setHidden(True)
            self.parent().api.favorite_vinyl = self.generator.favorite_vinyl.as_dict()
            return

        self.left_vinyl, self.right_vinyl = self.generator.next(next_round=next_round)
        self.round_lbl.setText(
            f"Round : {self.generator.round}/{self.generator.round_count}"
        )
        self.left_vinyl_btn.image = self.parent().api.get_image(
            self.left_vinyl.cover_file_name
        )
        self.left_vinyl_lbl.setText(self.left_vinyl.pretty_name)
        self.left_artist_lbl.setText(self.left_vinyl.artist_pretty_name)
        self.right_vinyl_btn.image = self.parent().api.get_image(
            self.right_vinyl.cover_file_name
        )
        self.right_vinyl_lbl.setText(self.right_vinyl.pretty_name)
        self.right_artist_lbl.setText(self.right_vinyl.artist_pretty_name)

    def vinyl_selected(self, vinyl):
        if vinyl is None or self.generator.is_last_round():
            return
        self.generator.select(vinyl)
        self.next()
