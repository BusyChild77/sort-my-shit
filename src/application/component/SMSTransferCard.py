from tkinter import Frame

from src.application.component.SMSLabel import SMSLabel
from src.application.service.Typography import Typography
from src.domain.entity.SortOperation import SortOperation
from src.domain.entity.Theme import Theme


class SMSTransferCard(Frame):
    """Preview row of a planned sort: where a file comes from and where it lands."""

    def __init__(
        self,
        master,
        theme: Theme,
        operation: SortOperation,
    ):
        super().__init__(
            master,
            background=theme.elevated,
            highlightbackground=theme.border,
            highlightthickness=1,
            height=62,
            padx=14,
            pady=8,
        )
        self.grid_propagate(0)
        self.columnconfigure(0, weight=1)

        SMSLabel(
            container=self,
            text=operation.source_path,
            bg=theme.elevated,
            fg=theme.text,
            font=Typography.SMALL,
        ).grid(row=0, column=0, sticky="w")

        SMSLabel(
            container=self,
            text=operation.category.upper(),
            bg=theme.elevated,
            fg=theme.accent,
            font=Typography.SMALL,
            anchor="e",
            padx=14,
        ).grid(row=0, column=1, rowspan=2, sticky="e")

        SMSLabel(
            container=self,
            text="→  " + operation.destination_path,
            bg=theme.elevated,
            fg=theme.muted,
            font=Typography.SMALL,
        ).grid(row=1, column=0, sticky="w")
