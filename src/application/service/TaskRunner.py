from threading import Thread
from tkinter import TclError
from typing import Callable

from src.domain.task.CancellationInterface import CancellationInterface


class TaskRunner(CancellationInterface):
    """Runs one screen's action off the Tk thread, and answers whether it was cancelled.

    Every action here walks folders, and a folder may be a network share, a cloud drive
    or a disk inside a virtual machine. Tk is single threaded: run that in the button's
    own callback and the window stops painting for as long as the walk takes, with no
    way out of it and nothing on screen to say it is still alive.

    So the work runs in a worker and the answer is handed back through widget.after(),
    the same way UpdatePrompt hands back a download. Stopping it is cooperative: cancel()
    only sets the flag the domain services read between two files, so a run always stops
    on a whole file rather than in the middle of one.

    One at a time on purpose. Two of these screens share their folders, and two scans
    deleting out of the same folder would be reading a list the other one is emptying.
    """

    def __init__(self):
        self.running = False
        self.cancelled = False

    def is_running(self) -> bool:
        return self.running

    def is_cancelled(self) -> bool:
        return self.cancelled

    def run(self, widget, work: Callable, done: Callable, failed: Callable) -> bool:
        """False when something else is still running, and nothing was started."""
        if self.running:
            return False

        self.running = True
        self.cancelled = False

        Thread(target=lambda: self.__worked(widget, work, done, failed), daemon=True).start()

        return True

    def cancel(self):
        self.cancelled = True

    def __worked(self, widget, work: Callable, done: Callable, failed: Callable):
        try:
            result = work()
        except Exception as failure:
            # Anything at all, not only OSError: a screen left showing a disabled toolbar
            # because the worker died quietly is worse than a message saying what broke.
            # The failure is passed on as an argument, before Python unbinds the name at
            # the end of this block.
            self.__hand_back(widget, failed, failure)
            return

        self.__hand_back(widget, done, result)

    def __hand_back(self, widget, call: Callable, value):
        try:
            widget.after(0, lambda: self.__finished(call, value))
        except (TclError, RuntimeError):
            # The window went away while the work was running. There is nobody left to
            # tell, and the runner has to be freed here or it stays busy forever.
            self.running = False

    def __finished(self, call: Callable, value):
        self.running = False
        call(value)
