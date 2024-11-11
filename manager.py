from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from gui.gui_main import ShittyModManager
import sys


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ShittyModManager()
    window.setWindowIcon(QIcon("data/icons/noita.svg"))
    sys.exit(app.exec())
