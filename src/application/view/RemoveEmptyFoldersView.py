from src.application.component.SMSFileCard import SMSFileCard
from src.application.service.EventManager import EventManager
from src.application.service.TaskRunner import TaskRunner
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
        task_runner: TaskRunner,
    ):
        self.settings_repository = settings_repository
        self.remove_empty_folder = remove_empty_folder
        self.tmp_storage_repository = tmp_storage_repository

        super().__init__(container, theme_provider, event_manager, task_runner)

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
        self.run_in_background(self.remove_empty_folder.list_empty_folders, self.__listed)

    def __listed(self, empty_folders: list):
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
        if self.tmp_storage_repository.has(self.STORAGE_KEY):
            self.__remove(self.tmp_storage_repository.fetch_one(self.STORAGE_KEY))
            return

        self.run_in_background(self.remove_empty_folder.list_empty_folders, self.__listed_then_remove)

    def __listed_then_remove(self, empty_folders: list):
        self.__listed(empty_folders)
        self.__remove(empty_folders)

    def __remove(self, empty_folders: list):
        self.run_in_background(
            lambda: self.remove_empty_folder.remove_empty_folders(empty_folders),
            self.__removed,
        )

    def __removed(self, result):
        self.render_results([], None)
        self.tmp_storage_repository.remove_one(self.STORAGE_KEY)
