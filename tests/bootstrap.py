from unittest import TestLoader, TestSuite, TextTestRunner

from tests.application.service.IconProviderTest import IconProviderTest
from tests.domain.entity.ThemeTest import ThemeTest
from tests.domain.service.CompareBinaryTest import BinaryComparatorTest
from tests.domain.service.CompareFileNameTest import FileNameComparatorTest
from tests.domain.service.ListDuplicateTest import ListDuplicateTest
from tests.domain.service.PlanSortTest import PlanSortTest
from tests.domain.service.RemoveDuplicateTest import RemoveDuplicateTest
from tests.domain.service.RemoveEmptyFileTest import RemoveEmptyFileTest
from tests.domain.service.RemoveEmptyFolderTest import RemoveEmptyFolderTest
from tests.domain.service.ResolveCategoryTest import ResolveCategoryTest
from tests.domain.service.SortFileTest import SortFileTest
from tests.infrastructure.repository.FileSystemRepositoryTest import FileSystemRepositoryTest
from tests.infrastructure.RunDirectoryTest import RunDirectoryTest
from tests.infrastructure.repository.SettingsRepositoryTest import SettingsRepositoryTest

test_cases = [
    IconProviderTest,
    ThemeTest,
    BinaryComparatorTest,
    FileNameComparatorTest,
    ListDuplicateTest,
    PlanSortTest,
    RemoveDuplicateTest,
    RemoveEmptyFileTest,
    RemoveEmptyFolderTest,
    ResolveCategoryTest,
    SortFileTest,
    FileSystemRepositoryTest,
    RunDirectoryTest,
    SettingsRepositoryTest,
]


def suite():
    loader = TestLoader()
    suite = TestSuite()

    for test_case in test_cases:
        suite.addTests(loader.loadTestsFromTestCase(test_case))

    return suite


if __name__ == '__main__':
    runner = TextTestRunner()
    runner.run(suite())
