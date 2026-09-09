from src.domain.event.EventManagerInterface import EventManagerInterface
from src.domain.repository.FileSystemRepositoryInterface import FileSystemRepositoryInterface
from src.domain.repository.SettingsRepositoryInterface import SettingsRepositoryInterface
from src.domain.service.folder.CheckFolder import CheckFolder
from src.domain.task.CancellationInterface import CancellationInterface


class RemoveEmptyFolder:
    def __init__(
        self,
        event_manager: EventManagerInterface,
        settings_repository: SettingsRepositoryInterface,
        file_system_repository: FileSystemRepositoryInterface,
        folder_check: CheckFolder,
        cancellation: CancellationInterface,
    ):
        self.event_manager = event_manager
        self.settings_repository = settings_repository
        self.file_system_repository = file_system_repository
        self.folder_check = folder_check
        self.cancellation = cancellation

    def list_empty_folders(self) -> list[str]:
        empty_folders = []
        self.event_manager.trigger("status", "Begin empty folders listing")

        source_folders, unreadable = self.folder_check.readable(
            self.settings_repository.fetch_one("source_folders")
        )

        for source_folder in source_folders:
            if self.cancellation.is_cancelled():
                self.event_manager.trigger("status", "Analysis cancelled")
                return empty_folders

            for empty_folder in self.file_system_repository.list_empty_folders(source_folder):
                empty_folders.append(empty_folder)
                self.event_manager.trigger(
                    "foundEmptyFolder",
                    f"Found empty directory {empty_folder}"
                )

        # The count is the last thing said, so a folder that could not be read is still
        # on screen rather than wiped by a "Done" nobody needed.
        self.event_manager.trigger(
            "status",
            f"Finished listing empty directories. {len(empty_folders)} folder(s) found."
            + self.folder_check.warning(unreadable)
        )

        return empty_folders

    def remove_empty_folders(self, empty_folders: list[str]) -> None:
        failures = 0

        for empty_folder in empty_folders:
            if self.cancellation.is_cancelled():
                self.event_manager.trigger("status", "Empty folder removal cancelled")
                return

            if not self.__remove(empty_folder):
                failures += 1

        self.event_manager.trigger(
            "status",
            "Finished deleting empty directories."
            if failures == 0
            else f"Finished deleting empty directories, {failures} folder(s) could not be deleted."
        )

    def __remove(self, empty_folder: str) -> bool:
        """False when the folder is still there. A folder that filled up again since the
        analysis, or one on a share that has gone, must not stop the others."""
        try:
            self.file_system_repository.remove_folder(empty_folder)
        except OSError as failure:
            self.event_manager.trigger("output", f"Could not delete empty directory {empty_folder}: {failure}")
            return False

        self.event_manager.trigger(
            "deletedEmptyFolder",
            f"Deleted empty directory {empty_folder}"
        )

        return True
