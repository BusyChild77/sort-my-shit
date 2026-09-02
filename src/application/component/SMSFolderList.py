from tkinter import Frame, StringVar, filedialog
from typing import Callable

from src.application.component.SMSButton import SMSButton
from src.application.component.SMSEntry import SMSEntry
from src.application.component.SMSLabel import SMSLabel
from src.application.service.Typography import Typography
from src.domain.entity.Theme import Theme


class SMSFolderList(Frame):
    """Editable list of folders: add through a file dialog, remove per row."""

    FIELD_WIDTH = 20

    def __init__(
        self,
        container,
        theme: Theme,
        text: str,
        folders: list[str],
        on_change: Callable,
    ):
        super().__init__(master=container, background=theme.background)
        self.columnconfigure(0, weight=1)
        self.theme = theme
        self.folders = list(folders)
        self.on_change = on_change
        # Tk drops a variable that nothing references, blanking the field it feeds.
        self.folder_vars = []

        SMSLabel(
            container=self,
            text=text,
            bg=theme.background,
            fg=theme.text,
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))

        self.rows = Frame(self, background=theme.background)
        self.rows.columnconfigure(0, weight=1)
        self.rows.grid(row=1, column=0, columnspan=2, sticky="ew")

        SMSButton(
            container=self,
            theme=theme,
            text="Add a folder",
            variant="ghost",
            width=14,
            command=self.__add_folder,
        ).grid(row=2, column=0, sticky="w", pady=(8, 0))

        self.__render_rows()

    def __add_folder(self):
        folder = filedialog.askdirectory(initialdir="~/", title="Select a directory")

        if not folder or folder in self.folders:
            return

        self.folders.append(folder)
        self.__commit()

    def __remove_folder(self, folder: str):
        self.folders.remove(folder)
        self.__commit()

    def __commit(self):
        self.__render_rows()
        self.on_change(list(self.folders))

    def __render_rows(self):
        for child in list(self.rows.children.values()):
            child.destroy()

        self.folder_vars.clear()

        if not self.folders:
            SMSLabel(
                container=self.rows,
                text="No folder yet",
                bg=self.theme.background,
                fg=self.theme.muted,
                font=Typography.SMALL,
            ).grid(row=0, column=0, sticky="w")
            return

        for row, folder in enumerate(self.folders):
            self.__create_row(folder).grid(row=row, column=0, sticky="ew", pady=3)

    def __create_row(self, folder: str) -> Frame:
        """The very field the folder browser uses, read only, with the button beside it
        rather than inside — so a listed folder and a browsed one read identically."""
        row = Frame(self.rows, background=self.theme.background)
        row.columnconfigure(0, weight=1)

        folder_var = StringVar(value=folder)
        self.folder_vars.append(folder_var)

        SMSEntry(
            container=row,
            theme=self.theme,
            string_var=folder_var,
            width=self.FIELD_WIDTH,
            state="readonly",
        ).grid(row=0, column=0, sticky="ew")

        SMSButton(
            container=row,
            theme=self.theme,
            text="Remove",
            variant="ghost",
            width=8,
            command=lambda folder=folder: self.__remove_folder(folder),
        ).grid(row=0, column=1, sticky="e", padx=(10, 0))

        return row
