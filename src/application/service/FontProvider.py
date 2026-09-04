# _MEIPASS only exists once PyInstaller has unpacked the bundle, so sys is read
# through getattr rather than imported from.
import ctypes
import sys

from os import path as os_path


class FontProvider:
    """Finds the title font shipped with the application and hands it to the system.

    Tk draws with the fonts the platform knows about and offers no way to load one from
    a file, so the file is registered with the platform's own font manager first -- for
    this process only, nothing is installed on the machine. Every call is allowed to
    fail: a font that could not be registered simply is not in the families Tk reports,
    and Typography falls back to a monospace the machine already has.
    """

    # The names the file answers to. One here, but the list stays: a font whose weight
    # is neither regular nor bold is listed by Windows under a family name of its own,
    # and both have to be asked for when that happens.
    FAMILIES = ("Monometric",)
    FONT_FILE = "title-font.otf"
    BUNDLED_ASSETS = os_path.join("src", "application", "assets")

    # AddFontResourceEx, FR_PRIVATE: visible to this process, added to no font folder.
    WINDOWS_PRIVATE_FONT = 0x10
    # CTFontManagerRegisterFontsForURL, kCTFontManagerScopeProcess: the same idea.
    MACOS_PROCESS_SCOPE = 1

    def __init__(self):
        self.registered = None

    def register(self) -> bool:
        """True once the platform has taken the font, and Tk can be asked for it."""
        if self.registered is None:
            self.registered = self.__register()

        return self.registered

    def path(self) -> str:
        bundle = getattr(sys, "_MEIPASS", None)

        if bundle is not None:
            return os_path.join(bundle, self.BUNDLED_ASSETS, self.FONT_FILE)

        return os_path.join(self.__assets_directory(), self.FONT_FILE)

    def __register(self) -> bool:
        font = self.path()

        if not os_path.isfile(font):
            return False

        try:
            if sys.platform == "win32":
                return self.__register_on_windows(font)

            if sys.platform == "darwin":
                return self.__register_on_macos(font)

            return self.__register_with_fontconfig(font)
        except (OSError, AttributeError):
            return False

    def __register_on_windows(self, font: str) -> bool:
        return ctypes.windll.gdi32.AddFontResourceExW(font, self.WINDOWS_PRIVATE_FONT, 0) > 0

    def __register_on_macos(self, font: str) -> bool:
        foundation = ctypes.cdll.LoadLibrary("/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation")
        text = ctypes.cdll.LoadLibrary("/System/Library/Frameworks/CoreText.framework/CoreText")

        foundation.CFURLCreateFromFileSystemRepresentation.restype = ctypes.c_void_p
        foundation.CFURLCreateFromFileSystemRepresentation.argtypes = [
            ctypes.c_void_p, ctypes.c_char_p, ctypes.c_long, ctypes.c_bool,
        ]
        text.CTFontManagerRegisterFontsForURL.restype = ctypes.c_bool
        text.CTFontManagerRegisterFontsForURL.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p]

        path = font.encode()
        url = foundation.CFURLCreateFromFileSystemRepresentation(None, path, len(path), False)

        return bool(text.CTFontManagerRegisterFontsForURL(url, self.MACOS_PROCESS_SCOPE, None))

    def __register_with_fontconfig(self, font: str) -> bool:
        fontconfig = ctypes.CDLL("libfontconfig.so.1")

        fontconfig.FcConfigAppFontAddFile.restype = ctypes.c_int
        fontconfig.FcConfigAppFontAddFile.argtypes = [ctypes.c_void_p, ctypes.c_char_p]

        # No configuration handed over: the one X11 and Tk are already reading is the
        # one the font has to end up in.
        return fontconfig.FcConfigAppFontAddFile(None, font.encode()) == 1

    def __assets_directory(self) -> str:
        return os_path.join(os_path.dirname(os_path.dirname(os_path.abspath(__file__))), "assets")
