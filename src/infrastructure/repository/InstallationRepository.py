# sys is read through getattr because "frozen" only exists once PyInstaller has
# packaged the app, and sys.platform is needed at class level nowhere else.
import sys

from os import chmod as os_chmod, environ as os_environ, execv as os_execv, path as os_path, \
    remove as os_remove, replace as os_replace
from shutil import move as shutil_move
from subprocess import Popen
from tempfile import gettempdir

from src.domain.repository.InstallationRepositoryInterface import InstallationRepositoryInterface


class InstallationRepository(InstallationRepositoryInterface):
    """What the running copy is, and how to swap it for a downloaded one.

    Each platform hides the executable somewhere different and defends it differently:
    an AppImage is the single file $APPIMAGE points at, Windows refuses to delete a
    running .exe but allows renaming it, and a macOS bundle is not replaced here at all.
    """

    EXECUTABLE_MODE = 0o755
    PREVIOUS_SUFFIX = ".old"

    def packaged_form(self) -> str:
        if not getattr(sys, "frozen", False):
            return self.SOURCES

        if os_environ.get("APPIMAGE"):
            return self.APPIMAGE

        if sys.platform == "win32":
            return self.WINDOWS

        if sys.platform == "darwin":
            return self.MACOS

        return self.SOURCES

    def downloads_folder(self) -> str:
        folder = os_path.join(os_path.expanduser("~"), "Downloads")

        return folder if os_path.isdir(folder) else gettempdir()

    def replace_with(self, downloaded_path: str):
        installed = self.__installed_path()

        if self.packaged_form() == self.WINDOWS:
            self.__replace_windows_executable(installed, downloaded_path)
            return

        os_chmod(downloaded_path, self.EXECUTABLE_MODE)
        shutil_move(downloaded_path, installed)

    def restart(self):
        """Never returns on anything but Windows, where the caller has to quit so the
        replaced executable is released."""
        installed = self.__installed_path()

        if self.packaged_form() == self.WINDOWS:
            Popen([installed], close_fds=True)
            return

        os_execv(installed, [installed])

    def reveal(self, path: str):
        Popen(self.__reveal_command(path))

    def __replace_windows_executable(self, installed: str, downloaded_path: str):
        """Windows will not delete a running executable, but it will rename it, so the
        outgoing version is moved aside and swept up by the next update."""
        previous = installed + self.PREVIOUS_SUFFIX

        if os_path.exists(previous):
            os_remove(previous)

        os_replace(installed, previous)
        shutil_move(downloaded_path, installed)

    def __installed_path(self) -> str:
        if self.packaged_form() == self.APPIMAGE:
            return os_environ["APPIMAGE"]

        return sys.executable

    def __reveal_command(self, path: str) -> list:
        if sys.platform == "darwin":
            return ["open", "-R", path]

        if sys.platform == "win32":
            return ["explorer", "/select,", path]

        return ["xdg-open", os_path.dirname(path)]
