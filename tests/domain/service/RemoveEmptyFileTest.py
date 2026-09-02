from unittest import TestCase
from unittest.mock import Mock
from pathlib import Path
from os import path as os_path, remove as os_remove

from src.domain.entity.FileInfo import FileInfo
from src.domain.service.remove.RemoveEmptyFile import RemoveEmptyFile
from src.domain.repository.SettingsRepositoryInterface import SettingsRepositoryInterface
from src.domain.event.EventManagerInterface import EventManagerInterface
from src.domain.repository.FileInfoRepositoryInterface import FileInfoRepositoryInterface


class RemoveEmptyFileTest(TestCase):
    def setUp(self):
        root_folder = (str(Path().resolve()) + "/tests/domain/service/RemoveEmptyFileTest")

        self.file_info1 = self._create_file(root_folder + "/filetest.txt", "")

        self.file_info_repository = Mock(FileInfoRepositoryInterface)
        self.settings_repository = Mock(SettingsRepositoryInterface)

        self.remove_empty_file = RemoveEmptyFile(
            Mock(EventManagerInterface),
            self.settings_repository,
            self.file_info_repository
        )

        super().setUp()

    def tearDown(self):
        if os_path.isfile(self.file_info1.full_path):
            os_remove(self.file_info1.full_path)

        super().tearDown()

    def test_given_empty_file_when_removing_empty_files_then_empty_file_removed(self):
        self.remove_empty_file.remove_empty_files([self.file_info1])
        self.file_info_repository.remove_one.assert_called_with(self.file_info1.full_path)

    def test_given_several_folders_when_listing_empty_files_then_every_one_of_them_is_scanned(self):
        self.settings_repository.fetch_one.return_value = ["/downloads", "/desktop"]
        self.file_info_repository.fetch_all_from_folder.side_effect = [[self.file_info1], []]

        empty_files = self.remove_empty_file.list_empty_files()

        self.assertEqual(
            [call[0][0] for call in self.file_info_repository.fetch_all_from_folder.call_args_list],
            ["/downloads", "/desktop"],
        )
        self.assertEqual(empty_files, [self.file_info1])

    def test_given_several_folders_when_listing_empty_files_then_empty_files_are_not_skipped_on_the_way_in(self):
        """fetch_all_from_folder drops empty files by default, which is precisely what
        this screen is looking for."""
        self.settings_repository.fetch_one.return_value = ["/downloads"]
        self.file_info_repository.fetch_all_from_folder.side_effect = [[]]

        self.remove_empty_file.list_empty_files()

        self.assertFalse(self.file_info_repository.fetch_all_from_folder.call_args[1]["skip_empty_files"])

    def _create_file(self, file_path, file_contents):
        with open(file_path, "w") as file:
            file.write(file_contents)
        return FileInfo(file_path, "", 0, file_contents)
