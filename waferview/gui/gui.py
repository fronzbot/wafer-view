"""GUI module."""
import importlib.metadata
import os
import wx
import wx.adv
import wx.lib.scrolledpanel as scrolled
from waferview.gui import semimap
from waferview.gui import constants

__version__ = importlib.metadata.version("wafer-view")


def run():
    """Run the GUI."""
    app = wx.App()
    top = AppTop("Wafer-View: Open Source Wafer Map Viewer Utility")
    top.Show()
    app.MainLoop()


class AppTop(wx.Frame):
    """Main application."""

    def __init__(self, title):
        """Initialize the app."""
        wx.Frame.__init__(self, None, title=title)
        self.window()
        self.initialize()

    def initialize(self):
        """Create all panels and frames for the GUI."""
        self.create_panels()
        self.create_menu()
        self.create_status()
        self.create_controls()
        self.create_viewer()
        self.left_panel.SetSizer(self.sizers["left"])
        self.right_panel.SetSizer(self.sizers["right"])
        self.grid_panel.SetSizerAndFit(self.sizers["grid"])
        self.legend_panel.SetSizer(self.sizers["legend"])
        # Super janky, but only way I could get everything to work in windows
        (sw, sh) = self.GetSize()
        self.SetSize(wx.Size(sw - 1, sh - 1))
        self.SetSize(wx.Size(sw, sh))

    def window(self):
        """Set the window size."""
        (screen_width, screen_height) = wx.DisplaySize()
        # Limit to 4:3 aspect ratio
        self.xSize = int(
            screen_height * constants.WINDOW_SCALE * constants.ASPECT_RATIO
        )
        self.ySize = int(screen_height * constants.WINDOW_SCALE)
        self.SetSize(wx.Size(self.xSize, self.ySize))

    def get_panel_sizes(self):
        """Get panel sizes based on screen size."""
        self.panel_size = self.GetSize()
        # Limit to square aspect ratio
        self.panel_size[0] = int(self.panel_size[1])

        # Make viewer square
        viewerX = (
            self.panel_size[1] * constants.VIEWER_SCALE - 2 * constants.BORDER_SIZE
        )
        viewerY = (
            self.panel_size[1] * constants.VIEWER_SCALE - 2 * constants.BORDER_SIZE
        )
        dataX = self.panel_size[0] * constants.DATA_SCALE - 2 * constants.BORDER_SIZE
        dataY = self.panel_size[1] * constants.DATA_SCALE - 2 * constants.BORDER_SIZE

        self.grid_size = (dataX, int(self.panel_size[1] * constants.GRID_SCALE))
        self.legend_size = (dataX, int(self.panel_size[1] * constants.LEGEND_SCALE))
        self.control_size = (dataX, 50)

        self.legend_pos = (
            constants.BORDER_SIZE + 5,
            self.legend_size[1] + constants.BORDER_SIZE,
        )

        self.viewer_size = (viewerX, viewerY)
        self.data_size = (dataX, dataY)

    def create_panels(self):
        """Create panel structure and sizer elements."""
        # First the main panel with left and right sub-panels
        self.top_panel = wx.Panel(self)
        self.get_panel_sizes()

        self.left_panel = wx.Panel(
            self.top_panel, size=self.data_size, name="Wafer Data"
        )
        self.right_panel = wx.Panel(
            self.top_panel, size=self.panel_size, name="Wafer Map"
        )

        # In the left panel, we have one panel for the grid and one for the legend
        self.grid_panel = wx.Panel(
            self.left_panel,
            size=self.grid_size,
            name="Data Grid",
        )

        self.control_panel = wx.Panel(
            self.left_panel, size=self.control_size, name="Control Panel."
        )

        # Add main panels to the primary sizer
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.main_sizer.Add(
            self.left_panel, 0, wx.EXPAND | wx.ALL, border=constants.BORDER_SIZE
        )
        self.main_sizer.Add(
            self.right_panel, 1, wx.EXPAND | wx.ALL, border=constants.BORDER_SIZE
        )
        self.top_panel.SetSizer(self.main_sizer)

        # Set background colors
        self.right_panel.SetBackgroundColour(constants.NULL_COLOR)
        self.right_panel.SetWindowStyle(wx.BORDER_THEME)

        self.left_panel.SetBackgroundColour("#AAAAAA")
        self.left_panel.SetWindowStyle(wx.BORDER_THEME)

        self.grid_panel.SetBackgroundColour("#AAAAAA")
        self.grid_panel.SetWindowStyle(wx.BORDER_THEME)

        # Create sizers for other panels
        self.sizers = {
            "left": wx.FlexGridSizer(rows=3, cols=1, vgap=1, hgap=1),
            "right": wx.BoxSizer(),
            "grid": wx.BoxSizer(),
        }

        # Draw the grid and legend panels at startup
        self.sizers["left"].Add(self.grid_panel, 1, wx.EXPAND | wx.ALL, border=1)

    def create_menu(self):
        """Create the menu bar."""
        self.menubar = MenuBar(self)
        self.SetMenuBar(self.menubar)

    def create_viewer(self):
        """Create the wafer map viewer."""
        try:
            pixels = self.viewer.pixel_elements
            colors = self.viewer.color_map
            scale = self.viewer.scale
            self.viewer.Destroy()
        except AttributeError:
            pixels = {}
            colors = {}
        self.create_legend()
        self.viewer = semimap.Viewer(
            self, self.right_panel, self.viewer_size[0], self.viewer_size[1]
        )
        try:
            self.viewer.scale = scale
        except UnboundLocalError:
            self.viewer.pixel_elements = pixels
        self.viewer.color_map = colors
        self.sizers["right"].Add(self.viewer, 1, wx.EXPAND | wx.ALL)
        self.viewer.Bind(wx.EVT_KEY_DOWN, self.process_keypress)

    def create_controls(self):
        """Create the wafermap controls section."""
        self.sizers["control"] = wx.FlexGridSizer(rows=2, cols=4, gap=wx.Size(1, 3))
        btn_down = wx.Button(self.control_panel, 1, "Down", size=(10, 10))
        btn_up = wx.Button(self.control_panel, 1, "Up")
        btn_left = wx.Button(self.control_panel, 1, "Left")
        btn_right = wx.Button(self.control_panel, 1, "Right")
        btn_zoom_out = wx.Button(self.control_panel, 1, "Zoom -")
        btn_zoom_in = wx.Button(self.control_panel, 1, "Zoom +")
        btn_fit = wx.Button(self.control_panel, 1, "Fit")

        self.sizers["control"].Add(btn_left, -1, wx.EXPAND | wx.ALL, border=1)
        self.sizers["control"].Add(btn_down, -1, wx.EXPAND | wx.ALL, border=1)
        self.sizers["control"].Add(btn_up, -1, wx.EXPAND | wx.ALL, border=1)
        self.sizers["control"].Add(btn_right, -1, wx.EXPAND | wx.ALL, border=1)

        self.sizers["control"].Add(btn_zoom_out, -1, wx.EXPAND | wx.ALL, border=1)
        self.sizers["control"].Add(btn_zoom_in, -1, wx.EXPAND | wx.ALL, border=1)
        self.sizers["control"].Add(btn_fit, -1, wx.EXPAND | wx.ALL, border=1)

        self.control_panel.SetSizer(self.sizers["control"])
        self.sizers["left"].Add(self.control_panel, 1, wx.EXPAND | wx.ALL, border=1)

        btn_left.Bind(
            wx.EVT_BUTTON, lambda event: self.set_offset(event, constants.STEP_LEFT)
        )
        btn_down.Bind(
            wx.EVT_BUTTON, lambda event: self.set_offset(event, constants.STEP_DOWN)
        )
        btn_up.Bind(
            wx.EVT_BUTTON, lambda event: self.set_offset(event, constants.STEP_UP)
        )
        btn_right.Bind(
            wx.EVT_BUTTON, lambda event: self.set_offset(event, constants.STEP_RIGHT)
        )

        btn_zoom_out.Bind(
            wx.EVT_BUTTON, lambda event: self.set_scale(event, constants.ZOOM_OUT)
        )
        btn_zoom_in.Bind(
            wx.EVT_BUTTON, lambda event: self.set_scale(event, constants.ZOOM_IN)
        )
        btn_fit.Bind(wx.EVT_BUTTON, lambda event: self.set_scale(event, 0))

        # Key mapping for events
        self.key_map = {
            wx.WXK_NUMPAD4: ("step", constants.STEP_LEFT),
            wx.WXK_LEFT: ("step", constants.STEP_LEFT),
            wx.WXK_NUMPAD2: ("step", constants.STEP_DOWN),
            wx.WXK_DOWN: ("step", constants.STEP_DOWN),
            wx.WXK_NUMPAD8: ("step", constants.STEP_UP),
            wx.WXK_UP: ("step", constants.STEP_UP),
            wx.WXK_NUMPAD6: ("step", constants.STEP_RIGHT),
            wx.WXK_RIGHT: ("step", constants.STEP_RIGHT),
            ord("h"): ("step", constants.STEP_LEFT),
            ord("H"): ("step", constants.STEP_LEFT),
            ord("j"): ("step", constants.STEP_DOWN),
            ord("J"): ("step", constants.STEP_DOWN),
            ord("k"): ("step", constants.STEP_UP),
            ord("K"): ("step", constants.STEP_UP),
            ord("l"): ("step", constants.STEP_RIGHT),
            ord("L"): ("step", constants.STEP_RIGHT),
            wx.WXK_PAGEDOWN: ("zoom", constants.ZOOM_IN),
            wx.WXK_PAGEUP: ("zoom", constants.ZOOM_OUT),
            wx.WXK_NUMPAD_ADD: ("zoom", constants.ZOOM_IN),
            wx.WXK_NUMPAD_SUBTRACT: ("zoom", constants.ZOOM_OUT),
            wx.WXK_NUMPAD_EQUAL: ("zoom", 0),
            wx.WXK_NUMPAD0: ("zoom", 0),
            ord("]"): ("zoom", constants.ZOOM_IN),
            ord("["): ("zoom", constants.ZOOM_OUT),
            ord("f"): ("zoom", 0),
            ord("F"): ("zoom", 0),
            ord("0"): ("zoom", 0),
        }

    def create_legend(self):
        """Create the legend section."""
        try:
            self.legend_panel.Destroy()
        except AttributeError:
            pass
        self.legend_panel = scrolled.ScrolledPanel(
            self.left_panel,
            size=self.legend_size,
            pos=self.legend_pos,
            name="Legend",
        )
        self.sizers["left"].Add(self.legend_panel, 1, wx.EXPAND | wx.ALL, border=2)
        self.sizers["legend"] = wx.BoxSizer(wx.VERTICAL)
        font = wx.Font(wx.FontInfo(16).Bold())
        legend_text = wx.StaticText(
            self.legend_panel, label="Wafer Map Legend", style=wx.ALIGN_CENTER
        )
        legend_text.SetFont(font)
        self.sizers["legend"].Add(legend_text, 1, wx.ALL | wx.ALIGN_CENTER, border=5)

    def create_status(self):
        """Create the data grid table."""
        self.data_grid = semimap.DataGrid(self.grid_panel)
        self.sizers["grid"].Add(self.data_grid, 1, wx.ALL)

    def map_filename(self):
        """Return the wafermap file name."""
        return self.filemenu.file_name

    def set_scale(self, event, zoom_type):
        """Set wafermap scaling based on zoom button input."""
        self.viewer.zoom_factor = zoom_type * self.viewer.zoom_factor
        if zoom_type == 0:
            self.viewer.zoom_factor = 1
            self.viewer.xorigin = 0
            self.viewer.yorigin = 0

        self.viewer.Refresh()
        self.viewer.Update()

    def set_offset(self, event, offset):
        """Set the frame offset."""
        self.viewer.xorigin = self.viewer.xorigin + offset[0] * self.viewer.zoom_factor
        self.viewer.yorigin = self.viewer.yorigin + offset[1] * self.viewer.zoom_factor
        self.viewer.Refresh()
        self.viewer.Update()

    def process_keypress(self, event):
        """Process a keypress event."""
        key_input = event.GetKeyCode()
        key_data = self.key_map.get(key_input, (None, None))
        if key_data[0] == "step":
            self.set_offset(None, key_data[1])
        elif key_data[0] == "zoom":
            self.set_scale(None, key_data[1])


