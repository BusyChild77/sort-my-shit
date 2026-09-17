# Application layer

Everything tkinter. The only layer allowed to import it.

## Components (`component/`)

Reusable widgets, all prefixed `SMS`, one class per file, each subclassing a tkinter
widget. **A component takes a `Theme` and reads its colors from it** — never a raw color
string, never a hardcoded `#RRGGBB`. Fonts come from `Typography`, so a widget with an
inline `("Arial", 14)` is a bug.

Components hold no business logic: they render, and call back the `Callable` they were
given.

## Views (`view/`)

One screen per file, subclassing `SMSView`, registered under a short name in
`Main.SortMyShit.views`. Their constructor arguments are resolved by `ViewManager` from
type annotations, so a view asks for what it needs by annotating it.

`SMSView` carries the shared skeleton, and a view composes the parts it needs in
`create_view()`. A screen with a long action also asks for a `TaskRunner` and passes it
to `super().__init__`; Settings, Appearance and Console only draw, and leave it out:

- `render_title(text, subtitle)` — heading
- `render_folders(settings_repository, {setting name: label})` — the folders the screen
  works on, bracketed by the two rules that split the screen into heading, folders and
  results
- `render_toolbar([(label, command, variant)])` — the action buttons
- `render_status()` — the one line state, fed by the `status` event
- `render_body(empty_message)` — the scrollable result list, showing `empty_message`
  until an action fills it
- `render_results(items, create_card)` — shows the items as cards, one page at a time,
  or the empty message when there is nothing to show
- `render_sections([create_section, …])` — setting sections laid side by side, collapsing
  to a single column when the window is too narrow
- `run_in_background(work, done)` — runs a scan or a removal in a worker and calls `done`
  with what it returned, back on the Tk thread

### Folders live on the screen that uses them

The folders an action works on are picked on that action's own screen, not in Settings,
which only holds the options changing *how* an action behaves. `render_folders` reads the
current value and saves on change: a list valued setting becomes an editable list, a
single folder a field with a browse button.

It also draws the two `SMSSeparator` rules, above and below itself. That is why the four
action screens are split into three blocks and Settings, Appearance and Console are not:
a screen with no folder to pick is one block and asks for no rule. Adding a rule
elsewhere means gridding an `SMSSeparator` into its own row, never packing one into an
existing one.

Two screens may share one setting — Sort files and Remove empty folders both use
`source_folders`, Remove duplicates and Remove empty files both use
`remove_duplicates_folders`. `SMSRenderer` therefore calls `refresh()` when a view becomes visible,
which rebuilds its folder area from the saved settings. A view that caches a folder value
anywhere else will go stale.

Long running work is triggered from a view but **lives in a domain service**. A view that
walks folders or moves files itself is in the wrong layer.

### Results are paged, never drawn all at once

A card is a handful of widgets, and an analysis over a real folder comes back with tens of
thousands of results: building one card each is a minute of widget creation on the only
thread Tk has, with the window frozen for all of it. `render_results` therefore keeps the
whole list and builds **only the page on screen** — `Pagination` does the arithmetic and
holds no widget, so it is unit tested without a window, and `SMSPager` under the body draws
the two buttons and the range. Showing a result costs the same whether the scan found forty
files or forty thousand.

A screen that grids its own widget into `ROW_BODY` instead of calling `render_body` — the
Console does — has no pager, which is right: it has no list of results to page through.

### Actions run in a worker

**An action never runs in the button's own callback.** Its folders may be a network share
or a cloud drive, and Tk is single threaded: the window would stop painting for as long as
the walk takes, with no way out of it. The four action screens take a `TaskRunner` and go
through `run_in_background`, which disables the toolbar, leaves Cancel enabled, and hands
the result back on the Tk thread.

That splits every action in two: the half that starts the work, and the `done` half that
draws what came back. A screen whose "run" step needs an analysis first starts the analysis
in the background and calls the run from *its* result, never from a return value.

`SMSView.subscribe` registers an `EventBridge` listener rather than the one it is given,
so a service reporting from the worker never touches a widget from there. **Status is
coalesced and output is not**: a binary comparison reports a status per pair of files, and
queueing every one of those would fill the Tk queue faster than it drains, while an output
line is the record of something that happened to a file and dropping one loses it from the
console and the log.

### The layout is fluid

**The window is resizable**, so nothing may be positioned at a fixed pixel width. A view
weights its single column, the body row soaks up the leftover height, and every child is
gridded `sticky="ew"` (or `"nsew"`) so it spans the room it is given. Cards, inputs and
folder rows therefore stretch with the window rather than clustering on the left. A
component that hardcodes a `width=` in pixels breaks that.

`render_sections` goes further and re-flows on `<Configure>`: it measures the widest
section and drops to a single column when two would no longer fit, rather than cutting
labels off. It measures the **scrolled area**, not the view, since the scrollbar is part
of what a column no longer has. Its sections sit in an `SMSScrollableFrame` for the same
reason the results do: one column of them is taller than the window at its minimum height,
and a section that does not fit has to be reachable rather than cut off.
`SMSRenderer.WINDOW_MINIMUM_WIDTH` / `WINDOW_MINIMUM_HEIGHT` set the floor below which the
window cannot be dragged; check a change still holds up at that size.

Where a long path sits next to a badge or a button, the neighbour carries a `padx` gutter:
Tk does not clip a label to its grid cell, so the text runs underneath whatever follows it
and the gutter is what keeps the truncation readable.

### Subscribing to events

