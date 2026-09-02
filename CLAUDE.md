# SortMyShit

Desktop app (Python 3.10+ / tkinter) that tidies up folders: sorts files by type into a
destination folder, and removes duplicates, empty files and empty folders.

## Commands

```bash
python3 -m venv .virtual && . .virtual/bin/activate   # first time only
pip install -r requirements.txt
python3 Main.py                                       # run the app
python3 -m unittest --failfast --verbose ./tests/bootstrap.py   # run the tests
flake8 . --max-line-length=160 --max-complexity=10    # lint (CI runs this)
sh compile.sh                                         # build a single executable
```

## Architecture

Layered, dependencies point inwards. Wiring happens once in `Main.py`, where every
service is registered in the [pysman](https://pypi.org/project/pysman/) `ServiceManager`
and every view in `ViewManager`. Both resolve constructor dependencies from **type
annotations**, so a new dependency is declared by annotating a constructor argument and
nothing else.

```
src/domain/          pure business logic, no tkinter, no os/shutil, no I/O
  entity/            plain data holders (FileInfo, DuplicateMatch, SortOperation, Theme, Settings, Version, Release)
  event/             EventManagerInterface
  repository/        interfaces the outer layers implement
  service/           the actual behaviour (compare/, list/, remove/, sort/, update/)
src/infrastructure/  the outside world: disk access, JSON settings, log file
  repository/        implementations of the domain repository interfaces
  logger/            LogFileLogger
  RunDirectory.py    where the app reads and writes its own files
src/application/     everything tkinter
  assets/            the icon, in the three formats the platforms want
  component/         reusable widgets, all prefixed SMS
  view/              one screen each, subclasses of SMSView
  service/           EventManager, ThemeProvider, IconProvider, Typography, SMSRenderer, UpdatePrompt
src/manager/         ViewManager
tests/               mirrors src/, see tests/CLAUDE.md
```

Layer rules, in order of importance:

- **`domain` imports nothing from `application` or `infrastructure`**, and never touches
  the filesystem directly. It goes through `FileSystemRepositoryInterface` /
  `FileInfoRepositoryInterface` so the services stay unit testable.
- `infrastructure` implements domain interfaces and may import from `domain`.
- `application` may import from both, and is the only layer allowed to import `tkinter`.
- Services talk to the interface, never the implementation: annotate a constructor
  argument with `SettingsRepositoryInterface`, and let the alias in `Main.py` bind it to
  `SettingsRepository`.

## Conventions

- **One class per file, the file is named after the class** (`PascalCase.py`). No module
  holding several classes, no `utils.py`, no file that does everything: when a class
  starts covering two responsibilities, split it (`PlanSort` decides, `SortFile` executes).
- Private methods are `__prefixed`, and a method that is only a wrapper around another
  call does not deserve to exist.
- Imports are aliased when they shadow a builtin-ish name: `from os import path as os_path`.
- Views and components take a `Theme`, never raw color strings. Fonts come from
  `Typography`, never inline `("Arial", 14)` tuples.
- Progress is reported by triggering `status` and `output` events on the `EventManager`,
  never by printing.
- flake8 with `--max-line-length=160`; keep functions under a complexity of 10.
- Commits follow conventional commits: `type(scope): description`.

## Icon and packaging

The icon lives in `src/application/assets/` in three formats, all the same artwork: the
poop on a tile in the `Midnight` palette. `icon.png` is the one the running app shows, and
the only one shipped inside the executable; `icon.ico` and `icon.icns` are build inputs,
read by PyInstaller when it stamps the Windows executable and the macOS bundle.

`IconProvider` is the only place that knows where that file is. It never uses the current
working directory — the app is launched from anywhere — and it looks inside the folder
PyInstaller unpacks the bundle into when the app is compiled. **A new asset read at
runtime has to be added to `datas` in `SortMyShit.spec`**, or it will be missing from
every packaged build while still working from the sources.

`SortMyShit.spec` is the single build recipe, run both by `compile.sh` and by
`.github/workflows/release.yml`, so a local build and a released one are the same thing.
Pushing to `main` bumps the patch version, builds the AppImage, the Windows executable and
the macOS disk image, publishes the GitHub release and mirrors it to SourceForge.

## Updating

The app knows its own version through `Version.CURRENT`, which stays at `0.0.0` in the
sources and is stamped by the release workflow before PyInstaller runs. **That stamp is
what makes the updater work at all**: an unstamped build is behind every release, so
`CheckForUpdate` refuses to look rather than offering an update forever. A run from the
sources is refused for the same reason — there is no file to replace.

`CheckForUpdate.look()` returns one of four outcomes rather than a release or nothing:
`UNREACHABLE` must never be shown as `UP_TO_DATE`, or a machine with no network would be
told it is current. `ApplyUpdate` then downloads the asset whose name matches this
platform and hands it to `InstallationRepository`, which swaps the AppImage or the .exe
in place. **macOS is deliberately never overwritten**: the bundle is unsigned, so a copy
replaced behind Gatekeeper's back is quarantined and refuses to open, and the disk image
is only revealed to the user instead.

The network call and the download run on a worker thread — `UpdatePrompt` marshals every
widget touch back through `widget.after()`, because Tk is single threaded.

## Settings

`settings.json` sits next to the executable and is read through `SettingsRepository`.
**Where "next to the executable" is** is `RunDirectory`'s decision, not
`SettingsRepository`'s: an AppImage runs from a read only mount and a macOS .app hides
its binary under `Contents/MacOS`, so the folder holding what the user actually launched
is resolved there, and falls back to the platform configuration folder when it cannot be
written to. Anything that packages the app in a new way is covered by
`RunDirectoryTest`.
Defaults live in `src/domain/entity/Settings.py`; anything missing from the file falls
back to them, so adding a setting is a one line change there.

The **folder** settings are edited on the screen that uses them, through
`SMSView.render_folders`. The Settings screen holds the options that change *how* an
action behaves, and no folder at all.

Settings written by older versions are migrated on read (`SettingsRepository.__migrate`):
`folder_to_process` became the `source_folders` list, and the flat `color1`..`color4`
became the `theme` object. **When you rename or reshape a setting, add it to
`renamed_user_settings` and cover it in `SettingsRepositoryTest`** — users must never
lose their configuration on upgrade.

## Testing

`unittest`, no external runner. Every test case must be imported and listed in
`tests/bootstrap.py`, which is what CI executes.

**Test coverage must always cover all critical features.** A change to any of them lands
with the tests that prove it, in the same commit:

- sorting: which file goes where, flatten vs. preserved tree, several source folders,
  name collisions, copy vs. move, deletion of emptied source folders;
- every operation that **deletes or moves user data** — duplicate removal, empty file and
  empty folder removal — including the cases where nothing should be touched;
- duplicate detection, binary and filename comparison alike;
- settings persistence and the migration of settings written by older versions,
  including where they are written from for each packaged form of the app;
- the updater: which asset each platform installs, that macOS is never overwritten, and
  that an unreachable GitHub is never reported as up to date.

Domain services are tested against mocked repository *interfaces* and never touch the
disk. Repository implementations get their own tests using a temporary folder under
`tests/`, created and removed by `setUp`/`tearDown`.
