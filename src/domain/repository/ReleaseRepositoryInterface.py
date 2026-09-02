from abc import ABC, abstractmethod

from src.domain.entity.Release import Release


class ReleaseRepositoryInterface(ABC):
    @abstractmethod
    def fetch_latest(self) -> Release:
        """The most recent published release, or None when it cannot be read.

        A machine with no network is the normal case, not an error: the app must
        carry on as if it were up to date.
        """

    @abstractmethod
    def download(self, url: str, destination_path: str) -> str:
        """Fetch url into destination_path and return the path actually written."""
