from unittest import TestCase
from unittest.mock import Mock

from src.domain.entity.Release import Release
from src.domain.entity.Version import Version
from src.domain.repository.InstallationRepositoryInterface import InstallationRepositoryInterface
from src.domain.repository.ReleaseRepositoryInterface import ReleaseRepositoryInterface
from src.domain.service.update.CheckForUpdate import CheckForUpdate


class CheckForUpdateTest(TestCase):
    RUNNING_VERSION = "1.0.2"

    def setUp(self):
        self.stamped_version = Version.CURRENT
        Version.CURRENT = self.RUNNING_VERSION

        self.release_repository_mock = Mock(ReleaseRepositoryInterface)
        self.installation_repository_mock = Mock(InstallationRepositoryInterface)
        self.installation_repository_mock.packaged_form.return_value = InstallationRepositoryInterface.APPIMAGE

        self.check_for_update = CheckForUpdate(
            self.release_repository_mock,
            self.installation_repository_mock,
        )

        super().setUp()

    def tearDown(self):
        Version.CURRENT = self.stamped_version

        super().tearDown()

    def test_given_a_newer_release_when_looking_then_it_is_offered(self):
        release = self.__release("v1.0.3")
        self.release_repository_mock.fetch_latest.return_value = release

        self.assertEqual(self.check_for_update.look(), (CheckForUpdate.AVAILABLE, release))

    def test_given_the_running_version_when_looking_then_nothing_is_offered(self):
        self.release_repository_mock.fetch_latest.return_value = self.__release("v1.0.2")

        self.assertEqual(self.check_for_update.look(), (CheckForUpdate.UP_TO_DATE, None))

    def test_given_an_older_release_when_looking_then_nothing_is_offered(self):
        """A release deleted from GitHub must never drag the app backwards."""
        self.release_repository_mock.fetch_latest.return_value = self.__release("v1.0.1")

        self.assertEqual(self.check_for_update.look(), (CheckForUpdate.UP_TO_DATE, None))

    def test_given_no_network_when_looking_then_it_says_so_rather_than_up_to_date(self):
        self.release_repository_mock.fetch_latest.return_value = None

        self.assertEqual(self.check_for_update.look(), (CheckForUpdate.UNREACHABLE, None))

    def test_given_a_run_from_the_sources_when_looking_then_nothing_is_checked(self):
        self.installation_repository_mock.packaged_form.return_value = InstallationRepositoryInterface.SOURCES

        self.assertEqual(self.check_for_update.look(), (CheckForUpdate.NOT_UPDATABLE, None))
        self.release_repository_mock.fetch_latest.assert_not_called()

    def test_given_an_unstamped_build_when_looking_then_nothing_is_checked(self):
        """0.0.0 is behind every release, so an unstamped build would update forever."""
        Version.CURRENT = Version.DEVELOPMENT

        self.assertEqual(self.check_for_update.look(), (CheckForUpdate.NOT_UPDATABLE, None))
        self.release_repository_mock.fetch_latest.assert_not_called()

    def __release(self, tag: str) -> Release:
        return Release(Version(tag), {"SortMyShit-x86_64.AppImage": "https://example.test/app"})
