# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.abspath("."))

from PySide6.QtWidgets import QApplication
from frontend.main_window import VinylLibraryUI


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = VinylLibraryUI()
    ui.show()
    style_file = "frontend/resources/style/style.qss"
    with open(style_file, "r") as f:
        ui.setStyleSheet(f.read())
    sys.exit(app.exec())
