from src.domain.entity.Theme import Theme
from src.infrastructure.repository.SettingsRepository import SettingsRepository
from src.application.service.EventManager import EventManager


class ThemeProvider:
    """Reads and writes the interface palette, and announces every change."""

    THEME_CHANGED = "theme_changed"

    def __init__(
        self,
        settings_repository: SettingsRepository,
        event_manager: EventManager,
    ):
        self.settings_repository = settings_repository
        self.event_manager = event_manager
        self.theme = None

    def get(self) -> Theme:
        if self.theme is None:
            self.theme = Theme(self.settings_repository.fetch_one("theme"))

        return self.theme

    def save_color(self, color_name: str, color: str) -> None:
        colors = self.get().as_dict()
        colors[color_name] = color
        self.save(colors)

    def apply_preset(self, preset_name: str) -> None:
        self.save(Theme.PRESETS[preset_name])

    def save(self, colors: dict) -> None:
        self.theme = Theme(colors)
        self.settings_repository.save_one("theme", self.theme.as_dict())
        self.event_manager.trigger(self.THEME_CHANGED)
