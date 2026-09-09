from abc import ABC, abstractmethod


class CancellationInterface(ABC):
    """Asked between two files by anything looping over user data, so a run started from
    a screen can be stopped without waiting for it to reach the end.

    Cancellation is cooperative on purpose: a service is never killed, it checks and
    stops before the next file, so a run is never interrupted with a copy half written
    or a folder half emptied.
    """

    @abstractmethod
    def is_cancelled(self) -> bool:
        pass
