from src.application.component.SMSFileCard import SMSFileCard
from src.application.service.EventManager import EventManager
from src.application.service.ThemeProvider import ThemeProvider
from src.application.view.SMSView import SMSView
from src.domain.service.remove.RemoveEmptyFolder import RemoveEmptyFolder
from src.infrastructure.repository.SettingsRepository import SettingsRepository
from src.infrastructure.repository.TmpStorageRepository import TmpStorageRepository


class RemoveEmptyFoldersView(SMSView):
    STORAGE_KEY = "empty_folders"

    def __init__(
        self,
        container,
        theme_provider: ThemeProvider,
        settings_repository: SettingsRepository,
        remove_empty_folder: RemoveEmptyFolder,
        tmp_storage_repository: TmpStorageRepository,
        event_manager: EventManager,
    ):
        self.settings_repository = settings_repository
        self.remove_empty_folder = remove_empty_folder
        self.tmp_storage_repository = tmp_storage_repository

        super().__init__(container, theme_provider, event_manager)

        self.create_view()

    def create_view(self):
        self.render_title(
            "Remove empty folders",
            "Folders left empty, including folders holding only empty folders.",
        )
        self.render_folders(self.settings_repository, {"source_folders": "Folders to process"})
        self.render_toolbar([
            ("Launch analysis", self.__list_empty_folders, "ghost"),
            ("Run empty folders removal", self.__remove_empty_folders, "primary"),
        ])
        self.render_status()
        self.render_body("Launch an analysis to list the empty folders found in these folders.")

    def __list_empty_folders(self):
        empty_folders = self.remove_empty_folder.list_empty_folders()

        self.render_results(
            empty_folders,
            lambda empty_folder: SMSFileCard(
                self.body.get_interior(),
                theme=self.theme,
                text=empty_folder,
                badge="empty folder",
            ),
        )

        self.tmp_storage_repository.save_one(self.STORAGE_KEY, empty_folders)

    def __remove_empty_folders(self):
        if not self.tmp_storage_repository.has(self.STORAGE_KEY):
            self.__list_empty_folders()

        self.remove_empty_folder.remove_empty_folders(self.tmp_storage_repository.fetch_one(self.STORAGE_KEY))
        self.render_results([], None)
        self.tmp_storage_repository.remove_one(self.STORAGE_KEY)
