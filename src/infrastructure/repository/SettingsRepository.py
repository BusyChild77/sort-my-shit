from json import load as json_load, dumps as json_dumps

from src.domain.entity.Settings import Settings
from src.domain.entity.Theme import Theme
from src.domain.repository.SettingsRepositoryInterface import SettingsRepositoryInterface


class SettingsRepository(SettingsRepositoryInterface):
    app_settings = Settings()
    runDir: str = None

    def __init__(self):
        # The application is the only writer, so the parsed file is kept in memory:
        # fetch_one is called inside the comparison and sorting loops.
        self.cached_settings = None

    def fetch_all(self):
        if self.cached_settings is not None:
            return dict(self.cached_settings)

        try:
            with open(self.runDir + "/settings.json") as json_user_settings_file:
                user_settings = json_load(json_user_settings_file)
        except FileNotFoundError:
            self.save_all(self.__with_defaults({}))
            return dict(self.cached_settings)

        self.cached_settings = self.__with_defaults(self.__migrate(user_settings))

        return dict(self.cached_settings)

    def fetch_one(self, name: str):
        return self.fetch_all()[name]

    def fetch_type_mapping(self) -> dict:
        return self.app_settings.default_type_mapping

    def save_all(self, user_settings):
        self.cached_settings = dict(user_settings)

        with open(self.runDir + "/settings.json", "w") as json_user_settings_file:
            json_user_settings_file.write(json_dumps(user_settings, indent=4))

    def save_one(self, name: str, value):
        user_settings = self.fetch_all()
        user_settings[name] = value
        self.save_all(user_settings)

    def __migrate(self, user_settings: dict) -> dict:
        """Bring settings written by an older version up to the current shape."""
        migrated = {
            name: value
            for name, value in user_settings.items()
            if name not in self.app_settings.legacy_theme_colors
        }

        for legacy_name, current_name in self.app_settings.renamed_user_settings.items():
            if legacy_name in migrated:
                migrated[current_name] = migrated.pop(legacy_name)

        for name in self.app_settings.folder_list_user_settings:
            if isinstance(migrated.get(name), str):
                migrated[name] = [migrated[name]]

        legacy_theme = {
            color_name: user_settings[legacy_name]
            for legacy_name, color_name in self.app_settings.legacy_theme_colors.items()
            if legacy_name in user_settings
        }

        if legacy_theme and "theme" not in migrated:
            migrated["theme"] = legacy_theme

        return migrated

    def __with_defaults(self, user_settings: dict) -> dict:
        settings = {**self.app_settings.default_user_settings, **user_settings}
        settings["theme"] = Theme(settings.get("theme")).as_dict()
        return settings
