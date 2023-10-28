"""Define constants for GUI."""

# Supported wafer map formats
SUPPORTED_FORMATS = [
    "SEMI G85-1101",
]

# GUI control
WINDOW_SIZE = (1100, 900)
VIEWER_SIZE = (800, 800)
NULL_COLOR = "#666666"
PASS_COLOR = "#66CC00"
FAIL_COLOR = "#CC3300"

# Wafer data keys
WAFER_ID = "wafer_id"
LOT_ID = "lot_id"
WAFER_SIZE = "wafer_size"
CHIP_SIZE = "chip_size"
PRODUCT_ID = "product_id"
CREATE_DATE = "created"
ALL_KEYS = [WAFER_ID, LOT_ID, CHIP_SIZE, PRODUCT_ID, CREATE_DATE]
