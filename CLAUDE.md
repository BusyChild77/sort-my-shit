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
  entity/            plain data holders (FileInfo, DuplicateMatch, SortOperation, Theme, Settings)
  event/             EventManagerInterface
  repository/        interfaces the outer layers implement
  service/           the actual behaviour (compare/, list/, remove/, sort/)
src/infrastructure/  the outside world: disk access, JSON settings, log file
  repository/        implementations of the domain repository interfaces
  logger/            LogFileLogger
src/application/     everything tkinter
  component/         reusable widgets, all prefixed SMS
  view/              one screen each, subclasses of SMSView
  service/           EventManager, ThemeProvider, Typography, SMSRenderer
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

## Settings

`settings.json` sits next to the executable and is read through `SettingsRepository`.
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
- settings persistence and the migration of settings written by older versions.

Domain services are tested against mocked repository *interfaces* and never touch the
disk. Repository implementations get their own tests using a temporary folder under
`tests/`, created and removed by `setUp`/`tearDown`.
