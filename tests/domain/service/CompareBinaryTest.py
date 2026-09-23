from unittest import TestCase
from unittest.mock import Mock

from src.domain.entity.FileInfo import FileInfo
from src.domain.event.EventManagerInterface import EventManagerInterface
from src.domain.repository.FileInfoRepositoryInterface import FileInfoRepositoryInterface
from src.domain.repository.SettingsRepositoryInterface import SettingsRepositoryInterface
from src.domain.service.compare.CompareBinary import CompareBinary
from src.domain.task.CancellationInterface import CancellationInterface


class BinaryComparatorTest(TestCase):
    def setUp(self):
        self.settings = {
            "binary_comparison_large_files_threshold": 50000,
            "binary_search_large_files": False,
        }
        self.settings_repository_mock = Mock(SettingsRepositoryInterface)
        self.settings_repository_mock.fetch_one.side_effect = lambda name: self.settings[name]

        self.digests = {}
        self.file_info_repository_mock = Mock(FileInfoRepositoryInterface)
        self.file_info_repository_mock.fetch_digest.side_effect = self.__fetch_digest

        self.cancellation_mock = Mock(CancellationInterface)
        self.cancellation_mock.is_cancelled.return_value = False

        self.event_manager_mock = Mock(EventManagerInterface)

        self.binary_comparator = CompareBinary(
            self.event_manager_mock,
            self.file_info_repository_mock,
            self.settings_repository_mock,
            self.cancellation_mock,
        )

        super().setUp()

    def test_given_two_files_with_same_content_when_grouping_then_they_are_grouped_together(self):
        file1 = self.__file("/a/report.pdf", 500, "SAME")
        file2 = self.__file("/b/report copy.pdf", 500, "SAME")

        self.assertEqual(self.binary_comparator.group([file1, file2]), [[file1, file2]])

    def test_given_two_files_with_different_content_when_grouping_then_they_are_not_grouped(self):
        file1 = self.__file("/a/report.pdf", 500, "ONE")
        file2 = self.__file("/b/report.pdf", 500, "OTHER")

        self.assertEqual(self.binary_comparator.group([file1, file2]), [])

    def test_given_two_files_of_different_sizes_when_grouping_then_neither_is_read(self):
        """Files of different sizes cannot be identical: reading them is wasted."""
        file1 = self.__file("/a/report.pdf", 500, "SAME")
        file2 = self.__file("/b/report.pdf", 501, "SAME")

        self.assertEqual(self.binary_comparator.group([file1, file2]), [])
        self.file_info_repository_mock.fetch_digest.assert_not_called()

    def test_given_two_files_with_different_first_bytes_when_grouping_then_neither_is_read(self):
        file1 = self.__file("/a/report.pdf", 500, "SAME", partial_contents=b"%PDF-1.4")
        file2 = self.__file("/b/report.pdf", 500, "SAME", partial_contents=b"%PDF-1.7")

        self.assertEqual(self.binary_comparator.group([file1, file2]), [])
        self.file_info_repository_mock.fetch_digest.assert_not_called()

    def test_given_three_copies_when_grouping_then_each_file_is_read_once(self):
        files = [self.__file(f"/{folder}/report.pdf", 500, "SAME") for folder in ("a", "b", "c")]

        self.assertEqual(self.binary_comparator.group(files), [files])
        self.assertEqual(self.file_info_repository_mock.fetch_digest.call_count, 3)

    def test_given_several_pairs_of_copies_when_grouping_then_every_pair_is_found(self):
        """Regression: removing matches from the list being walked skipped the file after
        each of them, and with it the last pair."""
        files = [
            self.__file(f"/{folder}/{name}.txt", 500, name.upper())
            for name in ("a", "b", "c") for folder in ("one", "two")
        ]

        self.assertEqual(
            self.binary_comparator.group(files),
            [files[0:2], files[2:4], files[4:6]],
        )

    def test_given_two_oversized_files_with_same_content_when_large_file_search_is_disabled_then_they_are_not_grouped(self):
        file1 = self.__file("/a/movie.mkv", 55000, "SAME")
        file2 = self.__file("/b/movie.mkv", 55000, "SAME")

        self.assertEqual(self.binary_comparator.group([file1, file2]), [])
        self.file_info_repository_mock.fetch_digest.assert_not_called()

    def test_given_two_oversized_files_with_same_content_when_large_file_search_is_enabled_then_they_are_grouped(self):
        self.settings["binary_search_large_files"] = True
        file1 = self.__file("/a/movie.mkv", 55000, "SAME")
        file2 = self.__file("/b/movie.mkv", 55000, "SAME")

        self.assertEqual(self.binary_comparator.group([file1, file2]), [[file1, file2]])

    def test_given_a_file_that_cannot_be_read_when_grouping_then_it_is_left_out_and_the_others_are_still_grouped(self):
        """A failed read says nothing about whether a file matches: nothing is deleted
        on a maybe, and one unreadable file does not end the analysis."""
        file1 = self.__file("/a/report.pdf", 500, "SAME")
        unreadable = self.__file("/nas/report.pdf", 500, None)
        file2 = self.__file("/b/report.pdf", 500, "SAME")

        self.assertEqual(self.binary_comparator.group([file1, unreadable, file2]), [[file1, file2]])
        self.event_manager_mock.trigger.assert_any_call(
            "output", "Could not compare /nas/report.pdf: unreadable"
        )

    def test_given_a_cancelled_run_when_grouping_then_nothing_is_read(self):
        self.cancellation_mock.is_cancelled.return_value = True
        file1 = self.__file("/a/report.pdf", 500, "SAME")
        file2 = self.__file("/b/report.pdf", 500, "SAME")

        self.assertEqual(self.binary_comparator.group([file1, file2]), [])
        self.file_info_repository_mock.fetch_digest.assert_not_called()

    def __file(self, full_path: str, size: int, digest: str, partial_contents: bytes = b"START") -> FileInfo:
        if digest is not None:
            self.digests[full_path] = digest

        return FileInfo(full_path, full_path.split("/")[-1], size, partial_contents)

    def __fetch_digest(self, full_path: str) -> str:
        """What the file at full_path reads back as, from the digests __file recorded. A
        path missing from them cannot be read."""
        if full_path not in self.digests:
            raise OSError("unreadable")

        return self.digests[full_path]
