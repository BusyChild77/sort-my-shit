from src.domain.event.EventManagerInterface import EventManagerInterface
from src.domain.entity.FileInfo import FileInfo


class CompareFileName:
    def __init__(
        self,
        event_manager: EventManagerInterface,
    ):
        self.event_manager = event_manager

    def group(self, files: list[FileInfo]) -> list[list[FileInfo]]:
        """The files sharing a name, in groups of two or more, each in the order it was
        listed."""
        self.event_manager.trigger("status", "Comparing file names")

        groups = {}

        for file in files:
            groups.setdefault(file.file_name, []).append(file)

        return [group for group in groups.values() if len(group) > 1]
