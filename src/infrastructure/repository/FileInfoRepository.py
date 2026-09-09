from os import path as os_path, walk as os_walk, remove as os_remove
from glob import glob

from src.domain.entity.FileInfo import FileInfo
from src.domain.repository.FileInfoRepositoryInterface import FileInfoRepositoryInterface
from src.infrastructure.repository.SettingsRepository import SettingsRepository
from src.application.service.EventManager import EventManager


class FileInfoRepository(FileInfoRepositoryInterface):
    PARTIAL_CONTENTS_LENGTH = 128

    def __init__(
        self,
        settings_repository: SettingsRepository,
        event_manager: EventManager,
    ):
        self.settings_repository = settings_repository
        self.event_manager = event_manager

    def fetch_all_from_folder(
        self,
        folder_path: str,
        skip_empty_files: bool = True,
        skip_large_files: bool = True,
    ) -> list[FileInfo]:
        all_file_full_paths = [
            y for x in os_walk(folder_path) for y in glob(os_path.join(x[0], "*.*"))
        ]

        all_files = []

        for file_full_path in all_file_full_paths:
            file_info = self.__fetch_from_folder(file_full_path, skip_empty_files, skip_large_files)

            if file_info is not None:
                all_files.append(file_info)

        return all_files

    def fetch_one(
        self, full_path: str, with_full_contents: bool = False, read_mode: str = "rb"
    ) -> FileInfo:
        file_contents = None
        with open(full_path, read_mode) as file_opened:
            file_partial_contents = file_opened.read(self.PARTIAL_CONTENTS_LENGTH)
            if with_full_contents:
                file_contents = file_opened.read()

        return FileInfo(
            full_path=full_path,
            file_name=os_path.basename(full_path),
            size=os_path.getsize(full_path),
            partial_contents=file_partial_contents,
            contents=file_contents,
        )

    def remove_one(self, file_path: str):
        os_remove(file_path)
        self.event_manager.trigger("output", "Removed file " + file_path)

    def __fetch_from_folder(self, file_full_path: str, skip_empty_files: bool, skip_large_files: bool) -> FileInfo:
        """None for a file this scan is not to work on, and for one that could not be
        read at all.

        A file that fails to open is dropped rather than handed on half filled: what
        reads these is also what deletes them, and a file whose contents never arrived
        is indistinguishable from an empty one once it is in the list. A share that goes
        down mid scan therefore costs the files it took with it, and nothing else.
        """
        if not os_path.isfile(file_full_path):
            return None

        try:
            size = os_path.getsize(file_full_path)

            if self.__is_skipped_as_large(size, skip_large_files):
                self.event_manager.trigger("output", "Skipping large file " + file_full_path)
                return None

            with open(file_full_path, "rb") as file_opened:
                file_partial_contents = file_opened.read(self.PARTIAL_CONTENTS_LENGTH)
        except OSError as failure:
            self.event_manager.trigger("output", f"Skipping unreadable file {file_full_path}: {failure}")
            return None

        if len(file_partial_contents) == 0 and skip_empty_files:
            self.event_manager.trigger("output", "Skipping empty File " + file_full_path)
            return None

        return FileInfo(
            full_path=file_full_path,
            file_name=os_path.basename(file_full_path),
            size=size,
            partial_contents=file_partial_contents,
        )

    def __is_skipped_as_large(self, size: int, skip_large_files: bool) -> bool:
        return (
            size > self.settings_repository.fetch_one("binary_comparison_large_files_threshold")
            and self.settings_repository.fetch_one("binary_search") is True
            and self.settings_repository.fetch_one("binary_search_large_files") is False
            and skip_large_files
        )
