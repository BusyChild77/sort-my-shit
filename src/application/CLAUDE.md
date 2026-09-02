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
`create_view()`:

- `render_title(text, subtitle)` — heading
- `render_folders(settings_repository, {setting name: label})` — the folders the screen
  works on
- `render_toolbar([(label, command, variant)])` — the action buttons
- `render_status()` — the one line state, fed by the `status` event
- `render_body(empty_message)` — the scrollable result list, showing `empty_message`
  until an action fills it
- `render_results(items, create_card)` — replaces the body with one card per item, or the
  empty message when there is nothing to show
- `render_sections([create_section, …])` — setting sections laid side by side, collapsing
  to a single column when the window is too narrow

### Folders live on the screen that uses them

The folders an action works on are picked on that action's own screen, not in Settings,
which only holds the options changing *how* an action behaves. `render_folders` reads the
current value and saves on change: a list valued setting becomes an editable list, a
single folder a field with a browse button.

Two screens may share one setting — Sort files and Remove empty folders both use
`source_folders`. `SMSRenderer` therefore calls `refresh()` when a view becomes visible,
which rebuilds its folder area from the saved settings. A view that caches a folder value
anywhere else will go stale.

Long running work is triggered from a view but **lives in a domain service**. A view that
walks folders or moves files itself is in the wrong layer.

### The layout is fluid

**The window is resizable**, so nothing may be positioned at a fixed pixel width. A view
weights its single column, the body row soaks up the leftover height, and every child is
gridded `sticky="ew"` (or `"nsew"`) so it spans the room it is given. Cards, inputs and
folder rows therefore stretch with the window rather than clustering on the left. A
component that hardcodes a `width=` in pixels breaks that.

`render_sections` goes further and re-flows on `<Configure>`: it measures the widest
section and drops to a single column when two would no longer fit, rather than cutting
labels off. `SMSRenderer.WINDOW_MINIMUM_WIDTH` / `WINDOW_MINIMUM_HEIGHT` set the floor
below which the window cannot be dragged; check a change still holds up at that size.

Where a long path sits next to a badge or a button, the neighbour carries a `padx` gutter:
Tk does not clip a label to its grid cell, so the text runs underneath whatever follows it
and the gutter is what keeps the truncation readable.

### Subscribing to events

Use `self.subscribe(event_name, listener)`, never `event_manager.subscribe` directly:
`SMSView.destroy()` unsubscribes what it registered. Without that, a view destroyed by a
theme reload keeps receiving events and calls into dead widgets.

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
directory.

## Rendering (`service/SMSRenderer.py`)

Owns the window chrome: side bar, menu, keyboard shortcuts, and which view is visible.
Adding a screen means adding it to `SortMyShit.views` and to `SMSRenderer.NAVIGATION`,
where the tuple is `(view_name, label, keyboard shortcut)`.
