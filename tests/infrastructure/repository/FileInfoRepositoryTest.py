from pathlib import Path
from shutil import rmtree
from unittest import TestCase
from unittest.mock import Mock, patch

from src.application.service.EventManager import EventManager
from src.infrastructure.repository.FileInfoRepository import FileInfoRepository
from src.infrastructure.repository.SettingsRepository import SettingsRepository


class FileInfoRepositoryTest(TestCase):
    def setUp(self):
        self.root_folder = str(Path().resolve() / "tests/infrastructure/repository/FileInfoRepositoryTest")
        rmtree(self.root_folder, ignore_errors=True)
        Path(self.root_folder).mkdir(parents=True, exist_ok=True)

        self.settings = {
            "binary_comparison_large_files_threshold": 5000000,
            "binary_search": True,
            "binary_search_large_files": False,
        }

        self.settings_repository_mock = Mock(SettingsRepository)
        self.settings_repository_mock.fetch_one.side_effect = lambda name: self.settings[name]

        self.file_info_repository = FileInfoRepository(
            self.settings_repository_mock,
            Mock(EventManager),
        )

        super().setUp()

    def tearDown(self):
        rmtree(self.root_folder, ignore_errors=True)
        super().tearDown()

    def test_given_files_in_a_folder_when_fetching_them_then_each_one_carries_its_size_and_first_bytes(self):
        self.__create_file("report.pdf", "TEST_FILE_CONTENT")

        files = self.file_info_repository.fetch_all_from_folder(self.root_folder)

        self.assertEqual([file.file_name for file in files], ["report.pdf"])
        self.assertEqual(files[0].size, len("TEST_FILE_CONTENT"))
        self.assertEqual(files[0].partial_contents, b"TEST_FILE_CONTENT")

    def test_given_a_file_that_cannot_be_read_when_fetching_a_folder_then_the_others_are_still_returned(self):
        """A share that drops mid scan costs the files it took with it, and nothing
        else. Raising here would end an analysis that has already read thousands."""
        self.__create_file("report.pdf", "TEST_FILE_CONTENT")
        self.__create_file("locked.pdf", "TEST_FILE_CONTENT")

        with patch("builtins.open", side_effect=self.__refuse_one("locked.pdf")):
            files = self.file_info_repository.fetch_all_from_folder(self.root_folder)

        self.assertEqual([file.file_name for file in files], ["report.pdf"])

    def test_given_a_file_that_cannot_be_read_when_fetching_a_folder_then_it_is_never_handed_on_as_empty(self):
        """It is what deletes these that reads them: a file whose contents never arrived
        is indistinguishable from an empty one once it is in the list."""
        self.__create_file("locked.pdf", "TEST_FILE_CONTENT")

        with patch("builtins.open", side_effect=self.__refuse_one("locked.pdf")):
            files = self.file_info_repository.fetch_all_from_folder(self.root_folder, skip_empty_files=False)

        self.assertEqual(files, [])

    def test_given_an_empty_file_when_fetching_a_folder_without_skipping_them_then_it_is_returned(self):
        self.__create_file("empty.txt", "")

        files = self.file_info_repository.fetch_all_from_folder(self.root_folder, skip_empty_files=False)

        self.assertEqual([file.file_name for file in files], ["empty.txt"])
        self.assertEqual(files[0].size, 0)

    def __create_file(self, relative_path: str, contents: str):
        file_path = Path(self.root_folder, relative_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(contents)

    @staticmethod
    def __refuse_one(file_name: str):
        real_open = open

        def opened(path, *args, **kwargs):
            if str(path).endswith(file_name):
                raise OSError("host is down")
            return real_open(path, *args, **kwargs)

        return opened
