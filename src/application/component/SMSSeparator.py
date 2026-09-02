from tkinter import Frame

from src.domain.entity.Theme import Theme


class SMSSeparator(Frame):
    """A one pixel rule, breaking a screen into the parts it is made of."""

    def __init__(self, container, theme: Theme):
        super().__init__(master=container, background=theme.border, height=1, bd=0)
