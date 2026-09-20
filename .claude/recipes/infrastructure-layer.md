# Infrastructure layer

Covers `src/infrastructure/`. Where the outside world is allowed in: the filesystem,
`settings.json`, the log file.

## Rules

- Every class here implements a `…Interface` from `src/domain/repository/`, and is bound
  to it by an alias in `Main.py`. Adding a repository means adding the interface in the
  domain first.
- Keep these classes dumb: they read, write, move and list. Any decision — which file
  goes where, what counts as a duplicate — belongs to a domain service.
- These are the classes that actually delete user data. They get their own tests against
  a temporary folder under `tests/`, created and removed in `setUp`/`tearDown`.

## Repositories

- `FileSystemRepository` — folders, moves and copies (`shutil`), and the listing of empty
  folders. `list_empty_folders` returns folders **children first** and reports a folder
  whose only content is empty folders, so removing the list in order works in one pass.
  `probe_folder` is the odd one: a stat on a share whose server has gone does not fail,
  it blocks, for as long as the kernel allows. So it runs the stat in a daemon worker and
  answers `UNREACHABLE` when the deadline passes rather than waiting. The worker is left
  behind rather than joined — there is nothing to wait for, and it must never be what
  keeps the app from closing.
- `FileInfoRepository` — reads file contents into `FileInfo`, and deletes files. It is
  the one that applies the large file and empty file skipping rules. **A file that cannot
  be read is dropped, never handed on half filled**: what reads these is what deletes
  them, and a file whose contents never arrived is indistinguishable from an empty one
  once it is in the list.
- `SettingsRepository` — `settings.json` next to the executable. `fetch_all` fills in
  missing keys from `Settings.default_user_settings` and migrates settings written by
  older versions; see [settings.md](settings.md) before renaming one.
- `TmpStorageRepository` — in memory hand off between a view's "analyse" and "run" steps.
  Not persistence, do not make it one.
- `GitHubReleaseRepository` — the releases feed and the download. **Every failure returns
  `None`** rather than raising: no network is the normal case for a desktop app, not an
  error to shout about.
- `InstallationRepository` — what the running copy is, and how to swap it. Each platform
  defends its executable differently: an AppImage is the file `$APPIMAGE` points at,
  Windows refuses to *delete* a running `.exe` but allows *renaming* it, so the outgoing
  version is moved to `.old` and swept up by the next update.

## RunDirectory

Not a repository, and the exception to the rule above: it implements no interface because
the domain has no say in it. It answers one question — which folder the app reads and
writes its own files in — and `Main.py` hands the answer to `SettingsRepository.runDir`.
The packaged forms are what make it non trivial: an AppImage mount is read only, a macOS
.app buries its binary, and a system wide install is not writable. Package the app a new
way, and this is the class to extend, with a case in `RunDirectoryTest`.
