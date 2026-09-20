# Fonts

Every family is picked once by `Typography.resolve_families`, from the first name in a
preferred list that Tk reports as installed. Body text takes `PREFERRED_FAMILIES`, the
console `PREFERRED_MONO_FAMILIES`, and the **titles** — the side bar wordmark and every
screen's heading, both `Typography.TITLE` — take `PREFERRED_TITLE_FAMILIES`. Views and
components never name a family: they take `Typography.TITLE`, `BODY`, `MONO`, so a change
here reaches every screen.

The titles are the one face the app ships: `assets/title-font.otf`, at the head of that
list.
Tk offers no way to load a font from a file, so `FontProvider` hands it to the platform's
own font manager first — for this process only, nothing is installed on the machine — and
`SMSRenderer` calls it **before** `Typography.resolve_families` reads the family list.
Registration is allowed to fail: the rest of the list is then what the titles are set in,
a monospace, Consolas where there is one, so no screen is left without a title. The font
is in `datas`, and **a font file swapped for another has to have `FontProvider.FAMILIES`
swapped with it** — the names in the file are what Tk is asked for, and
`FontProviderTest` reads them back out of the file to prove the two still agree.

**That face draws capitals and nothing else**, which is why every heading goes through
`Typography.in_title_case` — the side bar wordmark included — rather than being written
in capitals in the copy. A letter the font does not draw is silently set in whatever the
platform substitutes, in the middle of a heading, so `FontProviderTest` checks the
screens' own titles against the characters in the file. There is no bold in it either,
so Tk emboldens the titles itself.

`FAMILIES` is a list because a file can carry more than one name: a weight that is
neither regular nor bold is folded into the family name by Windows while fontconfig and
CoreText report the typographic family, and both then have to be asked for.
