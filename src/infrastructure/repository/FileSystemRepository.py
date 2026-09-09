from os import path as os_path, walk as os_walk, makedirs as os_makedirs, rmdir as os_rmdir
from shutil import copy2 as shutil_copy2, move as shutil_move
from threading import Thread

from src.domain.entity.FolderState import FolderState
from src.domain.repository.FileSystemRepositoryInterface import FileSystemRepositoryInterface


class FileSystemRepository(FileSystemRepositoryInterface):
    def probe_folder(self, folder_path: str, timeout_in_seconds: float) -> str:
        """A stat on a share that has gone away does not fail, it hangs: a hard mounted
        NFS export blocks until the server comes back, and a dropped SMB session for as
        long as the kernel's own timeout, which is counted in minutes. So the stat runs
        in a worker and the answer is whatever came back before the deadline.

        The worker is a daemon and is left behind rather than waited on. There is
        nothing to wait for, and it must never be what keeps the app from closing.
        """
        answer = []

        probe = Thread(target=lambda: self.__answer(folder_path, answer), daemon=True)
        probe.start()
        probe.join(timeout_in_seconds)

        if not answer:
            return FolderState.UNREACHABLE

        return FolderState.READABLE if answer[0] else FolderState.MISSING

    def list_file_paths(self, folder_path: str) -> list[str]:
        return [
            os_path.join(root, file_name)
            for root, folders, file_names in os_walk(folder_path)
            for file_name in file_names
        ]

    def list_empty_folders(self, folder_path: str) -> list[str]:
        """List folders left empty, children first, so a folder whose only
        content is empty folders is reported as empty too."""
        empty_folders = []

        for root, folders, file_names in os_walk(folder_path, topdown=False):
            if root == folder_path or file_names:
                continue

            if all(os_path.join(root, folder) in empty_folders for folder in folders):
                empty_folders.append(root)

        return empty_folders

    def folder_exists(self, folder_path: str) -> bool:
        return os_path.isdir(folder_path)

    def file_exists(self, file_path: str) -> bool:
        return os_path.isfile(file_path)

    def create_folder(self, folder_path: str):
        os_makedirs(folder_path, exist_ok=True)

    def remove_folder(self, folder_path: str):
        os_rmdir(folder_path)

    def move_file(self, source_path: str, destination_path: str):
        shutil_move(source_path, destination_path)

    def copy_file(self, source_path: str, destination_path: str):
        shutil_copy2(source_path, destination_path)

    @staticmethod
    def __answer(folder_path: str, answer: list):
        # Appending is what says the stat came back at all, so it happens whatever the
        # answer was. isdir swallows the usual refusals itself and returns False.
        try:
            answer.append(os_path.isdir(folder_path))
        except OSError:
            answer.append(False)
