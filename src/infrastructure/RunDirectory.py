from os import access as os_access, environ as os_environ, makedirs as os_makedirs, path as os_path, W_OK
from sys import argv as sys_argv, platform as sys_platform


class RunDirectory:
    """The folder the application reads and writes its own files in: settings.json,
    and the log folder next to it.

    That is the folder holding what the user launched, so the app stays portable: drop
    the executable anywhere and its settings follow it. Two packaged forms hide the
    real launcher, and one case makes that folder unusable:

    - an AppImage runs from a read only mount, and $APPIMAGE is the file that was
      actually clicked;
    - a macOS .app buries the binary under Contents/MacOS, so the bundle is what counts;
    - an executable installed system wide sits in a folder the user cannot write to,
      and the settings go to their own configuration folder instead.
    """

    APPLICATION_NAME = "SortMyShit"
    MACOS_BUNDLE_DEPTH = 3  # SortMyShit.app/Contents/MacOS/SortMyShit

    @classmethod
    def resolve(cls) -> str:
        launched_from = cls.__launched_from()

        if os_access(launched_from, W_OK):
            return launched_from

        configuration = cls.__configuration_directory()
        os_makedirs(configuration, exist_ok=True)

        return configuration

    @classmethod
    def __launched_from(cls) -> str:
        appimage = os_environ.get("APPIMAGE")

        if appimage:
            return os_path.dirname(os_path.abspath(appimage))

        executable = os_path.abspath(sys_argv[0])

        if ".app/Contents/MacOS/" in executable:
            for _ in range(cls.MACOS_BUNDLE_DEPTH):
                executable = os_path.dirname(executable)

            return os_path.dirname(executable)

        return os_path.dirname(executable)

    @classmethod
    def __configuration_directory(cls) -> str:
        if sys_platform == "win32":
            home = os_environ.get("APPDATA") or os_path.expanduser("~")
        elif sys_platform == "darwin":
            home = os_path.join(os_path.expanduser("~"), "Library", "Application Support")
        else:
            home = os_environ.get("XDG_CONFIG_HOME") or os_path.join(os_path.expanduser("~"), ".config")

        return os_path.join(home, cls.APPLICATION_NAME)
