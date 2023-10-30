"""GUI elements for wafer map."""

import wx
import wx.grid
from waferview import wafermap
from waferview.gui import constants


class Viewer(wx.Panel):
    """Frame for Wafer Visualization."""

    def __init__(self, top, parent, width, height):
        """Initialize the viewer panel."""
        width, height = parent.GetSize()
        wx.Panel.__init__(self, parent, size=(width, height))
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.top = top
        self.grid = top.data_grid
        self.legend_sizer = top.sizers["legend"]
        self.legend_parent = top.legend_panel
        self.pixel_elements = {}
        self.color_map = {}
        scale_val = 0.95 * min(width, height)
        self.xoffset = int((0.95 * width - scale_val) / 2)
        self.yoffset = int((0.95 * height - scale_val) / 2)
        self.scale = (scale_val, scale_val)

    def OnPaint(self, event):
        """Handle painting events."""
        self.Refresh()
        self.Update()
        dc = wx.PaintDC(self)
        dc.SetPen(
            wx.Pen(wx.Colour(constants.NULL_COLOR), width=0.1, style=wx.PENSTYLE_SOLID)
        )
        (width, height) = self.top.right_panel.GetSize()
        xScale = min(width, height) / self.scale[0]
        yScale = min(width, height) / self.scale[1]
        dc.SetUserScale(xScale, yScale)

        for key, rects in self.pixel_elements.items():
            try:
                color = self.color_map[key]
            except KeyError:
                color = wx.Colour(constants.NULL_COLOR)

            dc.SetBrush(wx.Brush(color, style=wx.BRUSHSTYLE_SOLID))
            dc.DrawRectangleList(rects)

    def generate_map(self, filename):
        """Generate the wafermap bitmap objects."""
        self.wmap = wafermap.WaferMap(filename)
        self.pixel_elements = {}
        self.color_map = {}
        prog_max = self.wmap.device_attr["rows"]
        prog_incr = self.wmap.device_attr["cols"]
        col_count = 0
        row_count = 0
        self.pass_count = 0
        self.total_count = 0
        dialog = wx.ProgressDialog(
            "Generating Visualization",
            "Time Remaining",
            prog_max,
            style=wx.PD_CAN_ABORT | wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME,
        )
        for pixel in self.wmap.pixels:
            loc = (
                pixel[0][0] * self.scale[0] + self.xoffset,
                pixel[0][1] * self.scale[1] + self.yoffset,
            )
            size = (pixel[1][0] * self.scale[0], pixel[1][1] * self.scale[1] - 1)
            color = wx.Colour(constants.NULL_COLOR)
            if pixel[2]:
                color = wx.Colour(constants.PASS_COLOR)
                self.pass_count += 1
                self.total_count += 1
            elif not pixel[2] and pixel[2] is not None:
                self.total_count += 1
                try:
                    color = wx.Colour(self.color_map[pixel[3]])
                except KeyError:
                    color = wx.Colour(constants.FAIL_COLOR)

            self.color_map[pixel[3]] = color
            rectangle = [loc[0], loc[1], size[0], size[1]]

            try:
                self.pixel_elements[pixel[3]].append(rectangle)
            except KeyError:
                self.pixel_elements[pixel[3]] = [rectangle]
            col_count += 1
            if col_count > prog_incr:
                col_count = 0
                row_count += 1
                dialog.Update(row_count)

        dialog.Destroy()
        self.wmap.device_attr["total_die"] = self.total_count
        self.wmap.device_attr["pass"] = self.pass_count
        self.wmap.device_attr["fail"] = self.total_count - self.pass_count
        self.wmap.device_attr["yield"] = round(
            self.pass_count / self.total_count * 100.0, 2
        )
        self.update_data()
        self.generate_legend()

    def update_pixels(self, key, new_color):
        """Update pixels in viewer."""
        self.color_map[key] = wx.Colour(new_color)

    def update_data(self):
        """Update data based on wafermap."""
        for row, loc in self.grid.row_map.items():
            value = self.wmap.device_attr[row]
            if row == constants.CHIP_SIZE:
                value = f"{value[0]}, {value[1]}"
            elif row == "yield":
                value = f"{value} %"
            self.grid.SetCellValue(loc, 0, str(value))

    def generate_legend(self):
        """Generate the color legend based on the wafer map."""
        for legend_key, color in self.color_map.items():
            self.legend_sizer.Add(
                LegendEntry(
                    self,
                    self.pixel_elements[legend_key],
                    self.legend_parent,
                    legend_key,
                    color,
                ),
                1,
                wx.EXPAND | wx.ALIGN_TOP,
            )

        self.top.legend_panel.SetSizer(self.legend_sizer)
        self.top.legend_panel.SetupScrolling()
        # Super janky, but only way I could get the legend to draw
        (sw, sh) = wx.DisplaySize()
        self.top.SetSize(
            wx.Size(
                min(sw, sh) * constants.WINDOW_SCALE - 1,
                min(sw, sh) * constants.WINDOW_SCALE - 1,
            )
        )
        self.top.window(no_center=True)


class DataGrid(wx.grid.Grid):
    """Data grid display."""

    def __init__(self, parent):
        """Initialize the data display grid."""
        wx.grid.Grid.__init__(self, parent, 1)
        self.initialize()

    def initialize(self):
        """Create the base structure for the data grid."""
        data_keys = constants.ALL_KEYS
        data_keys.extend(["total_die", "pass", "fail", "yield"])
        self.CreateGrid(len(data_keys), 1)
        self.SetColLabelValue(0, "Value")
        self.row_map = {}
        row_count = 0
        for key in data_keys:
            self.row_map[key] = row_count
            self.SetRowLabelValue(row_count, key)
            row_count += 1


class LegendEntry(wx.Panel):
    """Legend entry."""

    def __init__(self, viewer, pixels, parent, text, color):
        """Initialize the wafer map legend."""
        wx.Panel.__init__(self, parent)
        self.viewer = viewer
        self.pixels = pixels
        self.text = text
        self.color = color
        self.initialize()

    def initialize(self):
        """Create the base structure for the legend."""
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetBackgroundColour("#EAEAEA")
        self.SetWindowStyle(wx.BORDER_THEME)
        self.create_text()
        self.create_color_picker()
        self.SetSizer(self.sizer)

    def create_text(self):
        """Create the legend text."""
        self.text_panel = wx.Panel(self)
        self.check_box = wx.CheckBox(self.text_panel, -1, self.text)
        self.check_box.SetValue(True)
        self.Bind(wx.EVT_CHECKBOX, self.toggle_highlight)

        self.sizer.Add(self.text_panel, 1, wx.ALL, border=2)

    def create_color_picker(self):
        """Create the legend color chooser."""
        self.color_panel = wx.Panel(self)
        self.color_box = wx.ColourPickerCtrl(
            self.color_panel, colour=self.color, size=(40, 20)
        )
        self.Bind(wx.EVT_COLOURPICKER_CHANGED, self.update_color)
        self.sizer.Add(self.color_panel, 1, wx.EXPAND | wx.ALL)

    def toggle_highlight(self, event):
        """Re-draw the bitmaps when checkbox is toggled."""
        if self.check_box.GetValue():
            color = self.color
        else:
            color = constants.NULL_COLOR

        self.viewer.update_pixels(self.text, color)

    def update_color(self, event):
        """Re-draw the bitmaps when the color is changed."""
        color = wx.Colour(self.color_box.GetColour())
        self.color = color
        self.viewer.update_pixels(self.text, color)
