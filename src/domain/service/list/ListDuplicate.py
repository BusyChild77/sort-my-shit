from os import path as os_path

from src.domain.entity.FileInfo import FileInfo
from src.domain.entity.DuplicateMatch import DuplicateMatch
from src.domain.event.EventManagerInterface import EventManagerInterface
from src.domain.repository.SettingsRepositoryInterface import SettingsRepositoryInterface
from src.domain.repository.FileInfoRepositoryInterface import FileInfoRepositoryInterface
from src.domain.service.compare.CompareBinary import CompareBinary
from src.domain.service.compare.CompareFileName import CompareFileName
from src.domain.service.folder.CheckFolder import CheckFolder
from src.domain.task.CancellationInterface import CancellationInterface


class ListDuplicate:
    def __init__(
        self,
        event_manager: EventManagerInterface,
        settings_repository: SettingsRepositoryInterface,
        file_info_repository: FileInfoRepositoryInterface,
        binary_comparator: CompareBinary,
        file_name_comparator: CompareFileName,
        folder_check: CheckFolder,
        cancellation: CancellationInterface,
    ):
        self.event_manager = event_manager
        self.settings_repository = settings_repository
        self.file_info_repository = file_info_repository
        self.binary_comparator = binary_comparator
        self.file_name_comparator = file_name_comparator
        self.folder_check = folder_check
        self.cancellation = cancellation

    def list_duplicates(self):
        """In each match, the first file listed is kept and the others are its
        duplicates, see .claude/recipes/domain-layer.md:86."""
        self.event_manager.trigger("status", "Fetching files")

        folders, unreadable = self.folder_check.readable(
            self.settings_repository.fetch_one("remove_duplicates_folders")
        )

        all_files = self.__fetch_all_files(folders)

        if self.cancellation.is_cancelled():
            self.event_manager.trigger("status", "Analysis cancelled")
            return []

        self.event_manager.trigger("status", "Processing files")

        if self.settings_repository.fetch_one("binary_search") is True:
            groups = self.binary_comparator.group(all_files)
        else:
            groups = self.file_name_comparator.group(all_files)

        duplicate_matches = [DuplicateMatch(group[1:], group[0]) for group in groups]

        if self.cancellation.is_cancelled():
            self.event_manager.trigger("status", "Analysis cancelled")
            return duplicate_matches

        self.event_manager.trigger(
            "status",
            f"Done. {len(duplicate_matches)} duplicate(s) found." + self.folder_check.warning(unreadable)
        )

        return duplicate_matches

    def __fetch_all_files(self, folders: list[str]) -> list[FileInfo]:
        """Every folder into one list, so a file in one folder is matched against a copy
        of itself sitting in another. A folder picked along with one inside it lists the
        same file twice, and a file must never be offered up as a duplicate of itself:
        removing it would delete the only copy."""
        all_files = []
        seen_paths = set()

        for folder in folders:
            for file in self.file_info_repository.fetch_all_from_folder(folder):
                full_path = os_path.normpath(file.full_path)

                if full_path in seen_paths or not os_path.isfile(file.full_path):
                    continue

                seen_paths.add(full_path)
                all_files.append(file)

        return all_files
