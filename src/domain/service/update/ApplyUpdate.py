from os import path as os_path

from src.domain.entity.Release import Release
from src.domain.event.EventManagerInterface import EventManagerInterface
from src.domain.repository.InstallationRepositoryInterface import InstallationRepositoryInterface
from src.domain.repository.ReleaseRepositoryInterface import ReleaseRepositoryInterface


class ApplyUpdate:
    """Downloads the file this platform needs and puts it in place.

    Linux and Windows are swapped where they stand and the app restarts into the new
    version. macOS is downloaded and revealed instead: the bundle is neither signed nor
    notarised, so a copy replaced behind Gatekeeper's back is quarantined and refuses
    to open, which would leave the user with no working app at all.
    """

    ASSET_SUFFIX = {
        InstallationRepositoryInterface.APPIMAGE: ".AppImage",
        InstallationRepositoryInterface.WINDOWS: ".exe",
        InstallationRepositoryInterface.MACOS: ".dmg",
    }

    HANDED_OVER = "handed_over"
    REPLACED = "replaced"

    def __init__(
        self,
        release_repository: ReleaseRepositoryInterface,
        installation_repository: InstallationRepositoryInterface,
        event_manager: EventManagerInterface,
    ):
        self.release_repository = release_repository
        self.installation_repository = installation_repository
        self.event_manager = event_manager

    def apply(self, release: Release) -> str:
        """Returns REPLACED when the app is ready to restart into the new version, or
        HANDED_OVER when the download is waiting for the user to install it."""
        packaged_form = self.installation_repository.packaged_form()
        asset = release.asset_named_like(self.ASSET_SUFFIX[packaged_form])

        if asset is None:
            raise FileNotFoundError(f"{release.version} carries no file for this platform.")

        name, url = asset
        destination = os_path.join(self.installation_repository.downloads_folder(), name)

        self.event_manager.trigger("status", f"Downloading {name}...")
        downloaded = self.release_repository.download(url, destination)
        self.event_manager.trigger("output", f"Downloaded {release.version} to {downloaded}")

        if packaged_form == InstallationRepositoryInterface.MACOS:
            self.installation_repository.reveal(downloaded)
            return self.HANDED_OVER

        self.event_manager.trigger("status", f"Installing {release.version}...")
        self.installation_repository.replace_with(downloaded)
        self.event_manager.trigger("status", f"Updated to {release.version}.")

        return self.REPLACED
