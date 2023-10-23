from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from frontend.widgets.size_spinbox import SizeSpinbox
from frontend.widgets.splitters import HSplitter, VSplitter
from frontend.lib.utils import make_tool_button
from frontend.lib.mosaic_image_generator import MosaicImageGenerator
import os


class GenerateMosaicDialog(QDialog):
    PREVIEW_MAXIMUM_WIDTH = 1280
    PREVIEW_MAXIMUM_HEIGHT = 720

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.generator = MosaicImageGenerator(
            len(self.parent().api.vinyls),
            (500, 500),
            None,
            MosaicImageGenerator.CoverSizeModes.AUTO,
            [self.parent().api.get_image(v.cover_file_name) for v in self.parent().api.vinyls]
        )
        self.generated_pixmap = None

        # Layouts
        self.main_v_layout = None
        self.settings_h_layout = None
        self.generate_h_layout = None
        self.preview_h_layout = None
        self.output_h_layout = None

        # Widgets
        self.cover_count_lbl = None
        self.cover_count_spn = None
        self.image_size_lbl = None
        self.image_size_spn = None
        self.cover_size_lbl = None
        self.cover_size_cbx = None
        self.custom_cover_size_spn = None
        self.generate_btn = None
        self.preview_image = None
        self.output_path_edt = None
        self.browse_output_path_btn = None
        self.save_btn = None

    def init_ui(self):
        self.init_layouts()
        self.init_widgets()
        self.set_layouts()
        self.set_connections()
        self.set_default()
        self.generate()

    def init_layouts(self):
        self.main_v_layout = QVBoxLayout(self)
        self.settings_h_layout = QHBoxLayout()
        self.generate_h_layout = QHBoxLayout()
        self.preview_h_layout = QHBoxLayout()
        self.output_h_layout = QHBoxLayout()

    def init_widgets(self):
        self.cover_count_lbl = QLabel("Cover count :")
        self.cover_count_spn = QSpinBox()
        self.image_size_lbl = QLabel("Image size :")
        self.image_size_spn = SizeSpinbox()
        self.cover_size_lbl = QLabel("Cover size :")
        self.cover_size_cbx = QComboBox()
        self.custom_cover_size_spn = QSpinBox()
        self.generate_btn = QPushButton("Generate")
        self.preview_image = QLabel()
        self.output_path_edt = QLineEdit()
        self.browse_output_path_btn = make_tool_button("folder.png", tooltip="Browse path")
        self.save_btn = QPushButton("Save")

    def set_layouts(self):
        self.main_v_layout.addLayout(self.settings_h_layout)
        self.settings_h_layout.addWidget(self.cover_count_lbl)
        self.settings_h_layout.addWidget(self.cover_count_spn)
        self.settings_h_layout.addWidget(VSplitter())
        self.settings_h_layout.addWidget(self.image_size_lbl)
        self.settings_h_layout.addWidget(self.image_size_spn)
        self.settings_h_layout.addWidget(VSplitter())
        self.settings_h_layout.addWidget(self.cover_size_lbl)
        self.settings_h_layout.addWidget(self.cover_size_cbx)
        self.settings_h_layout.addWidget(self.custom_cover_size_spn)
        self.main_v_layout.addWidget(HSplitter())
        self.main_v_layout.addLayout(self.generate_h_layout)
        self.generate_h_layout.addWidget(self.generate_btn)
        self.main_v_layout.addLayout(self.preview_h_layout)
        self.preview_h_layout.addWidget(self.preview_image)
        self.main_v_layout.addStretch()
        self.main_v_layout.addWidget(HSplitter())
        self.main_v_layout.addLayout(self.output_h_layout)
        self.output_h_layout.addWidget(self.output_path_edt)
        self.output_h_layout.addWidget(self.browse_output_path_btn)
        self.output_h_layout.addWidget(self.save_btn)

    def set_connections(self):
        self.cover_count_spn.valueChanged.connect(self.cover_count_changed)
        self.image_size_spn.size_changed.connect(
            lambda w, h: (self.generator.set_image_size((w, h)), self.resize_preview_image())
        )
        self.cover_size_cbx.currentIndexChanged.connect(self.cover_size_mode_changed)
        self.custom_cover_size_spn.valueChanged.connect(self.cover_size_changed)
        self.generate_btn.clicked.connect(self.generate)
        self.browse_output_path_btn.clicked.connect(self.browse_output_path)
        self.save_btn.clicked.connect(self.save_image)

    def set_default(self):
        self.setWindowTitle("Generate mosaic image")
        for layout, alignment in (
            (self.main_v_layout, Qt.AlignTop),
            (self.settings_h_layout, Qt.AlignLeft),
            (self.generate_h_layout, Qt.AlignCenter),
            (self.preview_h_layout, Qt.AlignCenter),
            (self.output_h_layout, Qt.AlignLeft),
        ):
            layout.setAlignment(alignment)
        vinyl_count = len(self.parent().api.vinyls)
        self.cover_count_spn.setRange(1, vinyl_count)
        self.cover_count_spn.setValue(25 if 25 <= vinyl_count else vinyl_count)
        self.image_size_spn.set_ranges(5, 2048, 5, 2045)
        self.image_size_spn.set_output_size((500, 500))
        self.cover_size_cbx.addItems(("Auto", "Custom"))
        self.custom_cover_size_spn.setHidden(True)
        self.custom_cover_size_spn.setRange(5, self.PREVIEW_MAXIMUM_WIDTH)
        self.preview_image.setFixedSize(*self.preview_image_size)
        self.preview_image.setStyleSheet(".QLabel{ background-color: #2d3033; }")
        self.output_path_edt.setReadOnly(True)
        self.save_btn.setEnabled(False)

    def exec(self):
        self.init_ui()
        return super().exec()

    def set_cover_size_mode(self, mode):
        self.generator.set_cover_size_mode(mode)
        self.custom_cover_size_spn.setVisible(mode == MosaicImageGenerator.CoverSizeModes.CUSTOM)
        self.generator.set_cover_size(
            self.custom_cover_size_spn.value(
            ) if self.generator.cover_size_mode == MosaicImageGenerator.CoverSizeModes.CUSTOM else None
        )

    def set_cover_size(self, value):
        self.generator.set_cover_size(
            value if self.generator.cover_size_mode == MosaicImageGenerator.CoverSizeModes.CUSTOM else None
        )

    @property
    def preview_image_size(self):
        reel_width = self.image_size_spn.output_width
        reel_height = self.image_size_spn.output_height
        return (
            reel_width if reel_width <= self.PREVIEW_MAXIMUM_WIDTH else self.PREVIEW_MAXIMUM_WIDTH,
            reel_height if reel_height <= self.PREVIEW_MAXIMUM_HEIGHT else self.PREVIEW_MAXIMUM_HEIGHT
        )

    def resize_preview_image(self):
        self.preview_image.setFixedSize(*self.preview_image_size)
        self.draw_preview()

    def cover_count_changed(self, value):
        self.generator.set_cover_count(value)
        self.generate()

    def cover_size_mode_changed(self, mode):
        self.set_cover_size_mode(mode)
        self.generate()

    def cover_size_changed(self, value):
        self.set_cover_size(value)
        self.generate()

    def generate(self):
        self.generated_pixmap = self.generator.generate()
        self.draw_preview()

    def draw_preview(self):
        preview_pixmap = self.generated_pixmap.scaled(
            QSize(*self.preview_image_size),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.preview_image.setPixmap(preview_pixmap)

    def browse_output_path(self):
        output_path, _ = QFileDialog.getSaveFileName(
            self.parent(),
            "Output path",
            f"{os.environ['USERPROFILE']}",
            "*.png"
        )
        if not output_path:
            self.output_path_edt.clear()
            self.save_btn.setEnabled(False)
            return
        self.output_path_edt.setText(output_path.replace("\\", "/"))
        self.save_btn.setEnabled(True)

    def save_image(self):
        if not self.generated_pixmap:
            raise ValueError("No pixmap was generated")
        output_path = self.output_path_edt.text()
        if not output_path:
            raise ValueError("No output path provided")
        self.generator.save(self.generated_pixmap, output_path)

