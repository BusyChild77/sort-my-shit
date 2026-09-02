from src.application.component.SMSComparisonCard import SMSComparisonCard
from src.application.service.EventManager import EventManager
from src.application.service.ThemeProvider import ThemeProvider
from src.application.view.SMSView import SMSView
from src.domain.service.list.ListDuplicate import ListDuplicate
from src.domain.service.remove.RemoveDuplicate import RemoveDuplicate
from src.infrastructure.repository.SettingsRepository import SettingsRepository
from src.infrastructure.repository.TmpStorageRepository import TmpStorageRepository


class RemoveDuplicatesView(SMSView):
    STORAGE_KEY = "duplicate_matches"

    def __init__(
        self,
        container,
        theme_provider: ThemeProvider,
        settings_repository: SettingsRepository,
        list_duplicates: ListDuplicate,
        duplicate_remover: RemoveDuplicate,
        tmp_storage_repository: TmpStorageRepository,
        event_manager: EventManager,
    ):
        self.settings_repository = settings_repository
        self.list_duplicates = list_duplicates
        self.duplicate_remover = duplicate_remover
        self.tmp_storage_repository = tmp_storage_repository

        super().__init__(container, theme_provider, event_manager)

        self.create_view()

    def create_view(self):
        self.render_title(
            "Remove duplicates",
            "Files are compared inside the folder below, contents first when binary comparison is on.",
        )
        self.render_folders(self.settings_repository, {"remove_duplicates_folder": "Folder to process"})
        self.render_toolbar([
            ("Launch analysis", self.__list_duplicates, "ghost"),
            ("Run duplicate removal", self.__remove_duplicates, "primary"),
        ])
        self.render_status()
        self.render_body("Launch an analysis to list the duplicates found in this folder.")

    def __list_duplicates(self):
        duplicate_matches = self.list_duplicates.list_duplicates()

        self.render_results(
            duplicate_matches,
            lambda duplicate_match: SMSComparisonCard(
                self.body.get_interior(),
                theme=self.theme,
                duplicate_match=duplicate_match,
            ),
        )

        self.tmp_storage_repository.save_one(self.STORAGE_KEY, duplicate_matches)

    def __remove_duplicates(self):
        if not self.tmp_storage_repository.has(self.STORAGE_KEY):
            self.__list_duplicates()

        self.duplicate_remover.remove_duplicates(self.tmp_storage_repository.fetch_one(self.STORAGE_KEY))
        self.render_results([], None)
        self.tmp_storage_repository.remove_one(self.STORAGE_KEY)
