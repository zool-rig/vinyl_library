# -*- coding: utf-8 -*-
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QCompleter,
)

from frontend.dialogs.select_cover_file_dialog import CoverSelectorDialog
from frontend.lib.utils import make_tool_button
from frontend.widgets import HSplitter, CoverButton


class EditVinylDialog(QDialog):
    def __init__(
        self, parent, api, cover_file_name="no_image.jpg", vinyl_name="", artist_name=""
    ):
        super().__init__(parent=parent)
        self.api = api
        self.ok = False
        self._cover_file_name = cover_file_name
        self._vinyl_name = vinyl_name
        self._artist_name = artist_name

        # Layouts
        self.main_v_layout = None
        self.main_h_layout = None
        self.right_v_layout = None
        self.vinyl_h_layout = None
        self.artist_h_layout = None
        self.name_action_h_layout = None
        self.action_h_layout = None

        # Widgets
        self.image_btn = None
        self.vinyl_lbl = None
        self.vinyl_edt = None
        self.artist_lbl = None
        self.artist_edt = None
        self.copy_btn = None
        self.google_btn = None
        self.ok_btn = None
        self.cancel_btn = None

    def init_ui(self):
        self.init_layouts()
        self.init_widgets()
        self.set_layouts()
        self.set_connections()
        self.set_default()

    def init_layouts(self):
        self.main_v_layout = QVBoxLayout(self)
        self.main_h_layout = QHBoxLayout()
        self.right_v_layout = QVBoxLayout()
        self.vinyl_h_layout = QHBoxLayout()
        self.artist_h_layout = QHBoxLayout()
        self.name_action_h_layout = QHBoxLayout()
        self.action_h_layout = QHBoxLayout()

    def init_widgets(self):
        self.image_btn = CoverButton(size=QSize(150, 150))
        self.vinyl_lbl = QLabel("Vinyl name : ")
        self.vinyl_edt = QLineEdit()
        self.artist_lbl = QLabel("Artist name :")
        self.artist_edt = QLineEdit()
        self.copy_btn = make_tool_button(
            "clipboard.png", "Copy the vinyl's and artist's name to clipboard"
        )
        self.google_btn = make_tool_button(
            "google.png", "search the vinyl's and artist's name on google"
        )
        self.ok_btn = QPushButton("OK")
        self.cancel_btn = QPushButton("Cancel")

    def set_layouts(self):
        self.main_v_layout.addLayout(self.main_h_layout)
        self.main_h_layout.addWidget(self.image_btn)
        self.main_h_layout.addLayout(self.right_v_layout)
        self.right_v_layout.addLayout(self.vinyl_h_layout)
        self.vinyl_h_layout.addWidget(self.vinyl_lbl)
        self.vinyl_h_layout.addWidget(self.vinyl_edt)
        self.right_v_layout.addLayout(self.artist_h_layout)
        self.artist_h_layout.addWidget(self.artist_lbl)
        self.artist_h_layout.addWidget(self.artist_edt)
        self.right_v_layout.addLayout(self.name_action_h_layout)
        self.name_action_h_layout.addWidget(self.copy_btn)
        self.name_action_h_layout.addWidget(self.google_btn)
        self.main_v_layout.addWidget(HSplitter())
        self.main_v_layout.addLayout(self.action_h_layout)
        self.action_h_layout.addWidget(self.ok_btn)
        self.action_h_layout.addWidget(self.cancel_btn)

    def set_connections(self):
        self.image_btn.clicked.connect(self.browse_cover)
        self.vinyl_edt.textChanged.connect(self.check)
        self.artist_edt.textChanged.connect(self.check)
        self.copy_btn.clicked.connect(
            lambda: self.api.copy_to_clipboard(f"{self.vinyl_name} {self.artist_name}")
        )
        self.google_btn.clicked.connect(
            lambda: self.api.search_on_google(f"{self.vinyl_name} {self.artist_name}")
        )
        self.ok_btn.clicked.connect(lambda: (setattr(self, "ok", True), self.close()))
        self.cancel_btn.clicked.connect(self.close)

    def set_default(self):
        self.setWindowTitle("Edit vinyl")
        for layout, alignment in (
            (self.main_v_layout, Qt.AlignTop),
            (self.right_v_layout, Qt.AlignTop),
            (self.vinyl_h_layout, Qt.AlignLeft),
            (self.artist_h_layout, Qt.AlignLeft),
            (self.action_h_layout, Qt.AlignRight),
            (self.name_action_h_layout, Qt.AlignRight),
        ):
            layout.setAlignment(alignment)
        self.cover_file_name = self._cover_file_name
        self.vinyl_name = self._vinyl_name
        self.artist_name = self._artist_name
        completer = QCompleter([artist.name for artist in self.api.artists])
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.artist_edt.setCompleter(completer)
        self.check()
        self.vinyl_edt.setFocus()

    def exec(self):
        self.init_ui()
        super().exec()
        return self.ok, self.data if self.ok else None

    @property
    def cover_file_name(self):
        return self._cover_file_name

    @cover_file_name.setter
    def cover_file_name(self, value):
        self._cover_file_name = value
        self.image_btn.image = self.api.get_image(value)

    def browse_cover(self):
        ok, image = CoverSelectorDialog.select_cover(self)
        if ok:
            self._cover_file_name = image.name
            self.image_btn.image = image

    @property
    def vinyl_name(self):
        return self.vinyl_edt.text()

    @vinyl_name.setter
    def vinyl_name(self, value):
        self.vinyl_edt.setText(value)

    @property
    def artist_name(self):
        return self.artist_edt.text()

    @artist_name.setter
    def artist_name(self, value):
        self.artist_edt.setText(value)

    @property
    def data(self):
        return {
            "cover_file_name": self.cover_file_name,
            "vinyl_name": self.vinyl_name,
            "artist_name": self.artist_name,
        }

    def check(self, *_):
        self.ok_btn.setEnabled(bool(self.vinyl_name) and bool(self.artist_name))
