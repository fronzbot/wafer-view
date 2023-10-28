"""GUI elements for wafer map."""

import wx
import wx.grid
from waferview import wafermap
from waferview.gui import constants


def get_bitmap(parent, coord, size, color):
    """Generate bitmap for a given die."""
    red, green, blue, alpha = color.Get(includeAlpha=True)
    box = wx.Bitmap.FromRGBA(size[0], size[1], red, green, blue, alpha)
    return wx.StaticBitmap(parent, wx.ID_ANY, box, coord, size)


class Viewer(wx.Panel):
    """Frame for Wafer Visualization."""

    def __init__(self, top, parent, width, height):
        """Initialize the viewer panel."""
        wx.Panel.__init__(self, parent, size=(width, height))
        self.top = top
        self.grid = top.data_grid
        self.legend_sizer = top.sizers["legend"]
        self.legend_parent = top.legend_panel
        self.width = width - 20
        self.height = height - 20
        self.xoff = 10
        self.yoff = 0

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
                pixel[0][0] * self.width + self.xoff,
                pixel[0][1] * self.height + self.yoff,
            )
            size = (pixel[1][0] * self.width - 1, pixel[1][1] * self.height - 1)
            color = wx.Colour(constants.NULL_COLOR)
            if pixel[2]:
                color = wx.Colour(constants.PASS_COLOR)
                # self.color_map[pixel[3]] = constants.PASS_COLOR
                self.pass_count += 1
                self.total_count += 1
            elif not pixel[2] and pixel[2] is not None:
                self.total_count += 1
                try:
                    color = wx.Colour(self.color_map[pixel[3]])
                except KeyError:
                    self.color_map[pixel[3]] = constants.FAIL_COLOR
            try:
                self.pixel_elements[pixel[3]].append(get_bitmap(self, loc, size, color))
            except KeyError:
                self.pixel_elements[pixel[3]] = [get_bitmap(self, loc, size, color)]
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
                wx.EXPAND,
            )

        # Super janky, but only way I could get the legend to draw
        self.top.SetSize(
            wx.Size(constants.WINDOW_SIZE[0] - 1, constants.WINDOW_SIZE[1] - 1)
        )


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

        self.sizer.Add(self.text_panel, 1, wx.EXPAND | wx.ALL, border=2)

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
        color = wx.Colour(color)
        new_pixels = []
        prog_max = len(self.pixels)
        count = 0
        dialog = wx.ProgressDialog(
            "Filtering Die",
            "Time Remaining",
            prog_max,
            style=wx.PD_CAN_ABORT | wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME,
        )
        for pixel in self.pixels:
            new_pix = get_bitmap(
                self.viewer, pixel.GetPosition(), pixel.GetSize(), color
            )
            pixel.Destroy()
            new_pixels.append(new_pix)
            dialog.Update(count)
            count += 1
            if count % 250 == 0:
                dialog.Update(count)
        self.pixels = new_pixels
        dialog.Destroy()

    def update_color(self, event):
        """Re-draw the bitmaps when the color is changed."""
        color = wx.Colour(self.color_box.GetColour())
        new_pixels = []
        prog_max = len(self.pixels)
        count = 0
        dialog = wx.ProgressDialog(
            "Resetting Colors",
            "Time Remaining",
            prog_max,
            style=wx.PD_CAN_ABORT | wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME,
        )
        for pixel in self.pixels:
            new_pix = get_bitmap(
                self.viewer, pixel.GetPosition(), pixel.GetSize(), color
            )
            pixel.Destroy()
            new_pixels.append(new_pix)
            dialog.Update(count)
            count += 1
            if count % 250 == 0:
                dialog.Update(count)
        self.pixels = new_pixels
        dialog.Destroy()
