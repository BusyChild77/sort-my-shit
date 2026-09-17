from tkinter import Frame
from typing import Callable

from src.application.component.SMSButton import SMSButton
from src.application.component.SMSLabel import SMSLabel
from src.application.service.Pagination import Pagination
from src.application.service.Typography import Typography
from src.domain.entity.Theme import Theme


class SMSPager(Frame):
    """The strip under a result list: the two buttons moving the page, and the range on
    screen between them. The view hides it while there is no result to page through."""

    PREVIOUS_LABEL = "Previous"
    NEXT_LABEL = "Next"

    def __init__(self, container, theme: Theme, on_change: Callable):
        super().__init__(master=container, background=theme.background)
        self.columnconfigure(1, weight=1)
        self.on_change = on_change
        self.pagination = Pagination(0)

        self.previous_button = SMSButton(
            container=self,
            theme=theme,
            text=self.PREVIOUS_LABEL,
            command=lambda: self.__step(-1),
            variant="ghost",
            width=len(self.PREVIOUS_LABEL) + 2,
        )
        self.previous_button.grid(row=0, column=0, sticky="w")

        self.summary = SMSLabel(
            container=self,
            text="",
            bg=theme.background,
            fg=theme.muted,
            font=Typography.SMALL,
            anchor="center",
        )
        self.summary.grid(row=0, column=1, sticky="ew", padx=12)

        self.next_button = SMSButton(
            container=self,
            theme=theme,
            text=self.NEXT_LABEL,
            command=lambda: self.__step(1),
            variant="ghost",
            width=len(self.NEXT_LABEL) + 2,
        )
        self.next_button.grid(row=0, column=2, sticky="e")

    def show(self, pagination: Pagination):
        self.pagination = pagination
        self.summary.set_text(pagination.summary())
        self.previous_button.config(state="normal" if pagination.has_previous() else "disabled")
        self.next_button.config(state="normal" if pagination.has_next() else "disabled")

    def __step(self, offset: int):
        self.pagination.go_to(self.pagination.page + offset)
        self.on_change()
