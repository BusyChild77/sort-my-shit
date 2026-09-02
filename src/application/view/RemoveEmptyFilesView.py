from src.application.component.SMSFileCard import SMSFileCard
from src.application.service.EventManager import EventManager
from src.application.service.ThemeProvider import ThemeProvider
from src.application.view.SMSView import SMSView
from src.domain.service.remove.RemoveEmptyFile import RemoveEmptyFile
from src.infrastructure.repository.SettingsRepository import SettingsRepository
from src.infrastructure.repository.TmpStorageRepository import TmpStorageRepository


class RemoveEmptyFilesView(SMSView):
    STORAGE_KEY = "empty_files"

    def __init__(
        self,
        container,
        theme_provider: ThemeProvider,
        settings_repository: SettingsRepository,
        remove_empty_file: RemoveEmptyFile,
        tmp_storage_repository: TmpStorageRepository,
        event_manager: EventManager,
    ):
        self.settings_repository = settings_repository
        self.remove_empty_file = remove_empty_file
        self.tmp_storage_repository = tmp_storage_repository

        super().__init__(container, theme_provider, event_manager)

        self.create_view()

    def create_view(self):
        self.render_title(
            "Remove empty files",
            "Zero byte files found in the folder below.",
        )
        self.render_folders(self.settings_repository, {"remove_duplicates_folder": "Folder to process"})
        self.render_toolbar([
            ("Launch analysis", self.__list_empty_files, "ghost"),
            ("Run empty files removal", self.__remove_empty_files, "primary"),
        ])
        self.render_status()
        self.render_body("Launch an analysis to list the empty files found in this folder.")

    def __list_empty_files(self):
        empty_files = self.remove_empty_file.list_empty_files()

        self.render_results(
            empty_files,
            lambda empty_file: SMSFileCard(
                self.body.get_interior(),
                theme=self.theme,
                text=empty_file.full_path,
                badge="empty file",
            ),
        )

        self.tmp_storage_repository.save_one(self.STORAGE_KEY, empty_files)

    def __remove_empty_files(self):
        if not self.tmp_storage_repository.has(self.STORAGE_KEY):
            self.__list_empty_files()

        self.remove_empty_file.remove_empty_files(self.tmp_storage_repository.fetch_one(self.STORAGE_KEY))
        self.render_results([], None)
        self.tmp_storage_repository.remove_one(self.STORAGE_KEY)
