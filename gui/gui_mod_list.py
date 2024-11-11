from PyQt6.QtWidgets import QLayout, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QListWidget, QListWidgetItem, QPushButton, QSizePolicy
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon
from typing import cast
import helper.shared
import webbrowser
import os

MOD_ID_WIDTH = 200


class ModItemWidget(QWidget):
    checkbox_toggled = pyqtSignal(QWidget)

    def __init__(self, mod):
        super().__init__()
        self.mod = mod

        layout = QHBoxLayout()
        layout.setContentsMargins(11, 5, 0, 5)

        # Order label
        self.label_order = QLabel(f'{mod.order + 1:03}')
        self.label_order.setFixedWidth(41)
        layout.addWidget(self.label_order)

        # Enabled checkbox
        self.checkbox = QCheckBox()
        self.checkbox.setFixedWidth(40)
        self.checkbox.setChecked(mod.enabled)
        self.checkbox.toggled.connect(self.on_checkbox_toggled)
        layout.addWidget(self.checkbox)

        # Mod name label
        self.label_name = QLabel(mod.name)
        self.label_name.setFixedWidth(MOD_ID_WIDTH)
        layout.addWidget(self.label_name)

        # Mod id
        id_widget = QWidget()
        id_widget.setFixedWidth(MOD_ID_WIDTH)
        id_layout = QHBoxLayout(id_widget)
        id_layout.setContentsMargins(0, 0, 0, 0)
        self.label_id = QLabel(mod.id)
        # self.label_id.setFixedWidth(200)
        id_layout.addWidget(self.label_id)
        if self.mod.workshop_item_id > 0:
            self.steam_button = QPushButton()
            self.steam_button.setContentsMargins(0, 0, 0, 0)
            self.steam_button.setIcon(QIcon("data/icons/steam.svg"))
            self.steam_button.setToolTip("This is a Workshop Item\nClick to open in Steam Workshop")
            self.steam_button.setFlat(True)
            self.steam_button.clicked.connect(self.open_steam_page)
            id_layout.addWidget(self.steam_button)
        id_layout.insertStretch(-1, 1)
        layout.addWidget(id_widget)

        # Folder button
        self.folder_button = QPushButton()
        self.folder_button.setFixedWidth(40)
        self.folder_button.setIcon(QIcon("data/icons/folder.svg"))
        self.folder_button.setToolTip("Open Mod Folder")
        self.folder_button.setFlat(True)
        # self.folder_button.setStyleSheet("border: none")
        self.folder_button.clicked.connect(self.open_folder)
        layout.addWidget(self.folder_button)

        self.setLayout(layout)

    def on_checkbox_toggled(self):
        self.checkbox_toggled.emit(self)

    def open_folder(self):
        folder_path = self.mod.folder
        if os.path.exists(folder_path):
            os.startfile(folder_path) if os.name == 'nt' else os.system(f'open "{folder_path}"')

    def open_steam_page(self):
        steam_url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={self.mod.workshop_item_id}"
        webbrowser.open(steam_url)

    def update_order_label(self, new_order):
        self.label_order.setText(new_order)


class HeaderWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(21, 0, 0, 0)

        # Create labels with stretches applied
        order = QLabel("#")
        order.setFixedWidth(20)
        layout.addWidget(order)

        enabled = QLabel("Enabled")
        enabled.setFixedWidth(70)
        layout.addWidget(enabled)

        mod_name = QLabel("Mod Name")
        mod_name.setFixedWidth(MOD_ID_WIDTH)
        layout.addWidget(mod_name)

        mod_id = QLabel("Mod ID")
        mod_id.setFixedWidth(MOD_ID_WIDTH)
        layout.addWidget(mod_id)

        layout.addWidget(QLabel("Folder"))

        # Set layout for header
        self.setLayout(layout)


class ModListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.read_mods_data()

    def read_mods_data(self):
        self.clear()
        if helper.shared.mods:
            for mod in helper.shared.mods:
                self.add_mod_item(mod)

    def add_mod_item(self, mod):
        mod_widget = ModItemWidget(mod)
        mod_widget.checkbox_toggled.connect(self.checkbox_changed)
        list_item = QListWidgetItem(self)
        list_item.setSizeHint(mod_widget.sizeHint())
        self.addItem(list_item)
        self.setItemWidget(list_item, mod_widget)

    def checkbox_changed(self, mod_widget: ModItemWidget):
        mod_widget.mod.enabled = mod_widget.checkbox.isChecked()

    def dropEvent(self, event):
        super().dropEvent(event)
        self.update_mod_orders()

    def update_mod_orders(self):
        for index in range(self.count()):
            list_item = self.item(index)
            mod_widget = cast(ModItemWidget, self.itemWidget(list_item))
            if mod_widget is not None:
                mod_widget.update_order_label(f'{index + 1:03}')
                mod_widget.mod.order = index

        helper.shared.mods.sort(key=lambda mod: mod.order)


class ModList(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        layout.addWidget(HeaderWidget())
        self.mod_list = ModListWidget()
        layout.addWidget(self.mod_list)

    def adjust_size(self):
        column_size = self.mod_list.sizeHintForColumn(0)
        self.mod_list.setMinimumWidth(column_size + 30)
