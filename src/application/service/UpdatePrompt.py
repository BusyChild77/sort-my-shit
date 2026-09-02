from threading import Thread
from tkinter import messagebox

from src.application.service.EventManager import EventManager
from src.domain.entity.Version import Version
from src.domain.repository.InstallationRepositoryInterface import InstallationRepositoryInterface
from src.domain.service.update.ApplyUpdate import ApplyUpdate
from src.domain.service.update.CheckForUpdate import CheckForUpdate
from src.infrastructure.repository.SettingsRepository import SettingsRepository


class UpdatePrompt:
    """Checks for a new version, and asks before installing it.

    Tk is single threaded and a network call is not instant, so the lookup and the
    download run in a worker and everything touching a widget is handed back through
    widget.after(). Nothing is ever replaced without the user saying yes.
    """

    STARTUP_DELAY_IN_MS = 1500

    MESSAGES = {
        CheckForUpdate.UP_TO_DATE: "Up to date.",
        CheckForUpdate.UNREACHABLE: "Could not reach GitHub. Check your connection and try again.",
        CheckForUpdate.NOT_UPDATABLE: "Updates apply to the packaged app, not to a run from the sources.",
    }

    def __init__(
        self,
        check_for_update: CheckForUpdate,
        apply_update: ApplyUpdate,
        installation_repository: InstallationRepositoryInterface,
        settings_repository: SettingsRepository,
        event_manager: EventManager,
    ):
        self.check_for_update = check_for_update
        self.apply_update = apply_update
        self.installation_repository = installation_repository
        self.settings_repository = settings_repository
        self.event_manager = event_manager
        self.busy = False

    def check_on_startup(self, widget):
        """The quiet check: it only ever speaks up when there is something to install."""
        if not self.settings_repository.fetch_one("check_for_updates_on_startup"):
            return

        widget.after(self.STARTUP_DELAY_IN_MS, lambda: self.check(widget))

    def check(self, widget, announce=None):
        """announce is called on the main thread with a line to display. Left out — the
        startup check — only an available update is worth interrupting for."""
        if self.busy:
            return

        self.busy = True
        self.__announce(announce, "Checking for updates...")

        Thread(target=lambda: self.__looked(widget, announce), daemon=True).start()

    def __looked(self, widget, announce):
        outcome, release = self.check_for_update.look()
        widget.after(0, lambda: self.__offer(widget, announce, outcome, release))

    def __offer(self, widget, announce, outcome, release):
        self.busy = False

        if outcome != CheckForUpdate.AVAILABLE:
            self.__announce(announce, self.__up_to_date_message(outcome))
            return

        self.__announce(announce, f"{release.version} is available.")

        if not messagebox.askyesno(
            "Update available",
            f"{release.version} is available, you are running {Version.current()}.\n\nDownload and install it now?",
        ):
            return

        self.busy = True
        Thread(target=lambda: self.__applied(widget, announce, release), daemon=True).start()

    def __applied(self, widget, announce, release):
        try:
            outcome = self.apply_update.apply(release)
        except OSError as failure:
            # Bound as a default argument: Python unbinds the name at the end of the
            # except block, so a lambda closing over it would fire on nothing.
            widget.after(0, lambda error=failure: self.__failed(announce, error))
            return

        widget.after(0, lambda: self.__installed(widget, announce, outcome, release))

    def __installed(self, widget, announce, outcome, release):
        self.busy = False

        if outcome == ApplyUpdate.HANDED_OVER:
            self.__announce(announce, f"{release.version} downloaded.")
            messagebox.showinfo(
                "Update downloaded",
                f"{release.version} has been downloaded and shown in Finder.\n\n"
                "Drag SortMyShit to your Applications folder to finish the update.",
            )
            return

        self.__announce(announce, f"Updated to {release.version}.")

        if messagebox.askyesno("Update installed", f"SortMyShit is now {release.version}.\n\nRestart to use it?"):
            self.__restart(widget)

    def __restart(self, widget):
        # Windows spawns the new process and needs this one gone to release the file it
        # just replaced; everywhere else execv takes the process over and never returns.
        self.installation_repository.restart()
        widget.winfo_toplevel().destroy()

    def __failed(self, announce, failure: OSError):
        self.busy = False
        self.__announce(announce, f"Update failed: {failure}")
        self.event_manager.trigger("output", f"Update failed: {failure}")
        messagebox.showerror("Update failed", f"The update could not be installed.\n\n{failure}")

    def __up_to_date_message(self, outcome: str) -> str:
        if outcome == CheckForUpdate.UP_TO_DATE:
            return f"Up to date, running {Version.current()}."

        return self.MESSAGES[outcome]

    def __announce(self, announce, message: str):
        if announce is not None:
            announce(message)
