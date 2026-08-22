# The bulletin mini-archive — save and prune logic

*(Specified 2026-08-22 for Cowork to implement, from Bill's brief: a facility to download the last week's bulletin PDFs, a dropdown showing date, time and number of entries, and a statement in the site documentation that bulletins are kept for a week and older material is in the monthly reports. What follows is the design and the reasoning; the live procedure will be `RENDER.md` → The bulletin once it ships.)*

## Where it is stored — nowhere new, and that is the point

**The PDFs do not move.** They stay exactly where they are, at `site/bulletin/corpus-bulletin-YYYY-MM-DD[-N].pdf`. `prune-editions.py` states the rule this obeys — *"The file never moves. A downloaded edition stays at the URL it was cited at, because nothing relocates it; there is no `downloaded/` folder and no redirect, so no link this rule keeps ever changes address."* An `archive/` subdirectory would relocate files that are already published, and every colophon in a downloaded PDF names the old path. **The archive is a listing, not a location.**

One new file, and it is the whole of the new storage:

**`site/bulletin/editions.json`** — what the dropdown reads.

```json
{ "retention_days": 7,
  "editions": [
    {"edition": "2026-08-22-6", "file": "corpus-bulletin-2026-08-22-6.pdf",
     "compiled": "2026-08-22 09:35", "items": 25, "bytes": 302103}
  ] }
```

Newest first. `file` is relative to `site/bulletin/`, so the picker needs no base URL and the JSON is correct whether it is served from the site root or from a local preview.

## What has to be true before any of this ships

**The retention promise must be on the PDF, not only in the site documentation.** This is the one thing in the brief that is not yet covered by it, and it is the thing that makes deletion honest rather than a broken link.

A reader who downloads the PDF may never see the page it came from. §9's basis is explicit that the commitment here *"is a moral one, not a legal one"*, and that what is owed is that a document *"says plainly what it is, when it was cut, and that it is not revised afterwards"*. A file that will 404 in a week and does not say so fails that on its own terms — and it fails it for exactly the reader the section was written about, the one who cites in November what they downloaded in August.

So the bulletin colophon takes one more row, beside `Edition` and `This file`:

```
Retention · Kept until 2026-08-29. Older bulletins: the country pages and the monthly reports.
```

**Name the date, not the interval.** *Kept for a week* asks the reader to remember when they downloaded it; a date is checkable against nothing but a calendar. It is `edition_date + retention_days`, and it is the same number the pruner acts on, so the page cannot promise one thing while the script does another.

## The save logic

**`render.py` writes the entry at the moment it cuts a bulletin PDF**, because that is the only moment all three of the dropdown's facts are in hand: they come from the frontmatter it has just read — `compiled` for the time, `items` for the count, and the edition it is minting for the date. None of them is recoverable from the PDF afterwards, which is why this cannot be a script that walks the directory later.

Each write rebuilds the list rather than appending to it:

1. take the entries already in `editions.json`, add the one just cut, replacing any entry at the same edition;
2. **drop any entry whose file is not on disk** — self-healing, so a hand-deleted file or a prune that failed part-way cannot leave the picker offering a 404;
3. drop any entry outside the retention window;
4. sort newest first through `editions.edition_key`, **not** by string — `-10` sorts before `-2`, and `-2026-08-18-2.pdf` sorts before `-2026-08-18.pdf` because `-` precedes `.`, which is the trap that module exists to close;
5. write with `newline=""`, for the reason every other writer in this repo now carries it.

**A held-off render writes no entry**, because no PDF was cut. It still rewrites the page — the bulletin's own exception at `RENDER.md` → *The bulletin* — so the picker refreshes against the current manifest and picks up any deletion. That is the behaviour wanted and it comes free.

## The prune logic

**The bulletin leaves the download rule and takes a stated retention window instead. It is not subject to both.** This is the sharp edge of the whole feature, and it has to be a branch in `prune-editions.py` rather than a sixth condition bolted onto the existing five.

Condition 5 keeps any edition anybody ever fetched, for ever. If bulletins stayed under that rule and merely gained a window as well, then **the one-week promise would hold for every bulletin except the ones a reader actually took** — the files someone cared about would be the files that outlived the policy, and the site documentation would be false in precisely the cases that matter. The window replaces the download test for this document kind; it does not join it.

That is defensible for the bulletin and for nothing else, because the bulletin is the one document here that is explicitly not an archive (`documentation/bulletin.md` → *What it is not*) and whose content is fully preserved elsewhere: the country pages hold a month, the monthly reports hold the month, the catalogue holds every record, and git holds every version of the document itself. A report's superseded edition is the only copy of what that report used to say. A bulletin's is not.

**What survives of the five conditions, and what does not:**

