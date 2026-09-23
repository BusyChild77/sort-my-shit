from unittest import TestCase
from unittest.mock import Mock

from src.domain.entity.FileInfo import FileInfo
from src.domain.service.compare.CompareFileName import CompareFileName
from src.domain.event.EventManagerInterface import EventManagerInterface


class FileNameComparatorTest(TestCase):
    def setUp(self):
        self.file_name_comparator = CompareFileName(
            Mock(EventManagerInterface)
        )

        super().setUp()

    def test_given_two_files_with_the_same_name_in_different_folders_when_grouping_then_they_are_grouped_together(self):
        file1 = FileInfo("/tests/testFile1.txt", "testFile1.txt", 500, "")
        file2 = FileInfo("/tests/subfolder/testFile1.txt", "testFile1.txt", 500, "")

        self.assertEqual(self.file_name_comparator.group([file1, file2]), [[file1, file2]])

    def test_given_two_files_with_different_names_when_grouping_then_they_are_not_grouped(self):
        file1 = FileInfo("/tests/testFile1.txt", "testFile1.txt", 500, "")
        file2 = FileInfo("/tests/testFile2.txt", "testFile2.txt", 500, "")

        self.assertEqual(self.file_name_comparator.group([file1, file2]), [])

    def test_given_several_names_shared_when_grouping_then_one_group_per_name_in_the_order_listed(self):
        files = [
            FileInfo(f"/{folder}/{name}", name, 500, "")
            for name in ("a.txt", "b.txt", "c.txt") for folder in ("one", "two")
        ]

        self.assertEqual(
            self.file_name_comparator.group(files),
            [files[0:2], files[2:4], files[4:6]],
        )
