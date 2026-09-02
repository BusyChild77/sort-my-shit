from unittest import TestCase
from unittest.mock import Mock

from src.domain.entity.Release import Release
from src.domain.entity.Version import Version
from src.domain.event.EventManagerInterface import EventManagerInterface
from src.domain.repository.InstallationRepositoryInterface import InstallationRepositoryInterface
from src.domain.repository.ReleaseRepositoryInterface import ReleaseRepositoryInterface
from src.domain.service.update.ApplyUpdate import ApplyUpdate


class ApplyUpdateTest(TestCase):
    """The service replaces the running application, so what matters here is that it
    picks the file its own platform can use, and that macOS is never overwritten."""

    DOWNLOADS = "/home/someone/Downloads"

    ASSETS = {
        "SortMyShit-1.0.3-x86_64.AppImage": "https://example.test/appimage",
        "SortMyShit-1.0.3-windows-x86_64.exe": "https://example.test/exe",
        "SortMyShit-1.0.3-macos-arm64.dmg": "https://example.test/dmg",
    }

    def setUp(self):
        self.release_repository_mock = Mock(ReleaseRepositoryInterface)
        self.release_repository_mock.download.side_effect = lambda url, destination: destination

        self.installation_repository_mock = Mock(InstallationRepositoryInterface)
        self.installation_repository_mock.downloads_folder.return_value = self.DOWNLOADS

        self.apply_update = ApplyUpdate(
            self.release_repository_mock,
            self.installation_repository_mock,
            Mock(EventManagerInterface),
        )

        self.release = Release(Version("v1.0.3"), dict(self.ASSETS))

        super().setUp()

    def test_given_an_appimage_when_updating_then_the_appimage_asset_is_downloaded(self):
        self.__packaged_as(InstallationRepositoryInterface.APPIMAGE)

        self.apply_update.apply(self.release)

        self.release_repository_mock.download.assert_called_once_with(
            "https://example.test/appimage",
            self.DOWNLOADS + "/SortMyShit-1.0.3-x86_64.AppImage",
        )

    def test_given_windows_when_updating_then_the_exe_asset_is_downloaded(self):
        self.__packaged_as(InstallationRepositoryInterface.WINDOWS)

        self.apply_update.apply(self.release)

        self.assertEqual(self.release_repository_mock.download.call_args[0][0], "https://example.test/exe")

    def test_given_an_appimage_when_updating_then_the_running_file_is_replaced(self):
        self.__packaged_as(InstallationRepositoryInterface.APPIMAGE)

        outcome = self.apply_update.apply(self.release)

        self.assertEqual(outcome, ApplyUpdate.REPLACED)
        self.installation_repository_mock.replace_with.assert_called_once_with(
            self.DOWNLOADS + "/SortMyShit-1.0.3-x86_64.AppImage"
        )

    def test_given_macos_when_updating_then_the_bundle_is_never_overwritten(self):
        """An unsigned bundle replaced behind Gatekeeper's back refuses to open, so the
        disk image is only downloaded and shown to the user."""
        self.__packaged_as(InstallationRepositoryInterface.MACOS)

        outcome = self.apply_update.apply(self.release)

        self.assertEqual(outcome, ApplyUpdate.HANDED_OVER)
        self.installation_repository_mock.replace_with.assert_not_called()
        self.installation_repository_mock.reveal.assert_called_once_with(
            self.DOWNLOADS + "/SortMyShit-1.0.3-macos-arm64.dmg"
        )

    def test_given_a_release_missing_this_platform_when_updating_then_nothing_is_replaced(self):
        self.__packaged_as(InstallationRepositoryInterface.WINDOWS)
        release = Release(Version("v1.0.3"), {"SortMyShit-1.0.3-x86_64.AppImage": "https://example.test/appimage"})

        with self.assertRaises(FileNotFoundError):
            self.apply_update.apply(release)

        self.release_repository_mock.download.assert_not_called()
        self.installation_repository_mock.replace_with.assert_not_called()

    def __packaged_as(self, packaged_form: str):
        self.installation_repository_mock.packaged_form.return_value = packaged_form
