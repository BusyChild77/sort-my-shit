from tkinter import Frame

from src.domain.entity.Theme import Theme


class SMSButtonContainer(Frame):
    """Lays a set of buttons out as a row, as a column, or as a row wrapping onto the
    next line once `columns` of them have been placed."""

    def __init__(
        self,
        container,
        theme: Theme,
        direction: str = "horizontal",
        spacing: int = 10,
        columns: int = 0,
    ):
        """columns caps how many buttons share a line, for a row that would otherwise
        grow past the window and be cut off. 0 is no cap, and it is read for a
        horizontal container only -- a column already puts one on each line."""
        super().__init__(
            master=container,
            border=0,
            borderwidth=0,
            highlightthickness=0,
            bg=theme.background,
        )

        self.direction = direction
        self.spacing = spacing
        self.columns = columns

    def set_buttons(self, buttons: list):
        if self.direction == "vertical":
            self.__stack(buttons)
            return

        self.__line_up(buttons)

    def __stack(self, buttons: list):
        for index, button in enumerate(buttons):
            button.grid(
                row=index,
                column=0,
                sticky="w",
                pady=(0, 0 if index == len(buttons) - 1 else self.spacing),
            )

    def __line_up(self, buttons: list):
        per_line = self.columns or len(buttons)

        for index, button in enumerate(buttons):
            line, place = divmod(index, per_line)

            button.grid(
                row=line,
                column=place,
                sticky="w",
                padx=(0, 0 if place == per_line - 1 else self.spacing),
                pady=(0 if line == 0 else self.spacing, 0),
            )
