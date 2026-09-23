class Donation:
    """Where a user who wants to chip in is sent.

    The handle is the one the repository already declares in .github/FUNDING.yml --
    GitHub reads that file for the Sponsor button, the Settings screen reads this class,
    and DonationTest holds the two together: a handle changed in one place and not the
    other sends half the users to a page that is not the author's. PATREON_URL is the
    second door, see .claude/recipes/application-layer.md:179.
    """

    HANDLE = "busychild77"
    URL = f"https://www.buymeacoffee.com/{HANDLE}"

    PATREON_URL = "https://www.patreon.com/c/BusyChild77"
    PATREON_CALL_TO_ACTION = "Patreon Page"

    CALL_TO_ACTION = "Buy me a coffee"
    BLURB = (
        "SortMyShit is free, has no ads and asks for nothing. If it saved you an "
        "afternoon of dragging files around, you can buy me a coffee."
    )
