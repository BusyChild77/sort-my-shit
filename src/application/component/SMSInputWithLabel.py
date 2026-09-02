from tkinter import Frame, StringVar, filedialog

from src.application.component.SMSButton import SMSButton
from src.application.component.SMSEntry import SMSEntry
from src.application.component.SMSLabel import SMSLabel
from src.domain.entity.Theme import Theme


class SMSInputWithLabel(Frame):
    """A labelled folder field with a browse button."""

    def __init__(
        self,
        container,
        theme: Theme,
        text: str,
        setting_var: StringVar,
        width: int = 20,
    ):
        super().__init__(master=container, background=theme.background)
        self.columnconfigure(0, weight=1)

        SMSLabel(
            container=self,
            bg=theme.background,
            fg=theme.text,
            text=text,
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))

        SMSEntry(
            container=self,
            theme=theme,
            string_var=setting_var,
            width=width,
        ).grid(row=1, column=0, sticky="ew")

        SMSButton(
            container=self,
            theme=theme,
            text="Browse",
            variant="ghost",
            width=8,
            command=lambda: self.__browse(setting_var),
        ).grid(row=1, column=1, sticky="e", padx=(10, 0))

    @staticmethod
    def __browse(setting_var: StringVar):
        folder = filedialog.askdirectory(initialdir="~/", title="Select a directory")

        if folder:
            setting_var.set(folder)
