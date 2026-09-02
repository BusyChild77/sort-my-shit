from unittest import TestCase

from src.domain.entity.Version import Version


class VersionTest(TestCase):
    def test_given_a_tag_when_reading_it_then_the_leading_v_is_dropped(self):
        self.assertEqual(Version("v1.2.3").numbers, (1, 2, 3))

    def test_given_a_bare_number_when_reading_it_then_it_parses_the_same(self):
        self.assertEqual(Version("1.2.3").numbers, Version("v1.2.3").numbers)

    def test_given_a_later_patch_when_comparing_then_it_is_newer(self):
        self.assertTrue(Version("1.0.3").is_newer_than(Version("1.0.2")))

    def test_given_the_same_version_when_comparing_then_it_is_not_newer(self):
        self.assertFalse(Version("1.0.2").is_newer_than(Version("1.0.2")))

    def test_given_an_earlier_version_when_comparing_then_it_is_not_newer(self):
        self.assertFalse(Version("1.0.1").is_newer_than(Version("1.0.2")))

    def test_given_a_two_digit_patch_when_comparing_then_it_is_compared_as_a_number(self):
        """1.0.10 beats 1.0.9, which a string comparison would get backwards."""
        self.assertTrue(Version("1.0.10").is_newer_than(Version("1.0.9")))

    def test_given_a_later_minor_when_comparing_then_it_beats_a_higher_patch(self):
        self.assertTrue(Version("1.1.0").is_newer_than(Version("1.0.99")))

    def test_given_a_missing_patch_when_reading_it_then_it_reads_as_zero(self):
        self.assertEqual(Version("2.1").numbers, (2, 1, 0))

    def test_given_a_suffixed_patch_when_reading_it_then_the_number_is_kept(self):
        self.assertEqual(Version("1.0.2-beta").numbers, (1, 0, 2))

    def test_given_an_unreadable_tag_when_comparing_then_it_is_never_newer(self):
        """A malformed tag must not look like an update, or it would offer one forever."""
        self.assertFalse(Version("not a version").is_newer_than(Version("0.0.1")))

    def test_given_no_tag_when_reading_it_then_it_is_the_development_version(self):
        self.assertTrue(Version("").is_development())

    def test_given_the_development_version_when_reading_it_then_it_is_flagged_as_such(self):
        self.assertTrue(Version(Version.DEVELOPMENT).is_development())

    def test_given_a_released_version_when_reading_it_then_it_is_not_development(self):
        self.assertFalse(Version("1.0.0").is_development())

    def test_given_a_version_when_printing_it_then_it_reads_back_as_a_tag(self):
        self.assertEqual(str(Version("v1.2.3")), "v1.2.3")
