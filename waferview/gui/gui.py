"""GUI module."""
import wx
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
        self.create_status(self.sizers["grid"])
        self.create_viewer()
        self.left_panel.SetSizer(self.sizers["left"])
        self.right_panel.SetSizer(self.sizers["right"])
        self.grid_panel.SetSizerAndFit(self.sizers["grid"])
        self.legend_panel.SetSizer(self.sizers["legend"])

    def window(self):
        """Set the window size."""
        screen_width = constants.WINDOW_SIZE[0]
        screen_height = constants.WINDOW_SIZE[1]
        self.SetSize(wx.Size(screen_width, screen_height))
        self.Center()

    def create_panels(self):
        """Create panel structure and sizer elements."""
        # First the main panel with left and right sub-panels
        self.top_panel = wx.Panel(self)
        panel_size = (constants.VIEWER_SIZE[0] + 10, constants.VIEWER_SIZE[1] + 10)
        data_size = (
            constants.WINDOW_SIZE[0] - panel_size[0] - 40,
            constants.WINDOW_SIZE[1] - panel_size[1] - 20,
        )
        self.left_panel = wx.Panel(self.top_panel, size=data_size, name="Wafer Data")
        self.right_panel = wx.Panel(self.top_panel, size=panel_size, name="Wafer Map")

        # In the left panel, we have one panel for the grid and one for the legend
        self.grid_panel = wx.Panel(
            self.left_panel,
            size=(data_size[0], int(panel_size[1] / 3)),
            name="Data Grid",
        )
        self.legend_panel = wx.Panel(
            self.left_panel,
            size=(data_size[0], int(2 * panel_size[1] / 3)),
            pos=(15, int(panel_size[1] / 3) + 10),
            name="Legend",
        )

        # Add main panels to the primary sizer
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.main_sizer.Add(self.left_panel, 0, wx.EXPAND | wx.ALL, border=10)
        self.main_sizer.Add(self.right_panel, 0, wx.EXPAND | wx.ALL, border=10)
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
        self.sizers["left"].Add(self.grid_panel, 0, wx.EXPAND | wx.ALL, border=1)
        self.sizers["left"].Add(self.legend_panel, 0, wx.EXPAND | wx.ALL, border=2)

        # Add text to the legend panel
        font = wx.Font(wx.FontInfo(16).Bold())
        legend_text = wx.StaticText(
            self.legend_panel, label="Wafer Map Legend", style=wx.ALIGN_CENTER
        )
        legend_text.SetFont(font)
        self.sizers["legend"].Add(legend_text, 0, wx.EXPAND | wx.ALL, border=5)

    def create_menu(self):
        """Create the menu bar."""
        self.menubar = MenuBar(self)
        self.SetMenuBar(self.menubar)

    def create_viewer(self):
        """Create the wafer map viewer."""
        try:
            self.viewer.Destroy()
        except AttributeError:
            pass
        self.sizers["right"].AddStretchSpacer(1)
        self.viewer = semimap.Viewer(
            self, self.right_panel, constants.VIEWER_SIZE[0], constants.VIEWER_SIZE[1]
        )
        self.sizers["right"].Add(self.viewer, 0, wx.ALIGN_CENTER)
        self.sizers["right"].AddStretchSpacer(1)

    def create_status(self, sizer):
        """Create the data grid table."""
        self.data_grid = semimap.DataGrid(self.grid_panel)
        sizer.Add(self.data_grid, 1, wx.EXPAND | wx.ALL)

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
