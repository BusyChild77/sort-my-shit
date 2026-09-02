from src.domain.entity.Version import Version
from src.domain.repository.InstallationRepositoryInterface import InstallationRepositoryInterface
from src.domain.repository.ReleaseRepositoryInterface import ReleaseRepositoryInterface


class CheckForUpdate:
    """Decides whether the running build is behind the latest release."""

    AVAILABLE = "available"
    UP_TO_DATE = "up_to_date"
    UNREACHABLE = "unreachable"
    NOT_UPDATABLE = "not_updatable"

    def __init__(
        self,
        release_repository: ReleaseRepositoryInterface,
        installation_repository: InstallationRepositoryInterface,
    ):
        self.release_repository = release_repository
        self.installation_repository = installation_repository

    def look(self) -> tuple:
        """(outcome, release), the release being set only when the outcome is AVAILABLE.

        Four outcomes rather than a release or nothing: a machine with no network must
        never be told it is up to date, which is what it would hear if a failed lookup
        and a current version answered the same thing.
        """
        if not self.is_updatable():
            return self.NOT_UPDATABLE, None

        latest = self.release_repository.fetch_latest()

        if latest is None:
            return self.UNREACHABLE, None

        if not latest.version.is_newer_than(Version.current()):
            return self.UP_TO_DATE, None

        return self.AVAILABLE, latest

    def is_updatable(self) -> bool:
        """Run from the sources there is no file to replace, and an unstamped build has
        no version to compare — both would otherwise see every release as newer."""
        return (
            self.installation_repository.packaged_form() != InstallationRepositoryInterface.SOURCES
            and not Version.current().is_development()
        )
