from threading import Lock
from tkinter import TclError
from typing import Callable


class EventBridge:
    """Hands an event triggered off the Tk thread back to it, for one view.

    A screen's action runs in a worker so the window keeps painting, and the services
    behind it report their progress as they go. Every listener on the other end draws
    something — the status line, the console — and Tk may only be touched from the
    thread running its loop, so nothing is called where it was triggered.

    Status is coalesced, output is not. A binary comparison reports a status per pair of
    files, which is a message per comparison and squarely more of them than there are
    files; queueing every one of them would fill the Tk queue faster than it drains and
    hand back the freeze this is here to avoid. Only the last of those is worth drawing.
    An output line is the record of something that happened to a file, and dropping one
    would lose it from the console and from the log.
    """

    COALESCED = ("status",)

    def __init__(self, widget):
        self.widget = widget
        self.latest = {}
        self.queued = []
        self.scheduled = False
        self.lock = Lock()

    def listener_for(self, event_name: str, listener: Callable) -> Callable:
        """The listener to subscribe in place of the real one."""
        return lambda *args, **kwargs: self.__queue(event_name, listener, args, kwargs)

    def __queue(self, event_name: str, listener: Callable, args: tuple, kwargs: dict):
        with self.lock:
            if event_name in self.COALESCED:
                self.latest[(event_name, listener)] = (args, kwargs)
            else:
                self.queued.append((listener, args, kwargs))

            if self.scheduled:
                return

            self.scheduled = True

        try:
            self.widget.after(0, self.__flush)
        except (TclError, RuntimeError):
            self.scheduled = False

    def __flush(self):
        with self.lock:
            self.scheduled = False
            queued, self.queued = self.queued, []
            latest, self.latest = self.latest, {}

        if not self.widget.winfo_exists():
            return

        for listener, args, kwargs in queued:
            listener(*args, **kwargs)

        for (event_name, listener), (args, kwargs) in latest.items():
            listener(*args, **kwargs)
