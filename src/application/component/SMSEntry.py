from tkinter import Entry, StringVar, Frame

from src.application.service.Typography import Typography
from src.domain.entity.Theme import Theme


class SMSEntry(Frame):
    """Text field drawn on a padded card so it reads as a modern input."""

    def __init__(
        self,
        container,
        theme: Theme,
        string_var: StringVar,
        width: int = 50,
    ):
        super().__init__(
            master=container,
            background=theme.border,
            padx=1,
            pady=1,
        )

        self.entry = Entry(
            self,
            textvariable=string_var,
            background=theme.elevated,
            fg=theme.text,
            insertbackground=theme.text,
            disabledbackground=theme.elevated,
            readonlybackground=theme.elevated,
            selectbackground=theme.accent,
            selectforeground=theme.on_accent,
            relief="flat",
            border=0,
            borderwidth=0,
            highlightthickness=0,
            width=width,
            font=Typography.BODY,
        )
        self.entry.grid(row=0, column=0, sticky="ew", ipady=6, ipadx=8)

        self.columnconfigure(0, weight=1)
