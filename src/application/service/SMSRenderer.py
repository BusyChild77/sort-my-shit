from tkinter import Tk, Frame, Menu, font as tk_font

from src.application.component.SMSSidebar import SMSSidebar
from src.application.service.EventManager import EventManager
from src.application.service.IconProvider import IconProvider
from src.application.service.ThemeProvider import ThemeProvider
from src.application.service.Typography import Typography
from src.application.view.SMSView import SMSView
from src.manager.ViewManager import ViewManager


class SMSRenderer:
    """Owns the window chrome: side bar, menu, shortcuts, and the visible view."""

    WINDOW_SIZE = "1600x900"

    # Below this the toolbars and the two folder columns start fighting for room.
    WINDOW_MINIMUM_WIDTH = 1100
    WINDOW_MINIMUM_HEIGHT = 640

    NAVIGATION = [
        ("sort_files", "Sort files", "S"),
        ("remove_duplicates", "Remove duplicates", "D"),
        ("remove_empty_files", "Remove empty files", "I"),
        ("remove_empty_folders", "Remove empty folders", "F"),
        ("console", "Console", "C"),
        ("settings", "Settings", "P"),
        ("appearance", "Appearance", "A"),
    ]

    def __init__(
        self,
        theme_provider: ThemeProvider,
        event_manager: EventManager,
        icon_provider: IconProvider,
    ):
        self.theme_provider = theme_provider
        self.event_manager = event_manager
        self.icon_provider = icon_provider
        self.current_view_name = "sort_files"

    def render(self, root: Tk, view_manager: ViewManager):
        self.root = root
        self.view_manager = view_manager

        Typography.resolve_families(tk_font.families(root))
        tk_font.nametofont("TkDefaultFont").configure(family=Typography.FAMILY, size=11)
        tk_font.nametofont("TkMenuFont").configure(family=Typography.FAMILY, size=11)

        root.title("SortMyShit")
        # True so the dialogs the views open carry the icon as well.
        root.iconphoto(True, self.icon_provider.get())
        root.geometry(self.WINDOW_SIZE)
        root.minsize(self.WINDOW_MINIMUM_WIDTH, self.WINDOW_MINIMUM_HEIGHT)
        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        self.__bind_shortcuts()
        self.event_manager.subscribe(ThemeProvider.THEME_CHANGED, self.reload)

        self.__render_chrome()

    def reload(self):
        """Rebuild every widget against the current theme, once the click that
        asked for it has been handled."""
        self.root.after_idle(self.__rebuild)

    def __rebuild(self):
        self.view_manager.unmount()
        self.chrome.destroy()
        self.__render_chrome()

    def change_view(self, name: str):
        self.current_view_name = name
        self.__hide_current_view()
        self.__set_view(self.view_manager.get(name))
        self.view.refresh()
        self.sidebar.set_active(name)

    def __render_chrome(self):
        theme = self.theme_provider.get()

        self.root.configure(bg=theme.background)
        self.root.config(menu=self.__create_menu(theme))

        self.chrome = Frame(self.root, background=theme.background)
        self.chrome.grid(row=0, column=0, sticky="nsew")
        self.chrome.rowconfigure(0, weight=1)
        self.chrome.columnconfigure(1, weight=1)

        self.sidebar = SMSSidebar(
            container=self.chrome,
            theme=theme,
            entries=self.NAVIGATION,
            on_select=self.change_view,
        )
        self.sidebar.grid(row=0, column=0, sticky="ns")

        self.content = Frame(self.chrome, background=theme.background)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.rowconfigure(0, weight=1)
        self.content.columnconfigure(0, weight=1)

        self.view = None
        self.view_manager.mount(self.content)
        self.change_view(self.current_view_name)

    def __create_menu(self, theme) -> Menu:
        menu = Menu(self.root, background=theme.surface, foreground=theme.text, borderwidth=0)

        file_menu = Menu(menu, tearoff=0, background=theme.surface, foreground=theme.text)
        file_menu.add_command(label="Settings (P)", command=lambda: self.change_view("settings"))
        file_menu.add_command(label="Appearance (A)", command=lambda: self.change_view("appearance"))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)

        actions_menu = Menu(menu, tearoff=0, background=theme.surface, foreground=theme.text)
        for view_name, label, shortcut in self.NAVIGATION[:5]:
            actions_menu.add_command(
                label=f"{label} ({shortcut})",
                command=lambda view_name=view_name: self.change_view(view_name),
            )

        menu.add_cascade(label="File", menu=file_menu)
        menu.add_cascade(label="Actions", menu=actions_menu)

        return menu

    def __bind_shortcuts(self):
        for view_name, label, shortcut in self.NAVIGATION:
            self.root.bind(
                f"<KeyPress-{shortcut.lower()}>",
                lambda event, view_name=view_name: self.change_view(view_name),
            )

    def __set_view(self, view: SMSView):
        self.view = view
        self.view.grid(row=0, column=0, sticky="nswe")

    def __hide_current_view(self):
        if self.view is not None:
            self.view.grid_forget()
