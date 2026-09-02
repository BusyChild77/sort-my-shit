from tkinter import Button
from typing import Callable

from src.application.service.Typography import Typography
from src.domain.entity.Theme import Theme


class SMSButton(Button):
    """Flat button with a hover state. "primary" fills with the accent color,
    "ghost" stays on the surface color."""

    def __init__(
        self,
        container,
        theme: Theme,
        text: str,
        command: Callable,
        variant: str = "primary",
        width: int = 22,
        height: int = 1,
    ):
        self.idle_bg, self.hover_bg, foreground = self.__colors(theme, variant)

        super().__init__(
            master=container,
            text=text,
            background=self.idle_bg,
            fg=foreground,
            activebackground=self.hover_bg,
            activeforeground=foreground,
            disabledforeground=theme.muted,
            command=command,
            width=width,
            height=height,
            relief="flat",
            border=0,
            borderwidth=0,
            highlightthickness=0,
            cursor="hand2",
            padx=14,
            pady=8,
            font=Typography.BUTTON,
        )

        self.bind("<Enter>", lambda event: self.config(background=self.hover_bg))
        self.bind("<Leave>", lambda event: self.config(background=self.idle_bg))

    @staticmethod
    def __colors(theme: Theme, variant: str) -> tuple:
        if variant == "primary":
            return theme.accent, theme.accent_hover, theme.on_accent

        return theme.surface, theme.surface_hover, theme.text
