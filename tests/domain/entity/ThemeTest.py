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

    def test_given_every_preset_when_reading_it_then_it_sets_each_editable_color_and_no_other(self):
        for name, preset in Theme.PRESETS.items():
            with self.subTest(preset=name):
                self.assertEqual(preset.keys(), Theme.EDITABLE_COLORS.keys())
                self.assertTrue(all(Theme.is_valid(color) for color in preset.values()))

    def test_given_the_default_preset_when_looking_it_up_then_it_is_one_of_the_presets(self):
        self.assertIn(Theme.DEFAULT_PRESET, Theme.PRESETS)

    def test_given_every_preset_when_reading_its_colors_then_no_two_of_them_are_the_same(self):
        """Two colors of one palette that match flatten whatever they separate -- a side
        bar that disappears into the window, a card that disappears into the side bar."""
        for name, preset in Theme.PRESETS.items():
            with self.subTest(preset=name):
                self.assertEqual(len(set(preset.values())), len(preset))

    def test_given_every_preset_when_writing_text_on_it_then_the_text_is_readable_on_every_surface(self):
        """The three the interface draws text on, held to the 4.5:1 of WCAG AA. A preset
        is picked for how it looks, and this is what stops one being picked that cannot
        be read."""
        for name in Theme.PRESETS:
            theme = Theme(Theme.PRESETS[name])

            for surface in ("background", "surface", "elevated"):
                with self.subTest(preset=name, on=surface):
                    self.assertGreaterEqual(self.__contrast(theme.text, getattr(theme, surface)), 4.5)

    def test_given_every_preset_when_reading_its_derived_shades_then_they_hold_up_against_the_palette(self):
        """Muted text, the label on a filled button and the accent itself are held to the
        3:1 WCAG AA asks of large text and of interface components, which is what they
        are: the muted line is a caption, the button label is bold on a filled button."""
        for name in Theme.PRESETS:
            theme = Theme(Theme.PRESETS[name])

            with self.subTest(preset=name):
                self.assertGreaterEqual(self.__contrast(theme.muted, theme.background), 3.0)
                self.assertGreaterEqual(self.__contrast(theme.on_accent, theme.accent), 3.0)
                self.assertGreaterEqual(self.__contrast(theme.accent, theme.background), 3.0)

    def test_given_a_saved_theme_when_reading_it_back_then_it_is_unchanged(self):
        colors = {
            "background": "#101010",
            "surface": "#202020",
            "elevated": "#303030",
            "accent": "#405060",
            "text": "#F0F0F0",
        }

        self.assertEqual(Theme(Theme(colors).as_dict()).as_dict(), colors)

    @classmethod
    def __contrast(cls, one: str, two: str) -> float:
        """The WCAG ratio between two colors, 1 for two identical ones and 21 for black
        on white. Written here rather than in Theme: the interface never needs it, only
        the check that a palette can be read does."""
        lighter, darker = sorted((cls.__luminance(one), cls.__luminance(two)), reverse=True)

        return (lighter + 0.05) / (darker + 0.05)

    @staticmethod
    def __luminance(color: str) -> float:
        channels = [
            value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4
            for value in (channel / 255 for channel in Theme.to_rgb(color))
        ]

        return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]
