from unittest import TestCase

from src.domain.entity.Theme import Theme


class ThemeTest(TestCase):
    def test_given_no_color_when_building_a_theme_then_the_default_preset_is_used(self):
        self.assertEqual(Theme().as_dict(), Theme.PRESETS[Theme.DEFAULT_PRESET])

    def test_given_a_single_color_when_building_a_theme_then_the_other_colors_keep_their_default(self):
        theme = Theme({"accent": "#ff0000"})

        self.assertEqual(theme.accent, "#FF0000")
        self.assertEqual(theme.background, Theme.PRESETS[Theme.DEFAULT_PRESET]["background"])

    def test_given_an_invalid_color_when_building_a_theme_then_it_is_ignored(self):
        self.assertEqual(
            Theme({"accent": "not a color"}).accent,
            Theme.PRESETS[Theme.DEFAULT_PRESET]["accent"],
        )

    def test_given_an_unknown_color_name_when_building_a_theme_then_it_is_ignored(self):
        self.assertNotIn("unknown", Theme({"unknown": "#FF0000"}).as_dict())

    def test_given_a_light_accent_when_reading_the_text_on_it_then_a_dark_text_is_returned(self):
        self.assertEqual(Theme({"accent": "#FFFFFF"}).on_accent, "#10141A")

    def test_given_a_dark_accent_when_reading_the_text_on_it_then_a_light_text_is_returned(self):
        self.assertEqual(Theme({"accent": "#000000"}).on_accent, "#FFFFFF")

    def test_given_two_colors_when_mixing_them_halfway_then_the_middle_color_is_returned(self):
        self.assertEqual(Theme.mix("#000000", "#FFFFFF", 0.5), "#808080")

    def test_given_a_saved_theme_when_reading_it_back_then_it_is_unchanged(self):
        colors = {
            "background": "#101010",
            "surface": "#202020",
            "elevated": "#303030",
            "accent": "#405060",
            "text": "#F0F0F0",
        }

        self.assertEqual(Theme(Theme(colors).as_dict()).as_dict(), colors)
