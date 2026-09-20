# Desktop identity

A window carries two names. `DesktopIdentity.NAME` — "Sort My Shit" — is the one the user
reads, in the title bar and under the icon. `DesktopIdentity.APPLICATION` is the one the
desktop matches against the launcher the app was started from, and it is the reason the
window is built in `DesktopIdentity.window()` rather than in `Main`: a class name can only
be handed to Tk as the window is created, and left alone Tk uses `Tk`, which matches no
launcher and puts the window on the dock under a second icon labelled "Tk".

**Tk title cases the class name it is given**, so what ends up in `WM_CLASS` is
`DesktopIdentity.window_class()` and not `APPLICATION` itself. That is the string
`StartupWMClass` carries in `packaging/SortMyShit.desktop`, and the two only meet on an
exact match. macOS reads the bundle rather than the window, so `NAME` is repeated as
`CFBundleName` / `CFBundleDisplayName` in `SortMyShit.spec`. **All three are held together
by `DesktopIdentityTest`** — nothing fails loudly when they drift, the app simply appears
twice on the dock. Windows is left to group by the executable itself: an explicit
AppUserModelID with no installed shortcut carrying the same one would split the window
from a pinned launcher, which is the bug being fixed here.
