from src.domain.entity.FolderState import FolderState
from src.domain.event.EventManagerInterface import EventManagerInterface
from src.domain.repository.FileSystemRepositoryInterface import FileSystemRepositoryInterface


class CheckFolder:
    """The folders an action is about to work on, looked at before it walks them.

    A cloud drive, a network share and a folder inside a virtual machine are all just
    paths here, and all three can be gone by the time an action runs. Walking one that
    has gone away finds nothing, and every screen reports "nothing found" the same way
    it reports a folder that really is clean. So an unreadable folder is dropped from
    the scan and said out loud instead.

    The probe carries a deadline because a share whose server has gone does not answer
    at all: a stat on a hard mounted NFS export, or on a dropped SMB session, blocks for
    as long as the kernel allows rather than failing.
    """

    TIMEOUT_IN_SECONDS = 5

    MESSAGES = {
        FolderState.MISSING: "Skipping {folder}: no such folder.",
        FolderState.UNREACHABLE: (
            "Skipping {folder}: it did not answer within {timeout} seconds. A drive or share that is "
            "not connected is not an empty folder, so nothing inside it was looked at."
        ),
    }

    def __init__(
        self,
        event_manager: EventManagerInterface,
        file_system_repository: FileSystemRepositoryInterface,
    ):
        self.event_manager = event_manager
        self.file_system_repository = file_system_repository

    def readable(self, folder_paths: list[str]) -> tuple[list[str], list[str]]:
        """Splits the folders into the ones that answered and can be walked, and the ones
        that could not, each of those reported as it is dropped."""
        readable = []
        unreadable = []

        for folder_path in folder_paths:
            state = self.file_system_repository.probe_folder(folder_path, self.TIMEOUT_IN_SECONDS)

            if state == FolderState.READABLE:
                readable.append(folder_path)
                continue

            unreadable.append(folder_path)
            self.event_manager.trigger("output", self.__message(state, folder_path))

        return readable, unreadable

    def reachable(self, folder_path: str) -> bool:
        """Whether the folder answered at all, which is the question a destination asks:
        one that is not there yet is fine and gets created, one behind a mount that says
        nothing is not, and every file of the sort would fail against it."""
        if self.file_system_repository.probe_folder(folder_path, self.TIMEOUT_IN_SECONDS) != FolderState.UNREACHABLE:
            return True

        self.event_manager.trigger("output", self.__message(FolderState.UNREACHABLE, folder_path))

        return False

    def warning(self, unreadable: list[str]) -> str:
        """Appended to the count a screen reports, so a share that has gone away is never
        left to read as a folder with nothing in it."""
        if not unreadable:
            return ""

        return f" {len(unreadable)} folder(s) could not be read and were skipped."

    def __message(self, state: str, folder_path: str) -> str:
        return self.MESSAGES[state].format(folder=folder_path, timeout=self.TIMEOUT_IN_SECONDS)
