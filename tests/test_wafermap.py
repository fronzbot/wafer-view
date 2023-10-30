"""Tests for wafermap module."""

import unittest
from waferview import wafermap
from waferview.gui.constants import (
    SUPPORTED_FORMATS,
    WAFER_ID,
    LOT_ID,
    WAFER_SIZE,
    CHIP_SIZE,
    PRODUCT_ID,
    CREATE_DATE,
    DEFAULT_WAFER_SIZE,
)


TEST_XML = "./xml/SEMI_G85/SEMI_G85_1101_MIN.xml"


class TestWaferMap(unittest.TestCase):
    """Test the WaferMap class."""

    def setUp(self):
        """Set up a WaferMap instance."""
        self.test_wmap = MockWaferMap()

    def tearDown(self):
        """Tear down a WaferMap instance."""
        self.test_wmap = None

    def test_check_format_ok(self):
        """Test the check_format method."""
        self.test_wmap._map_data = {"@FormatRevision": SUPPORTED_FORMATS[0]}
        self.test_wmap.check_format()
        self.assertEqual(self.test_wmap.format, SUPPORTED_FORMATS[0])
        self.assertTrue(self.test_wmap.is_valid)

    def test_check_format_ng(self):
        """Test the check_format method with bad versioning."""
        self.test_wmap._map_data = {"@FormatRevision": "foobar"}
        self.test_wmap.check_format()
        self.assertFalse(self.test_wmap.is_valid)

    def test_check_get_attributes_min(self):
        """Test the get_attributes method."""
        self.test_wmap._map_data = {"Device": {"@Rows": "13", "@Columns": "17"}}
        self.test_wmap.get_attributes()
        self.assertEqual(self.test_wmap.device_attr[WAFER_ID], None)
        self.assertEqual(self.test_wmap.device_attr[LOT_ID], None)
        self.assertEqual(self.test_wmap.device_attr[WAFER_SIZE], DEFAULT_WAFER_SIZE)
        self.assertEqual(self.test_wmap.device_attr[CHIP_SIZE], [0, 0])
        self.assertEqual(self.test_wmap.device_attr[PRODUCT_ID], None)
        self.assertEqual(self.test_wmap.device_attr[CREATE_DATE], None)
        self.assertEqual(self.test_wmap.device_attr["rows"], 13)
        self.assertEqual(self.test_wmap.device_attr["cols"], 17)

    def test_check_get_attributes_all(self):
        """Test the get_attributes method with everything extracted."""
        self.test_wmap._map_data = {
            "@WaferId": "foo",
            "Device": {
                "@LotId": "bar",
                "@WaferSize": "100",
                "@DeviceSizeX": "42",
                "@DeviceSizeY": "24",
                "@ProductId": "deadbeef",
                "@Rows": "13",
                "@Columns": "17",
                "@CreateDate": "19700101",
            },
        }
        self.test_wmap.get_attributes()
        self.assertEqual(self.test_wmap.device_attr[WAFER_ID], "foo")
        self.assertEqual(self.test_wmap.device_attr[LOT_ID], "bar")
        self.assertEqual(self.test_wmap.device_attr[WAFER_SIZE], 100)
        self.assertEqual(self.test_wmap.device_attr[CHIP_SIZE], [42, 24])
        self.assertEqual(self.test_wmap.device_attr[PRODUCT_ID], "deadbeef")
        self.assertEqual(self.test_wmap.device_attr[CREATE_DATE], "19700101")
        self.assertEqual(self.test_wmap.device_attr["rows"], 13)
        self.assertEqual(self.test_wmap.device_attr["cols"], 17)

    def test_get_codes_min(self):
        """Test the get_codes method with minimal input."""
        self.test_wmap._map_data = {
            "Device": {
                "@NullBin": "255",
                "Bin": [
                    {"@BinCode": "000", "@BinQuality": "Pass", "@BinCount": "100"},
                    {"@BinCode": "111", "@BinQuality": "Fail", "@BinCount": "10"},
                    {"@BinCode": "222", "@BinQuality": "Fail", "@BinCount": "1"},
                ],
            }
        }

        self.test_wmap.get_codes()

        self.assertTrue("000" in self.test_wmap.bin_codes)
        self.assertTrue("111" in self.test_wmap.bin_codes)
        self.assertTrue("222" in self.test_wmap.bin_codes)
        self.assertTrue("255" in self.test_wmap.bin_codes)

        self.assertTrue(self.test_wmap.bin_codes["000"]["status"])
        self.assertFalse(self.test_wmap.bin_codes["111"]["status"])
        self.assertFalse(self.test_wmap.bin_codes["222"]["status"])
        self.assertEqual(self.test_wmap.bin_codes["255"]["status"], None)

        self.assertEqual(self.test_wmap.bin_codes["000"]["desc"], "0")
        self.assertEqual(self.test_wmap.bin_codes["111"]["desc"], "1")
        self.assertEqual(self.test_wmap.bin_codes["222"]["desc"], "2")
        self.assertEqual(self.test_wmap.bin_codes["255"]["desc"], "NULL")

        self.assertEqual(self.test_wmap.bin_codes["000"]["count"], "100")
        self.assertEqual(self.test_wmap.bin_codes["111"]["count"], "10")
        self.assertEqual(self.test_wmap.bin_codes["222"]["count"], "1")
        self.assertEqual(self.test_wmap.bin_codes["255"]["count"], None)

    def test_get_codes_all(self):
        """Test the get_codes method with all input."""
        self.test_wmap._map_data = {
            "Device": {
                "@NullBin": "255",
                "Bin": [
                    {
                        "@BinCode": "000",
                        "@BinQuality": "Pass",
                        "@BinCount": "100",
                        "@BinDescription": "foo",
                    },
                    {
                        "@BinCode": "111",
                        "@BinQuality": "Fail",
                        "@BinCount": "10",
                        "@BinDescription": "bar",
                    },
                    {
                        "@BinCode": "222",
                        "@BinQuality": "Fail",
                        "@BinCount": "1",
                        "@BinDescription": "beef",
                    },
                    {
                        "@BinCode": "255",
                        "@BinQuality": "NULL",
                        "@BinCount": "0",
                        "@BinDescription": "Null bin",
                    },
                ],
            }
        }

        self.test_wmap.get_codes()

        self.assertTrue("000" in self.test_wmap.bin_codes)
        self.assertTrue("111" in self.test_wmap.bin_codes)
        self.assertTrue("222" in self.test_wmap.bin_codes)
        self.assertTrue("255" in self.test_wmap.bin_codes)

        self.assertTrue(self.test_wmap.bin_codes["000"]["status"])
        self.assertFalse(self.test_wmap.bin_codes["111"]["status"])
        self.assertFalse(self.test_wmap.bin_codes["222"]["status"])
        self.assertEqual(self.test_wmap.bin_codes["255"]["status"], None)

        self.assertEqual(self.test_wmap.bin_codes["000"]["desc"], "foo")
        self.assertEqual(self.test_wmap.bin_codes["111"]["desc"], "bar")
        self.assertEqual(self.test_wmap.bin_codes["222"]["desc"], "beef")
        self.assertEqual(self.test_wmap.bin_codes["255"]["desc"], "Null bin")

        self.assertEqual(self.test_wmap.bin_codes["000"]["count"], "100")
        self.assertEqual(self.test_wmap.bin_codes["111"]["count"], "10")
        self.assertEqual(self.test_wmap.bin_codes["222"]["count"], "1")
        self.assertEqual(self.test_wmap.bin_codes["255"]["count"], "0")

    def test_gen_map_dec_bins(self):
        """Test the gen_map method."""
        self.test_wmap.device_attr = {}
        self.test_wmap.device_attr[CHIP_SIZE] = [1, 1]
        self.test_wmap.device_attr["rows"] = 2
        self.test_wmap.device_attr["cols"] = 2
        self.test_wmap.bin_codes = {
            "000": {"status": True, "desc": None, "count": "1"},
            "111": {"status": False, "desc": None, "count": "2"},
            "222": {"status": None, "desc": "NULL", "count": "3"},
        }
        self.test_wmap._map_data = {
            "Device": {
                "@BinType": "Decimal",
                "Data": {
                    "Row": ["000111", "111222"],
                },
            }
        }

        self.test_wmap.gen_map()
        self.assertTrue([(0, 0.5), (0.5, 0.5), True, None] in self.test_wmap.pixels)
        self.assertTrue([(0.5, 0.5), (0.5, 0.5), False, None] in self.test_wmap.pixels)
        self.assertTrue([(0, 0), (0.5, 0.5), False, None] in self.test_wmap.pixels)
        self.assertTrue([(0.5, 0), (0.5, 0.5), None, "NULL"] in self.test_wmap.pixels)

    def test_gen_map_dec_bins_min(self):
        """Test the gen_map method with no chip size."""
        self.test_wmap.device_attr = {}
        self.test_wmap.device_attr[CHIP_SIZE] = [0, 0]
        self.test_wmap.device_attr[WAFER_SIZE] = 0.002
        self.test_wmap.device_attr["rows"] = 2
        self.test_wmap.device_attr["cols"] = 2
        self.test_wmap.bin_codes = {
            "000": {"status": True, "desc": None, "count": "1"},
            "111": {"status": False, "desc": None, "count": "2"},
            "222": {"status": None, "desc": "NULL", "count": "3"},
        }
        self.test_wmap._map_data = {
            "Device": {
                "@BinType": "Decimal",
                "Data": {
                    "Row": ["000111", "111222"],
                },
            }
        }

        self.test_wmap.gen_map()
        self.assertTrue([(0, 0.5), (0.5, 0.5), True, None] in self.test_wmap.pixels)
        self.assertTrue([(0.5, 0.5), (0.5, 0.5), False, None] in self.test_wmap.pixels)
        self.assertTrue([(0, 0), (0.5, 0.5), False, None] in self.test_wmap.pixels)
        self.assertTrue([(0.5, 0), (0.5, 0.5), None, "NULL"] in self.test_wmap.pixels)

    def test_gen_map_hex_bins(self):
        """Test the gen_map method."""
        self.test_wmap.device_attr = {}
        self.test_wmap.device_attr[CHIP_SIZE] = [1, 1]
        self.test_wmap.device_attr["rows"] = 2
        self.test_wmap.device_attr["cols"] = 2
        self.test_wmap.bin_codes = {
            "00": {"status": True, "desc": None, "count": "1"},
            "11": {"status": False, "desc": None, "count": "2"},
            "22": {"status": None, "desc": "NULL", "count": "3"},
        }
        self.test_wmap._map_data = {
            "Device": {
                "@BinType": "HexaDecimal",
                "Data": {
                    "Row": ["0011", "1122"],
                },
            }
        }

        self.test_wmap.gen_map()
        self.assertTrue([(0, 0.5), (0.5, 0.5), True, None] in self.test_wmap.pixels)
        self.assertTrue([(0.5, 0.5), (0.5, 0.5), False, None] in self.test_wmap.pixels)
        self.assertTrue([(0, 0), (0.5, 0.5), False, None] in self.test_wmap.pixels)
        self.assertTrue([(0.5, 0), (0.5, 0.5), None, "NULL"] in self.test_wmap.pixels)

    def test_gen_map_bad_units(self):
        """Test the gen_map method with incorrectly spec'd bins."""
        self.test_wmap.device_attr = {}
        self.test_wmap.device_attr[CHIP_SIZE] = [1, 1]
        self.test_wmap.device_attr["rows"] = 2
        self.test_wmap.device_attr["cols"] = 2
        self.test_wmap.bin_codes = {
            "000": {"status": True, "desc": None, "count": "1"},
            "111": {"status": False, "desc": None, "count": "2"},
            "222": {"status": None, "desc": "NULL", "count": "3"},
        }
        self.test_wmap._map_data = {
            "Device": {
                "@BinType": "Decimal",
                "Data": {
                    "Row": ["0011", "1122"],
                },
            }
        }

        with self.assertRaises(KeyError):
            self.test_wmap.gen_map()


class MockWaferMap(wafermap.WaferMap):
    """Mock of a wafermap class."""

    def __init__(self):
        """Override init of wafermap."""
        pass
