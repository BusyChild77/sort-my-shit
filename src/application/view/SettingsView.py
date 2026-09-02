from tkinter import BooleanVar

from src.application.component.SMSButton import SMSButton
from src.application.component.SMSCheckButton import SMSCheckButton
from src.application.component.SMSLabel import SMSLabel
from src.application.component.SMSSection import SMSSection
from src.application.service.EventManager import EventManager
from src.application.service.ThemeProvider import ThemeProvider
from src.application.service.Typography import Typography
from src.application.service.UpdatePrompt import UpdatePrompt
from src.application.view.SMSView import SMSView
from src.domain.entity.Version import Version
from src.infrastructure.repository.SettingsRepository import SettingsRepository


class SettingsView(SMSView):
    """The options that change how an action behaves. The folders each action works on
    are picked on the action's own screen."""

    def __init__(
        self,
        container,
        theme_provider: ThemeProvider,
        settings_repository: SettingsRepository,
        update_prompt: UpdatePrompt,
        event_manager: EventManager,
    ):
        self.settings_repository = settings_repository
        self.update_prompt = update_prompt
        self.update_state = None

        super().__init__(container, theme_provider, event_manager)

        self.create_view()

    def create_view(self):
        self.render_title("Settings", "Saved as soon as you change them.")

        self.render_sections([
            self.__create_sorting_section,
            self.__create_duplicates_section,
            self.__create_general_section,
            self.__create_updates_section,
        ])

    def __create_sorting_section(self, container) -> SMSSection:
        section = SMSSection(container, self.theme, "Sort files")

        self.__check_button(
            container=section.get_body(),
            setting_name="preserve_folder_tree",
            text="Keep the original folder tree, sorting inside each level instead of flattening",
        ).grid(row=0, column=0, sticky="w")

        self.__check_button(
            container=section.get_body(),
            setting_name="keep_original_files",
            text="Keep the source files (copy instead of move)",
        ).grid(row=1, column=0, sticky="w")

        self.__check_button(
            container=section.get_body(),
            setting_name="delete_empty_source_folders",
            text="Delete source folders left empty (only when source files are moved)",
        ).grid(row=2, column=0, sticky="w")

        self.__check_button(
            container=section.get_body(),
            setting_name="preview_before_sorting",
            text="Ask for a confirmation before sorting",
        ).grid(row=3, column=0, sticky="w")

        return section

    def __create_duplicates_section(self, container) -> SMSSection:
        section = SMSSection(container, self.theme, "Remove duplicates")

        self.__check_button(
            container=section.get_body(),
            setting_name="binary_search",
            text="Binary comparison (if disabled, will do a filename comparison instead)",
        ).grid(row=0, column=0, sticky="w")

        self.__check_button(
            container=section.get_body(),
            setting_name="binary_search_large_files",
            text="Enable binary comparison for large files (warning: may crash on large files)",
        ).grid(row=1, column=0, sticky="w")

        return section

    def __create_general_section(self, container) -> SMSSection:
        section = SMSSection(container, self.theme, "General")

        self.__check_button(
            container=section.get_body(),
            setting_name="log_output_in_file",
            text="Log output in logfile",
        ).grid(row=0, column=0, sticky="w")

        return section

    def __create_updates_section(self, container) -> SMSSection:
        section = SMSSection(container, self.theme, "Updates")

        self.__check_button(
            container=section.get_body(),
            setting_name="check_for_updates_on_startup",
            text="Check for a new version on startup, and offer to install it",
        ).grid(row=0, column=0, sticky="w")

        SMSButton(
            container=section.get_body(),
            theme=self.theme,
            text="Check for updates",
            command=self.__check_for_updates,
            variant="ghost",
            width=len("Check for updates") + 2,
        ).grid(row=1, column=0, sticky="w", pady=(10, 0))

        self.update_state = SMSLabel(
            container=section.get_body(),
            text=f"Running {Version.current()}.",
            bg=self.theme.background,
            fg=self.theme.muted,
            font=Typography.SMALL,
        )
        self.update_state.grid(row=2, column=0, sticky="w", pady=(6, 0))

        return section

    def __check_for_updates(self):
        self.update_prompt.check(self, announce=self.__announce_update)

    def __announce_update(self, message: str):
        # The section is rebuilt on a theme change, so the label may be gone by the time
        # a check started before it comes back with an answer.
        if self.update_state is not None and self.update_state.winfo_exists():
            self.update_state.set_text(message)

    def __check_button(self, container, setting_name: str, text: str) -> SMSCheckButton:
        boolean_var = BooleanVar(value=self.settings_repository.fetch_one(setting_name))

        return SMSCheckButton(
            container=container,
            theme=self.theme,
            text=text,
            variable=boolean_var,
            command=lambda: self.settings_repository.save_one(setting_name, boolean_var.get()),
        )
