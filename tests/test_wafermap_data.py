"""Test wafermap with dummy data."""

import os
import unittest
from waferview import wafermap
from waferview.gui.constants import (
    WAFER_ID,
    LOT_ID,
    WAFER_SIZE,
    CHIP_SIZE,
    PRODUCT_ID,
    CREATE_DATE,
)


TEST_PATH = os.path.split(os.path.abspath(__file__))[0]


class TestWaferMapData(unittest.TestCase):
    """Test the WaferMap class on real XML data."""

    def test_semi_g85_1101_minimal(self):
        """Test G85-1101 minimal standard."""
        TEST_XML = os.path.join(TEST_PATH, "xml/SEMI_G85/SEMI_G85_1101_MIN.xml")
        test_wmap = wafermap.WaferMap(TEST_XML)
        self.assertTrue("00" in test_wmap.bin_codes)
        self.assertTrue("DE" in test_wmap.bin_codes)
        self.assertTrue("AD" in test_wmap.bin_codes)
        self.assertTrue("FF" in test_wmap.bin_codes)
        self.assertEqual(test_wmap.device_attr["rows"], 60)
        self.assertEqual(test_wmap.device_attr["cols"], 60)
        self.assertTrue(test_wmap.bin_codes["00"]["status"])
        self.assertFalse(test_wmap.bin_codes["DE"]["status"])
        self.assertFalse(test_wmap.bin_codes["AD"]["status"])
        self.assertEqual(test_wmap.bin_codes["FF"]["status"], None)
        self.assertEqual(test_wmap.bin_codes["00"]["count"], "2765")
        self.assertEqual(test_wmap.bin_codes["DE"]["count"], "38")
        self.assertEqual(test_wmap.bin_codes["AD"]["count"], "5")
        self.assertEqual(len(test_wmap.pixels), 3600)

    def test_semi_g85_1101_full(self):
        """Test G85-1101 full standard."""
        TEST_XML = os.path.join(TEST_PATH, "xml/SEMI_G85/SEMI_G85_1101_ALL.xml")
        test_wmap = wafermap.WaferMap(TEST_XML)
        self.assertTrue("00" in test_wmap.bin_codes)
        self.assertTrue("DE" in test_wmap.bin_codes)
        self.assertTrue("AD" in test_wmap.bin_codes)
        self.assertTrue("FF" in test_wmap.bin_codes)
        self.assertEqual(test_wmap.device_attr["rows"], 60)
        self.assertEqual(test_wmap.device_attr["cols"], 60)
        self.assertTrue(test_wmap.bin_codes["00"]["status"])
        self.assertFalse(test_wmap.bin_codes["DE"]["status"])
        self.assertFalse(test_wmap.bin_codes["AD"]["status"])
        self.assertEqual(test_wmap.bin_codes["FF"]["status"], None)
        self.assertEqual(test_wmap.bin_codes["00"]["count"], "2765")
        self.assertEqual(test_wmap.bin_codes["DE"]["count"], "38")
        self.assertEqual(test_wmap.bin_codes["AD"]["count"], "5")
        self.assertEqual(len(test_wmap.pixels), 3600)

        exp_attr = {
            WAFER_ID: "ABCD123",
            LOT_ID: "DEADBEEF",
            WAFER_SIZE: 300,
            CHIP_SIZE: [5000, 5000],
            PRODUCT_ID: "FOOBAR",
            CREATE_DATE: "20231028123456",
            "rows": 60,
            "cols": 60,
        }
        self.assertDictEqual(test_wmap.device_attr, exp_attr)
