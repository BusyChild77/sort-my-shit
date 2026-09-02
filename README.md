# SortMyShit

SortMyShit is an open-source Python project designed to help you organize and manage your files effortlessly. It provides customizable sorting rules to keep your directories clean and structured.

## Download

Every push to `main` publishes a build, on the
[GitHub releases page](https://github.com/BusyChild77/sort-my-shit/releases) and
[on SourceForge](https://sourceforge.net/projects/sortmyshit/):

| Platform | File | Notes |
| --- | --- | --- |
| Linux | `SortMyShit-<version>-x86_64.AppImage` | `chmod +x` it and run it, nothing to install |
| Windows | `SortMyShit-<version>-windows-x86_64.exe` | Single executable |
| macOS | `SortMyShit-<version>-macos-arm64.dmg` | Apple Silicon, unsigned: open it from the right click menu the first time |

## Features

- Sort files by type, from **several source folders at once**, into a single destination folder.
- **Keep the original folder tree** and sort inside each level, or flatten everything into
  one folder per category.
- **Preview every move before it happens**: the dry run lists exactly which file lands
  where, and nothing touches the disk until you confirm.
- Choose whether the source files are **kept (copied) or moved**, and whether the source
  folders left empty are deleted.
- Never overwrites: a file whose name is already taken in the destination is numbered.
- Remove duplicate files, by binary comparison or by filename, **across several folders at
  once**, so a copy sitting in another folder is found too.
- Remove empty files and empty folders, including folders holding only empty folders.
- **Customisable interface**: four built-in themes, and a color picker for each interface
  color, applied live.
- **Updates itself**: checks GitHub on startup and from a button in Settings, and installs
  the new version after asking.
- Resizable window: the layout re-flows to the size you give it.

## Installation

Clone the repository:

```bash
git clone https://github.com/noviplex/SortMyShit.git
cd SortMyShit
```

Create and use a virtual environment if needed (python3-venv required):

```bash
python3 -m venv .virtual
. .virtual/bin/activate 
```


Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the project:

```bash
python3 Main.py
```

Compile into a single executable for the platform you are on:

```bash
sh compile.sh
```

The recipe lives in `SortMyShit.spec`, which is also what the release workflow runs, so
a local build and a released one are the same thing. It picks the right icon per platform
and packs the window icon into the executable.

## Configuration

Everything is saved to `settings.json` next to the executable, as soon as you change it,
so the app stays portable: move the executable and its settings go with it. When that
folder cannot be written to — a system wide install, or the read only mount an AppImage
runs from — the settings go to the usual place for the platform instead
(`~/.config/SortMyShit`, `~/Library/Application Support/SortMyShit`, `%APPDATA%\SortMyShit`).
Settings written by an older version are migrated automatically.

**The folders each action works on are picked on that action's own screen**, so you can
change them without leaving what you are doing. Every one of them takes **as many folders
as you like**, except the sort destination — there is only one place files land:

| Folder | Picked on |
| --- | --- |
| `source_folders` | **Sort files** and **Remove empty folders** |
| `destination_folder` | **Sort files** |
| `remove_duplicates_folders` | **Remove duplicates** and **Remove empty files** |

The **Settings** screen holds the options that change how an action behaves:

| Setting | What it does |
| --- | --- |
| `preserve_folder_tree` | Mirror the source tree and sort inside each level, instead of flattening |
| `keep_original_files` | Copy instead of move, leaving the sources untouched |
| `delete_empty_source_folders` | Delete source folders left empty (only when files are moved) |
| `preview_before_sorting` | Ask for a confirmation before a sort runs |
| `binary_search` | Compare file contents rather than filenames |
| `binary_search_large_files` | Include large files in the binary comparison |
| `log_output_in_file` | Write the console output to `log/log.txt` |
| `check_for_updates_on_startup` | Look for a new release on launch and offer to install it |
| `theme` | The five interface colors, edited from the **Appearance** screen |

## Updates

**Settings → Updates** holds a *Check for updates* button, and the app also looks on its
own each launch unless you turn `check_for_updates_on_startup` off. Nothing is ever
downloaded or replaced without you saying yes.

On Linux and Windows the new version is installed over the running one and the app offers
to restart into it. On macOS the disk image is downloaded and shown in Finder for you to
drag across instead: the bundle is not signed or notarised, and a copy replaced behind
Gatekeeper's back is quarantined and refuses to open.

Running from the sources there is nothing to replace, so the check reports that and stops.

## VSCode support

Comes pre-configured to run in debugging mode with VSCode

Comes pre-configured with linting on vscode using flake8 

Comes pre-configured for testing using unittest with VSCode

## Releasing

Pushing to `main` builds the three executables, tags the next patch version, creates the
GitHub release and mirrors the files to SourceForge. Add `[skip release]` to a commit
*subject* to land a change without releasing it — only the subject line is looked at, so
a commit body can mention it freely.

The SourceForge mirror is skipped, with a warning rather than a failure, until these
repository secrets are set:

| Secret | What it is |
| --- | --- |
| `SOURCEFORGE_USER` | The SourceForge user with release rights on the project |
| `SOURCEFORGE_SSH_KEY` | The private key whose public half is on that account |
| `SOURCEFORGE_API_KEY` | Optional, used to point the download button of each platform at its own file |

## Licensing and Contrubition

See CONTRIBUTING.md and LICENSE files for more details

## Acknowledgments

Thanks to the open-source community for inspiration and support!
