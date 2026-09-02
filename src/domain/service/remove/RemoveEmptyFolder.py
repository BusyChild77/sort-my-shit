from src.domain.event.EventManagerInterface import EventManagerInterface
from src.domain.repository.FileSystemRepositoryInterface import FileSystemRepositoryInterface
from src.domain.repository.SettingsRepositoryInterface import SettingsRepositoryInterface


class RemoveEmptyFolder:
    def __init__(
        self,
        event_manager: EventManagerInterface,
        settings_repository: SettingsRepositoryInterface,
        file_system_repository: FileSystemRepositoryInterface,
    ):
        self.event_manager = event_manager
        self.settings_repository = settings_repository
        self.file_system_repository = file_system_repository

    def list_empty_folders(self) -> list[str]:
        empty_folders = []
        self.event_manager.trigger("status", "Begin empty folders listing")

        for source_folder in self.settings_repository.fetch_one("source_folders"):
            for empty_folder in self.file_system_repository.list_empty_folders(source_folder):
                empty_folders.append(empty_folder)
                self.event_manager.trigger(
                    "foundEmptyFolder",
                    f"Found empty directory {empty_folder}"
                )

        self.event_manager.trigger(
            "status",
            f"Finished listing empty directories. {len(empty_folders)} folder(s) found"
        )

        self.event_manager.trigger("status", "Done")
        return empty_folders

    def remove_empty_folders(self, empty_folders: list[str]) -> None:
        for empty_folder in empty_folders:
            self.file_system_repository.remove_folder(empty_folder)

            self.event_manager.trigger(
                "deletedEmptyFolder",
                f"Deleted empty directory {empty_folder}"
            )

        self.event_manager.trigger(
            "status",
            "Finished deleting empty directories."
        )

        self.event_manager.trigger("status", "Done")
