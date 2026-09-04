from os import path as os_path
from struct import unpack
from sys import modules as sys_modules
from unittest import TestCase

from src.application.service.FontProvider import FontProvider
from src.application.service.Typography import Typography


class FontProviderTest(TestCase):
    """The font is a file shipped alongside the code, so what is tested here is that it
    is found -- from the sources and from a bundle -- and that the file really carries
    the families the interface asks Tk for. A font registered under another name is a
    silent fall back to whatever the machine happens to have installed."""

    def setUp(self):
        self.sys_module = sys_modules["sys"]

    def tearDown(self):
        if hasattr(self.sys_module, "_MEIPASS"):
            delattr(self.sys_module, "_MEIPASS")

    def test_given_the_sources_when_reading_the_font_path_then_an_existing_file_is_returned(self):
        self.assertTrue(os_path.isfile(FontProvider().path()))

    def test_given_the_sources_when_reading_the_font_path_then_it_does_not_depend_on_the_working_directory(self):
        self.assertTrue(os_path.isabs(FontProvider().path()))

    def test_given_a_bundle_when_reading_the_font_path_then_it_points_inside_the_unpacked_folder(self):
        self.sys_module._MEIPASS = os_path.join("_", "unpacked")

        self.assertEqual(
            FontProvider().path(),
            os_path.join("_", "unpacked", "src", "application", "assets", "title-font.otf"),
        )

    def test_given_the_shipped_font_when_reading_it_then_it_is_a_font_the_platforms_can_take(self):
        """TrueType outlines or, as here, OpenType ones -- both are registered the same
        way, and anything else is a file the platform will refuse."""
        with open(FontProvider().path(), "rb") as font_file:
            self.assertIn(font_file.read(4), (b"\x00\x01\x00\x00", b"OTTO"))

    def test_given_the_shipped_font_when_reading_its_families_then_they_are_the_ones_the_titles_ask_for(self):
        """Both of them: the file names itself one way for Windows and another for the
        rest, and a title is only set in it when the name asked for is one of the two."""
        self.assertEqual(self.__families_of(FontProvider().path()), set(FontProvider.FAMILIES))

    def test_given_the_shipped_font_when_reading_it_then_it_draws_the_letters_a_title_is_made_of(self):
        """The headings, as they are drawn: capitals, since Typography sets them that
        way. A font swapped for one that does not draw them all leaves the missing
        letters to whatever the platform substitutes, in the middle of a heading."""
        titles = Typography.in_title_case(
            "SortMyShit Sort files by type Remove duplicates Remove empty files "
            "Remove empty folders Console output Settings Appearance"
        )

        self.assertEqual(set(titles) - self.__characters_of(FontProvider().path()), set())

    def test_given_the_shipped_font_when_registering_it_then_the_answer_is_remembered(self):
        font_provider = FontProvider()

        self.assertEqual(font_provider.register(), font_provider.register())

    def test_given_a_missing_font_when_registering_it_then_nothing_is_registered(self):
        self.sys_module._MEIPASS = os_path.join("_", "nowhere")

        self.assertFalse(FontProvider().register())

    def __families_of(self, path: str) -> set:
        """Every family the font names itself: name 1, and name 16 where the file splits
        the family it belongs to from the weight it is."""
        font = self.__read(path)
        table = self.__table(font, b"name")
        count, offset = unpack(">HH", font[table + 2:table + 6])
        families = set()

        for record in range(count):
            platform, _, _, name, length, position = unpack(">HHHHHH", font[table + 6 + record * 12:table + 18 + record * 12])

            if name in (1, 16):
                start = table + offset + position
                encoding = "utf-16-be" if platform == 3 else "latin-1"
                families.add(font[start:start + length].decode(encoding))

        if not families:
            raise AssertionError("The font carries no family name.")

        return families

    def __characters_of(self, path: str) -> set:
        """The characters the font draws, out of its format 4 character map."""
        font = self.__read(path)
        table = self.__character_map(font)
        segments = unpack(">H", font[table + 6:table + 8])[0] // 2
        ends = table + 14
        starts = ends + segments * 2 + 2

        characters = set()

        for segment in range(segments):
            last = unpack(">H", font[ends + segment * 2:ends + segment * 2 + 2])[0]
            first = unpack(">H", font[starts + segment * 2:starts + segment * 2 + 2])[0]
            characters.update(chr(code) for code in range(first, min(last, 0xFFFE) + 1))

        return characters

    def __character_map(self, font: bytes) -> int:
        """The windows character map, past the encodings the table starts with."""
        table = self.__table(font, b"cmap")

        for encoding in range(unpack(">H", font[table + 2:table + 4])[0]):
            platform, _, offset = unpack(">HHI", font[table + 4 + encoding * 8:table + 12 + encoding * 8])

            if platform == 3:
                return table + offset

        raise AssertionError("The font carries no windows character map.")

    def __read(self, path: str) -> bytes:
        with open(path, "rb") as font_file:
            return font_file.read()

    def __table(self, font: bytes, wanted: bytes) -> int:
        for entry in range(unpack(">H", font[4:6])[0]):
            tag, _, offset, _ = unpack(">4sIII", font[12 + entry * 16:28 + entry * 16])

            if tag == wanted:
                return offset

        raise AssertionError(f"The font carries no {wanted.decode()} table.")
