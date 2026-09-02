from tkinter import Frame

from src.domain.entity.Theme import Theme


class SMSButtonContainer(Frame):
    def __init__(
        self,
        container,
        theme: Theme,
        direction: str = "horizontal",
        spacing: int = 10,
    ):
        super().__init__(
            master=container,
            border=0,
            borderwidth=0,
            highlightthickness=0,
            bg=theme.background,
        )

        self.direction = direction
        self.spacing = spacing

    def set_buttons(self, buttons: list):
        for index, button in enumerate(buttons):
            is_last = index == len(buttons) - 1
            gap = 0 if is_last else self.spacing

            button.grid(
                row=index if self.direction == "vertical" else 0,
                column=index if self.direction == "horizontal" else 0,
                sticky="w",
                padx=(0, gap) if self.direction == "horizontal" else 0,
                pady=(0, gap) if self.direction == "vertical" else 0,
            )
