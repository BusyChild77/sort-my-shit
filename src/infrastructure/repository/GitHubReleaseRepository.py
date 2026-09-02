from json import loads as json_loads
from shutil import copyfileobj as shutil_copyfileobj
from urllib.error import URLError
from urllib.request import Request, urlopen

from src.domain.entity.Release import Release
from src.domain.entity.Version import Version
from src.domain.repository.ReleaseRepositoryInterface import ReleaseRepositoryInterface


class GitHubReleaseRepository(ReleaseRepositoryInterface):
    """Reads the published releases from the GitHub API.

    Every failure reads as "no release found": a desktop app with no network, or one
    hitting the anonymous rate limit, has to carry on rather than raise at the user.
    """

    LATEST_RELEASE_URL = "https://api.github.com/repos/BusyChild77/sort-my-shit/releases/latest"
    TIMEOUT_IN_SECONDS = 15
    USER_AGENT = "SortMyShit"

    def fetch_latest(self) -> Release:
        try:
            payload = json_loads(self.__read(self.LATEST_RELEASE_URL))
        except (URLError, OSError, ValueError, TimeoutError):
            return None

        return Release(
            version=Version(payload.get("tag_name", "")),
            assets={
                asset["name"]: asset["browser_download_url"]
                for asset in payload.get("assets", [])
                if "name" in asset and "browser_download_url" in asset
            },
            page_url=payload.get("html_url", ""),
        )

    def download(self, url: str, destination_path: str) -> str:
        with urlopen(self.__request(url), timeout=self.TIMEOUT_IN_SECONDS) as response:
            with open(destination_path, "wb") as downloaded_file:
                shutil_copyfileobj(response, downloaded_file)

        return destination_path

    def __read(self, url: str) -> str:
        with urlopen(self.__request(url), timeout=self.TIMEOUT_IN_SECONDS) as response:
            return response.read().decode("utf-8")

    def __request(self, url: str) -> Request:
        return Request(url, headers={"User-Agent": self.USER_AGENT, "Accept": "application/vnd.github+json"})
