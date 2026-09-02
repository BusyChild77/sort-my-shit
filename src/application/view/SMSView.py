from abc import ABC, abstractmethod
from tkinter import Frame, StringVar

from src.application.component.SMSButton import SMSButton
from src.application.component.SMSButtonContainer import SMSButtonContainer
from src.application.component.SMSFolderList import SMSFolderList
from src.application.component.SMSInputWithLabel import SMSInputWithLabel
from src.application.component.SMSLabel import SMSLabel
from src.application.component.SMSScrollableFrame import SMSScrollableFrame
from src.application.component.SMSSeparator import SMSSeparator
from src.application.service.EventManager import EventManager
from src.application.service.ThemeProvider import ThemeProvider
from src.application.service.Typography import Typography
from src.domain.repository.SettingsRepositoryInterface import SettingsRepositoryInterface


class SMSView(ABC, Frame):
    """Shared skeleton of every screen: a title, the folders it works on, a toolbar,
    a status line and a body.

    Subclasses call the render_* helpers they need from create_view().
    """

    ROW_TITLE = 0
    ROW_TITLE_RULE = 1
    ROW_FOLDERS = 2
    ROW_FOLDERS_RULE = 3
    ROW_TOOLBAR = 4
    ROW_STATUS = 5
    ROW_BODY = 6

    STATUS_MAX_LENGTH = 150
    PADDING = 32
    SECTION_GUTTER = 40

    def __init__(
        self,
        container,
        theme_provider: ThemeProvider,
        event_manager: EventManager,
    ):
        self.theme = theme_provider.get()
        self.event_manager = event_manager
        self.subscriptions = []
        self.current_state = None
        self.body = None
        self.body_empty_message = None
        self.folders = None
        self.folder_settings = {}
        self.folder_settings_repository = None
        self.sections = []
        self.sections_body = None
        self.section_columns = 0

        super().__init__(
            container,
            padx=self.PADDING,
            pady=26,
            background=self.theme.background,
        )
        self.columnconfigure(0, weight=1)
        self.rowconfigure(self.ROW_BODY, weight=1)

    @abstractmethod
    def create_view(self):
        pass

    def render_title(self, text: str, subtitle: str = None):
        header = Frame(self, background=self.theme.background)
        header.grid(row=self.ROW_TITLE, column=0, sticky="ew")

        SMSLabel(
            container=header,
            text=text,
            bg=self.theme.background,
            fg=self.theme.text,
            font=Typography.TITLE,
        ).grid(row=0, column=0, sticky="w")

        if subtitle is not None:
            SMSLabel(
                container=header,
                text=subtitle,
                bg=self.theme.background,
                fg=self.theme.muted,
                font=Typography.SMALL,
            ).grid(row=1, column=0, sticky="w", pady=(4, 0))

    def render_folders(self, settings_repository: SettingsRepositoryInterface, settings: dict):
        """The folders this screen works on, edited here rather than in the settings.

        settings maps a setting name to its label. A setting holding a list of folders
        is rendered as an editable list, a single folder as a field with a browse button.
        """
        self.folder_settings_repository = settings_repository
        self.folder_settings = settings

        # The folder area is what separates the heading from the results, so it is
        # the one bracketing the screen with its two rules. A screen without folders
        # — Settings, Appearance, Console — is a single block and gets neither.
        SMSSeparator(self, self.theme).grid(row=self.ROW_TITLE_RULE, column=0, sticky="ew", pady=(18, 0))

        self.folders = Frame(self, background=self.theme.background)
        self.folders.grid(row=self.ROW_FOLDERS, column=0, sticky="ew", pady=(18, 0))

        SMSSeparator(self, self.theme).grid(row=self.ROW_FOLDERS_RULE, column=0, sticky="ew", pady=(20, 0))

        self.__render_folder_settings()

    def refresh(self):
        """Re-read what another screen may have changed since this one was built."""
        if self.folders is None:
            return

        for child in list(self.folders.children.values()):
            child.destroy()

        self.__render_folder_settings()

    def render_toolbar(self, buttons: list) -> SMSButtonContainer:
        """buttons: a list of (label, command, variant) tuples."""
        toolbar = SMSButtonContainer(container=self, theme=self.theme, direction="horizontal")
        toolbar.set_buttons([
            SMSButton(
                container=toolbar,
                theme=self.theme,
                text=label,
                command=command,
                variant=variant,
                width=len(label) + 2,
            )
            for label, command, variant in buttons
        ])
        toolbar.grid(row=self.ROW_TOOLBAR, column=0, sticky="w", pady=(20, 14))

        return toolbar

    def render_sections(self, create_sections: list) -> Frame:
        """Lay out setting sections side by side, falling back to a single column when
        the window is too narrow to hold two without cutting their labels.

        create_sections is a list of callables taking the container and returning a section.
        """
        body = Frame(self, background=self.theme.background)
        body.grid(row=self.ROW_BODY, column=0, sticky="new", pady=(22, 0))
        body.columnconfigure(0, weight=1)

        self.sections = [create_section(body) for create_section in create_sections]
        self.sections_body = body
        self.section_columns = 0

        self.bind("<Configure>", lambda event: self.__reflow_sections())
        self.__reflow_sections()

        return body

    def render_status(self):
        self.current_state = SMSLabel(
            container=self,
            text="Idle",
            bg=self.theme.background,
            fg=self.theme.muted,
            font=Typography.SMALL,
        )
        self.current_state.grid(row=self.ROW_STATUS, column=0, sticky="ew", pady=(0, 14))

        self.subscribe("status", self.__change_current_state)

    def render_body(self, empty_message: str) -> SMSScrollableFrame:
        """The result list, filling the room left below the toolbar. Until an action
        fills it, it shows empty_message rather than a blank area."""
        self.body_empty_message = empty_message

        self.body = SMSScrollableFrame(self, self.theme)
        self.body.grid(row=self.ROW_BODY, column=0, sticky="nsew")

        self.render_results([], None)

        return self.body

    def render_results(self, items: list, create_card):
        """Replace the body with one card per item, or the empty message when there
        is nothing to show. create_card takes an item and returns the card."""
        self.body.reload()

        if not items:
            SMSLabel(
                container=self.body.get_interior(),
                text=self.body_empty_message,
                bg=self.theme.background,
                fg=self.theme.muted,
                font=Typography.SMALL,
            ).grid(row=0, column=0, sticky="w", pady=14)
            return

        for row, item in enumerate(items):
            create_card(item).grid(row=row, column=0, sticky="ew", pady=3)

    def subscribe(self, event_name: str, listener):
        """Subscribe for as long as the view lives, listeners are dropped on destroy."""
        self.event_manager.subscribe(event_name, listener)
        self.subscriptions.append((event_name, listener))

    def destroy(self):
        for event_name, listener in self.subscriptions:
            self.event_manager.unsubscribe(event_name, listener)
        self.subscriptions.clear()

        super().destroy()

    def __reflow_sections(self):
        columns = self.__section_columns_that_fit()

        if columns == self.section_columns:
            return

        self.section_columns = columns
        self.sections_body.columnconfigure(1, weight=1 if columns > 1 else 0)

        for index, section in enumerate(self.sections):
            row, column = divmod(index, columns)
            section.grid(
                row=row,
                column=column,
                sticky="new",
                padx=(0, self.SECTION_GUTTER) if columns > 1 and column == 0 else 0,
                pady=(0 if row == 0 else self.SECTION_GUTTER, 0),
            )

    def __section_columns_that_fit(self) -> int:
        widest_section = max(section.winfo_reqwidth() for section in self.sections)
        available = self.winfo_width() - 2 * self.PADDING

        return 2 if available >= 2 * widest_section + self.SECTION_GUTTER else 1

    def __render_folder_settings(self):
        for column, (setting_name, label) in enumerate(self.folder_settings.items()):
            self.folders.columnconfigure(column, weight=1, uniform="folder")
            self.__create_folder_setting(setting_name, label).grid(
                row=0, column=column, sticky="new", padx=(0, 40 if column < len(self.folder_settings) - 1 else 0)
            )

    def __create_folder_setting(self, setting_name: str, label: str) -> Frame:
        value = self.folder_settings_repository.fetch_one(setting_name)

        if isinstance(value, list):
            return SMSFolderList(
                container=self.folders,
                theme=self.theme,
                text=label,
                folders=value,
                on_change=lambda folders: self.folder_settings_repository.save_one(setting_name, folders),
            )

        setting_var = StringVar(value=value)
        setting_var.trace_add(
            "write",
            lambda name, index, mode: self.folder_settings_repository.save_one(setting_name, setting_var.get()),
        )

        return SMSInputWithLabel(
            container=self.folders,
            theme=self.theme,
            text=label,
            setting_var=setting_var,
        )

    def __change_current_state(self, text: str):
        if len(text) > self.STATUS_MAX_LENGTH:
            text = text[:self.STATUS_MAX_LENGTH - 3] + "..."

        self.current_state.set_text(text)
