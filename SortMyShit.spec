# -*- mode: python ; coding: utf-8 -*-
"""One build recipe for every platform, used by compile.sh and by the release workflow.

Keeping it here rather than in the pyinstaller command line is what lets the window
icon travel inside the executable, where IconProvider reads it back at startup.
"""

from sys import path as sys_path, platform

# PyInstaller runs the spec from its own entry point, where the project is not importable.
sys_path.insert(0, SPECPATH)  # noqa: F821 - injected by PyInstaller

from src.domain.entity.Version import Version  # noqa: E402

WINDOW_ICON = "src/application/assets/icon.png"
TITLE_FONT = "src/application/assets/title-font.otf"
EXECUTABLE_ICON = {
    "win32": "src/application/assets/icon.ico",
    "darwin": "src/application/assets/icon.icns",
}.get(platform, WINDOW_ICON)


def windows_version_info():
    """What Windows reads off the executable: the name and version in its properties, and
    FileDescription, which is what Task Manager lists the process under.

    An executable carrying none looks to Defender like one with something to hide, and
    SignPath refuses to sign one whose product name and version are not set, see
    .claude/recipes/icon-and-packaging.md:21. The version is the one the release workflow
    stamped, so a local build reads 0.0.0.
    """
    from PyInstaller.utils.win32.versioninfo import (
        FixedFileInfo, StringFileInfo, StringStruct, StringTable, VarFileInfo, VarStruct, VSVersionInfo,
    )

    numbers = Version.current().numbers
    version = ".".join(str(number) for number in numbers)

    return VSVersionInfo(
        ffi=FixedFileInfo(filevers=numbers + (0,), prodvers=numbers + (0,)),
        kids=[
            # 0409 04B0: US English, Unicode -- the table and the translation have to agree.
            StringFileInfo([
                StringTable("040904B0", [
                    StringStruct("FileDescription", "Sort My Shit"),
                    StringStruct("FileVersion", version),
                    StringStruct("InternalName", "SortMyShit"),
                    StringStruct("LegalCopyright", "Copyright (c) 2025 noviplex"),
                    StringStruct("OriginalFilename", "SortMyShit.exe"),
                    StringStruct("ProductName", "Sort My Shit"),
                    StringStruct("ProductVersion", version),
                ]),
            ]),
            VarFileInfo([VarStruct("Translation", [0x0409, 0x04B0])]),
        ],
    )


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
    # Only Windows has a version resource; handed one anywhere else, PyInstaller warns.
    version=windows_version_info() if platform == "win32" else None,
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
