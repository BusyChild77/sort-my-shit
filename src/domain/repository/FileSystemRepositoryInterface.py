from abc import ABC, abstractmethod


class FileSystemRepositoryInterface(ABC):
    @abstractmethod
    def probe_folder(self, folder_path: str, timeout_in_seconds: float) -> str:
        """One of the FolderState constants, within the deadline given.

        folder_exists answers whether a folder is there and takes as long as the
        filesystem holding it decides to take. This one answers UNREACHABLE instead of
        waiting forever, which is what a disconnected share needs.
        """
        pass

    @abstractmethod
    def list_file_paths(self, folder_path: str) -> list[str]:
        pass

    @abstractmethod
    def list_empty_folders(self, folder_path: str) -> list[str]:
        pass

    @abstractmethod
    def folder_exists(self, folder_path: str) -> bool:
        pass

    @abstractmethod
    def file_exists(self, file_path: str) -> bool:
        pass

    @abstractmethod
    def create_folder(self, folder_path: str):
        pass

    @abstractmethod
    def remove_folder(self, folder_path: str):
        pass

    @abstractmethod
    def move_file(self, source_path: str, destination_path: str):
        pass

    @abstractmethod
    def copy_file(self, source_path: str, destination_path: str):
        pass
