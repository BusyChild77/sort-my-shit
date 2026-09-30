# Icon and packaging

The icon lives in `src/application/assets/` in three formats, all the same artwork: the
poop as one flat gold shape — no face, no shading, no outline, no background — so it
reads at 16 pixels and sits on any desktop without carrying a tile of its own.
`icon.png` is the one the running app shows, and the only one shipped inside the
executable; `icon.ico` and `icon.icns` are build inputs, read by PyInstaller when it
stamps the Windows executable and the macOS bundle.

`IconProvider` is the only place that knows where that file is. It never uses the current
working directory — the app is launched from anywhere — and it looks inside the folder
PyInstaller unpacks the bundle into when the app is compiled. **A new asset read at
runtime has to be added to `datas` in `SortMyShit.spec`**, or it will be missing from
every packaged build while still working from the sources.

`SortMyShit.spec` is the single build recipe, run both by `compile.sh` and by
`.github/workflows/release.yml`, so a local build and a released one are the same thing.
Pushing to `main` bumps the patch version, builds the AppImage, the Windows executable and
the macOS disk image, publishes the GitHub release and mirrors it to SourceForge.

## Getting the Windows executable trusted

Windows treats an unknown executable as guilty until proven otherwise, and three things in
the build exist for that alone. **The version information** — `windows_version_info()` in
the spec — puts the name and the stamped version in the file's properties. Its
`FileDescription` and `ProductName` repeat `DesktopIdentity.NAME`, held together by
`DesktopIdentityTest`, and SignPath refuses to sign an executable that leaves them empty.
**The bootloader** is compiled on the runner (`PYINSTALLER_COMPILE_BOOTLOADER`) instead of
taken prebuilt from the wheel: the prebuilt stub is shared with enough malware that
Defender flags the stub, not the app. Linux and macOS keep the prebuilt one.

**Signing** goes through SignPath Foundation, free for open source, which issues the
certificate in its own name: the publisher Windows shows is "SignPath Foundation". The
unsigned `.exe` is uploaded as an artifact of the run, SignPath fetches it, signs it and
hands it back, and the signature is checked before it is packaged. The unsigned copy is
named outside the `SortMyShit-*` pattern the release jobs download, so it is never
published. Until `SIGNPATH_API_TOKEN` (a secret) and `SIGNPATH_ORGANIZATION_ID` (a
variable) are set, signing is skipped with a warning and the release ships unsigned, as
the SourceForge mirror does. Once they are, **every release waits for a hand approval on
SignPath** — an hour at most, after which the Windows build fails and the release with it;
re-running the failed job asks again. A release on every push is an approval on every
push, which is one more reason for `[skip release]`.

Unsigned, SmartScreen keeps its reputation per file, so every release starts from zero.
Signed, the reputation belongs to the certificate and carries from one release to the next.
