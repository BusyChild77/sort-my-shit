from os import path as os_path

from src.domain.event.EventManagerInterface import EventManagerInterface
from src.domain.repository.FileInfoRepositoryInterface import FileInfoRepositoryInterface
from src.domain.entity.DuplicateMatch import DuplicateMatch
from src.domain.entity.FileInfo import FileInfo
from src.domain.task.CancellationInterface import CancellationInterface


class RemoveDuplicate:
    def __init__(
            self,
            file_info_repository: FileInfoRepositoryInterface,
            event_manager: EventManagerInterface,
            cancellation: CancellationInterface,
    ):
        self.file_info_repository = file_info_repository
        self.event_manager = event_manager
        self.cancellation = cancellation

    def remove_duplicates(self, duplicatesList: list[DuplicateMatch]):
        self.event_manager.trigger("status", "Removing duplicate files")

        failures = 0

        for duplicate in duplicatesList:
            for file in duplicate.files:
                if self.cancellation.is_cancelled():
                    self.event_manager.trigger("status", "Duplicate removal cancelled")
                    return

                if not self.__remove(file, duplicate):
                    failures += 1

        self.event_manager.trigger(
            "status",
            "Done" if failures == 0 else f"Done, {failures} file(s) could not be removed"
        )

    def __remove(self, file: FileInfo, duplicate: DuplicateMatch) -> bool:
        """False when the file is still there. A share that dropped between the analysis
        and the removal takes its own files with it and nobody else's."""
        if not os_path.isfile(file.full_path):
            return True

        try:
            self.file_info_repository.remove_one(file.full_path)
        except OSError as failure:
            self.event_manager.trigger("output", f"Could not remove {file.full_path}: {failure}")
            return False

        self.event_manager.trigger(
            "output",
            f"Removed {file.full_path} duplicate of {duplicate.duplicate_of.full_path}"
        )

        return True
