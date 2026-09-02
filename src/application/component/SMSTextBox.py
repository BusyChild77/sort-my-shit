from tkinter import Text, constants as tk_constants

from src.application.service.Typography import Typography
from src.domain.entity.Theme import Theme


class SMSTextBox(Text):
    """Read only monospaced area, sized by the grid cell it is placed in."""

    def __init__(self, container, theme: Theme):
        super().__init__(
            master=container,
            bg=theme.elevated,
            fg=theme.text,
            insertbackground=theme.text,
            selectbackground=theme.accent,
            selectforeground=theme.on_accent,
            width=1,
            height=1,
            relief="flat",
            border=0,
            borderwidth=0,
            highlightcolor=theme.border,
            highlightbackground=theme.border,
            highlightthickness=1,
            padx=14,
            pady=12,
            wrap="none",
            font=Typography.MONO,
        )

        self.config(state=tk_constants.DISABLED)
