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
  entity/            plain data holders (FileInfo, DuplicateMatch, SortOperation, Theme, Settings, Version, Release, FolderState)
  event/             EventManagerInterface
  task/              CancellationInterface
  repository/        interfaces the outer layers implement
  service/           the actual behaviour (compare/, folder/, list/, remove/, sort/, update/)
src/infrastructure/  the outside world: disk access, JSON settings, log file
  repository/        implementations of the domain repository interfaces
  logger/            LogFileLogger
  RunDirectory.py    where the app reads and writes its own files
src/application/     everything tkinter
  assets/            the icon, in the three formats the platforms want
  component/         reusable widgets, all prefixed SMS
  view/              one screen each, subclasses of SMSView
  service/           EventManager, EventBridge, TaskRunner, ThemeProvider, IconProvider, Typography, Pagination, Shortcut, SMSRenderer, UpdatePrompt
src/manager/         ViewManager
tests/               mirrors src/, one <ClassName>Test.py per class
.claude/recipes/     the detail behind each area, read on demand — see below
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

## Recipes

The detail lives in `.claude/recipes/`, one file per area. This file is the whole of what
always applies; **read the recipe for the area you are about to touch** before changing it.

| Read this | Before |
| --- | --- |
| [domain-layer.md](.claude/recipes/domain-layer.md) | touching `src/domain/` — sorting, duplicate detection, removal, cancelling, progress reporting, and why a folder that did not answer is never an empty one |
| [application-layer.md](.claude/recipes/application-layer.md) | touching `src/application/` — views, components, the worker every action runs in, paging, theming, the side bar and the window chrome |
| [infrastructure-layer.md](.claude/recipes/infrastructure-layer.md) | touching `src/infrastructure/` — what each repository is allowed to do, and `RunDirectory` |
| [testing.md](.claude/recipes/testing.md) | writing or changing a test — the coverage that is not negotiable, the naming, and `tests/bootstrap.py` |
| [settings.md](.claude/recipes/settings.md) | adding, renaming or reshaping a setting — migration is what keeps users from losing their configuration |
| [non-local-folders.md](.claude/recipes/non-local-folders.md) | anything to do with cloud drives, network shares, mapped drives or WSL paths |
| [updating.md](.claude/recipes/updating.md) | touching the updater — what each platform installs, and why macOS is never overwritten |
| [icon-and-packaging.md](.claude/recipes/icon-and-packaging.md) | adding an asset read at runtime, or changing `SortMyShit.spec` / the release workflow |
| [desktop-identity.md](.claude/recipes/desktop-identity.md) | changing the window title, the class name, the `.desktop` file or the bundle names |
| [fonts.md](.claude/recipes/fonts.md) | swapping the title font, or adding a heading — the face draws capitals and nothing else |
