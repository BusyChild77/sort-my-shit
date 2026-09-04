from tkinter import Label, StringVar

from src.application.service.Typography import Typography


class SMSLabel(Label):
    def __init__(
        self,
        container,
        text: str,
        bg: str,
        fg: str,
        font: tuple = None,
        padx: int = 0,
        pady: int = 0,
        anchor: str = "w",
        wraplength: int = 0,
    ):
        self.text_variable = StringVar(container, text)

        super().__init__(
            master=container,
            bg=bg,
            fg=fg,
            textvariable=self.text_variable,
            padx=padx,
            pady=pady,
            anchor=anchor,
            justify="left",
            # 0 is Tk's own "never wrap", which is what every other label wants.
            wraplength=wraplength,
            font=font or Typography.BODY,
        )

    def set_text(self, text: str):
        self.text_variable.set(text)
        self.update_idletasks()
