"""Define constants for GUI."""

# Supported wafer map formats
SUPPORTED_FORMATS = [
    "SEMI G85-1101",
]

# GUI control
WINDOW_SIZE = (1100, 900)
VIEWER_SIZE = (800, 800)
ASPECT_RATIO = 1.35
WINDOW_SCALE = 0.65
VIEWER_SCALE = 0.6
DATA_SCALE = 0.4
GRID_SCALE = 0.3
LEGEND_SCALE = 0.7
BORDER_SIZE = 10
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

# Various constants
PASS = "Pass"
FAIL = "Fail"
NULL = "NULL"
DEFAULT_WAFER_SIZE = 300
