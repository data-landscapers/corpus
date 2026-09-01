---
type: guide
title: editing-content.md — how to change the words on the site
last_reviewed: 2026-09-01
status: in force; Corpus-owned
---

# editing-content.md — how to change the words on the site

**Every sentence the site shows a reader that was not derived from data lives in `content/`.** Nothing reader-facing is a string constant in a Python file any more, and nothing should go back to being one. This note is the procedure for changing those words. It is for you, not for a run: the whole point of `content/` is that a sentence can be edited by the person who wants it changed, without reading Python.

## Two kinds of file, and they behave differently

`python scripts/copy_lib.py` prints every file, every `##` in it and its word count. That listing is the map, and it is worth running before an edit rather than guessing.

**Whole-page files.** `methodology.md`, `document-lifecycle.md`, `process-inventory.md`, `methodology-lookups.md`. The file *is* the page: `##` is a section heading the reader sees, the order on the page is the order in the file, and adding, removing or renaming a section changes the page. `scripts/methodology.py` converts and wraps them. Write ordinary markdown — headings, paragraphs, lists, tables, links — and nothing above the first `##`, because there is no room on the page for it.

**Block files.** `home.md`, `country.md`, `catalogue.md`, `finance.md`, `topic.md`, `topics.md`, `countries.md`, `document.md`. Here `##` is **a key a builder asks for by name**, not a heading anybody sees, and the order in the file means nothing. Anything above the first `##` is a comment to whoever is editing and is never rendered. Change the words under a key freely; **renaming or deleting a key breaks the build**, because a missing key raises rather than rendering an empty space.

## The rules that will bite

- **Do not rename or delete a `##` key in a block file** without changing the builder that asks for it. `grep -rn "your-key-name" scripts/` finds every caller. The build stopping is the designed outcome and is better than the alternative, which is a page that looks finished and has a hole in it.
- **`{something}` in a block file is a placeholder** the builder fills, and the name has to survive the edit. A literal brace must be doubled — `{{` — as in `str.format`. This does not apply to the whole-page files: `methodology.py` never calls `.format()` on them, which is why `outputs/reports/{ISO3}/` sits in the process inventory table as plain text.
- **Numbers pasted into prose go stale silently.** If a figure can be counted from `outputs/`, the builder should be passing it in rather than the sentence carrying it.
- **Nothing in `content/` is an edition.** These pages are rebuilt in place and carry no dated file, so an edit here is fully reversible and needs no `-2` suffix and no thought about §9. That is the opposite of the reports.

## Adding a section to a whole-page file

Write the `## Heading` and its text. Two things follow automatically: it gets an anchor id (`## National newspapers` → `#national-newspapers`), so anything on the site can deep-link it, and on `lookups` and `document-lifecycle` it joins the contents bar at the top of the page. Nothing needs to be registered anywhere.

Deep-link it from another page with a relative link — `[financiers](lookups/#financiers)` from the methodology page, `../lookups/#financiers` from one of the annexes.

## Adding a whole new page

One row in `PAGES` at the top of `scripts/methodology.py` — content file, URL slug, `<h1>`, `<title>`, the nav label the see-also bars use, whether it wants a contents bar, and the meta description — plus the content file itself. The see-also bar on all the other pages picks it up, because it is derived from that list rather than written into each file.

## Then

```bash
python scripts/methodology.py         # the four methodology pages
python scripts/copy_lib.py            # what is where, after the edit
```

For a block file, the builder that owns the page has to run instead — `home.py`, `country.py`, `catalogue.py`, `finance.py`, `topic-page.py` — and `RENDER.md` steps 3 to 6 are the list. Then `git add site content` and push; the GitHub Pages workflow serves what was committed.

Nothing here reads OSINT, nothing here mints an edition, and nothing here needs a full render. An edit to `content/` and the one builder that owns it is the whole job.
