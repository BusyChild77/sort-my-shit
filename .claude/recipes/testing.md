# Testing

Covers `tests/`. `unittest`, no external runner, run by CI as
`python3 -m unittest --failfast --verbose ./tests/bootstrap.py`.

## Coverage expectation

**Test coverage must always cover all critical features.** A change to one of them ships
with the tests that prove it, in the same commit. The critical features are:

- **sorting** — which file goes where, flattened vs. preserved folder tree, several source
  folders merged into one destination, name collisions, copy vs. move, and the deletion of
  source folders left empty;
- **anything that deletes or moves user data** — duplicate removal, empty file removal,
  empty folder removal — including the negative cases: what must *not* be touched. A file
  that read back nothing but has a size is one of those: it is a cloud placeholder or a
  read that failed, and deleting it loses the contents;
- **folders that may not be there** — that a folder which did not answer is skipped and
  reported rather than walked and counted as clean, that the probe gives up on its
  deadline instead of blocking, and that one file or folder failing does not stop the
  ones after it;
- **cancelling** — that a cancelled run touches nothing after the file it was on;
- **duplicate detection** — binary and filename comparison, and the large file rules;
- **settings** — persistence, defaults for a missing key, and the migration of settings
  written by an older version, and where they are written from for each packaged form of
  the app. A user must never lose their configuration on upgrade;
- **updating** — it replaces the running application, so: which asset each platform
  installs, that macOS is handed over rather than overwritten, that an unreachable GitHub
  never reads as up to date, and that a run from the sources or an unstamped build never
  updates at all.

A bug fix in any of the above starts with the failing test.

## Layout and conventions

- The tree mirrors `src/`: `tests/domain/service/SortFileTest.py` covers
  `src/domain/service/sort/SortFile.py`.
- One file per class under test, named `<ClassName>Test.py`.
- **Every test case must be imported and listed in `tests/bootstrap.py`.** A test file
  absent from it does not run in CI.
- Test names read as a sentence:
  `test_given_<situation>_when_<action>_then_<expected outcome>`.
- Domain services are tested against `Mock(SomeRepositoryInterface)` and never touch the
  disk — mock the interface, not the implementation, so the test breaks when the contract
  changes.
- Tests that do need files create them under their own folder in `tests/`, and clean up in
  `tearDown` whatever they created in `setUp`, including after a failure.
- No test depends on the order the suite runs in, or on the developer's `settings.json`.
