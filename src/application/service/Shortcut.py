class Shortcut:
    """How a navigation shortcut is bound, and how it is written on screen.

    The shortcuts were bare letters bound on the window, and a folder is typed as often
    as it is browsed: writing a path into a folder field pressed S, the binding fired on
    its way up to the window, and the screen changed under the cursor mid-word. Alt is
    what keeps a shortcut and a character apart -- Tk's own Entry bindings drop an Alt
    keypress instead of inserting it, so it reaches the window and nothing else.

    Both halves live here because they have to agree: a shortcut bound but written
    differently is one the user cannot find, and one written but not bound does nothing.
    """

    MODIFIER = "Alt"

    @classmethod
    def sequence(cls, letter: str) -> str:
        """Bound in lower case: with no Shift held, Tk reports the lower case keysym
        whatever the side bar writes beside the entry."""
        return f"<{cls.MODIFIER}-KeyPress-{letter.lower()}>"

    @classmethod
    def label(cls, letter: str) -> str:
        return f"{cls.MODIFIER}+{letter.upper()}"
