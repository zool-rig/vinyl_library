import sys
import os
sys.path.append(os.path.abspath("."))

from PySide6.QtWidgets import QApplication
from frontend.main_window import VinylLibraryUI


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = VinylLibraryUI()
    ui.show()
    sys.exit(app.exec())