class MenuBar(wx.MenuBar):
    """File Menu Bar."""

    def __init__(self, parent):
        """Initialize the menu bar."""
        wx.MenuBar.__init__(self)
        self.parent = parent
        self.initialize()

    def initialize(self):
        """Generate the menu bar structure."""
        filemenu = wx.Menu()
        self.Append(filemenu, "&File")
        filemenu.Append(wx.ID_OPEN, "O&pen\tCtrl-O")
        filemenu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program")
        filemenu.Append(wx.ID_SAVE, "S&ave\tCtrl-S", "Save wafermap image")
        self.parent.Bind(wx.EVT_MENU, self.save_image, id=wx.ID_SAVE)
        self.parent.Bind(wx.EVT_MENU, self.file_browser, id=wx.ID_OPEN)

        helpmenu = wx.Menu()
        self.Append(helpmenu, "&Help")
        helpmenu.Append(wx.ID_ABOUT, "", "About Waferview")
        self.parent.Bind(wx.EVT_MENU, self.about_screen, id=wx.ID_ABOUT)

    def about_screen(self, event):
        """Open the About dialog on event."""
        about = wx.adv.AboutDialogInfo()
        about.SetName("Wafer-View")
        about.SetVersion(__version__)
        about.SetLicense("Apache 2.0 <https://github.com/fronzbot/wafer-view/LICENSE>")
        about.SetDescription("Open source wafer map viewer utility")
        about.SetCopyright("(C) 2023")
        about.SetWebSite("http://github.com/fronzbot/wafer-view")
        about.AddDeveloper("Kevin Fronczak <kfronczak@gmail.com>")

        wx.adv.AboutBox(about)

    def save_image(self, event):
        """Save image drawn on wafermap viewer."""
        with wx.DirDialog(
            self,
            message="Choose save directory",
            defaultPath=".",
        ) as dir_dialog:
            if dir_dialog.ShowModal() == wx.ID_CANCEL:
                return
            dir_name = dir_dialog.GetPath()

        dc = self.parent.viewer.OnPaint(None)
        size = self.parent.viewer.GetSize()
        bmp = wx.Bitmap(size.width, size.height)
        memdc = wx.MemoryDC()
        memdc.SelectObject(bmp)

        memdc.Blit(0, 0, size.width, size.height, dc, 0, 0)
        memdc.SelectObject(wx.NullBitmap)

        img = bmp.ConvertToImage()
        file_name = os.path.join(dir_name, "wafermap.bmp")
        img.SaveFile(file_name, wx.BITMAP_TYPE_PNG)

        notif = wx.MessageDialog(
            None,
            f"{file_name}",
            caption="Wafer Map Image Saved!",
            style=wx.OK | wx.ALIGN_RIGHT,
        )
        notif.ShowModal()

    def file_browser(self, event):
        """Open the file browser on event."""
        with wx.FileDialog(
            self,
            message="Choose file",
            defaultDir=".",
            defaultFile="",
            wildcard="XML files (*.xml)|*.xml",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
        ) as file_dialog:
            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return
            self.file_name = file_dialog.GetPath()

        # Once a file is selected, we need to generate the map and viewer
        self.parent.create_viewer()
        self.parent.viewer.generate_map(self.file_name)
