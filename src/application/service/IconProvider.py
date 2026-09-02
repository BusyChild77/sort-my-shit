# _MEIPASS only exists once PyInstaller has unpacked the bundle, so sys is read
# through getattr rather than imported from.
import sys

from os import path as os_path
from tkinter import PhotoImage


class IconProvider:
    """Finds the application icon and hands it over as a Tk image.

    The file sits next to the sources when the app is run with python, and inside the
    folder PyInstaller unpacks the bundle into once it is compiled, so the lookup goes
    through both rather than through the current working directory.
    """

    ICON_FILE = "icon.png"
    BUNDLED_ASSETS = os_path.join("src", "application", "assets")

    def __init__(self):
        self.icon = None

    def get(self) -> PhotoImage:
        # Tk keeps no reference of its own and drops the icon as soon as the
        # PhotoImage is garbage collected, so the instance is held here.
        if self.icon is None:
            self.icon = PhotoImage(file=self.path())

        return self.icon

    def path(self) -> str:
        bundle = getattr(sys, "_MEIPASS", None)

        if bundle is not None:
            return os_path.join(bundle, self.BUNDLED_ASSETS, self.ICON_FILE)

        return os_path.join(self.__assets_directory(), self.ICON_FILE)

    def __assets_directory(self) -> str:
        return os_path.join(os_path.dirname(os_path.dirname(os_path.abspath(__file__))), "assets")
