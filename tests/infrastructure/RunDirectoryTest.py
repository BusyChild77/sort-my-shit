from os import environ as os_environ, path as os_path
from unittest import TestCase
from unittest.mock import patch

from src.infrastructure.RunDirectory import RunDirectory


class RunDirectoryTest(TestCase):
    """Where settings.json lands. Getting this wrong either loses a user's configuration
    on upgrade, or crashes the app on a read only install, so every packaged form is
    covered here."""

    def setUp(self):
        self.environment = patch.dict(os_environ, {}, clear=False)
        self.environment.start()
        os_environ.pop("APPIMAGE", None)

    def tearDown(self):
        self.environment.stop()

    def test_given_a_plain_executable_when_resolving_then_its_own_folder_is_used(self):
        with patch("src.infrastructure.RunDirectory.sys_argv", [os_path.join("/writable", "SortMyShit")]):
            with patch("src.infrastructure.RunDirectory.os_access", return_value=True):
                self.assertEqual(RunDirectory.resolve(), "/writable")

    def test_given_an_appimage_when_resolving_then_the_folder_of_the_appimage_is_used(self):
        os_environ["APPIMAGE"] = "/home/someone/Applications/SortMyShit-1.0.0-x86_64.AppImage"

        with patch("src.infrastructure.RunDirectory.sys_argv", ["/tmp/.mount_abc/usr/bin/SortMyShit"]):
            with patch("src.infrastructure.RunDirectory.os_access", return_value=True):
                self.assertEqual(RunDirectory.resolve(), "/home/someone/Applications")

    def test_given_a_macos_bundle_when_resolving_then_the_folder_holding_the_bundle_is_used(self):
        executable = "/Applications/SortMyShit.app/Contents/MacOS/SortMyShit"

        with patch("src.infrastructure.RunDirectory.sys_argv", [executable]):
            with patch("src.infrastructure.RunDirectory.os_access", return_value=True):
                self.assertEqual(RunDirectory.resolve(), "/Applications")

    def test_given_a_folder_it_cannot_write_to_when_resolving_then_the_configuration_folder_is_used(self):
        with patch("src.infrastructure.RunDirectory.sys_argv", ["/usr/bin/SortMyShit"]):
            with patch("src.infrastructure.RunDirectory.os_access", return_value=False):
                with patch("src.infrastructure.RunDirectory.os_makedirs") as makedirs:
                    resolved = RunDirectory.resolve()

        self.assertNotEqual(resolved, "/usr/bin")
        self.assertTrue(resolved.endswith(RunDirectory.APPLICATION_NAME))
        makedirs.assert_called_once_with(resolved, exist_ok=True)

    def test_given_no_xdg_configuration_folder_when_resolving_then_it_falls_back_under_the_home_folder(self):
        os_environ.pop("XDG_CONFIG_HOME", None)

        with patch("src.infrastructure.RunDirectory.sys_platform", "linux"):
            with patch("src.infrastructure.RunDirectory.sys_argv", ["/usr/bin/SortMyShit"]):
                with patch("src.infrastructure.RunDirectory.os_access", return_value=False):
                    with patch("src.infrastructure.RunDirectory.os_makedirs"):
                        resolved = RunDirectory.resolve()

        self.assertEqual(resolved, os_path.join(os_path.expanduser("~"), ".config", "SortMyShit"))
