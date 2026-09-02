from tkinter import Frame, colorchooser
from typing import Callable

from src.application.component.SMSLabel import SMSLabel
from src.application.service.Typography import Typography
from src.domain.entity.Theme import Theme


class SMSColorPicker(Frame):
    """A color swatch that opens the system color chooser when clicked."""

    def __init__(
        self,
        container,
        theme: Theme,
        label: str,
        color: str,
        on_pick: Callable,
    ):
        super().__init__(master=container, background=theme.background)
        self.color = color
        self.on_pick = on_pick

        self.swatch = Frame(
            self,
            background=color,
            highlightbackground=theme.border,
            highlightthickness=1,
            width=46,
            height=30,
            cursor="hand2",
        )
        self.swatch.grid_propagate(0)
        self.swatch.grid(row=0, column=0, rowspan=2, sticky="w")
        self.swatch.bind("<Button-1>", lambda event: self.__pick())

        SMSLabel(
            container=self,
            text=label,
            bg=theme.background,
            fg=theme.text,
            font=Typography.BODY,
        ).grid(row=0, column=1, sticky="w", padx=(12, 0))

        self.value_label = SMSLabel(
            container=self,
            text=color,
            bg=theme.background,
            fg=theme.muted,
            font=Typography.SMALL,
        )
        self.value_label.grid(row=1, column=1, sticky="w", padx=(12, 0))

    def __pick(self):
        picked = colorchooser.askcolor(color=self.color, title="Pick a color")[1]

        if picked is None:
            return

        self.color = picked.upper()
        self.swatch.config(background=self.color)
        self.value_label.set_text(self.color)
        self.on_pick(self.color)
