class Theme:
    """Semantic interface colors, persisted under the "theme" user setting.

    Only the colors listed in EDITABLE_COLORS are stored; every other shade
    used by the interface is derived from them so a palette stays coherent.
    """

    EDITABLE_COLORS = {
        "background": "Window background",
        "surface": "Side bar, panels and separators",
        "elevated": "Inputs, cards and console",
        "accent": "Buttons and highlights",
        "text": "Text",
    }

    PRESETS = {
        "Midnight": {
            "background": "#0C1821",
            "surface": "#1B2A41",
            "elevated": "#324A5F",
            "accent": "#4F8FB5",
            "text": "#CCC9DC",
        },
        "Graphite": {
            "background": "#15161A",
            "surface": "#1F2126",
            "elevated": "#2C2F36",
            "accent": "#7C9CF5",
            "text": "#E4E6EB",
        },
        "Forest": {
            "background": "#0F1A14",
            "surface": "#17281E",
            "elevated": "#23392B",
            "accent": "#5FBF7D",
            "text": "#D6E4D8",
        },
        "Paper": {
            "background": "#F1F3F6",
            "surface": "#E2E5EB",
            "elevated": "#FFFFFF",
            "accent": "#2F6FEB",
            "text": "#1B1F24",
        },
    }

    DEFAULT_PRESET = "Midnight"

    def __init__(self, colors: dict = None):
        palette = dict(self.PRESETS[self.DEFAULT_PRESET])

        for name, color in (colors or {}).items():
            if name in self.EDITABLE_COLORS and self.is_valid(color):
                palette[name] = color.upper()

        self.background = palette["background"]
        self.surface = palette["surface"]
        self.elevated = palette["elevated"]
        self.accent = palette["accent"]
        self.text = palette["text"]

    @property
    def border(self) -> str:
        return self.mix(self.surface, self.text, 0.18)

    @property
    def muted(self) -> str:
        return self.mix(self.text, self.background, 0.40)

    @property
    def surface_hover(self) -> str:
        return self.mix(self.surface, self.text, 0.12)

    @property
    def accent_hover(self) -> str:
        return self.mix(self.accent, self.text, 0.22)

    @property
    def on_accent(self) -> str:
        return "#10141A" if self.is_light(self.accent) else "#FFFFFF"

    def as_dict(self) -> dict:
        return {name: getattr(self, name) for name in self.EDITABLE_COLORS}

    @staticmethod
    def is_valid(color) -> bool:
        if not isinstance(color, str) or len(color) != 7 or not color.startswith("#"):
            return False
        try:
            int(color[1:], 16)
        except ValueError:
            return False
        return True

    @staticmethod
    def to_rgb(color: str) -> tuple:
        return tuple(int(color[index:index + 2], 16) for index in (1, 3, 5))

    @staticmethod
    def to_hex(rgb: tuple) -> str:
        return "#%02X%02X%02X" % tuple(max(0, min(255, round(channel))) for channel in rgb)

    @classmethod
    def mix(cls, color: str, towards: str, ratio: float) -> str:
        return cls.to_hex(
            tuple(
                base + (target - base) * ratio
                for base, target in zip(cls.to_rgb(color), cls.to_rgb(towards))
            )
        )

    @classmethod
    def is_light(cls, color: str) -> bool:
        red, green, blue = cls.to_rgb(color)
        return (red * 0.299 + green * 0.587 + blue * 0.114) > 150
