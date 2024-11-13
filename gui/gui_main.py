from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QMessageBox
from gui.gui_mod_list import ModList
from gui.gui_controls import ModControls
from gui.gui_presets import SettingsPanel
from gui.gui_path_selector import PathSelectorSection
import helper.shared


class ShittyModManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Shitty ModManager')

        # Initialize components
        self.mod_list = ModList()

        # New mod data control buttons directly below ScrollBox
        mod_data_controls = ModControls(self.read_mod_data, self.write_mod_data)

        # Other UI components
        settings_panel = SettingsPanel()
        settings_panel.preset_loaded.connect(self.mod_list.mod_list.read_mods_data)
        self.path_selector_section = PathSelectorSection(self.mod_list.mod_list.read_mods_data)

        # Main layout
        main_layout = QVBoxLayout(self)

        # Upper layout with scrollbox and settings panel
        upper_layout = QHBoxLayout()

        # Scrollbox with nested layout for controls
        mod_list_widget = QWidget()
        mod_list_layout = QVBoxLayout(mod_list_widget)
        mod_list_layout.setContentsMargins(0, 0, 0, 0)
        mod_list_layout.addWidget(self.mod_list)       # Add ScrollBox
        mod_list_layout.addWidget(mod_data_controls)   # Add Read/Save buttons directly under ScrollBox

        # Add mod list layout and settings panel to upper layout
        upper_layout.addWidget(mod_list_widget, stretch=3)
        upper_layout.addWidget(settings_panel, stretch=1)

        # Add components to main layout
        main_layout.addLayout(upper_layout)
        main_layout.addWidget(self.path_selector_section)

        self.setLayout(main_layout)

        self.initialize()

    def initialize(self):
        self.check_paths_on_startup()
        self.show()
        self.mod_list.adjust_size()

    def check_paths_on_startup(self):
        """Checks if all paths are set, and prompts if missing."""
        if self.path_selector_section.path_selector.are_paths_complete():
            self.read_mod_data()
            self.path_selector_section.init_done = True
        else:
            self.path_selector_section.fold_button.setChecked(True)
            self.path_selector_section.toggle_path_selector()

    def check_paths_complete(self):
        """Verify if all necessary paths are complete."""
        if not self.path_selector_section.path_selector.are_paths_complete():
            QMessageBox.warning(self, "Error", "Paths are not complete.")
            return False
        return True

    def read_mod_data(self):
        """Reads mod data."""
        if not self.check_paths_complete():
            return

        helper.shared.mods.read_xml()
        helper.shared.config.read_xml()
        self.mod_list.mod_list.read_mods_data()
        self.mod_list.adjust_size()
        print("Reading mods...")

    def write_mod_data(self):
        """Writes mod data back to file."""
        if not self.check_paths_complete():
            return
        helper.shared.mods.write_back()
        helper.shared.config.write_back()
        print("Saved mods.")
