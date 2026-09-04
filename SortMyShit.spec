# -*- mode: python ; coding: utf-8 -*-
"""One build recipe for every platform, used by compile.sh and by the release workflow.

Keeping it here rather than in the pyinstaller command line is what lets the window
icon travel inside the executable, where IconProvider reads it back at startup.
"""

from sys import platform

WINDOW_ICON = "src/application/assets/icon.png"
TITLE_FONT = "src/application/assets/title-font.otf"
EXECUTABLE_ICON = {
    "win32": "src/application/assets/icon.ico",
    "darwin": "src/application/assets/icon.icns",
}.get(platform, WINDOW_ICON)

analysis = Analysis(  # noqa: F821 - injected by PyInstaller
    ["Main.py"],
    # Only the window icon and the title font are read at runtime; the .ico and .icns
    # are build inputs.
    datas=[
        (WINDOW_ICON, "src/application/assets"),
        (TITLE_FONT, "src/application/assets"),
    ],
)

executable = EXE(  # noqa: F821 - injected by PyInstaller
    PYZ(analysis.pure),  # noqa: F821 - injected by PyInstaller
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    name="SortMyShit",
    console=False,
    icon=EXECUTABLE_ICON,
)

if platform == "darwin":
    BUNDLE(  # noqa: F821 - injected by PyInstaller
        executable,
        name="SortMyShit.app",
        icon=EXECUTABLE_ICON,
        bundle_identifier="io.github.busychild77.sortmyshit",
        info_plist={
            # What the Dock and the menu bar read. Left out they fall back to the
            # name of the bundle, and the application is listed as "SortMyShit".
            # DesktopIdentity.NAME is the same string, kept so by DesktopIdentityTest.
            "CFBundleName": "Sort My Shit",
            "CFBundleDisplayName": "Sort My Shit",
            "NSHighResolutionCapable": True,
        },
    )
