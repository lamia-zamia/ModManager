import os
import json

DEFAULT_PATH = {"noita_root": "", "noita_save": "", "steam_root": ""}


class ModManagerData():
    def __init__(self):
        self._manager_file_path = "manager.json"
        self.presets = {}
        self.paths = {}
        self.read_file()

    def _read_data_from_file(self):
        """Reads JSON data from manager file and initializes _data with default values if empty or corrupt."""
        self._data = {}
        if os.path.exists(self._manager_file_path):
            try:
                with open(self._manager_file_path, "r") as file:
                    self._data = json.load(file)
            except json.JSONDecodeError:
                print(f"Couldn\'t parse {self._manager_file_path}, using default data.")

    def _set_defaults(self):
        """Sets default values for paths and presets if not present in _data."""
        self.presets = self._data.get("presets", {})
        self.paths = self._data.get("paths", DEFAULT_PATH.copy())

    def _update_from_data(self):
        self._set_defaults()
        self._verify_path()

    def _verify_path(self):
        for path in DEFAULT_PATH:
            if not path in self.paths:
                self.paths[path] = ""

    def read_file(self):
        self._read_data_from_file()
        self._update_from_data()
        self._verify_path()

    def write_to_file(self):
        """Writes the current data to file with verification of necessary keys."""
        self._data["presets"] = self.presets
        self._data["paths"] = self.paths
        with open(self._manager_file_path, "w") as file:
            json.dump(self._data, file, indent=4)
        print(f"Data written to {self._manager_file_path}.")
