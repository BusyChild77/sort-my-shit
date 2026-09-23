from src.domain.event.EventManagerInterface import EventManagerInterface
from src.domain.entity.FileInfo import FileInfo
from src.domain.repository.FileInfoRepositoryInterface import FileInfoRepositoryInterface
from src.domain.repository.SettingsRepositoryInterface import SettingsRepositoryInterface
from src.domain.task.CancellationInterface import CancellationInterface


class CompareBinary:
    def __init__(
        self,
        event_manager: EventManagerInterface,
        file_info_repository: FileInfoRepositoryInterface,
        settings_repository: SettingsRepositoryInterface,
        cancellation: CancellationInterface,
    ):
        self.event_manager = event_manager
        self.file_info_repository = file_info_repository
        self.settings_repository = settings_repository
        self.cancellation = cancellation

    def group(self, files: list[FileInfo]) -> list[list[FileInfo]]:
        """The files with identical contents, in groups of two or more, each in the order
        it was listed. Cheapest test first: the size and the first bytes are already
        known, so only the files agreeing on both are read, and each of them once."""
        groups = []

        for candidates in self.__group_by(self.__comparable(files), lambda file: (file.size, file.partial_contents)):
            if self.cancellation.is_cancelled():
                break

            groups += self.__group_by_contents(candidates)

        return groups

    def __comparable(self, files: list[FileInfo]) -> list[FileInfo]:
        if self.settings_repository.fetch_one("binary_search_large_files") is True:
            return files

        file_size_threshold = self.settings_repository.fetch_one(
            "binary_comparison_large_files_threshold"
        )

        return [file for file in files if file.size < file_size_threshold]

    def __group_by_contents(self, files: list[FileInfo]) -> list[list[FileInfo]]:
        """Cancellation is checked before each file, see
        .claude/recipes/domain-layer.md:98."""
        digests = {}

        for file in files:
            if self.cancellation.is_cancelled():
                return []

            digest = self.__digest(file)

            if digest is not None:
                digests.setdefault(digest, []).append(file)

        return [group for group in digests.values() if len(group) > 1]

    def __digest(self, file: FileInfo) -> str:
        """None for a file that could not be read, which is where a slow or flaky folder
        shows up. A failed read says nothing about whether it matches, so the file is
        left out rather than raising: nothing is deleted on a maybe, and one unreadable
        file does not end an analysis that has already read thousands."""
        self.event_manager.trigger("status", f"Reading {file.full_path}")

        try:
            return self.file_info_repository.fetch_digest(file.full_path)
        except OSError as failure:
            self.event_manager.trigger("output", f"Could not compare {file.full_path}: {failure}")
            return None

    @staticmethod
    def __group_by(files: list[FileInfo], key) -> list[list[FileInfo]]:
        groups = {}

        for file in files:
            groups.setdefault(key(file), []).append(file)

        return [group for group in groups.values() if len(group) > 1]
