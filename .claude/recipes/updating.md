# Updating

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
