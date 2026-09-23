# Domain layer

Covers `src/domain/`. The business logic, and the only layer with no dependency on
anything else in the project.

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
- `task/` — the `CancellationInterface` a long run is stopped through.
- `repository/` — the interfaces the infrastructure layer implements.
- `service/` — one folder per verb: `compare/`, `folder/`, `list/`, `remove/`, `sort/`,
  `update/`.

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

## Folders that may not be there

A folder here is a path and nothing else, and the path may be a cloud drive, a network
share or a disk inside a virtual machine. All three go away without warning, and a walk
over one that has gone finds nothing — which is exactly what a folder with nothing in it
looks like. **Every service that walks user folders asks `CheckFolder.readable()` first**
and works on what it hands back, so a share that dropped is reported and skipped rather
than counted as clean. `CheckFolder.warning()` goes on the end of the count a service
reports, because the status line is where a user would otherwise read "0 found" as "all
tidy". A destination is a different question and asks `reachable()`: one that is not
there yet is created on the way, one behind a mount that says nothing is not.

`FolderState` keeps `MISSING` and `UNREACHABLE` apart for the same reason `CheckForUpdate`
keeps `UNREACHABLE` out of `UP_TO_DATE`.

## Failing one file at a time

**A single file may fail without ending the run.** Every copy, move and delete is wrapped,
the failure goes out on `output`, the loop carries on, and the closing status says how
many could not be done. A share that drops halfway through costs the files it took with
it and nothing else; raising instead leaves the work half finished and says nothing about
how far it got.

`RemoveEmptyFile` is the one to be most careful with: **the recorded size and the bytes
read back both have to say a file is empty** before it is offered up. A cloud placeholder
and a read that failed both hand back nothing for a file that is not empty, and this is
the service that deletes them. It asks again at removal time, because a file listed
minutes ago may have been written to since.

## Duplicate detection

`CompareBinary` and `CompareFileName` never compare two files: each takes the whole list
and hands back groups of files that match, the first one listed being the one kept.
`CompareBinary` goes cheapest test first — size, then the first bytes already read, then
a digest streamed by `FileInfoRepository.fetch_digest` — so a file is only read when
another one agrees with it on both, and then once. `ListDuplicate` drops a path listed
twice before grouping: two folders picked one inside the other list the same file twice,
and a file grouped with itself is the only copy deleted.

## Cancelling

Anything looping over user data takes a `CancellationInterface` and checks it between two
files. It is cooperative: a service is never killed, so a run always stops on a whole file
rather than in the middle of one. `CompareBinary` checks it before reading each file as
well — reading a file whole is what takes minutes over a share. A cancelled sort returns before deleting emptied source folders: half a
sort leaves files behind, and the folders holding them are not empty.

## Progress reporting

Services report through `event_manager.trigger("status", …)` for the one line state, and
`("output", …)` for the console log. Never print, never raise a dialog from here.
