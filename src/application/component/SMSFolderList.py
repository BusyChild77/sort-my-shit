from tkinter import Frame, StringVar, filedialog
from typing import Callable

from src.application.component.SMSButton import SMSButton
from src.application.component.SMSEntry import SMSEntry
from src.application.component.SMSLabel import SMSLabel
from src.application.service.Typography import Typography
from src.domain.entity.Theme import Theme


class SMSFolderList(Frame):
    """Editable list of folders: typed or picked through a file dialog, removed per row.

    Typing matters as much as browsing. The dialog only shows what the platform already
    puts in front of it, which leaves out every folder that is not mounted where a file
    browser looks: a UNC share (\\\\server\\share), a distribution under \\\\wsl$, a
    mount point the dialog will not descend into. Those are addresses a user knows and
    can write down, and without a field there is nowhere to write them.

    Nothing typed is checked against the disk. A share that is offline right now is
    still the folder the user means, and the screens say so themselves when they run.
    """

    FIELD_WIDTH = 20
    HINT = "Pick a folder, or type a path — a network share or a mount point the browser will not show."

    def __init__(
        self,
        container,
        theme: Theme,
        text: str,
        folders: list[str],
        on_change: Callable,
    ):
        """folder_vars holds on to every field's variable: Tk drops a variable that
        nothing references, blanking the field it feeds."""
        super().__init__(master=container, background=theme.background)
        self.columnconfigure(0, weight=1)
        self.theme = theme
        self.folders = list(folders)
        self.on_change = on_change
        self.folder_vars = []
        self.typed_folder = StringVar()

        SMSLabel(
            container=self,
            text=text,
            bg=theme.background,
            fg=theme.text,
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))

        self.rows = Frame(self, background=theme.background)
        self.rows.columnconfigure(0, weight=1)
        self.rows.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.__create_entry_row().grid(row=2, column=0, columnspan=2, sticky="ew", pady=(8, 0))

        SMSLabel(
            container=self,
            text=self.HINT,
            bg=theme.background,
            fg=theme.muted,
            font=Typography.SMALL,
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(4, 0))

        self.__render_rows()

    def __create_entry_row(self) -> Frame:
        row = Frame(self, background=self.theme.background)
        row.columnconfigure(0, weight=1)

        SMSEntry(
            container=row,
            theme=self.theme,
            string_var=self.typed_folder,
            width=self.FIELD_WIDTH,
            on_submit=self.__add_typed_folder,
        ).grid(row=0, column=0, sticky="ew")

        SMSButton(
            container=row,
            theme=self.theme,
            text="Add",
            variant="ghost",
            width=6,
            command=self.__add_typed_folder,
        ).grid(row=0, column=1, sticky="e", padx=(10, 0))

        SMSButton(
            container=row,
            theme=self.theme,
            text="Browse",
            variant="ghost",
            width=8,
            command=self.__browse_folder,
        ).grid(row=0, column=2, sticky="e", padx=(10, 0))

        return row

    def __add_typed_folder(self):
        if self.__add(self.__cleaned(self.typed_folder.get())):
            self.typed_folder.set("")

    def __browse_folder(self):
        self.__add(filedialog.askdirectory(initialdir="~/", title="Select a directory"))

    def __add(self, folder: str) -> bool:
        if not folder or folder in self.folders:
            return False

        self.folders.append(folder)
        self.__commit()

        return True

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

    @staticmethod
    def __cleaned(folder: str) -> str:
        """A trailing separator is what a path pasted out of a file browser carries, and
        it is the difference between one entry in the list and two of the same folder.
        The last one is dropped unless it is the whole path, which is how a root is
        written."""
        folder = folder.strip()

        while len(folder) > 1 and folder[-1] in ("/", "\\"):
            folder = folder[:-1]

        return folder
