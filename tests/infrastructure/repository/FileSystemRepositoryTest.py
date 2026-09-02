from pathlib import Path
from shutil import rmtree
from unittest import TestCase

from src.infrastructure.repository.FileSystemRepository import FileSystemRepository


class FileSystemRepositoryTest(TestCase):
    def setUp(self):
        self.root_folder = str(Path().resolve() / "tests/infrastructure/repository/FileSystemRepositoryTest")
        rmtree(self.root_folder, ignore_errors=True)

        self.file_system_repository = FileSystemRepository()

        super().setUp()

    def tearDown(self):
        rmtree(self.root_folder, ignore_errors=True)
        super().tearDown()

    def test_given_nested_folders_when_listing_files_then_every_file_is_returned(self):
        self.__create_file("report.pdf")
        self.__create_file("2024/january/invoice.pdf")

        self.assertEqual(
            sorted(self.file_system_repository.list_file_paths(self.root_folder)),
            [f"{self.root_folder}/2024/january/invoice.pdf", f"{self.root_folder}/report.pdf"],
        )

    def test_given_folders_holding_only_empty_folders_when_listing_empty_folders_then_they_are_all_returned(self):
        self.__create_folder("empty/deeper")
        self.__create_file("full/report.pdf")

        self.assertEqual(
            self.file_system_repository.list_empty_folders(self.root_folder),
            [f"{self.root_folder}/empty/deeper", f"{self.root_folder}/empty"],
        )

    def test_given_an_empty_folder_list_when_removing_them_in_order_then_the_deepest_goes_first(self):
        self.__create_folder("empty/deeper")

        for folder in self.file_system_repository.list_empty_folders(self.root_folder):
            self.file_system_repository.remove_folder(folder)

        self.assertFalse(self.file_system_repository.folder_exists(f"{self.root_folder}/empty"))

    def test_given_a_file_when_moving_it_then_it_only_exists_at_its_destination(self):
        self.__create_file("report.pdf")
        self.__create_folder("sorted")

        self.file_system_repository.move_file(
            f"{self.root_folder}/report.pdf", f"{self.root_folder}/sorted/report.pdf"
        )

        self.assertFalse(self.file_system_repository.file_exists(f"{self.root_folder}/report.pdf"))
        self.assertTrue(self.file_system_repository.file_exists(f"{self.root_folder}/sorted/report.pdf"))

    def test_given_a_file_when_copying_it_then_it_exists_on_both_sides(self):
        self.__create_file("report.pdf")
        self.__create_folder("sorted")

        self.file_system_repository.copy_file(
            f"{self.root_folder}/report.pdf", f"{self.root_folder}/sorted/report.pdf"
        )

        self.assertTrue(self.file_system_repository.file_exists(f"{self.root_folder}/report.pdf"))
        self.assertTrue(self.file_system_repository.file_exists(f"{self.root_folder}/sorted/report.pdf"))

    def test_given_a_missing_nested_folder_when_creating_it_then_every_level_is_created(self):
        self.file_system_repository.create_folder(f"{self.root_folder}/a/b/c")

        self.assertTrue(self.file_system_repository.folder_exists(f"{self.root_folder}/a/b/c"))

    def __create_folder(self, relative_path: str):
        Path(self.root_folder, relative_path).mkdir(parents=True, exist_ok=True)

    def __create_file(self, relative_path: str):
        file_path = Path(self.root_folder, relative_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("TEST_FILE_CONTENT")
