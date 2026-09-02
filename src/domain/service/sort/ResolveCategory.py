from os import path as os_path

from src.domain.repository.SettingsRepositoryInterface import SettingsRepositoryInterface


class ResolveCategory:
    def __init__(self, settings_repository: SettingsRepositoryInterface):
        self.settings_repository = settings_repository
        self.__categories_by_extension = None

    def resolve(self, file_path: str) -> str:
        """Return the category a file belongs to, or None when its extension is unknown."""
        extension = os_path.splitext(file_path)[1].lstrip(".").lower()

        if extension == "":
            return None

        return self.__categories().get(extension)

    def __categories(self) -> dict:
        if self.__categories_by_extension is None:
            type_mapping = self.settings_repository.fetch_type_mapping()
            self.__categories_by_extension = {
                extension.lower(): category
                for category, extensions in type_mapping.items()
                for extension in extensions
            }

        return self.__categories_by_extension
