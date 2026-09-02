from os import path as os_path

from src.domain.entity.SortOperation import SortOperation
from src.domain.event.EventManagerInterface import EventManagerInterface
from src.domain.repository.FileSystemRepositoryInterface import FileSystemRepositoryInterface
from src.domain.repository.SettingsRepositoryInterface import SettingsRepositoryInterface
from src.domain.service.sort.ResolveCategory import ResolveCategory


class PlanSort:
    """Builds the list of moves a sort would perform, without touching the disk."""

    def __init__(
        self,
        event_manager: EventManagerInterface,
        settings_repository: SettingsRepositoryInterface,
        file_system_repository: FileSystemRepositoryInterface,
        category_resolver: ResolveCategory,
    ):
        self.event_manager = event_manager
        self.settings_repository = settings_repository
        self.file_system_repository = file_system_repository
        self.category_resolver = category_resolver

    def plan(self) -> list[SortOperation]:
        settings = self.settings_repository.fetch_all()
        destination_folder = os_path.abspath(settings["destination_folder"])
        preserve_folder_tree = settings["preserve_folder_tree"]

        self.event_manager.trigger("status", "Planning the sort")

        operations = []
        taken_destinations = set()

        for source_folder in settings["source_folders"]:
            operations += self.__plan_source_folder(
                os_path.abspath(source_folder),
                destination_folder,
                preserve_folder_tree,
                taken_destinations,
            )

        self.event_manager.trigger(
            "status",
            f"{len(operations)} file(s) to sort into {destination_folder}"
        )

        return operations

    def __plan_source_folder(
        self,
        source_folder: str,
        destination_folder: str,
        preserve_folder_tree: bool,
        taken_destinations: set,
    ) -> list[SortOperation]:
        if not self.file_system_repository.folder_exists(source_folder):
            self.event_manager.trigger("output", f"Skipping missing source folder {source_folder}")
            return []

        operations = []

        for file_path in sorted(self.file_system_repository.list_file_paths(source_folder)):
            if self.__is_inside(file_path, destination_folder):
                continue

            category = self.category_resolver.resolve(file_path)

            if category is None:
                continue

            operations.append(
                SortOperation(
                    source_path=file_path,
                    destination_path=self.__resolve_destination_path(
                        file_path,
                        self.__category_folder(
                            file_path, source_folder, destination_folder, category, preserve_folder_tree
                        ),
                        taken_destinations,
                    ),
                    category=category,
                )
            )

        return operations

    def __category_folder(
        self,
        file_path: str,
        source_folder: str,
        destination_folder: str,
        category: str,
        preserve_folder_tree: bool,
    ) -> str:
        if not preserve_folder_tree:
            return os_path.join(destination_folder, category)

        relative_folder = os_path.relpath(os_path.dirname(file_path), source_folder)

        if relative_folder == ".":
            return os_path.join(destination_folder, category)

        return os_path.join(destination_folder, relative_folder, category)

    def __resolve_destination_path(self, file_path: str, category_folder: str, taken_destinations: set) -> str:
        file_name, extension = os_path.splitext(os_path.basename(file_path))
        destination_path = os_path.join(category_folder, file_name + extension)
        duplicate_index = 1

        while destination_path in taken_destinations or self.file_system_repository.file_exists(destination_path):
            destination_path = os_path.join(category_folder, f"{file_name} ({duplicate_index}){extension}")
            duplicate_index += 1

        taken_destinations.add(destination_path)

        return destination_path

    @staticmethod
    def __is_inside(path: str, folder: str) -> bool:
        try:
            return os_path.commonpath([os_path.abspath(path), folder]) == folder
        except ValueError:
            return False
