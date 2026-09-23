from unittest import TestCase

from src.domain.entity.Settings import Settings


class SettingsTest(TestCase):
    def test_given_the_default_type_mapping_when_reading_it_then_no_extension_belongs_to_two_categories(self):
        """The last category listing an extension would silently win over the first."""
        extensions = [
            extension
            for category_extensions in Settings.default_type_mapping.values()
            for extension in category_extensions
        ]

        self.assertEqual(
            sorted({extension for extension in extensions if extensions.count(extension) > 1}),
            [],
        )

    def test_given_the_default_type_mapping_when_reading_it_then_every_extension_is_lower_case_without_a_dot(self):
        for category, extensions in Settings.default_type_mapping.items():
            for extension in extensions:
                self.assertEqual(extension, extension.lower().lstrip("."), category)
