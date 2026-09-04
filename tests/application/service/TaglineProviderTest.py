from unittest import TestCase

from src.application.service.TaglineProvider import TaglineProvider


class TaglineProviderTest(TestCase):
    """The tagline rotates from one run to the next, but never within one: the side bar
    is rebuilt every time the theme changes, and the line under the wordmark must not
    move under the user when it is."""

    def test_given_a_provider_when_asking_for_the_tagline_then_it_is_one_of_the_written_ones(self):
        self.assertIn(TaglineProvider().get(), TaglineProvider.TAGLINES)

    def test_given_a_provider_when_asking_twice_then_the_same_tagline_comes_back(self):
        provider = TaglineProvider()

        self.assertEqual(provider.get(), provider.get())

    def test_given_enough_runs_when_asking_for_the_tagline_then_every_sentence_is_drawn(self):
        """A sentence that could never come out would go unnoticed otherwise."""
        drawn = {TaglineProvider().get() for _ in range(2000)}

        self.assertEqual(drawn, set(TaglineProvider.TAGLINES))

    def test_given_the_taglines_when_reading_them_then_none_is_empty_or_written_twice(self):
        self.assertEqual(len(set(TaglineProvider.TAGLINES)), len(TaglineProvider.TAGLINES))
        self.assertTrue(all(tagline.strip() for tagline in TaglineProvider.TAGLINES))
