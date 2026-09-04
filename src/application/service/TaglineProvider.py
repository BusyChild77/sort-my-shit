from random import choice


class TaglineProvider:
    """The line under the side bar wordmark.

    There is no single one: a tagline is drawn from the list below, once, when the
    application starts -- and held from then on, so changing the theme or walking
    through the screens rebuilds the side bar without the line moving under the user.
    """

    TAGLINES = (
        "from shit to neat",
        "clean up your mess",
        "arbor fasciculorum sana in computatro sano",
        "no more excuses.",
        "oh, I forgot about this pic",
        "sorting your crap since 2025",
        "can it get any messier?",
    )

    def __init__(self):
        self.tagline = None

    def get(self) -> str:
        if self.tagline is None:
            self.tagline = choice(self.TAGLINES)

        return self.tagline
