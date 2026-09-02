from unittest import TestCase
from unittest.mock import Mock

from src.domain.event.EventManagerInterface import EventManagerInterface
from src.domain.repository.FileSystemRepositoryInterface import FileSystemRepositoryInterface
from src.domain.repository.SettingsRepositoryInterface import SettingsRepositoryInterface
from src.domain.service.remove.RemoveEmptyFolder import RemoveEmptyFolder


class RemoveEmptyFolderTest(TestCase):
    def setUp(self):
        self.settings_repository_mock = Mock(SettingsRepositoryInterface)
        self.settings_repository_mock.fetch_one.return_value = ["/downloads"]

        self.file_system_repository_mock = Mock(FileSystemRepositoryInterface)

        self.empty_folder_remover = RemoveEmptyFolder(
            Mock(EventManagerInterface),
            self.settings_repository_mock,
            self.file_system_repository_mock,
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
