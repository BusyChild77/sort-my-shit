class Typography:
    """Single source of truth for the fonts used across the interface."""

    PREFERRED_FAMILIES = ("Inter", "Segoe UI", "Ubuntu", "Cantarell", "DejaVu Sans", "Arial")
    PREFERRED_MONO_FAMILIES = ("JetBrains Mono", "Cascadia Code", "Ubuntu Mono", "DejaVu Sans Mono", "Courier New")

    FAMILY = "DejaVu Sans"
    MONO_FAMILY = "DejaVu Sans Mono"

    TITLE = (FAMILY, 22, "bold")
    SECTION = (FAMILY, 14, "bold")
    BODY = (FAMILY, 12)
    SMALL = (FAMILY, 11)
    BUTTON = (FAMILY, 12, "bold")
    MONO = (MONO_FAMILY, 11)

    @classmethod
    def resolve_families(cls, installed_families: tuple) -> None:
        """Pick the nicest installed families, called once when the window opens."""
        cls.FAMILY = cls.__first_installed(cls.PREFERRED_FAMILIES, installed_families, cls.FAMILY)
        cls.MONO_FAMILY = cls.__first_installed(cls.PREFERRED_MONO_FAMILIES, installed_families, cls.MONO_FAMILY)

        cls.TITLE = (cls.FAMILY, 22, "bold")
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
