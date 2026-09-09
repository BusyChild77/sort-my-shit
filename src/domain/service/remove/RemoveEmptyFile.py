from os import path as os_path

from src.domain.entity.FileInfo import FileInfo
from src.domain.event.EventManagerInterface import EventManagerInterface
from src.domain.repository.SettingsRepositoryInterface import SettingsRepositoryInterface
from src.domain.repository.FileInfoRepositoryInterface import FileInfoRepositoryInterface
from src.domain.service.folder.CheckFolder import CheckFolder
from src.domain.task.CancellationInterface import CancellationInterface


class RemoveEmptyFile:
    def __init__(
        self,
        event_manager: EventManagerInterface,
        settings_repository: SettingsRepositoryInterface,
        file_info_repository: FileInfoRepositoryInterface,
        folder_check: CheckFolder,
        cancellation: CancellationInterface,
    ):
        self.event_manager = event_manager
        self.settings_repository = settings_repository
        self.file_info_repository = file_info_repository
        self.folder_check = folder_check
        self.cancellation = cancellation

    def list_empty_files(self):
        self.event_manager.trigger("status", "Fetching files")

        folders, unreadable = self.folder_check.readable(
            self.settings_repository.fetch_one("remove_duplicates_folders")
        )

        all_files = []

        for folder in folders:
            all_files += self.file_info_repository.fetch_all_from_folder(folder, skip_empty_files=False)

        empty_files = []

        file: FileInfo
        for file in all_files:
            if self.cancellation.is_cancelled():
                self.event_manager.trigger("status", "Analysis cancelled")
                return empty_files

            if self.__is_certainly_empty(file):
                empty_files.append(file)

        self.event_manager.trigger(
            "status",
            f"Done. {len(empty_files)} empty file(s) found." + self.folder_check.warning(unreadable)
        )

        return empty_files

    def remove_empty_files(self, empty_files: list[FileInfo]):
        self.event_manager.trigger("status", "Removing empty files")

        failures = 0

        for file in empty_files:
            if self.cancellation.is_cancelled():
                self.event_manager.trigger("status", "Empty file removal cancelled")
                return

            if not self.__remove(file):
                failures += 1

        self.event_manager.trigger(
            "status",
            "Done" if failures == 0 else f"Done, {failures} file(s) could not be removed"
        )

    def __remove(self, file: FileInfo) -> bool:
        # Asked a second time, on the way out rather than on the way in: a file listed
        # minutes ago may have been written to, or finally downloaded, since.
        if not self.__is_certainly_empty(file):
            return True

        try:
            self.file_info_repository.remove_one(file.full_path)
        except OSError as failure:
            self.event_manager.trigger("output", f"Could not remove {file.full_path}: {failure}")
            return False

        self.event_manager.trigger("output", f"Removed empty file {file.full_path}")

        return True

    @staticmethod
    def __is_certainly_empty(file: FileInfo) -> bool:
        """The size on the record and the bytes that came back both have to say so.

        A file that is genuinely empty reports a size of zero and reads back nothing. A
        cloud file that is only a placeholder on this machine, and a file on a share that
        dropped mid read, report their real size and also read back nothing. Believing
        the read on its own is what deletes a file that had contents in it.
        """
        if not os_path.isfile(file.full_path):
            return False

        return file.size == 0 and file.partial_contents is not None and len(file.partial_contents) == 0
