# Settings

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
`folder_to_process` became the `source_folders` list, `remove_duplicates_folder` became
the `remove_duplicates_folders` list, and the flat `color1`..`color4` became the `theme`
object. A setting listed in `Settings.folder_list_user_settings` is coerced from the
single string it used to be, so reshaping a folder setting into a list means adding it
there as well as to `renamed_user_settings`. **When you rename or reshape a setting, add it to
`renamed_user_settings` and cover it in `SettingsRepositoryTest`** — users must never
lose their configuration on upgrade.
