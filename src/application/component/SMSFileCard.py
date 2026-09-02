from tkinter import Frame

from src.application.component.SMSLabel import SMSLabel
from src.application.service.Typography import Typography
from src.domain.entity.Theme import Theme


class SMSFileCard(Frame):
    """One row of a result list: a path, optionally tagged with a short badge."""

    def __init__(
        self,
        master,
        theme: Theme,
        text: str,
        badge: str = None,
    ):
        super().__init__(
            master,
            background=theme.elevated,
            highlightbackground=theme.border,
            highlightthickness=1,
            height=44,
            padx=14,
            pady=10,
        )
        self.grid_propagate(0)
        self.columnconfigure(0, weight=1)

        SMSLabel(
            container=self,
            text=text,
            bg=theme.elevated,
            fg=theme.text,
            font=Typography.SMALL,
        ).grid(row=0, column=0, sticky="w")

        if badge is not None:
            SMSLabel(
                container=self,
                text=badge.upper(),
                bg=theme.elevated,
                fg=theme.accent,
                font=Typography.SMALL,
                anchor="e",
                padx=14,
            ).grid(row=0, column=1, sticky="e")
