from unittest import TestCase
from unittest.mock import Mock
from pathlib import Path
from os import path as os_path, remove as os_remove

from src.domain.entity.FileInfo import FileInfo
from src.domain.service.remove.RemoveEmptyFile import RemoveEmptyFile
from src.domain.repository.SettingsRepositoryInterface import SettingsRepositoryInterface
from src.domain.event.EventManagerInterface import EventManagerInterface
from src.domain.repository.FileInfoRepositoryInterface import FileInfoRepositoryInterface
from src.domain.service.folder.CheckFolder import CheckFolder
from src.domain.task.CancellationInterface import CancellationInterface


class RemoveEmptyFileTest(TestCase):
    def setUp(self):
        root_folder = (str(Path().resolve()) + "/tests/domain/service/RemoveEmptyFileTest")

        self.file_info1 = self._create_file(root_folder + "/filetest.txt", "")

        self.file_info_repository = Mock(FileInfoRepositoryInterface)
        self.settings_repository = Mock(SettingsRepositoryInterface)

        self.folder_check_mock = Mock(CheckFolder)
        self.folder_check_mock.readable.side_effect = lambda folders: (list(folders), [])
        self.folder_check_mock.warning.return_value = ""

        self.cancellation_mock = Mock(CancellationInterface)
        self.cancellation_mock.is_cancelled.return_value = False

        self.remove_empty_file = RemoveEmptyFile(
            Mock(EventManagerInterface),
            self.settings_repository,
            self.file_info_repository,
            self.folder_check_mock,
            self.cancellation_mock,
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

    def test_given_a_file_that_read_back_nothing_but_has_a_size_when_listing_then_it_is_not_empty(self):
        """A cloud placeholder and a share that dropped mid read both report their real
        size and hand back no bytes. Believing the read alone deletes a file that has
        contents in it."""
        placeholder = FileInfo(self.file_info1.full_path, "", 4096, b"")
        self.settings_repository.fetch_one.return_value = ["/downloads"]
        self.file_info_repository.fetch_all_from_folder.return_value = [placeholder]

        self.assertEqual(self.remove_empty_file.list_empty_files(), [])

    def test_given_a_file_that_read_back_nothing_but_has_a_size_when_removing_then_it_is_left_alone(self):
        self.remove_empty_file.remove_empty_files([FileInfo(self.file_info1.full_path, "", 4096, b"")])

        self.file_info_repository.remove_one.assert_not_called()

    def test_given_a_file_filled_since_the_analysis_when_removing_then_it_is_left_alone(self):
        with open(self.file_info1.full_path, "w") as file:
            file.write("no longer empty")

        self.remove_empty_file.remove_empty_files([FileInfo(self.file_info1.full_path, "", 15, "no longer empty")])

        self.file_info_repository.remove_one.assert_not_called()

    def test_given_an_unreadable_folder_when_listing_empty_files_then_it_is_not_scanned(self):
        self.settings_repository.fetch_one.return_value = ["/downloads", "/nas"]
        self.folder_check_mock.readable.side_effect = lambda folders: ([folders[0]], [folders[1]])
        self.file_info_repository.fetch_all_from_folder.return_value = []

        self.remove_empty_file.list_empty_files()

        self.assertEqual(
            [call[0][0] for call in self.file_info_repository.fetch_all_from_folder.call_args_list],
            ["/downloads"],
        )

    def test_given_a_cancelled_run_when_removing_empty_files_then_no_file_is_removed(self):
        self.cancellation_mock.is_cancelled.return_value = True

        self.remove_empty_file.remove_empty_files([self.file_info1])

        self.file_info_repository.remove_one.assert_not_called()

    def test_given_a_file_that_cannot_be_removed_when_removing_then_the_rest_is_still_removed(self):
        second = self._create_file(os_path.dirname(self.file_info1.full_path) + "/other.txt", "")
        self.file_info_repository.remove_one.side_effect = [OSError("host is down"), None]

        try:
            self.remove_empty_file.remove_empty_files([self.file_info1, second])

            self.assertEqual(
                [call.args[0] for call in self.file_info_repository.remove_one.call_args_list],
                [self.file_info1.full_path, second.full_path],
            )
        finally:
            if os_path.isfile(second.full_path):
                os_remove(second.full_path)

    def _create_file(self, file_path, file_contents):
        with open(file_path, "w") as file:
            file.write(file_contents)
        return FileInfo(file_path, "", len(file_contents), file_contents)
