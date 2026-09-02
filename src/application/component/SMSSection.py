from tkinter import Frame

from src.application.component.SMSLabel import SMSLabel
from src.application.service.Typography import Typography
from src.domain.entity.Theme import Theme


class SMSSection(Frame):
    """Titled block of settings: a heading, a rule, and a body to grid rows into."""

    def __init__(self, container, theme: Theme, title: str):
        super().__init__(master=container, background=theme.background)
        self.columnconfigure(0, weight=1)

        SMSLabel(
            container=self,
            text=title.upper(),
            bg=theme.background,
            fg=theme.muted,
            font=Typography.SECTION,
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        Frame(self, bg=theme.border, height=1, bd=0).grid(row=1, column=0, sticky="ew")

        self.body = Frame(self, background=theme.background, pady=10)
        self.body.columnconfigure(0, weight=1)
        self.body.grid(row=2, column=0, sticky="ew")

    def get_body(self) -> Frame:
        return self.body
