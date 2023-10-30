"""GUI module."""
import wx
import wx.lib.scrolledpanel as scrolled
from waferview.gui import semimap
from waferview.gui import constants


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
        self.create_viewer()
        self.left_panel.SetSizer(self.sizers["left"])
        self.right_panel.SetSizer(self.sizers["right"])
        self.grid_panel.SetSizerAndFit(self.sizers["grid"])
        self.legend_panel.SetSizer(self.sizers["legend"])

    def window(self, no_center=False):
        """Set the window size."""
        (screen_width, screen_height) = wx.DisplaySize()
        # Limit to 4:3 aspect ratio
        self.xSize = int(screen_height * constants.WINDOW_SCALE * constants.ASPECT_RATIO)
        self.ySize = int(screen_height * constants.WINDOW_SCALE)
        self.SetSize(wx.Size(self.xSize, self.ySize))
        if not no_center:
            self.Center()

    def get_panel_sizes(self):
        self.panel_size = self.GetSize()
        # Limit to square aspect ratio
        self.panel_size[0] = int(self.panel_size[1])

        # Make viewer square
        viewerX = self.panel_size[1] * constants.VIEWER_SCALE - 2*constants.BORDER_SIZE
        viewerY = self.panel_size[1] * constants.VIEWER_SCALE - 2*constants.BORDER_SIZE
        dataX = self.panel_size[0] * constants.DATA_SCALE - 2*constants.BORDER_SIZE
        dataY = self.panel_size[1] * constants.DATA_SCALE - 2*constants.BORDER_SIZE

        self.grid_size = (dataX, int(self.panel_size[1] * constants.GRID_SCALE))
        self.legend_size = (dataX, int(self.panel_size[1] * constants.LEGEND_SCALE))

        self.legend_pos = (constants.BORDER_SIZE + 5, self.legend_size[1] + constants.BORDER_SIZE)

        self.viewer_size = (viewerX, viewerY)
        self.data_size = (dataX, dataY)

    def create_panels(self):
        """Create panel structure and sizer elements."""
        # First the main panel with left and right sub-panels
        self.top_panel = wx.Panel(self)
        self.get_panel_sizes()

        self.left_panel = wx.Panel(self.top_panel, size=self.data_size, name="Wafer Data")
        self.right_panel = wx.Panel(self.top_panel, size=self.panel_size, name="Wafer Map")

        # In the left panel, we have one panel for the grid and one for the legend
        self.grid_panel = wx.Panel(
            self.left_panel,
            size=self.grid_size,
            name="Data Grid",
        )
        self.legend_panel = scrolled.ScrolledPanel(
            self.left_panel,
            size=self.legend_size,
            pos=self.legend_pos,
            name="Legend",
        )

        # Add main panels to the primary sizer
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.main_sizer.Add(self.left_panel, 0, wx.EXPAND | wx.ALL, border=constants.BORDER_SIZE)
        self.main_sizer.Add(self.right_panel, 1, wx.EXPAND | wx.ALL, border=constants.BORDER_SIZE)
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
            "left": wx.BoxSizer(wx.VERTICAL),
            "right": wx.BoxSizer(),
            "grid": wx.BoxSizer(),
            "legend": wx.BoxSizer(wx.VERTICAL),
        }

        # Draw the grid and legend panels at startup
        self.sizers["left"].Add(self.grid_panel, 1, wx.EXPAND | wx.ALL, border=1)
        self.sizers["left"].Add(self.legend_panel, 1, wx.EXPAND | wx.ALL, border=2)

        # Add text to the legend panel
        font = wx.Font(wx.FontInfo(16).Bold())
        legend_text = wx.StaticText(
            self.legend_panel, label="Wafer Map Legend", style=wx.ALIGN_CENTER
        )
        legend_text.SetFont(font)
        self.sizers["legend"].Add(legend_text, 1, wx.ALL|wx.ALIGN_CENTER, border=5)

    def create_menu(self):
        """Create the menu bar."""
        self.menubar = MenuBar(self)
        self.SetMenuBar(self.menubar)

    def create_viewer(self):
        """Create the wafer map viewer."""
        try:
            pixels = self.viewer.pixel_elements
            colors = self.viewer.color_map
            self.viewer.Destroy()
        except AttributeError:
            pixels = {}
            colors = {}
#        self.sizers["right"].AddStretchSpacer(1)
        self.viewer = semimap.Viewer(
            self, self.right_panel, self.viewer_size[0], self.viewer_size[1]
        )
        self.viewer.pixel_elements = pixels
        self.viewer.color_map = colors
        self.sizers["right"].Add(self.viewer, 1, wx.EXPAND | wx.ALL)
#        self.sizers["right"].AddStretchSpacer(1)

    def create_status(self):
        """Create the data grid table."""
        self.data_grid = semimap.DataGrid(self.grid_panel)
        self.sizers["grid"].Add(self.data_grid, 1, wx.ALL)

    def map_filename(self):
        """Return the wafermap file name."""
        return self.filemenu.file_name


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
        self.parent.Bind(wx.EVT_MENU, self.file_browser, id=wx.ID_OPEN)

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
