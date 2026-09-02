from tkinter import Frame

from src.application.component.SMSLabel import SMSLabel
from src.application.service.Typography import Typography
from src.domain.entity.DuplicateMatch import DuplicateMatch
from src.domain.entity.FileInfo import FileInfo
from src.domain.entity.Theme import Theme


class SMSComparisonCard(Frame):
    """A kept file next to the duplicates that will be removed."""

    def __init__(
        self,
        master,
        theme: Theme,
        duplicate_match: DuplicateMatch,
    ):
        super().__init__(
            master,
            background=theme.elevated,
            highlightbackground=theme.border,
            highlightthickness=1,
            padx=14,
            pady=12,
        )
        self.theme = theme
        self.columnconfigure(1, weight=1)

        self.__create_column_title("Kept file").grid(row=0, column=0, sticky="w")
        self.__create_column_title("Duplicates").grid(row=0, column=1, sticky="w", padx=(24, 0))

        self.__create_file_line(duplicate_match.duplicate_of).grid(row=1, column=0, sticky="w", pady=2)

        for row, file in enumerate(duplicate_match.files, start=1):
            self.__create_file_line(file).grid(row=row, column=1, sticky="w", padx=(24, 0), pady=2)

    def __create_column_title(self, text: str) -> SMSLabel:
        return SMSLabel(
            container=self,
            text=text,
            bg=self.theme.elevated,
            fg=self.theme.muted,
            font=Typography.SMALL,
        )

    def __create_file_line(self, file: FileInfo) -> SMSLabel:
        return SMSLabel(
            container=self,
            text=file.file_name,
            bg=self.theme.elevated,
            fg=self.theme.text,
            font=Typography.BODY,
        )
