from os import path as os_path

from src.domain.entity.SortOperation import SortOperation
from src.domain.event.EventManagerInterface import EventManagerInterface
from src.domain.repository.FileSystemRepositoryInterface import FileSystemRepositoryInterface
from src.domain.repository.SettingsRepositoryInterface import SettingsRepositoryInterface
from src.domain.service.sort.PlanSort import PlanSort


class SortFile:
    def __init__(
        self,
        event_manager: EventManagerInterface,
        settings_repository: SettingsRepositoryInterface,
        file_system_repository: FileSystemRepositoryInterface,
        sort_planner: PlanSort,
    ):
        self.event_manager = event_manager
        self.settings_repository = settings_repository
        self.file_system_repository = file_system_repository
        self.sort_planner = sort_planner

    def plan_sort(self) -> list[SortOperation]:
        return self.sort_planner.plan()

    def sort(self, operations: list[SortOperation]) -> None:
        keep_original_files = self.settings_repository.fetch_one("keep_original_files")

        self.event_manager.trigger("status", "Begin moving files to sorted folder")

        for operation in operations:
            self.__transfer(operation, keep_original_files)

        if not keep_original_files and self.settings_repository.fetch_one("delete_empty_source_folders"):
            self.__delete_empty_source_folders()

        self.event_manager.trigger("status", "Done")

    def __transfer(self, operation: SortOperation, keep_original_files: bool) -> None:
        if not self.file_system_repository.file_exists(operation.source_path):
            self.event_manager.trigger("output", f"Skipping missing file {operation.source_path}")
            return

        destination_folder = os_path.dirname(operation.destination_path)

        if not self.file_system_repository.folder_exists(destination_folder):
            self.event_manager.trigger("status", f"Creating folder {destination_folder}")
            self.file_system_repository.create_folder(destination_folder)

        if keep_original_files:
            self.file_system_repository.copy_file(operation.source_path, operation.destination_path)
            action = "copied"
        else:
            self.file_system_repository.move_file(operation.source_path, operation.destination_path)
            action = "moved"

        self.event_manager.trigger(
            "output",
            f"{operation.source_path} {action} successfully, now into {operation.destination_path}",
        )

    def __delete_empty_source_folders(self) -> None:
        self.event_manager.trigger("status", "Deleting source folders left empty")

        for source_folder in self.settings_repository.fetch_one("source_folders"):
            for empty_folder in self.file_system_repository.list_empty_folders(source_folder):
                self.file_system_repository.remove_folder(empty_folder)
                self.event_manager.trigger("output", f"Deleted empty source folder {empty_folder}")
