from src.application.service.FontProvider import FontProvider


class Typography:
    """Single source of truth for the fonts used across the interface.

    PREFERRED_TITLE_FAMILIES opens on the face the application ships, see
    .claude/recipes/fonts.md:10. Its fallbacks are a list of their own rather than the
    console's, since a title is 22 and bold and not every console face carries that
    weight.
    """

    PREFERRED_FAMILIES = ("Inter", "Segoe UI", "Ubuntu", "Cantarell", "DejaVu Sans", "Arial")
    PREFERRED_MONO_FAMILIES = ("JetBrains Mono", "Cascadia Code", "Ubuntu Mono", "DejaVu Sans Mono", "Courier New")
    PREFERRED_TITLE_FAMILIES = FontProvider.FAMILIES + (
        "Consolas", "Cascadia Mono", "Menlo", "SF Mono", "JetBrains Mono",
        "DejaVu Sans Mono", "Noto Sans Mono", "Liberation Mono", "Ubuntu Mono", "Courier New",
    )

    FAMILY = "DejaVu Sans"
    MONO_FAMILY = "DejaVu Sans Mono"
    TITLE_FAMILY = MONO_FAMILY

    TITLE = (TITLE_FAMILY, 22, "bold")
    SECTION = (FAMILY, 14, "bold")
    BODY = (FAMILY, 12)
    SMALL = (FAMILY, 11)
    BUTTON = (FAMILY, 12, "bold")
    MONO = (MONO_FAMILY, 11)

    @classmethod
    def in_title_case(cls, text: str) -> str:
        """The title face draws capitals and nothing else, so a heading is set in them
        rather than losing its lower case to whatever the platform substitutes. Done
        here rather than in the copy: the screens keep reading as sentences, and the day
        the face changes this is the one line to drop."""
        return text.upper()

    @classmethod
    def resolve_families(cls, installed_families: tuple) -> None:
        """Pick the nicest installed families, called once when the window opens. With
        nothing monospaced installed, a title falls back on the body family, the face
        the rest of the screen is set in, rather than on the console one."""
        cls.FAMILY = cls.__first_installed(cls.PREFERRED_FAMILIES, installed_families, cls.FAMILY)
        cls.MONO_FAMILY = cls.__first_installed(cls.PREFERRED_MONO_FAMILIES, installed_families, cls.MONO_FAMILY)
        cls.TITLE_FAMILY = cls.__first_installed(cls.PREFERRED_TITLE_FAMILIES, installed_families, cls.FAMILY)

        cls.TITLE = (cls.TITLE_FAMILY, 22, "bold")
        cls.SECTION = (cls.FAMILY, 14, "bold")
        cls.BODY = (cls.FAMILY, 12)
        cls.SMALL = (cls.FAMILY, 11)
        cls.BUTTON = (cls.FAMILY, 12, "bold")
        cls.MONO = (cls.MONO_FAMILY, 11)

    @staticmethod
    def __first_installed(preferred: tuple, installed: tuple, fallback: str) -> str:
        for family in preferred:
            if family in installed:
                return family

        return fallback
