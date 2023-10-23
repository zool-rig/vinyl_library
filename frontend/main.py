# -*- coding: utf-8 -*-
import sys
import os
import ctypes
from uuid import uuid4

sys.path.append(os.path.abspath("."))

from PySide6.QtWidgets import QApplication
from frontend.main_window import VinylLibraryUI


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app_id = uuid4().hex
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    ui = VinylLibraryUI()
    ui.show()
    style_file = "frontend/resources/style/style.qss"
    with open(style_file, "r") as f:
        ui.setStyleSheet(f.read())
    sys.exit(app.exec())
