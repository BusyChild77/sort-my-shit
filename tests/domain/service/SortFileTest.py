from unittest import TestCase
from unittest.mock import Mock

from src.domain.entity.SortOperation import SortOperation
from src.domain.event.EventManagerInterface import EventManagerInterface
from src.domain.repository.FileSystemRepositoryInterface import FileSystemRepositoryInterface
from src.domain.repository.SettingsRepositoryInterface import SettingsRepositoryInterface
from src.domain.service.sort.PlanSort import PlanSort
from src.domain.service.sort.SortFile import SortFile


class SortFileTest(TestCase):
    def setUp(self):
        self.settings = {
            "source_folders": ["/source"],
            "keep_original_files": True,
            "delete_empty_source_folders": False,
        }

        self.settings_repository_mock = Mock(SettingsRepositoryInterface)
        self.settings_repository_mock.fetch_one.side_effect = lambda name: self.settings[name]

        self.file_system_repository_mock = Mock(FileSystemRepositoryInterface)
        self.file_system_repository_mock.file_exists.return_value = True
        self.file_system_repository_mock.folder_exists.return_value = True
        self.file_system_repository_mock.list_empty_folders.return_value = []

        self.sort_planner_mock = Mock(PlanSort)

        self.sort_file = SortFile(
            Mock(EventManagerInterface),
            self.settings_repository_mock,
            self.file_system_repository_mock,
            self.sort_planner_mock,
        )

        self.operation = SortOperation("/source/report.pdf", "/destination/docs/report.pdf", "docs")

        super().setUp()

    def test_given_the_source_files_are_kept_when_sorting_then_files_are_copied(self):
        self.sort_file.sort([self.operation])

        self.file_system_repository_mock.copy_file.assert_called_once_with(
            "/source/report.pdf", "/destination/docs/report.pdf"
        )
        self.file_system_repository_mock.move_file.assert_not_called()

    def test_given_the_source_files_are_not_kept_when_sorting_then_files_are_moved(self):
        self.settings["keep_original_files"] = False

        self.sort_file.sort([self.operation])

        self.file_system_repository_mock.move_file.assert_called_once_with(
            "/source/report.pdf", "/destination/docs/report.pdf"
        )
        self.file_system_repository_mock.copy_file.assert_not_called()

    def test_given_a_missing_destination_folder_when_sorting_then_it_is_created(self):
        self.file_system_repository_mock.folder_exists.return_value = False

        self.sort_file.sort([self.operation])

        self.file_system_repository_mock.create_folder.assert_called_once_with("/destination/docs")

    def test_given_an_existing_destination_folder_when_sorting_then_it_is_not_created_again(self):
        self.sort_file.sort([self.operation])

        self.file_system_repository_mock.create_folder.assert_not_called()

    def test_given_a_source_file_removed_since_the_preview_when_sorting_then_it_is_skipped(self):
        self.file_system_repository_mock.file_exists.return_value = False

        self.sort_file.sort([self.operation])

        self.file_system_repository_mock.copy_file.assert_not_called()

    def test_given_emptied_source_folders_when_sorting_moves_files_then_they_are_deleted(self):
        self.settings["keep_original_files"] = False
        self.settings["delete_empty_source_folders"] = True
        self.file_system_repository_mock.list_empty_folders.return_value = ["/source/2024"]

        self.sort_file.sort([self.operation])

        self.file_system_repository_mock.remove_folder.assert_called_once_with("/source/2024")

    def test_given_emptied_source_folders_when_sorting_copies_files_then_they_are_kept(self):
        self.settings["delete_empty_source_folders"] = True
        self.file_system_repository_mock.list_empty_folders.return_value = ["/source/2024"]

        self.sort_file.sort([self.operation])

        self.file_system_repository_mock.remove_folder.assert_not_called()

    def test_when_planning_a_sort_then_the_planner_is_asked(self):
        self.sort_planner_mock.plan.return_value = [self.operation]

        self.assertEqual(self.sort_file.plan_sort(), [self.operation])
