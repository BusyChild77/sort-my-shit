from unittest import TestCase

from src.application.service.FontProvider import FontProvider
from src.application.service.Typography import Typography


class TypographyTest(TestCase):
    """Resolving the families is the one moment the interface decides what it is drawn
    in, and the titles are the only place the shipped font is meant to appear."""

    def setUp(self):
        self.families = (Typography.FAMILY, Typography.MONO_FAMILY, Typography.TITLE_FAMILY)

    def tearDown(self):
        Typography.resolve_families(self.families)

    def test_given_the_shipped_font_is_registered_when_resolving_the_families_then_the_titles_are_set_in_it(self):
        Typography.resolve_families(("Arial", "DejaVu Sans", "DejaVu Sans Mono", "Consolas", FontProvider.FAMILIES[0]))

        self.assertEqual(Typography.TITLE_FAMILY, FontProvider.FAMILIES[0])
        self.assertEqual(Typography.TITLE, (FontProvider.FAMILIES[0], 22, "bold"))

    def test_given_the_shipped_font_is_registered_when_resolving_the_families_then_the_rest_is_left_alone(self):
        Typography.resolve_families(("Arial", "DejaVu Sans", "DejaVu Sans Mono", FontProvider.FAMILIES[0]))

        self.assertEqual(Typography.BODY, (Typography.FAMILY, 12))
        self.assertNotEqual(Typography.FAMILY, FontProvider.FAMILIES[0])

    def test_given_the_platform_refused_the_font_when_resolving_the_families_then_the_titles_fall_back_on_consolas(self):
        Typography.resolve_families(("Arial", "DejaVu Sans", "DejaVu Sans Mono", "Consolas"))

        self.assertEqual(Typography.TITLE_FAMILY, "Consolas")

    def test_given_neither_the_shipped_font_nor_consolas_when_resolving_the_families_then_the_titles_take_the_closest_monospace(self):
        Typography.resolve_families(("Arial", "DejaVu Sans", "DejaVu Sans Mono"))

        self.assertEqual(Typography.TITLE_FAMILY, "DejaVu Sans Mono")

    def test_given_two_monospaces_when_resolving_the_families_then_the_titles_take_the_preferred_one(self):
        Typography.resolve_families(("DejaVu Sans", "Courier New", "Menlo", "DejaVu Sans Mono"))

        self.assertEqual(Typography.TITLE_FAMILY, "Menlo")

    def test_given_a_heading_when_setting_it_in_the_title_face_then_it_is_drawn_in_capitals(self):
        """The shipped face draws no lower case, so a heading that kept its own would
        lose half its letters to a substituted font."""
        self.assertEqual(Typography.in_title_case("Remove empty folders"), "REMOVE EMPTY FOLDERS")

    def test_given_nothing_monospaced_is_installed_when_resolving_the_families_then_the_titles_keep_the_body_family(self):
        Typography.resolve_families(("Arial", "DejaVu Sans"))

        self.assertEqual(Typography.TITLE_FAMILY, Typography.FAMILY)
        self.assertEqual(Typography.TITLE, (Typography.FAMILY, 22, "bold"))
