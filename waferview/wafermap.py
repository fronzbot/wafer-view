"""Creates memory structure for wafer map."""

import re
import xml.etree.ElementTree as ET
import xmltodict
from waferview.gui.constants import (
    SUPPORTED_FORMATS,
    WAFER_ID,
    LOT_ID,
    WAFER_SIZE,
    CHIP_SIZE,
    PRODUCT_ID,
    CREATE_DATE,
    DEFAULT_WAFER_SIZE
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
            WAFER_SIZE: float(device_data.get("@WaferSize", DEFAULT_WAFER_SIZE)),
            CHIP_SIZE: [
                float(device_data.get("@DeviceSizeX", 0)),
                float(device_data.get("@DeviceSizeY", 0)),
            ],
            PRODUCT_ID: device_data.get("@ProductId", None),
            CREATE_DATE: device_data.get("@CreateDate", None),
            "rows": int(device_data.get("@Rows", 1)),
            "cols": int(device_data.get("@Columns", 1)),
        }

    def get_codes(self):
        """Get all bin codes."""
        bins = self._map_data["Device"]["Bin"]
        null_bin = self._map_data["Device"]["@NullBin"]
        self.bin_codes = {}
        bin_incr = 0
        for code in bins:
            code_val = code["@BinCode"]
            code_pass = code["@BinQuality"] == "Pass"
            code_desc = code.get("@BinDescription", str(bin_incr))
            code_count = code["@BinCount"]
            if code["@BinQuality"] == "NULL":
                code_pass = None
            self.bin_codes[code_val] = {
                "status": code_pass,
                "desc": code_desc,
                "count": code_count,
            }
            bin_incr += 1

        if null_bin not in self.bin_codes:
            self.bin_codes[null_bin] = {
                "status": None,
                "desc": "NULL",
                "count": None,
            }

    def gen_map(self):
        """Generate a wafer map with data and coordinates."""
        if self.device_attr[CHIP_SIZE] == [0, 0]:
            # Need to use rows and columns to guess size
            self.device_attr[CHIP_SIZE][0] = 1000 * self.device_attr[WAFER_SIZE] / self.device_attr["cols"]
            self.device_attr[CHIP_SIZE][1] = 1000 * self.device_attr[WAFER_SIZE] / self.device_attr["rows"]

        # Normalize locations to a 0 to 1 grid with 0,0 at bottom left and
        # 1,1, at top right
        xmax = self.device_attr[CHIP_SIZE][0] * self.device_attr["cols"]
        ymax = self.device_attr[CHIP_SIZE][1] * self.device_attr["rows"]
        xstep = self.device_attr[CHIP_SIZE][0] / xmax
        ystep = -1 * self.device_attr[CHIP_SIZE][1] / ymax

        self.pixels = []

        xloc = 0
        yloc = 1

        bin_type = self._map_data["Device"]["@BinType"]
        find_str = ".."
        if bin_type == "Decimal":
            find_str = "..."

        for row in self._map_data["Device"]["Data"]["Row"]:
            # Split data into one byte chunks
            row_bins = re.findall(find_str, row)
            for data in row_bins:
                status = self.bin_codes[data]["status"]
                desc = self.bin_codes[data]["desc"]
                coord = (xloc, yloc + ystep)
                size = (xstep, -1 * ystep)
                self.pixels.append([coord, size, status, desc])
                xloc += xstep
            xloc = 0
            yloc += ystep
