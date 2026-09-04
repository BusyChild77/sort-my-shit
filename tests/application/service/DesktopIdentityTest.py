from os import path as os_path
from tkinter import TclError
from unittest import TestCase

from src.application.service.DesktopIdentity import DesktopIdentity


class DesktopIdentityTest(TestCase):
    """The window names itself in one place and the packaging repeats it in two others,
    so what is tested here is that the three still agree. They do not fail loudly when
    they drift: the application simply appears twice on the dock, once under the
    launcher that was clicked and once under a nameless icon of its own."""

    PROJECT = os_path.dirname(os_path.dirname(os_path.dirname(os_path.dirname(os_path.abspath(__file__)))))
    DESKTOP_ENTRY = os_path.join("packaging", "SortMyShit.desktop")
    BUILD_RECIPE = "SortMyShit.spec"

    def test_given_the_desktop_entry_when_reading_its_startup_class_then_it_is_the_one_tk_puts_on_the_window(self):
        """The match GNOME makes between a window and the launcher it came from. A
        StartupWMClass that is not exactly the WM_CLASS matches nothing at all."""
        self.assertEqual(self.__desktop_entry()["StartupWMClass"], DesktopIdentity.window_class())

    def test_given_the_desktop_entry_when_reading_its_name_then_it_is_the_name_the_window_carries(self):
        self.assertEqual(self.__desktop_entry()["Name"], DesktopIdentity.NAME)

    def test_given_the_desktop_entry_when_reading_it_then_it_names_the_icon_that_is_shipped_beside_it(self):
        """The AppImage carries the icon under this basename, and an entry pointing at
        one that is not there falls back to a blank tile on the dock."""
        self.assertEqual(self.__desktop_entry()["Icon"], "SortMyShit")

    def test_given_the_macos_bundle_when_reading_its_name_then_it_is_the_name_the_window_carries(self):
        """The Dock and the menu bar read the bundle rather than the window, so the name
        is repeated in the build recipe -- and has to stay the same string."""
        recipe = self.__build_recipe()

        self.assertIn(f'"CFBundleName": "{DesktopIdentity.NAME}"', recipe)
        self.assertIn(f'"CFBundleDisplayName": "{DesktopIdentity.NAME}"', recipe)

    def test_given_the_application_name_when_tk_is_given_it_then_the_window_class_is_the_title_cased_one(self):
        """Tk title cases whatever it is handed, so the class the desktop sees is never
        quite the name given here. Asking Tk for the name itself is what leaves an entry
        matching nothing."""
        self.assertEqual(DesktopIdentity.window_class(), "Sortmyshit")
        self.assertNotEqual(DesktopIdentity.window_class(), DesktopIdentity.APPLICATION)

    def test_given_a_display_when_opening_the_window_then_it_carries_both_names(self):
        """The one check that reads the names off a real window rather than restating
        them. Skipped where there is no display to open one on, CI included."""
        try:
            window = DesktopIdentity().window()
        except TclError:
            self.skipTest("no display to open a window on")

        try:
            self.assertEqual(window.winfo_class(), DesktopIdentity.window_class())
            self.assertEqual(window.title(), DesktopIdentity.NAME)
        finally:
            window.destroy()

    def __desktop_entry(self) -> dict:
        entry = {}

        with open(os_path.join(self.PROJECT, self.DESKTOP_ENTRY), encoding="utf-8") as entry_file:
            for line in entry_file:
                line = line.strip()

                if line.startswith("#") or "=" not in line:
                    continue

                key, value = line.split("=", 1)
                entry[key] = value

        return entry

    def __build_recipe(self) -> str:
        with open(os_path.join(self.PROJECT, self.BUILD_RECIPE), encoding="utf-8") as recipe_file:
            return recipe_file.read()
