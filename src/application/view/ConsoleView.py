from tkinter import constants as tk_constants

from src.application.component.SMSTextBox import SMSTextBox
from src.application.service.EventManager import EventManager
from src.application.service.ThemeProvider import ThemeProvider
from src.application.view.SMSView import SMSView


class ConsoleView(SMSView):
    def __init__(
        self,
        container,
        theme_provider: ThemeProvider,
        event_manager: EventManager,
    ):
        super().__init__(container, theme_provider, event_manager)

        self.create_view()

    def create_view(self):
        self.render_title("Console output", "Everything the running actions report.")
        self.render_toolbar([("Clear", self.__clear, "ghost")])
        self.render_status()

        self.output = SMSTextBox(container=self, theme=self.theme)
        self.output.grid(row=self.ROW_BODY, column=0, sticky="nsew")

        self.subscribe("output", self.__show_entry_in_main_output)

    def __show_entry_in_main_output(self, message: str):
        self.output.config(state=tk_constants.NORMAL)
        self.output.insert(tk_constants.END, message + "\n")
        self.output.see(tk_constants.END)
        self.output.config(state=tk_constants.DISABLED)

    def __clear(self):
        self.output.config(state=tk_constants.NORMAL)
        self.output.delete("1.0", tk_constants.END)
        self.output.config(state=tk_constants.DISABLED)
