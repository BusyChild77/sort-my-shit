from tkinter import Frame
from typing import Callable

from src.application.component.SMSLabel import SMSLabel
from src.application.service.Typography import Typography
from src.domain.entity.Theme import Theme


class SMSSidebar(Frame):
    """Left hand navigation. One entry per view, the active one is highlighted."""

    def __init__(
        self,
        container,
        theme: Theme,
        entries: list,
        on_select: Callable,
        width: int = 250,
    ):
        super().__init__(master=container, background=theme.surface, width=width, padx=16, pady=22)
        self.grid_propagate(0)
        self.theme = theme
        self.on_select = on_select
        self.buttons = {}

        SMSLabel(
            container=self,
            text=Typography.in_title_case("SortMyShit"),
            bg=theme.surface,
            fg=theme.text,
            font=Typography.TITLE,
        ).grid(row=0, column=0, sticky="w")

        SMSLabel(
            container=self,
            text="Tidy up your folders",
            bg=theme.surface,
            fg=theme.muted,
            font=Typography.SMALL,
        ).grid(row=1, column=0, sticky="w", pady=(0, 22))

        for row, (view_name, label, shortcut) in enumerate(entries, start=2):
            button = self.__create_entry(view_name, label, shortcut)
            button.grid(row=row, column=0, sticky="ew", pady=2)
            self.buttons[view_name] = button

    def set_active(self, view_name: str):
        for name, entry in self.buttons.items():
            is_active = name == view_name
            background = self.theme.accent if is_active else self.theme.surface

            entry.config(background=background)
            entry.label.config(background=background, fg=self.theme.on_accent if is_active else self.theme.text)
            entry.shortcut.config(background=background, fg=self.theme.on_accent if is_active else self.theme.muted)

    def __create_entry(self, view_name: str, label: str, shortcut: str) -> Frame:
        entry = Frame(self, background=self.theme.surface, width=218, height=42, padx=12, cursor="hand2")
        entry.grid_propagate(0)
        entry.columnconfigure(0, weight=1)

        entry.label = SMSLabel(
            container=entry,
            text=label,
            bg=self.theme.surface,
            fg=self.theme.text,
            font=Typography.BODY,
        )
        entry.label.grid(row=0, column=0, sticky="w", pady=10)

        entry.shortcut = SMSLabel(
            container=entry,
            text=shortcut,
            bg=self.theme.surface,
            fg=self.theme.muted,
            font=Typography.SMALL,
            anchor="e",
        )
        entry.shortcut.grid(row=0, column=1, sticky="e")

        for widget in [entry] + list(entry.children.values()):
            widget.bind("<Button-1>", lambda event, name=view_name: self.on_select(name))

        return entry
