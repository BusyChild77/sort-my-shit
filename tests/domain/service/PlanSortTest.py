from unittest import TestCase
from unittest.mock import Mock

from src.domain.event.EventManagerInterface import EventManagerInterface
from src.domain.repository.FileSystemRepositoryInterface import FileSystemRepositoryInterface
from src.domain.repository.SettingsRepositoryInterface import SettingsRepositoryInterface
from src.domain.service.sort.PlanSort import PlanSort
from src.domain.service.sort.ResolveCategory import ResolveCategory


class PlanSortTest(TestCase):
    def setUp(self):
        self.settings = {
            "source_folders": ["/source"],
            "destination_folder": "/destination",
            "preserve_folder_tree": False,
        }

        self.settings_repository_mock = Mock(SettingsRepositoryInterface)
        self.settings_repository_mock.fetch_all.side_effect = lambda: dict(self.settings)
        self.settings_repository_mock.fetch_type_mapping.return_value = {
            "docs": ["pdf", "txt"],
            "pics": ["jpg"],
        }

        self.file_system_repository_mock = Mock(FileSystemRepositoryInterface)
        self.file_system_repository_mock.folder_exists.return_value = True
        self.file_system_repository_mock.file_exists.return_value = False

        self.sort_planner = PlanSort(
            Mock(EventManagerInterface),
            self.settings_repository_mock,
            self.file_system_repository_mock,
            ResolveCategory(self.settings_repository_mock),
        )

        super().setUp()

    def test_given_a_flat_source_folder_when_planning_then_files_land_in_their_category_folder(self):
        self.__given_files(["/source/report.pdf", "/source/holiday.jpg"])

        operations = self.sort_planner.plan()

        self.assertEqual(
            [operation.destination_path for operation in operations],
            ["/destination/pics/holiday.jpg", "/destination/docs/report.pdf"],
        )

    def test_given_nested_folders_when_flattening_then_every_file_lands_in_the_same_category_folder(self):
        self.__given_files(["/source/report.pdf", "/source/2024/january/invoice.pdf"])

        operations = self.sort_planner.plan()

        self.assertEqual(
            sorted(operation.destination_path for operation in operations),
            ["/destination/docs/invoice.pdf", "/destination/docs/report.pdf"],
        )

    def test_given_nested_folders_when_preserving_the_tree_then_files_are_sorted_at_their_own_level(self):
        self.settings["preserve_folder_tree"] = True
        self.__given_files(["/source/report.pdf", "/source/2024/january/invoice.pdf", "/source/2024/photo.jpg"])

        operations = self.sort_planner.plan()

        self.assertEqual(
            sorted(operation.destination_path for operation in operations),
            [
                "/destination/2024/january/docs/invoice.pdf",
                "/destination/2024/pics/photo.jpg",
                "/destination/docs/report.pdf",
            ],
        )

    def test_given_several_source_folders_when_planning_then_every_file_lands_in_the_same_destination(self):
        self.settings["source_folders"] = ["/downloads", "/desktop"]
        self.file_system_repository_mock.list_file_paths.side_effect = [
            ["/downloads/report.pdf"],
            ["/desktop/holiday.jpg"],
        ]

        operations = self.sort_planner.plan()

        self.assertEqual(
            sorted(operation.destination_path for operation in operations),
            ["/destination/docs/report.pdf", "/destination/pics/holiday.jpg"],
        )

    def test_given_two_source_files_sharing_a_name_when_planning_then_the_second_one_is_renamed(self):
        self.settings["source_folders"] = ["/downloads", "/desktop"]
        self.file_system_repository_mock.list_file_paths.side_effect = [
            ["/downloads/report.pdf"],
            ["/desktop/report.pdf"],
        ]

        operations = self.sort_planner.plan()

        self.assertEqual(
            [operation.destination_path for operation in operations],
            ["/destination/docs/report.pdf", "/destination/docs/report (1).pdf"],
        )

    def test_given_a_file_already_in_the_destination_when_planning_then_the_planned_file_is_renamed(self):
        self.file_system_repository_mock.file_exists.side_effect = [True, False]
        self.__given_files(["/source/report.pdf"])

        operations = self.sort_planner.plan()

        self.assertEqual(operations[0].destination_path, "/destination/docs/report (1).pdf")

    def test_given_a_destination_folder_inside_a_source_folder_when_planning_then_sorted_files_are_left_alone(self):
        self.settings["destination_folder"] = "/source/sorted"
        self.__given_files(["/source/report.pdf", "/source/sorted/docs/already_sorted.pdf"])

        operations = self.sort_planner.plan()

        self.assertEqual([operation.source_path for operation in operations], ["/source/report.pdf"])

    def test_given_an_unknown_extension_when_planning_then_the_file_is_left_alone(self):
        self.__given_files(["/source/notes.xyz"])

        self.assertEqual(self.sort_planner.plan(), [])

    def test_given_a_missing_source_folder_when_planning_then_it_is_skipped(self):
        self.file_system_repository_mock.folder_exists.return_value = False

        self.assertEqual(self.sort_planner.plan(), [])
        self.file_system_repository_mock.list_file_paths.assert_not_called()

    def __given_files(self, file_paths: list):
        self.file_system_repository_mock.list_file_paths.return_value = file_paths
