from unittest import TestCase
from unittest.mock import Mock
from pathlib import Path
from os import path as os_path, remove as os_remove

from src.domain.entity.FileInfo import FileInfo
from src.domain.event.EventManagerInterface import EventManagerInterface
from src.domain.service.compare.CompareBinary import CompareBinary
from src.domain.service.list.ListDuplicate import ListDuplicate
from src.domain.service.compare.CompareFileName import CompareFileName
from src.domain.repository.FileInfoRepositoryInterface import FileInfoRepositoryInterface
from src.domain.repository.SettingsRepositoryInterface import SettingsRepositoryInterface
from src.domain.service.folder.CheckFolder import CheckFolder
from src.domain.task.CancellationInterface import CancellationInterface


class ListDuplicateTest(TestCase):
    def setUp(self):
        self.binary_comparator_mock = Mock(CompareBinary)
        self.binary_comparator_mock.group.return_value = []
        self.file_info_repository_mock = Mock(FileInfoRepositoryInterface)
        self.settings_repository_mock = Mock(SettingsRepositoryInterface)

        self.file_name_comparator_mock = Mock(CompareFileName)
        self.file_name_comparator_mock.group.return_value = []

        self.folder_check_mock = Mock(CheckFolder)
        self.folder_check_mock.readable.side_effect = lambda folders: (list(folders), [])
        self.folder_check_mock.warning.return_value = ""

        self.cancellation_mock = Mock(CancellationInterface)
        self.cancellation_mock.is_cancelled.return_value = False

        self.list_duplicate = ListDuplicate(
            Mock(EventManagerInterface),
            self.settings_repository_mock,
            self.file_info_repository_mock,
            self.binary_comparator_mock,
            self.file_name_comparator_mock,
            self.folder_check_mock,
            self.cancellation_mock,
        )

        base_path = Path().resolve() / "tests/domain/service/DuplicateTest"
        self.file1_path = str(base_path / "testFile1.txt")
        self.file2_path = str(base_path / "testFile2.txt")
        self.file3_path = str(base_path / "testFile3.txt")

        self.file_info1 = self._create_file(self.file1_path, "TEST_FILE_CONTENT")
        self.file_info2 = self._create_file(self.file2_path, "TEST_FILE_CONTENT")
        self.file_info3 = self._create_file(self.file3_path, "TEST_FILE_CONTENT")

        super().setUp()

    def tearDown(self):
        if os_path.isfile(self.file1_path):
            os_remove(self.file1_path)
        if os_path.isfile(self.file2_path):
            os_remove(self.file2_path)
        if os_path.isfile(self.file3_path):
            os_remove(self.file3_path)

        super().tearDown()

    def test_given_files_with_same_content_when_listing_duplicates_then_the_first_listed_is_kept_and_the_others_are_its_duplicates(self):
        self._given_settings(["/downloads"], binary_search=True)
        self.binary_comparator_mock.group.return_value = [[self.file_info1, self.file_info2, self.file_info3]]
        self.file_info_repository_mock.fetch_all_from_folder.return_value = [self.file_info1, self.file_info2, self.file_info3]

        duplicates = self.list_duplicate.list_duplicates()

        self.assertEqual(duplicates[0].files, [self.file_info2, self.file_info3])
        self.assertEqual(duplicates[0].duplicate_of, self.file_info1)
        self.file_name_comparator_mock.group.assert_not_called()

    def test_given_files_with_same_name_when_comparing_names_then_a_duplicate_match_holding_a_file_list_is_returned(self):
        self._given_settings(["/downloads"], binary_search=False)
        self.file_name_comparator_mock.group.return_value = [[self.file_info1, self.file_info2, self.file_info3]]
        self.file_info_repository_mock.fetch_all_from_folder.return_value = [self.file_info1, self.file_info2, self.file_info3]

        duplicates = self.list_duplicate.list_duplicates()

        self.assertEqual(duplicates[0].files, [self.file_info2, self.file_info3])
        self.assertEqual(duplicates[0].duplicate_of, self.file_info1)
        self.binary_comparator_mock.group.assert_not_called()

    def test_given_several_groups_when_listing_duplicates_then_there_is_one_match_per_group(self):
        self._given_settings(["/downloads"], binary_search=True)
        self.binary_comparator_mock.group.return_value = [[self.file_info1, self.file_info2], [self.file_info3, self.file_info1]]
        self.file_info_repository_mock.fetch_all_from_folder.return_value = [self.file_info1, self.file_info2, self.file_info3]

        duplicates = self.list_duplicate.list_duplicates()

        self.assertEqual(
            [(match.duplicate_of, match.files) for match in duplicates],
            [(self.file_info1, [self.file_info2]), (self.file_info3, [self.file_info1])],
        )

    def test_given_several_folders_when_listing_duplicates_then_every_one_of_them_is_scanned(self):
        self._given_settings(["/downloads", "/desktop"], binary_search=True)
        self.file_info_repository_mock.fetch_all_from_folder.side_effect = [[self.file_info1], [self.file_info2]]

        self.list_duplicate.list_duplicates()

        self.assertEqual(
            [call[0][0] for call in self.file_info_repository_mock.fetch_all_from_folder.call_args_list],
            ["/downloads", "/desktop"],
        )

    def test_given_a_copy_in_another_folder_when_listing_duplicates_then_both_are_compared_together(self):
        """The whole point of several folders: the same file sitting in two of them."""
        self._given_settings(["/downloads", "/desktop"], binary_search=True)
        self.file_info_repository_mock.fetch_all_from_folder.side_effect = [[self.file_info1], [self.file_info2]]

        self.list_duplicate.list_duplicates()

        self.binary_comparator_mock.group.assert_called_once_with([self.file_info1, self.file_info2])

    def test_given_a_folder_picked_along_with_one_inside_it_when_listing_duplicates_then_a_file_is_never_compared_with_itself(self):
        """Listed twice, a file would be offered up as its own duplicate, and removing it
        would delete the only copy."""
        self._given_settings(["/downloads", "/downloads/pictures"], binary_search=True)
        listed_again = FileInfo(
            self.file1_path.replace("DuplicateTest", "DuplicateTest/./"), "testFile1.txt", 500, "TEST_FILE_CONTENT"
        )
        self.file_info_repository_mock.fetch_all_from_folder.side_effect = [[self.file_info1, self.file_info2], [listed_again]]

        self.list_duplicate.list_duplicates()

        self.binary_comparator_mock.group.assert_called_once_with([self.file_info1, self.file_info2])

    def test_given_a_file_gone_since_it_was_listed_when_listing_duplicates_then_it_is_not_compared(self):
        self._given_settings(["/downloads"], binary_search=True)
        self.file_info_repository_mock.fetch_all_from_folder.return_value = [self.file_info1, self.file_info2]
        os_remove(self.file2_path)

        self.list_duplicate.list_duplicates()

        self.binary_comparator_mock.group.assert_called_once_with([self.file_info1])

    def test_given_an_unreadable_folder_when_listing_duplicates_then_it_is_not_scanned(self):
        """The folder that did not answer is dropped, not walked and found empty."""
        self._given_settings(["/downloads", "/nas"], binary_search=True)
        self.folder_check_mock.readable.side_effect = lambda folders: ([folders[0]], [folders[1]])
        self.file_info_repository_mock.fetch_all_from_folder.return_value = [self.file_info1]

        self.list_duplicate.list_duplicates()

        self.assertEqual(
            [call[0][0] for call in self.file_info_repository_mock.fetch_all_from_folder.call_args_list],
            ["/downloads"],
        )

    def test_given_a_cancelled_run_when_listing_duplicates_then_nothing_is_compared(self):
        self._given_settings(["/downloads"], binary_search=True)
        self.cancellation_mock.is_cancelled.return_value = True
        self.file_info_repository_mock.fetch_all_from_folder.return_value = [self.file_info1, self.file_info2]

        self.assertEqual(self.list_duplicate.list_duplicates(), [])
        self.binary_comparator_mock.group.assert_not_called()

    def _given_settings(self, folders: list, binary_search: bool):
        settings = {"remove_duplicates_folders": folders, "binary_search": binary_search}
        self.settings_repository_mock.fetch_one.side_effect = lambda name: settings[name]

    def _create_file(self, file_path, file_contents):
        with open(file_path, "w") as file:
            file.write(file_contents)
        return FileInfo(
            file_path,
            os_path.basename(file_path),
            500,
            file_contents,
        )
