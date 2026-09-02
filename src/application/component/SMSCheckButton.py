from tkinter import Checkbutton

from src.application.service.Typography import Typography
from src.domain.entity.Theme import Theme


class SMSCheckButton(Checkbutton):
    def __init__(
        self,
        container,
        theme: Theme,
        text: str,
        variable,
        command,
        padx: int = 0,
        pady: int = 6,
    ):
        super().__init__(
            container,
            text=text,
            variable=variable,
            command=command,
            background=theme.background,
            activebackground=theme.background,
            fg=theme.text,
            activeforeground=theme.text,
            selectcolor=theme.elevated,
            border=0,
            borderwidth=0,
            highlightthickness=0,
            anchor="w",
            cursor="hand2",
            padx=padx,
            pady=pady,
            font=Typography.BODY,
        )
