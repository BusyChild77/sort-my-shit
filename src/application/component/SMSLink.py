from tkinter import Label
from typing import Callable
from webbrowser import Error as BrowserError, open_new_tab

from src.application.service.Typography import Typography
from src.domain.entity.Theme import Theme


class SMSLink(Label):
    """A line of text that opens a page in the browser when it is clicked.

    Underlined and set in the accent color, so it reads as a link rather than as a
    sentence that happens to react. There is no browser to open on every machine -- a
    desktop with none installed, an AppImage run from a session that exposes none -- and
    the page is the whole point of the widget, so a refusal is handed to on_failure
    instead of being swallowed.
    """

    def __init__(
        self,
        container,
        theme: Theme,
        text: str,
        url: str,
        on_failure: Callable = None,
        font: tuple = None,
    ):
        self.url = url
        self.on_failure = on_failure

        super().__init__(
            master=container,
            text=text,
            bg=theme.background,
            fg=theme.accent,
            activeforeground=theme.accent_hover,
            padx=0,
            pady=0,
            anchor="w",
            justify="left",
            cursor="hand2",
            font=(font or Typography.BODY) + ("underline",),
        )

        self.idle_fg, self.hover_fg = theme.accent, theme.accent_hover

        self.bind("<Button-1>", lambda event: self.__open())
        self.bind("<Enter>", lambda event: self.config(fg=self.hover_fg))
        self.bind("<Leave>", lambda event: self.config(fg=self.idle_fg))

    def __open(self):
        try:
            opened = open_new_tab(self.url)
        except (BrowserError, OSError):
            opened = False

        if not opened and self.on_failure is not None:
            self.on_failure(self.url)
