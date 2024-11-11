from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton, QLineEdit, QListWidget, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
import helper.shared


class SettingsPanel(QFrame):
    preset_loaded = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)

        # Create layout and add components
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Mod Presets"))

        # Presets list
        self.presets_list = QListWidget()
        self.presets_list.itemSelectionChanged.connect(self.preset_selected)
        self.update_presets_list()

        # Preset name input field
        self.preset_name_input = QLineEdit()
        self.preset_name_input.textChanged.connect(self.input_text_changed)
        self.preset_name_input.setPlaceholderText("Enter preset name")

        layout.addWidget(self.preset_name_input)
        layout.addWidget(self.presets_list)

        self.update_preset_button = QPushButton("Create Preset")
        self.update_preset_button.clicked.connect(self.update_preset)
        layout.addWidget(self.update_preset_button)

        load_preset_button = QPushButton("Load Preset")
        load_preset_button.clicked.connect(self.load_preset)
        layout.addWidget(load_preset_button)

        delete_preset_button = QPushButton("Delete Preset")
        delete_preset_button.clicked.connect(self.delete_preset)
        layout.addWidget(delete_preset_button)

        self.setFixedWidth(200)

    def get_preset_name(self):
        """Retrieve and validate preset name."""
        preset_name = self.preset_name_input.text().strip()
        if not preset_name:
            preset_name = f'Preset {self.presets_list.count() + 1}'
        return preset_name

    def input_text_changed(self):
        text = self.preset_name_input.text()
        if self.presets_list.findItems(text, Qt.MatchFlag.MatchExactly):
            self.update_preset_button.setText("Update Preset")
        else:
            self.update_preset_button.setText("Create Preset")

    def preset_selected(self):
        current_item = self.presets_list.currentItem()
        if current_item:
            preset_name = current_item.text()
            self.preset_name_input.setText(preset_name)

    def update_presets_list(self):
        """Update presets list in GUI"""
        self.presets_list.clear()  # Clear the list to avoid duplicates
        for preset_name in helper.shared.data.presets:
            self.presets_list.addItem(preset_name)

    def save_preset(self, preset_name):
        """Save the current enabled mods to the specified preset."""
        enabled_mods = [mod._uid for mod in helper.shared.mods if mod.enabled]
        helper.shared.data.presets[preset_name] = enabled_mods
        helper.shared.data.write_to_file()
        self.update_presets_list()
        self.presets_list.setCurrentItem(self.presets_list.findItems(preset_name, Qt.MatchFlag.MatchExactly)[0])
        print(f"Preset '{preset_name}' saved.")

    def update_preset(self):
        """Update or create a preset with the current enabled mods."""
        preset_name = self.get_preset_name()

        if preset_name in helper.shared.data.presets:
            response = QMessageBox.question(self, "Confirm Update", f"The preset '{preset_name}' already exists. Do you want to overwrite it?")
            if response != QMessageBox.StandardButton.Yes:
                return

        self.save_preset(preset_name)

    def load_preset(self):
        """Apply the selected preset and merge it with the current mods list."""
        current_item = self.presets_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Error", "Please select a preset to apply.")
            return

        selected_preset_name = current_item.text()
        preset_mods = helper.shared.data.presets[selected_preset_name]

        for mod in helper.shared.mods:
            if mod._uid in preset_mods:
                mod.enabled = True
            else:
                mod.enabled = False

        self.preset_loaded.emit()

    def delete_preset(self):
        """Delete the selected preset."""
        current_item = self.presets_list.currentItem()
        if not current_item:
            return

        selected_preset_name = current_item.text()
        del helper.shared.data.presets[selected_preset_name]
        helper.shared.data.write_to_file()
        self.update_presets_list()
