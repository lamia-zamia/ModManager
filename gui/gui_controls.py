from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton


class ModControls(QWidget):
    """Controls with 'Read' and 'Save' buttons."""

    def __init__(self, read_callback, save_callback):
        super().__init__()

        # Layout for the buttons
        layout = QHBoxLayout(self)

        # Read button
        self.read_button = QPushButton("Read Mod Data")
        self.read_button.clicked.connect(read_callback)
        layout.addWidget(self.read_button)

        # Save button
        self.save_button = QPushButton("Write Mod Data")
        self.save_button.clicked.connect(save_callback)
        layout.addWidget(self.save_button)

        self.setLayout(layout)
