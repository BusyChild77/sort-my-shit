from unittest import TestCase

from src.application.service.OtherProject import OtherProject


class OtherProjectTest(TestCase):
    """The address is both the word the user clicks and the page it opens, and the two
    are written apart. A name that no longer matches the address it opens is a link
    reading as one site and landing on another."""

    def test_given_the_link_when_reading_it_then_it_opens_the_site_the_word_names(self):
        self.assertEqual(OtherProject.URL, f"https://www.{OtherProject.NAME}")

    def test_given_the_link_when_reading_it_then_it_is_served_over_https(self):
        self.assertTrue(OtherProject.URL.startswith("https://"))

    def test_given_the_sentence_above_the_link_when_reading_it_then_it_says_what_the_link_is(self):
        """The link is the site's address and nothing more, so the line above it is all
        a user has to go on before clicking."""
        self.assertTrue(OtherProject.BLURB.strip())