| | Reports and CSVs | Bulletin |
|---|---|---|
| 1. Never the current edition | applies | **applies** — the live page must always be able to offer its own PDF, even if the site goes quiet for a month |
| 2. Forward only (`--from`) | applies | not needed; nothing bulletin-side predates the rule by more than the window |
| 3. Superseded more than `--lag-days` ago | applies | **replaced** by the retention window |
| 4. Download record healthy | applies | **not consulted** — so bulletin retention keeps working on a machine with no Cloudflare token, where everything else correctly declines |
| 5. Never fetched | applies | **deliberately not applied** — see above |

**The window is measured on the edition date, not on supersession.** Delete a bulletin edition when `today − edition_date > retention_days`. Supersession is the wrong clock here: a bulletin is superseded within hours by its own next cut, so a lag measured from it would delete this morning's edition next Saturday and last Sunday's the Sunday after — a week each, but a different week each, and none of them the week the colophon named.

**Prune updates `editions.json` when it deletes.** The party doing the deleting owns the listing; anything else opens a window between `RENDER.md` Step 6a and the next render in which the picker offers a file that is gone. Prune already writes a ledger, so this is one more write inside an operation it is doing anyway.

**And RENDER asserts the two agree** — every entry in `editions.json` resolves to a file on disk, or the run says so. Cheap, mechanical, and it is what makes a derived listing safe to trust: the same principle as `lint-shared-assets.py`, which exists because a copy is not sharing unless something notices when it goes stale.

## The dropdown

**In the colophon, beside `This file`** — not in the header next to `↓ PDF`. Two reasons. §1's ruling is *"expose only current plus a quiet earlier editions affordance — no version picker to maintain"*, and while this brief reverses that for the bulletin (below), *quiet* is still the right register. The header row ends on what the document is, and it is already `flex-wrap: nowrap` with the byline shrinking inside its own box, so a third control there is a layout problem as well as an emphasis one. The colophon is where `This file` already names the dated PDF, which makes *and here are the earlier ones* the sentence that belongs beside it.

**Labels carry date, time and count**, per the brief:

```
Saturday 22 August, 09:35 — 25 entries
Friday 21 August, 16:31 — 24 entries
```

The time is the `compiled` stamp, which is **OSINT's last ingest and not our build clock** (`documentation/bulletin.md`). That is the right number to show: it says how fresh the material in that edition is, which is the question a reader choosing between two cuts of the same day is actually asking.

**Progressive enhancement, exactly as the country filter does it.** The control renders `hidden` and the script removes the attribute; a missing or malformed `editions.json` leaves it hidden rather than empty. And **give it an explicit `[hidden] { display: none }` if it is ever given a `display` of its own** — an author `display` outranks the UA stylesheet's rule whatever its specificity, which is the whole of the bug that cost 2026-08-22 an afternoon.

**Every option is a dated URL**, so §9's *no undated download URL exists at all* is untouched.

## Two things to watch, neither blocking

**Today's six editions are not the steady state.** 2026-08-22 cut six because of a CSS fix pushed through with `--force` and then two content fixes. The normal day is the nightly cycle plus the late-morning top-up — **about two a day, fourteen in a week**. If it does run noisy, the lever is to list only the last cut of each day and leave the rest reachable by URL; but do not reach for it early, because a picker that omits an edition a reader has cited is a picker they cannot use to find it again.

**Deleting a PDF from `site/` does not get the space back from git.** `prune-editions.py` says so already: the saving is against GitHub Pages' soft ceiling, not the repository, and the blob stays in history for ever. At ~300 KB and two cuts a day that is roughly 200 MB a year of permanent repository weight — a standing cost of minting editions at all rather than anything this feature adds, and worth stating only because this repo has been bitten by that arithmetic once, at 1,053 PDFs and 314 MB in a fortnight.

## What this reverses, stated plainly

**§1 ruled out a version picker** — *"Retain silently, expose only current plus a quiet earlier editions affordance — no version picker to maintain."* This is a version picker, for one document.

It is the right exception, and the reason is the bulletin's alone: **for every other document an earlier edition is a worse version of the same claims, and for the bulletin it is a different day's news.** Nobody needs `KEN-status-2026-08-06.pdf` once the 21st's exists, except to check a citation. The bulletin of the 20th is the only place the 20th's bulletin is, and no later edition supersedes it in the sense §1 assumed. A picker over the reports would be maintenance with no reader behind it; a picker over a week of bulletins is the affordance §1 asked for, in the one place a flat *earlier editions* link would not do the job.

## The documentation sentence

`content/document.md` → `bulletin-notes`, which is the whole of *About this document* on this page. It already sends a reader to the country pages for the last month and to the catalogue for everything; the new clause is the retention and the monthly reports. That block appears on the bulletin alone, so unlike `report-notes` a sentence added here is added once — but the file's own editing rule still stands: say less rather than more.
