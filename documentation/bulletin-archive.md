# The bulletin mini-archive — save and prune logic

*(A facility to download the last week's bulletin PDFs, a dropdown with date, time and entry count, and a stated retention promise. The live procedure is `RENDER.md` → *The bulletin*; `scripts/bulletin_editions.py` holds the manifest rules — it has two writers, and a rule with two writers belongs in neither of them. `render.py` writes on cut, `prune-editions.py` rewrites on delete; `scripts/test_prune_editions.py` covers the branch.)*

## Where it is stored — nowhere new

**The PDFs do not move.** They stay at `site/bulletin/corpus-bulletin-YYYY-MM-DD[-N].pdf` — a downloaded edition stays at the URL it was cited at; there is no `archive/` folder and no redirect. **The archive is a listing, not a location**: one new file, **`site/bulletin/editions.json`**, is what the dropdown reads —

```json
{ "retention_days": 7,
  "editions": [
    {"edition": "2026-08-22-6", "file": "corpus-bulletin-2026-08-22-6.pdf",
     "compiled": "2026-08-22 09:35", "items": 25, "bytes": 302103}
  ] }
```

Newest first; `file` is relative to `site/bulletin/`, so the picker needs no base URL.

## The retention promise is on the PDF

A reader who downloads the PDF may never see the page again, and a file that will 404 in a week and does not say so fails §9's own basis (*a document says plainly what it is*). So the colophon carries a row beside `Edition` and `This file`:

```
Retention · Kept until 2026-08-29. Older bulletins: the country pages and the monthly reports.
```

**Name the date, not the interval** — *kept for a week* asks the reader to remember when they downloaded it. It is `edition_date + retention_days`, the same number the pruner acts on, so the page cannot promise one thing while the script does another.

## The save logic

**`render.py` writes the entry at the moment it cuts a bulletin PDF** — the only moment the picker's three facts are in hand (`compiled` and `items` from the frontmatter it has just read, and the edition it is minting); none is recoverable from the PDF afterwards. Each write rebuilds the list: add the new entry, replacing any at the same edition; **drop any entry whose file is not on disk** (self-healing — a hand-deleted file or a part-failed prune cannot leave the picker offering a 404); **adopt any bulletin PDF on disk that nothing recorded** (edition from the filename, no invented count — `label()` prints the date alone); drop entries outside the window; sort through `editions.edition_key`, never by string (`-2026-08-18-2.pdf` sorts before `-2026-08-18.pdf` because `-` precedes `.`); write with `newline=""`.

**A held-off render writes no entry** (no PDF was cut) but still rewrites the page, so the picker refreshes against the current manifest and picks up any deletion.

## The prune logic

**The bulletin leaves the download rule and takes a stated retention window instead — not both.** If bulletins also kept condition 5 (any fetched edition kept for ever), the one-week promise would hold for every bulletin except the ones a reader actually took. That is defensible for the bulletin alone, because it is the one document that is explicitly not an archive and whose content is fully preserved elsewhere — the country pages, the monthly reports, the catalogue, and git. A report's superseded edition is the only copy of what that report used to say; a bulletin's is not.

| Condition | Reports and CSVs | Bulletin |
|---|---|---|
| 1. Never the current edition | applies | **applies** — the live page must always offer its own PDF |
| 2. Forward only | applies | not needed |
| 3. Superseded more than `--lag-days` ago | applies | **replaced** by the retention window |
| 4. Download record healthy | applies | **not consulted** — bulletin retention works with no Cloudflare token |
| 5. Never fetched | applies | **deliberately not applied** |

**The window is measured on the edition date, not supersession** — a bulletin is superseded within hours by its own next cut, so a supersession lag would keep each edition a different week, none of them the week the colophon named.

**Prune updates `editions.json` when it deletes** — the party doing the deleting owns the listing — **and RENDER asserts the two agree** (`python scripts/bulletin_editions.py`: every entry resolves to a file on disk, or the run says so). A derived listing is only safe while something notices when it stops describing what it describes.

Condition-4 refusals in `prune-editions.py` are **per row**, not run-wide: everything the download record governs keeps, and the run says so; the bulletin window applies regardless. It fails in the same direction it always did — a missing record protects every file whose protection depends on it.

## The dropdown

**In the colophon, beside `This file`** — *quiet* is still the right register, and the header row ends on what the document is. Labels carry date, time and count (`Saturday 22 August, 09:35 — 25 entries`); the time is `compiled`, OSINT's last ingest — how fresh the material in that edition is, which is what a reader choosing between two cuts of one day is asking.

**Progressive enhancement, as the country filter does it**: the control renders `hidden`, the script removes the attribute, and a missing or malformed `editions.json` leaves it hidden rather than empty. If it is ever given a `display` of its own, give it an explicit `[hidden] { display: none }` — an author `display` outranks the UA stylesheet's rule whatever its specificity. **The picker is not written into the PDF** (the PDF runs no script; the `Retention` row travels, the control does not), and **a picker with one option is not written at all**. Every option is a dated URL, so §9's *no undated download URL* is untouched.

## The exception, stated plainly

design.md §1 ruled out a version picker; this is one, for one document, and it is the right exception: **for every other document an earlier edition is a worse version of the same claims; for the bulletin it is a different day's news.** No later edition supersedes the 20th's bulletin in the sense §1 assumed.

**Two things to watch, neither blocking.** The steady state is about two cuts a day, fourteen listed; if it runs noisy, the lever is to list only the last cut of each day — but not early, because a picker that omits a cited edition is one the reader cannot use. And deleting a PDF from `site/` gets nothing back from git — the saving is against GitHub Pages' ceiling; the blob is permanent, roughly 200 MB a year at two cuts a day, a standing cost of minting editions at all.

The documentation sentence lives in `content/document.md` → `bulletin-notes` — the whole of *About this document* on this page; say less rather than more.
