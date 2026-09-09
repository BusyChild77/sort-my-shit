class FolderState:
    """What a folder answered when it was last looked at.

    A folder that is not there and a folder behind a mount that never answered are two
    different things, and neither of them is an empty folder. Collapsing them into
    "nothing found" tells a user whose network share has dropped that their folder is
    already clean, which is the one answer that must never be given.
    """

    READABLE = "readable"
    MISSING = "missing"
    UNREACHABLE = "unreachable"
