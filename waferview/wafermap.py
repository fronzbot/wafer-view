"""Creates memory structure for wafer map."""

import re
import xml.etree.ElementTree as ET
import xmltodict
from waferview.gui.constants import (
    SUPPORTED_FORMATS,
    WAFER_ID,
    LOT_ID,
    CHIP_SIZE,
    PRODUCT_ID,
    CREATE_DATE,
)


class WaferMap:
    """Representation of a wafer map."""

    def __init__(self, xmlfile):
        """Initialize a wafer map structure."""
        self.parse(xmlfile)
        self.check_format()
        self.get_attributes()
        self.get_codes()
        self.gen_map()

    def parse(self, xmlfile):
        """Parse an xml wafer map."""
        tree = ET.iterparse(xmlfile)
        # Strip namespace from XML file
        for _, elem in tree:
            _, _, elem.tag = elem.tag.rpartition("}")
        # tree = ET.parse(xmlfile)
        xml_data = tree.root
        xmlstr = ET.tostring(xml_data, encoding="utf-8", method="xml")
        xml_dict = xmltodict.parse(xmlstr)
        self._map_data = xml_dict["Map"]

    def check_format(self):
        """Verify format is supported by library."""
        self.is_valid = False
        self.format = self._map_data.get("@FormatRevision", None)
        if self.format in SUPPORTED_FORMATS:
            self.is_valid = True

    def get_attributes(self):
        """Retrieve all wafer attributes."""
        device_data = self._map_data["Device"]
        self.device_attr = {
            WAFER_ID: self._map_data.get("@WaferId", None),
            LOT_ID: device_data.get("@LotId", None),
            CHIP_SIZE: [
                float(device_data.get("@DeviceSizeX", None)),
                float(device_data.get("@DeviceSizeY", None)),
            ],
            PRODUCT_ID: device_data.get("@ProductId", None),
            CREATE_DATE: device_data["Data"].get("@CreateDate"),
            "rows": int(device_data.get("@Rows", None)),
            "cols": int(device_data.get("@Columns", None)),
        }

    def get_codes(self):
        """Get all bin codes."""
        bins = self._map_data["Device"]["Bin"]
        self.bin_codes = {}
        for code in bins:
            code_val = code["@BinCode"]
            code_pass = code["@BinQuality"] == "Pass"
            code_desc = code["@BinDescription"]
            code_count = code["@BinCount"]
            if code["@BinQuality"] == "NULL":
                code_pass = None
            self.bin_codes[code_val] = {
                "status": code_pass,
                "desc": code_desc,
                "count": code_count,
            }

    def gen_map(self):
        """Generate a wafer map with data and coordinates."""
        if self.device_attr[CHIP_SIZE] is None:
            self.semimap = None
            return
        # Normalize locations to a 0 to 1 grid with 0,0 at bottom left and
        # 1,1, at top right
        xmax = self.device_attr[CHIP_SIZE][0] * self.device_attr["cols"]
        ymax = self.device_attr[CHIP_SIZE][1] * self.device_attr["rows"]
        xstep = self.device_attr[CHIP_SIZE][0] / xmax
        ystep = -1 * self.device_attr[CHIP_SIZE][1] / ymax

        self.pixels = []

        xloc = 0
        yloc = 1

        for row in self._map_data["Device"]["Data"]["Row"]:
            # Split data into one byte chunks
            row_bins = re.findall("..", row)
            for data in row_bins:
                status = self.bin_codes[data]["status"]
                desc = self.bin_codes[data]["desc"]
                coord = (xloc, yloc + ystep)
                size = (xstep, -1 * ystep)
                self.pixels.append([coord, size, status, desc])
                xloc += xstep
            xloc = 0
            yloc += ystep
