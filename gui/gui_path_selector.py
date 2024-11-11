import os
from PyQt6.QtWidgets import QFrame, QWidget, QVBoxLayout, QGridLayout, QLineEdit, QPushButton, QFileDialog, QLabel
from PyQt6.QtCore import pyqtSignal
import helper.shared


class NoitaPathLine(QLineEdit):
    # Signal emitted when a correct path is set
    changed_correct = pyqtSignal()

    def __init__(self, placeholder, join_part):
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.join_part = join_part
        self.editingFinished.connect(self.verify)  # Verify on editing finished
        self.valid = False

    def setText(self, a0: str | None) -> None:
        """Sets the text and verifies the path."""
        super().setText(a0)
        self.verify()

    def getFullPath(self) -> str:
        """Returns the full path, including the joined part."""
        return os.path.join(self.text(), self.join_part)

    def verify(self):
        """Checks if the full path exists and emits a signal if valid."""
        if os.path.exists(self.getFullPath()):
            self.setStyleSheet("")
            self.valid = True
            self.changed_correct.emit()  # Path is valid, emit signal
        else:
            self.setStyleSheet("color: yellow")  # Path is invalid
            self.valid = False


class PathSelectorWidget(QWidget):
    changed_correct = pyqtSignal()

    def __init__(self):
        super().__init__()

        # Define paths with placeholders and verification requirements
        self.paths = {
            "noita_root": NoitaPathLine("Example: Steam/steamapps/common/Noita", "noita.exe"),
            "noita_save": NoitaPathLine("Example: AppData/LocalLow/Nolla_Games_Noita", "save00"),
            "steam_root": NoitaPathLine("Example: C:/Program Files/Steam", "steamapps")
        }
        self.update_paths()

        # Set up the UI layout
        layout = QGridLayout(self)

        # Add path rows
        self.add_path_row(layout, "Path to Noita", self.paths["noita_root"])
        self.add_path_row(layout, "Path to Save Folder", self.paths["noita_save"])
        self.add_path_row(layout, "Path to Steam", self.paths["steam_root"])

        self.setLayout(layout)

    def update_paths(self):
        """Reads data from data and connect each path's correct signal to save and initialize"""
        for key, line_widget in self.paths.items():
            stored_path = helper.shared.data.paths[key]
            if stored_path:
                line_widget.setText(stored_path)
            line_widget.changed_correct.connect(self.save_and_init)

    def add_path_row(self, layout: QGridLayout, label_text: str, line_edit: NoitaPathLine):
        """Adds a row to the layout with label, path line edit, and selection button."""
        row = layout.rowCount()
        label = QLabel(label_text)
        select_button = QPushButton("Select Path")
        select_button.clicked.connect(lambda: self.select_path(line_edit))

        layout.addWidget(label, row, 0)
        layout.addWidget(line_edit, row, 1)
        layout.addWidget(select_button, row, 2)

    def select_path(self, line_edit: NoitaPathLine):
        """Opens a file dialog to select a folder and updates QLineEdit."""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            line_edit.setText(folder)

    def save_and_init(self):
        """Saves paths to file and reinitializes mod list with new path."""
        self.initialize_mod_list()
        helper.shared.data.write_to_file()
        if self.are_paths_complete():
            self.changed_correct.emit()

    def are_paths_complete(self) -> bool:
        """Checks if all paths are filled in and verified."""
        return all(line_edit.valid for line_edit in self.paths.values())

    def initialize_mod_list(self):
        """Initialize the mod list with the selected save file path if valid."""
        for key, line_widget in self.paths.items():
            path = line_widget.text()
            if path:
                helper.shared.data.paths[key] = path


class PathSelectorSection(QFrame):
    def __init__(self, gui_refresh):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.gui_refresh = gui_refresh

        # Create layout for the section
        layout = QVBoxLayout(self)

        # Toggle button to show or hide the path selector
        self.fold_button = QPushButton("Show Path Config")
        self.fold_button.setCheckable(True)
        self.fold_button.clicked.connect(self.toggle_path_selector)

        # Path selector widget (initially hidden)
        self.path_selector = PathSelectorWidget()
        self.path_selector.setVisible(False)
        self.path_selector.changed_correct.connect(self.validate)

        # Add button and path selector to layout
        layout.addWidget(self.fold_button)
        layout.addWidget(self.path_selector)

        self.init_done = False

    def validate(self):
        if not self.init_done:
            self.init_done = True
            self.fold_button.setChecked(False)
            self.toggle_path_selector()
            self.gui_refresh()

    def toggle_path_selector(self):
        """Toggles the visibility of the path selection section."""
        if not self.init_done:
            self.fold_button.setChecked(True)
            self.path_selector.setVisible(True)
            self.fold_button.setText("Paths are incomplete")
            return

        is_open = self.fold_button.isChecked()
        self.path_selector.setVisible(is_open)
        self.fold_button.setText("Show Path Config" if not is_open else "Hide Path Config")
