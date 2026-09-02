from unittest import TestCase
from unittest.mock import Mock

from src.domain.repository.SettingsRepositoryInterface import SettingsRepositoryInterface
from src.domain.service.sort.ResolveCategory import ResolveCategory


class ResolveCategoryTest(TestCase):
    def setUp(self):
        settings_repository_mock = Mock(SettingsRepositoryInterface)
        settings_repository_mock.fetch_type_mapping.return_value = {
            "docs": ["pdf", "txt"],
            "pics": ["jpg"],
        }

        self.category_resolver = ResolveCategory(settings_repository_mock)

        super().setUp()

    def test_given_a_known_extension_when_resolving_then_its_category_is_returned(self):
        self.assertEqual(self.category_resolver.resolve("/folder/report.pdf"), "docs")

    def test_given_an_uppercase_extension_when_resolving_then_its_category_is_returned(self):
        self.assertEqual(self.category_resolver.resolve("/folder/HOLIDAY.JPG"), "pics")

    def test_given_an_unknown_extension_when_resolving_then_nothing_is_returned(self):
        self.assertIsNone(self.category_resolver.resolve("/folder/archive.xyz"))

    def test_given_a_file_without_extension_when_resolving_then_nothing_is_returned(self):
        self.assertIsNone(self.category_resolver.resolve("/folder/README"))
