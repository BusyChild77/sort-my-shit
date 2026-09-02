from abc import ABC, abstractmethod


class InstallationRepositoryInterface(ABC):
    """What the running copy of the app is, and how it can be swapped for a new one."""

    APPIMAGE = "appimage"
    WINDOWS = "windows"
    MACOS = "macos"
    SOURCES = "sources"

    @abstractmethod
    def packaged_form(self) -> str:
        """One of the constants above. SOURCES means there is nothing to replace."""

    @abstractmethod
    def downloads_folder(self) -> str:
        pass

    @abstractmethod
    def replace_with(self, downloaded_path: str):
        """Put the downloaded file where the running one lives."""

    @abstractmethod
    def reveal(self, path: str):
        """Show the file to the user in whatever their platform calls a file manager."""

    @abstractmethod
    def restart(self):
        pass
