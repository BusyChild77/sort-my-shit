from tkinter import messagebox

from src.application.component.SMSTransferCard import SMSTransferCard
from src.application.service.EventManager import EventManager
from src.application.service.ThemeProvider import ThemeProvider
from src.application.view.SMSView import SMSView
from src.domain.service.sort.SortFile import SortFile
from src.infrastructure.repository.SettingsRepository import SettingsRepository
from src.infrastructure.repository.TmpStorageRepository import TmpStorageRepository


class SortFilesView(SMSView):
    PLAN_STORAGE_KEY = "sort_operations"

    def __init__(
        self,
        container,
        theme_provider: ThemeProvider,
        settings_repository: SettingsRepository,
        sort_files: SortFile,
        tmp_storage_repository: TmpStorageRepository,
        event_manager: EventManager,
    ):
        self.settings_repository = settings_repository
        self.sort_files = sort_files
        self.tmp_storage_repository = tmp_storage_repository

        super().__init__(container, theme_provider, event_manager)

        self.create_view()

    def create_view(self):
        self.render_title(
            "Sort files by type",
            "Files are copied or moved from every source folder into the destination folder.",
        )
        self.render_folders(self.settings_repository, {
            "source_folders": "Folders to sort",
            "destination_folder": "Destination folder",
        })
        self.render_toolbar([
            ("Preview sort", self.__preview_sort, "ghost"),
            ("Run sort", self.__run_sort, "primary"),
        ])
        self.render_status()
        self.render_body("Preview a sort to see exactly which file lands where.")

    def __preview_sort(self):
        operations = self.sort_files.plan_sort()
        self.tmp_storage_repository.save_one(self.PLAN_STORAGE_KEY, operations)
        self.__display(operations)

        return operations

    def __run_sort(self):
        operations = self.__planned_operations()

        if len(operations) == 0:
            messagebox.showinfo("Sort files", "Nothing to sort in the configured source folders.")
            return

        if not self.__confirmed(operations):
            return

        self.sort_files.sort(operations)
        self.tmp_storage_repository.remove_one(self.PLAN_STORAGE_KEY)
        self.render_results([], None)

    def __planned_operations(self) -> list:
        if self.tmp_storage_repository.has(self.PLAN_STORAGE_KEY):
            return self.tmp_storage_repository.fetch_one(self.PLAN_STORAGE_KEY)

        return self.__preview_sort()

    def __confirmed(self, operations: list) -> bool:
        if not self.settings_repository.fetch_one("preview_before_sorting"):
            return True

        action = "copied" if self.settings_repository.fetch_one("keep_original_files") else "moved"

        return messagebox.askyesno(
            "Sort files",
            f"{len(operations)} file(s) will be {action} into "
            f"{self.settings_repository.fetch_one('destination_folder')}.\n\nProceed?",
        )

    def __display(self, operations: list):
        self.render_results(
            operations,
            lambda operation: SMSTransferCard(
                self.body.get_interior(),
                theme=self.theme,
                operation=operation,
            ),
        )
