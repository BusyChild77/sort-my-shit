from unittest import TestCase

from src.application.service.Shortcut import Shortcut
from src.application.service.SMSRenderer import SMSRenderer


class ShortcutTest(TestCase):
    """The shortcuts were bare letters bound on the window, so a letter typed into a
    folder field reached the binding and changed the screen mid-path. They are held with
    Alt now, and what is checked here is that none of them can be produced by typing:
    a sequence that lost its modifier is the bug coming straight back."""

    def test_given_a_letter_when_binding_it_then_the_sequence_asks_for_the_alt_modifier(self):
        self.assertEqual(Shortcut.sequence("S"), "<Alt-KeyPress-s>")

    def test_given_a_letter_when_binding_it_then_it_is_bound_in_lower_case(self):
        """With no Shift held, Tk reports the lower case keysym whatever the side bar
        writes beside the entry."""
        self.assertEqual(Shortcut.sequence("D"), Shortcut.sequence("d"))

    def test_given_a_letter_when_writing_it_on_screen_then_the_modifier_is_written_with_it(self):
        self.assertEqual(Shortcut.label("s"), "Alt+S")

    def test_given_the_navigation_when_reading_its_shortcuts_then_no_two_screens_share_one(self):
        letters = [shortcut for _, _, shortcut in SMSRenderer.NAVIGATION]

        self.assertEqual(len(set(letters)), len(letters))

    def test_given_the_navigation_when_binding_its_shortcuts_then_every_one_of_them_is_held_with_alt(self):
        for _, _, shortcut in SMSRenderer.NAVIGATION:
            self.assertTrue(Shortcut.sequence(shortcut).startswith(f"<{Shortcut.MODIFIER}-"))

    def test_given_the_navigation_when_splitting_it_between_the_menus_then_neither_of_them_is_left_empty(self):
        """The Actions menu takes the first entries and the File menu the rest, so a
        split that ran past either end would hand one of the two nothing to list."""
        self.assertGreater(SMSRenderer.ACTION_ENTRIES, 0)
        self.assertLess(SMSRenderer.ACTION_ENTRIES, len(SMSRenderer.NAVIGATION))
