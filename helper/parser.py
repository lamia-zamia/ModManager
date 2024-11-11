import os
import xml.etree.ElementTree as ET
import helper.shared


class NoitaModXmlData:
    def __init__(self, index, mod_attrib):
        self.order = index
        self.enabled = self.noita_to_bool(mod_attrib.get("enabled", "0"))
        self.id = mod_attrib.get("name", "")
        self._settings_fold_open = mod_attrib.get("settings_fold_open", "0")
        self.workshop_item_id = int(mod_attrib.get("workshop_item_id", 0))
        self.folder = ""
        self.name = ""
        self._uid = f'{self.id}_workshop_{self.workshop_item_id}' if self.workshop_item_id > 0 else self.id

    @staticmethod
    def bool_to_noita(value: bool) -> str:
        """Converts a boolean to Noita XML string format."""
        return "1" if value else "0"

    @staticmethod
    def noita_to_bool(value: str) -> bool:
        """Converts Noita XML string format to boolean."""
        return value == "1"


class NoitaModXml(list):
    def __init__(self):
        """Initialize with mod paths and load XML data."""
        super().__init__()

    def read_xml(self):
        """Load mod data from the XML file specified in save path."""
        self.clear()
        save_path = os.path.join(helper.shared.data.paths.get("noita_save", ""), "save00", "mod_config.xml")

        if not save_path or not os.path.exists(save_path):
            print(f"Warning: Save path '{save_path}' does not exist.")
            return

        # Parse XML and instantiate mod data objects
        tree = ET.parse(save_path)
        root = tree.getroot()

        for index, mod in enumerate(root.findall('./Mod')):
            mod_data = NoitaModXmlData(index, mod.attrib)
            self.append(mod_data)
            self._set_mod_paths(mod_data)

    def _set_mod_paths(self, mod):
        """Set the folder path and name for each mod based on local or workshop ID."""
        if mod.workshop_item_id > 0:
            mod.folder = os.path.join(
                helper.shared.data.paths.get("steam_root", ""),
                "steamapps",
                "workshop",
                "content",
                "881100",
                str(mod.workshop_item_id)
            )
        else:
            mod.folder = os.path.join(helper.shared.data.paths.get("noita_root", ""), "mods", mod.id)

        # Attempt to read the mod's display name from its 'mod.xml' file
        mod_xml_file = os.path.join(mod.folder, "mod.xml")
        if os.path.exists(mod_xml_file):
            try:
                tree = ET.parse(mod_xml_file)
                root = tree.getroot()
                mod.name = root.attrib.get("name", mod.id)  # Use ID if name is missing
            except ET.ParseError:
                print(f"Warning: Could not parse mod XML file at '{mod_xml_file}'.")

    @staticmethod
    def create_mod_element(mod):
        """Create an XML element for a mod, including attributes and formatting."""
        mod_element = ET.Element(
            "Mod",
            enabled=NoitaModXmlData.bool_to_noita(mod.enabled),
            name=mod.id,
            settings_fold_open=mod._settings_fold_open,
            workshop_item_id=str(mod.workshop_item_id)
        )
        mod_element.text = "\n\n  "
        return mod_element

    def write_back(self):
        """Write modified mod data back to the XML file, formatted for readability."""
        root = ET.Element("Mods")
        root.text = "\n\n"

        for mod in self:
            root.append(self.create_mod_element(mod))

        # Write formatted XML to file
        path = os.path.join(helper.shared.data.paths.get("noita_save", ""), "save00", "mod_config.xml")
        if not path:
            print("Warning: No path specified for writing XML data.")
            return

        try:
            tree = ET.ElementTree(root)
            ET.indent(tree, space='\n  ', level=0)
            # tree.indent(root, space='  ', level=0)
            with open(path, 'wb') as file:
                tree.write(file)
            print(f"Successfully wrote mod data to '{path}'.")
        except FileNotFoundError:
            print(f"Error: Path '{path}' not found.")
        except PermissionError:
            print(f"Error: Insufficient permissions to write to '{path}'.")
