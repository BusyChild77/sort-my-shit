import sys

from os import path as os_path
from tkinter import PhotoImage


class IconProvider:
    """Finds the application icon and hands it over as a Tk image.

    The file sits next to the sources when the app is run with python, and inside the
    folder PyInstaller unpacks the bundle into once it is compiled, so the lookup goes
    through both rather than through the current working directory.

    LOGO_SIZE is the side of the side bar logo in pixels, see
    .claude/recipes/application-layer.md:156.
    """

    ICON_FILE = "icon.png"
    BUNDLED_ASSETS = os_path.join("src", "application", "assets")

    LOGO_SIZE = 32

    def __init__(self):
        self.icon = None
        self.logo_image = None

    def get(self) -> PhotoImage:
        """Held once built, see .claude/recipes/application-layer.md:150."""
        if self.icon is None:
            self.icon = PhotoImage(file=self.path())

        return self.icon

    def logo(self) -> PhotoImage:
        """The same artwork, small enough to sit beside a line of text."""
        if self.logo_image is None:
            icon = self.get()
            self.logo_image = icon.subsample(self.scale_factor(icon.width()))

        return self.logo_image

    @classmethod
    def scale_factor(cls, width: int) -> int:
        """Tk subsamples by keeping one pixel out of every n, so the divisor is what is
        computed here rather than a target size -- and it is never zero, whatever the
        icon happens to measure."""
        return max(1, width // cls.LOGO_SIZE)

    def path(self) -> str:
        """_MEIPASS only exists once PyInstaller has unpacked the bundle, so it is read
        through getattr."""
        bundle = getattr(sys, "_MEIPASS", None)

        if bundle is not None:
            return os_path.join(bundle, self.BUNDLED_ASSETS, self.ICON_FILE)

        return os_path.join(self.__assets_directory(), self.ICON_FILE)

    def __assets_directory(self) -> str:
        return os_path.join(os_path.dirname(os_path.dirname(os_path.abspath(__file__))), "assets")
