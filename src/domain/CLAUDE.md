# Domain layer

The business logic, and the only layer with no dependency on anything else in the project.

## Rules

- **No `tkinter`, no `os`/`shutil`/`open` for anything that touches user files.** Reading
  and writing goes through `FileSystemRepositoryInterface` (folders, moves, copies) or
  `FileInfoRepositoryInterface` (file contents). `os.path` is fine for pure path maths.
- Depend on the interfaces in `repository/` and `event/`, never on a class from
  `src/infrastructure` or `src/application`. That is what makes these services testable
  with a `Mock(SomeRepositoryInterface)`.
- Adding a method to a repository interface means implementing it in
  `src/infrastructure/repository/` and covering it there.

## Layout

- `entity/` — data holders only, no behaviour beyond deriving their own values.
  `Theme` is the exception and owns its color maths, because that is what a palette is.
- `event/` — the `EventManagerInterface` used to report progress.
- `repository/` — the interfaces the infrastructure layer implements.
- `service/` — one folder per verb: `compare/`, `list/`, `remove/`, `sort/`, `update/`.

## Sorting

Three collaborators, deliberately kept apart:

- `ResolveCategory` answers "which category does this file belong to", from the extension
  mapping in `Settings.default_type_mapping`.
- `PlanSort` builds the `list[SortOperation]` a sort would perform: it applies
  `preserve_folder_tree`, walks every folder in `source_folders`, skips files that are
  already inside the destination, and renames a destination that is already taken
  (`report (1).pdf`) so nothing is ever silently overwritten. **It never touches the disk**,
  which is what makes the preview in `SortFilesView` a true dry run.
- `SortFile` executes a plan: creates the destination folders, copies or moves depending
  on `keep_original_files`, then deletes source folders left empty when
  `delete_empty_source_folders` is on.

Keep that split. Anything deciding *where a file goes* belongs in `PlanSort`, anything
*doing it* belongs in `SortFile`.

## Updating

`CheckForUpdate` decides, `ApplyUpdate` executes — the same split as `PlanSort` and
`SortFile`. `look()` answers with one of `AVAILABLE`, `UP_TO_DATE`, `UNREACHABLE` or
`NOT_UPDATABLE`; collapsing the last three into "nothing to do" would tell a user with no
network that they are up to date.

`Version` compares as numbers, never as strings, so `1.0.10` beats `1.0.9`, and anything
unreadable parses to `0.0.0` — a malformed tag is never newer than what is running.

## Progress reporting

Services report through `event_manager.trigger("status", …)` for the one line state, and
`("output", …)` for the console log. Never print, never raise a dialog from here.
