from os import path as os_path
from sys import modules as sys_modules
from unittest import TestCase

from src.application.service.IconProvider import IconProvider


class IconProviderTest(TestCase):
    """The icon is a file shipped alongside the code, so what is tested here is that it
    is found — from the sources and from a bundle — and that it is actually there."""

    def setUp(self):
        self.sys_module = sys_modules["sys"]

    def tearDown(self):
        if hasattr(self.sys_module, "_MEIPASS"):
            delattr(self.sys_module, "_MEIPASS")

    def test_given_the_sources_when_reading_the_icon_path_then_an_existing_file_is_returned(self):
        self.assertTrue(os_path.isfile(IconProvider().path()))

    def test_given_the_sources_when_reading_the_icon_path_then_it_does_not_depend_on_the_working_directory(self):
        self.assertTrue(os_path.isabs(IconProvider().path()))

    def test_given_a_bundle_when_reading_the_icon_path_then_it_points_inside_the_unpacked_folder(self):
        self.sys_module._MEIPASS = os_path.join("_", "unpacked")

        self.assertEqual(
            IconProvider().path(),
            os_path.join("_", "unpacked", "src", "application", "assets", "icon.png"),
        )

    def test_given_the_shipped_icon_when_scaling_it_down_then_the_logo_comes_out_at_the_asked_for_size(self):
        """Tk shrinks an image by keeping one pixel out of every n, so the factor is
        what decides the size the logo beside the wordmark is drawn at."""
        icon_side = 512

        self.assertEqual(icon_side // IconProvider.scale_factor(icon_side), IconProvider.LOGO_SIZE)

    def test_given_an_icon_smaller_than_the_logo_when_scaling_it_down_then_it_is_left_alone(self):
        """Subsampling by zero is an error and by one is a copy: an artwork already
        smaller than the logo keeps its size rather than breaking the side bar."""
        self.assertEqual(IconProvider.scale_factor(16), 1)

    def test_given_the_shipped_icon_when_reading_it_then_it_is_a_png_tkinter_can_load(self):
        with open(IconProvider().path(), "rb") as icon_file:
            self.assertEqual(icon_file.read(8), b"\x89PNG\r\n\x1a\n")
