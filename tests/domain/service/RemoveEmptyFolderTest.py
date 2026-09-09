from unittest import TestCase
from unittest.mock import Mock

from src.domain.event.EventManagerInterface import EventManagerInterface
from src.domain.repository.FileSystemRepositoryInterface import FileSystemRepositoryInterface
from src.domain.repository.SettingsRepositoryInterface import SettingsRepositoryInterface
from src.domain.service.folder.CheckFolder import CheckFolder
from src.domain.service.remove.RemoveEmptyFolder import RemoveEmptyFolder
from src.domain.task.CancellationInterface import CancellationInterface


class RemoveEmptyFolderTest(TestCase):
    def setUp(self):
        self.settings_repository_mock = Mock(SettingsRepositoryInterface)
        self.settings_repository_mock.fetch_one.return_value = ["/downloads"]

        self.file_system_repository_mock = Mock(FileSystemRepositoryInterface)

        self.folder_check_mock = Mock(CheckFolder)
        self.folder_check_mock.readable.side_effect = lambda folders: (list(folders), [])
        self.folder_check_mock.warning.return_value = ""

        self.cancellation_mock = Mock(CancellationInterface)
        self.cancellation_mock.is_cancelled.return_value = False

        self.empty_folder_remover = RemoveEmptyFolder(
            Mock(EventManagerInterface),
            self.settings_repository_mock,
            self.file_system_repository_mock,
            self.folder_check_mock,
            self.cancellation_mock,
        )

        super().setUp()

    def test_given_a_source_folder_when_listing_empty_folders_then_only_the_empty_ones_are_returned(self):
        self.file_system_repository_mock.list_empty_folders.return_value = ["/downloads/empty"]

        self.assertEqual(self.empty_folder_remover.list_empty_folders(), ["/downloads/empty"])

    def test_given_several_source_folders_when_listing_empty_folders_then_all_of_them_are_scanned(self):
        self.settings_repository_mock.fetch_one.return_value = ["/downloads", "/desktop"]
        self.file_system_repository_mock.list_empty_folders.side_effect = [
            ["/downloads/empty"],
            ["/desktop/empty"],
        ]

        self.assertEqual(
            self.empty_folder_remover.list_empty_folders(),
            ["/downloads/empty", "/desktop/empty"],
        )

    def test_given_empty_folders_when_removing_them_then_every_one_is_deleted(self):
        self.empty_folder_remover.remove_empty_folders(["/downloads/empty", "/downloads/other"])

        self.assertEqual(
            [call.args[0] for call in self.file_system_repository_mock.remove_folder.call_args_list],
            ["/downloads/empty", "/downloads/other"],
        )

    def test_given_an_unreadable_folder_when_listing_empty_folders_then_it_is_not_walked(self):
        """A share that has gone reports nothing, and nothing is what an empty folder
        reports too. It is dropped instead of being counted as clean."""
        self.settings_repository_mock.fetch_one.return_value = ["/downloads", "/nas"]
        self.folder_check_mock.readable.side_effect = lambda folders: ([folders[0]], [folders[1]])
        self.file_system_repository_mock.list_empty_folders.return_value = []

        self.empty_folder_remover.list_empty_folders()

        self.file_system_repository_mock.list_empty_folders.assert_called_once_with("/downloads")

    def test_given_a_folder_that_cannot_be_deleted_when_removing_then_the_rest_is_still_deleted(self):
        self.file_system_repository_mock.remove_folder.side_effect = [OSError("not empty"), None]

        self.empty_folder_remover.remove_empty_folders(["/downloads/empty", "/downloads/other"])

        self.assertEqual(
            [call.args[0] for call in self.file_system_repository_mock.remove_folder.call_args_list],
            ["/downloads/empty", "/downloads/other"],
        )

    def test_given_a_cancelled_run_when_removing_empty_folders_then_no_folder_is_deleted(self):
        self.cancellation_mock.is_cancelled.return_value = True

        self.empty_folder_remover.remove_empty_folders(["/downloads/empty"])

        self.file_system_repository_mock.remove_folder.assert_not_called()

    def test_given_a_cancelled_run_when_listing_empty_folders_then_nothing_is_walked(self):
        self.cancellation_mock.is_cancelled.return_value = True

        self.assertEqual(self.empty_folder_remover.list_empty_folders(), [])
        self.file_system_repository_mock.list_empty_folders.assert_not_called()
