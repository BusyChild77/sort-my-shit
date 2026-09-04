from tkinter import Tk


class DesktopIdentity:
    """Names the window the two ways a desktop reads it.

    A window carries the name the user reads, and the class the desktop matches against
    the launcher the application was started from. Left to itself Tk sets that class to
    "Tk", which matches no launcher, so GNOME -- and every dock that follows it -- shows
    the window under an icon of its own labelled "Tk", beside the one that was clicked.

    The class can only be given to Tk as the window is created, so the window is built
    here rather than in Main, and the two names are set in the one place.
    """

    # The title bar, and the label under the icon once the window has been matched to
    # its launcher.
    NAME = "Sort My Shit"

    # What that match is made on: the WM_CLASS of the window under X11, and under
    # Wayland through XWayland, which Tk is what runs on.
    APPLICATION = "sortmyshit"

    def window(self) -> Tk:
        root = Tk(className=self.APPLICATION)
        root.title(self.NAME)

        return root

    @classmethod
    def window_class(cls) -> str:
        """The class Tk ends up putting on the window, which is not quite the name handed
        to it: Tk title cases it. This is the string the desktop entry has to carry as
        its StartupWMClass, and the one a window with no launcher is labelled with."""
        return cls.APPLICATION.capitalize()
