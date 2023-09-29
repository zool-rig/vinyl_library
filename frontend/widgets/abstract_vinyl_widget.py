from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from frontend.lib.utils import get_image_average_pixel_color, make_icon


class AbstractVinylWidget(QWidget):
    IMAGE_SIZE = (0, 0)
    MINIMUM_SIZE = (0, 0)
    LARGE_IMAGE_SIZE = (500, 500)
    edit_requested = Signal(QObject)
    delete_requested = Signal(QObject)
    listen_requested = Signal(str, object)

    def __init__(self, vinyl):
        super().__init__()
        self.vinyl = vinyl
        self.layout = None
        self.image_icon = None
        self.name_lbl = None
        self.artist_lbl = None
        self.is_loaded = False
        self.image_average_color = QColor()
        self.image = None
        self.setMinimumSize(*self.MINIMUM_SIZE)

    def load(self, image):
        self.image_icon = QLabel()
        self.name_lbl = QLabel(self.vinyl.pretty_name)
        self.artist_lbl = QLabel(self.vinyl.artist_pretty_name)
        self.load_image(image)

    def load_image(self, image):
        pixmap = QPixmap(image)
        pixmap = pixmap.scaled(QSize(*self.IMAGE_SIZE), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_icon.setPixmap(pixmap)
        self.is_loaded = True
        self.image_average_color = QColor(*get_image_average_pixel_color(image))
        self.image = image

    def enterEvent(self, event):
        if self.is_loaded:
            shadow_effect = QGraphicsDropShadowEffect(self)
            shadow_effect.setBlurRadius(20)
            shadow_effect.setXOffset(0)
            shadow_effect.setYOffset(0)
            shadow_effect.setColor(self.image_average_color)
            self.image_icon.setGraphicsEffect(shadow_effect)

    def leaveEvent(self, event):
        if self.is_loaded:
            self.image_icon.setGraphicsEffect(None)

    def show_cover(self):
        dialog = QDialog(self.parent())
        dialog.setWindowTitle(f"{self.vinyl.pretty_name} - {self.vinyl.artist_pretty_name}")
        layout = QVBoxLayout(dialog)
        pixmap = QPixmap(self.image)
        pixmap = pixmap.scaled(QSize(*self.LARGE_IMAGE_SIZE), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        image_icon = QLabel()
        image_icon.setPixmap(pixmap)
        layout.addWidget(image_icon)
        dialog.exec()

    def show_context_menu(self, pos):
        menu = QMenu(self.parent())
        edit_action = menu.addAction("Edit")
        edit_action.setIcon(make_icon("edit.png"))
        edit_action.triggered.connect(lambda: self.edit_requested.emit(self))
        delete_action = menu.addAction("Delete")
        delete_action.setIcon(make_icon("delete.png"))
        delete_action.triggered.connect(lambda: self.delete_requested.emit(self))
        menu.addSeparator()
        deezer_action = menu.addAction("Listen on Deezer")
        deezer_action.setIcon(make_icon("deezer.png"))
        deezer_action.triggered.connect(lambda: self.listen_requested.emit("deezer", self.vinyl))
        # spotify_action = menu.addAction("Listen on Spotify")
        # spotify_action.triggered.connect(lambda: self.listen_requested.emit("spotify", self.vinyl))
        youtube_action = menu.addAction("Listen on Youtube")
        youtube_action.setIcon(make_icon("youtube.png"))
        youtube_action.triggered.connect(lambda: self.listen_requested.emit("youtube", self.vinyl))
        menu.exec(pos)

    def mouseReleaseEvent(self, event):
        if not self.image_icon.geometry().contains(event.pos()):
            return
        if event.button() == Qt.LeftButton:
            self.show_cover()
        elif event.button() == Qt.RightButton:
            self.show_context_menu(self.mapToGlobal(event.pos()))

    def update_vinyl(self, vinyl, image):
        self.vinyl = vinyl
        self.load_image(image)
        self.name_lbl.setText(self.vinyl.pretty_name)
        self.artist_lbl.setText(self.vinyl.artist_pretty_name)
        self.is_loaded = True
