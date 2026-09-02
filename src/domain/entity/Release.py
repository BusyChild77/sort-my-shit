from src.domain.entity.Version import Version


class Release:
    """A published release: the version it carries, and the file to download per platform."""

    def __init__(self, version: Version, assets: dict, page_url: str = ""):
        self.version = version
        self.assets = assets  # {file name: download url}
        self.page_url = page_url

    def asset_named_like(self, suffix: str) -> tuple:
        """(file name, download url) of the first asset whose name ends with suffix,
        or None when this release carries nothing for that platform."""
        for name, url in self.assets.items():
            if name.lower().endswith(suffix.lower()):
                return name, url

        return None
