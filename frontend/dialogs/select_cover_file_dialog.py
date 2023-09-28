import os
from functools import partial

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from frontend.widgets import FlowLayout
from frontend.widgets import HSplitter


class CoverSelectorDialog(QDialog):
    @classmethod
    def select_cover(cls, parent):
        dialog = cls(parent)
        return dialog.exec()

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.images = self.parent().api.get_images()
        self.image_buttons = list()
        self.selected_image = None
        self.ok = False
        
        # Layouts
        self.v_layout = None
        self.flow_layout = None
        self.actions_h_layout = None
        
        # Widgets
        self.upload_btn = None
        self.existing_images_lbl = None
        self.scroll_area = None
        self.scroll_area_widget = None
        self.apply_selected_btn = None
        self.cancel_btn = None

    def init_ui(self):
        self.init_layouts()
        self.init_widgets()
        self.set_layouts()
        self.set_connections()
        self.set_default()
        self.fill_existing_images()

    def init_layouts(self):
        self.v_layout = QVBoxLayout(self)
        self.flow_layout = FlowLayout()
        self.actions_h_layout = QHBoxLayout()

    def init_widgets(self):
        self.upload_btn = QPushButton("Upload image")
        self.existing_images_lbl = QLabel("Existing images :")
        self.scroll_area = QScrollArea()
        self.scroll_area_widget = QWidget()
        self.apply_selected_btn = QPushButton("Apply selected image")
        self.cancel_btn = QPushButton("Cancel")
    
    def set_layouts(self):
        self.v_layout.addWidget(self.upload_btn)
        self.v_layout.addWidget(HSplitter())
        self.v_layout.addWidget(self.existing_images_lbl)
        self.v_layout.addWidget(self.scroll_area)
        self.scroll_area.setWidget(self.scroll_area_widget)
        self.scroll_area_widget.setLayout(self.flow_layout)
        self.v_layout.addLayout(self.actions_h_layout)
        self.actions_h_layout.addWidget(self.apply_selected_btn)
        self.actions_h_layout.addWidget(self.cancel_btn)

    def set_connections(self):
        self.upload_btn.clicked.connect(self.upload)
        self.apply_selected_btn.clicked.connect(self.ok_close)
        self.cancel_btn.clicked.connect(self.close)

    def set_default(self):
        self.setWindowTitle("Select a cover image")
        self.v_layout.setAlignment(Qt.AlignTop)
        self.actions_h_layout.setAlignment(Qt.AlignRight)
        self.scroll_area.setWidgetResizable(True)
        self.apply_selected_btn.setEnabled(False)

    def exec(self):
        self.init_ui()
        super().exec()
        return self.ok, self.selected_image

    def showEvent(self, arg__1):
        self.resize(400, 500)

    def existing_image_selected(self, button):
        state = button.isChecked()
        for btn in self.image_buttons:
            if btn != button and state:
                btn.setChecked(False)
        self.selected_image = button.image if state else None
        self.apply_selected_btn.setEnabled(state)

    def fill_existing_images(self):
        for image in self.images:
            button = QToolButton()
            button.setIcon(QIcon(QPixmap.fromImage(image)))
            button.setIconSize(QSize(100, 100))
            button.setCheckable(True)
            button.clicked.connect(partial(self.existing_image_selected, button))
            setattr(button, "image", image)
            self.flow_layout.addWidget(button)
            self.image_buttons.append(button)
            button.setObjectName("CoverButton")

    def upload(self):
        image_path, _ = QFileDialog.getOpenFileName(
            self,
            "Browse cover image",
            f"{os.environ['HOMEDRIVE']}{os.environ['HOMEPATH']}",
            "Images (*.png *.jpeg *.jpg)"
        )
        if not image_path:
            return

        self.selected_image = self.parent().api.upload_image(image_path)
        self.ok_close()

    def ok_close(self):
        self.ok = True
        self.close()
