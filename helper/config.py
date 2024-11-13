import os
import xml.etree.ElementTree as ET
import helper.shared


class NoitaConfig(list):
    def __init__(self):
        super().__init__()

    def read_xml(self):
        """Load mod data from the XML file specified in save path."""
        self.clear()
        self.config = os.path.join(helper.shared.data.paths.get("noita_save", ""), "save_shared", "config.xml")

        if not self.config or not os.path.exists(self.config):
            print(f"Warning: Config path '{self.config}' does not exist.")
            return

        # Parse XML and instantiate mod data objects
        self.tree = ET.parse(self.config)
        ET.indent(self.tree, space='\n  ', level=0)
        root = self.tree.getroot()
        root.attrib["mods_sandbox_enabled"] = "0"

    def write_back(self):
        if self.tree:
            self.tree.write(self.config)