Use `self.subscribe(event_name, listener)`, never `event_manager.subscribe` directly:
`SMSView.destroy()` unsubscribes what it registered. Without that, a view destroyed by a
theme reload keeps receiving events and calls into dead widgets.

## Running actions (`service/TaskRunner.py`, `service/EventBridge.py`)

`TaskRunner` is one shared service and runs **one action at a time**: two of these screens
share their folders, and two scans deleting out of the same folder would be reading a list
the other is emptying. It is also the app's `CancellationInterface` — `cancel()` sets the
flag the domain services read between two files, so a run stops on a whole file rather
than being killed in the middle of one.

`EventBridge` is not a registered service. Each `SMSView` builds its own with itself as
the widget, because a bridge is only useful with a widget to hand events back through.

Both catch `RuntimeError` around `widget.after()`: Tk refuses a call from another thread
unless the main thread is inside `mainloop()`, which is exactly what happens when the
window is being torn down. There is nobody left to tell at that point, and the runner has
to free itself there or it stays busy forever.

## Theme (`service/ThemeProvider.py`)

`ThemeProvider` is the single door to the palette: `get()` returns the current `Theme`,
`save_color()` / `apply_preset()` persist a change and trigger `THEME_CHANGED`.
`SMSRenderer` listens and rebuilds the whole interface, which is why views must be
disposable and must never cache colors anywhere but in `self.theme`.

Only the five colors in `Theme.EDITABLE_COLORS` are stored. Every other shade — `border`,
`muted`, `accent_hover`, `on_accent`, `surface_hover` — is derived, so a user palette stays
coherent whatever they pick. Need a new shade? Derive it in `Theme`, do not add a setting.

## Icon (`service/IconProvider.py`)

Resolves the window icon and caches the `PhotoImage`, because Tk keeps no reference of
its own and drops an icon that gets garbage collected. `SMSRenderer` applies it with
`iconphoto(True, ...)` so the dialogs the views open carry it as well. The lookup goes
through the sources and through the PyInstaller bundle, never through the current working
directory — see the packaging section of the root `CLAUDE.md`.

`logo()` hands back the same artwork at `LOGO_SIZE`, for the side bar wordmark. Tk only
shrinks an image by keeping one pixel out of every n, so the artwork stays a square whose
side divides cleanly by that size, and the logo is cached like the icon it comes from.

## Tagline (`service/TaglineProvider.py`)

The line under the wordmark, drawn from `TAGLINES` **once per run** and held: the side bar
is rebuilt whenever the theme changes, and a line picked again on each rebuild would move
under the user. Adding a sentence is one entry in that tuple — the side bar wraps it, so
its length is free.

The side bar is the one part of the window with a width in pixels; everything it holds is
sized from `SMSSidebar.inner_width` rather than from a number of its own, so widening it
for a longer wordmark keeps the entries and the tagline in step.

## Donating (`service/Donation.py`)

The address the Support section of the Settings screen sends a user to, and the copy
written around it. The handle is also declared in `.github/FUNDING.yml`, for the Sponsor
button GitHub puts on the repository, so **the two are held together by `DonationTest`**:
nothing breaks when they drift, the users who click one of them simply land on somebody
else's page.

`Donation.PATREON_URL` is the second door, for a user who would rather give monthly than
once, and `OtherProject` is the author's other site, mentioned under both. All three read
the same: a line of copy, then the address on its own line as an `SMSLink` in the body
font. A link set apart from the others is one a user reads as something else.

`SMSLink` is what opens all three. There is no browser to open on every machine, so a
refusal is handed back to the view rather than swallowed, and the Settings screen puts the
address on the clipboard instead — the link is the whole point of the widget, and a user
has no way of copying a Tk label. The address that was clicked is the one that goes on the
clipboard, written out in full on the one line the section keeps for it, which stays out
of the layout until there is something to say.

## Updating (`service/UpdatePrompt.py`)

The one place that talks to the user about versions, shared by the startup check
(`SMSRenderer` calls `check_on_startup`) and the button on the Settings screen.

**Tk is single threaded**, so the lookup and the download run in a worker and every
widget touch is handed back through `widget.after()`. Doing the network call inline
freezes the window for as long as GitHub takes to answer.

Nothing is replaced without a `messagebox` answer first. The Settings screen passes an
`announce` callback to get the outcome as a line of text; the startup check passes none,
so it stays silent unless there is something to install.

## Desktop identity (`service/DesktopIdentity.py`)

Builds the root window, because the class name the desktop matches the launcher on can
only be given to Tk as the window is created. It sets the title too, which is why
`SMSRenderer` does not. See the desktop identity section of the root `CLAUDE.md` for what
the packaging has to repeat.

## Rendering (`service/SMSRenderer.py`)

Owns the window chrome: side bar, menu, keyboard shortcuts, and which view is visible.
Adding a screen means adding it to `SortMyShit.views` and to `SMSRenderer.NAVIGATION`,
where the tuple is `(view_name, label, shortcut letter)`. The first `ACTION_ENTRIES` of
them are what the Actions menu lists, the rest what the File menu holds.

**A shortcut is a letter held with Alt**, and both the binding and the label written beside
it come from `Shortcut` so the two cannot drift. They were bare letters once, bound on the
window: a folder is typed as often as it is browsed, and pressing S inside a folder field
sent the event up to the window and changed the screen mid-path. Tk's own `Entry` bindings
drop an Alt keypress instead of inserting it, so a shortcut now reaches the window and
nothing else. A new binding on the window has to carry a modifier for the same reason.
