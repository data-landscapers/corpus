---
type: plan
title: catalogue-split-plan.md — how the catalogue split gets done, in four shippable parts
last_reviewed: 2026-09-08
status: live — Part 1 starting 2026-09-08; all four to land before go-live
---

# Doing the catalogue split

*(The **what** and the **why** are in `documentation/catalogue-serving-shape.md`, decided
2026-09-04 and amended 2026-09-08 for the hero text. This is the **how and in what order**, written
2026-09-08 when Bill set a go-live date of the week of 2026-09-14. It is a working document: parts
get ticked off and it is archived when the last one lands.)*

## Why before go-live rather than after

**Nothing has cited the catalogue yet.** Filter state travels in the URL fragment and those
fragments are citable in the same sense everything else on the site is — but only once there are
readers to cite them. The chunk boundary, the fragment grammar and the export's source can all
still be chosen freely today. After launch each of them acquires the property that changing it
breaks somebody.

That is the same trap `raw-catalogue.json` fell into: private and re-choosable, right up until the
export started reading it, at which point it became a format to be preserved. Doing this before
anybody arrives is the cheapest this job will ever be.

**The freeze does not apply and the reason has changed.** The freeze (to 2026-09-27) transfers
capacity from process to reports. A launch is not a process improvement, and the argument that the
marginal report beats the marginal refactor does not survive the page the reports are served from
shipping 3.7 MB before it draws. Bill's call, 2026-09-08.

## The estimate

About a day of working time, two sessions. Sized against the code as it stands:
`catalogue.py` 1,012 lines, `site/catalogue/index.html` 680 lines with 567 of inline JS across 30
functions, `build-names-index.py` 324 lines.

| Piece | Effort | Why that size |
|---|---|---|
| Filter index + row-text chunks in `catalogue.py` | 1.5–2h | ~690 lines of packing logic already exists; the output shape changes, the logic mostly does not |
| Title + hero search shards | ~1h | `build-names-index.py` is a working model for exactly this, and the shards go to R2, which now exists |
| Rewrite the page's JS | 2–3h | The filtering half survives largely intact — it already works on packed arrays. `drawResults` becomes async, and the export has to be rewired |
| Bake the first screen at build time | ~1h | Small, and the piece with the most lasting value |
| Drop `raw-catalogue.json` | ~1h | The export must come out byte-identical from a different source |
| Verification | 1–2h | See *The risk* below |

## The risk is proving it works, not building it

The R2 move of 2026-09-08 was safe because every claim was checkable with `curl` and there was a
fallback to GitHub Pages the whole way. **Neither is true here.**

**There is exactly one test on the catalogue.** `scripts/test_catalogue_export.py` lifts `csvCell`
and `toCSV` out of the *built* `index.html` — testing a copy of the logic would only prove the copy
right — runs them over every item, and compares the result to `raw-catalogue.csv` byte for byte.
It covers the highest-stakes path and it is the strictest constraint in the whole job. Everything
else — facets, sorting, deep links, search, empty results — has no automated check at all.

Two things help. That export test keeps working throughout and fails loudly. And the session has
browser automation, so the real page can be driven and its interactions observed rather than
reasoned about.

## The four parts

**Staged, not big-bang.** Each part is independently shippable and independently revertible; a
problem in one does not mean reverting the others. This does not make the job faster — it is the
same day of work — but it turns one risky change to the page readers use into four small ones.

### Part 1 — Bake the first screen at build time

**No dependencies. Start here.** The newest ~100 rows and the facet menus are all known when
`catalogue.py` runs. Write them into `index.html` as real markup, and let the live filtering
upgrade over the top when the payload lands.

This is the move that matters most for the long run, because it **decouples time-to-useful from
corpus size permanently** rather than setting a second threshold to be rediscovered at 80,000. It
is also worth having on its own even if the rest slipped: today the page draws nothing until 2.95 MB
has downloaded and parsed.

*Done when:* the page shows results with JavaScript disabled, and shows the same results it shows
today once the payload lands.

### Part 2 — Title and hero search shards

**No dependencies; can go before or after Part 1.** Tokenise title *and* `catalogue_hero` at build
time into prefix shards posting document ids, on the `build-names-index.py` model. The shards live
in R2 with `names/`.

**Hero must be tokenised alongside title, not after it.** `index.html` line 191 folds hero into the
per-row search blob (`r._s = r[0] + r[1] + r[12] + r[7] + …`), so it is searched today. Missing it
would silently narrow what search finds — the results just look thinner and nobody reports that.

*Done when:* a search that matches only on hero text returns the same rows it does today.

### Part 3 — Filter index and row-text chunks

**The big one, and it depends on nothing but is best done after Part 1**, so that a failure still
leaves a page that draws.

- **Filter index**, fetched rather than `<script src>`: dates as day offsets, publisher
  dictionary-encoded, places, topics, entities, artefact flag, completeness, plus the vocabularies.
  Re-measured with hero filled in on every record, this is **~1.3 MB gzipped at 40,000** — the
  number the whole decision rests on, and it survives the new column.
- **Row-text chunks**, fixed 500-row files in stored order: title, URL, slug, hero, plus the five
  fields the export needs. **~177 KB raw per chunk** at 40,000, fetched only for rows about to be
  drawn.

**State in `catalogue.py` that the chunk files are internal and carry no stability promise**, and
that `raw-catalogue.csv` is the supported way to consume this data. Say it in the file that writes
them, or the boundary acquires a second consumer the way the last one did.

*Done when:* every facet, every combination and every sort returns what it returns today, and a
deep link from before the change resolves to the same result set.

### Part 4 — Drop `raw-catalogue.json`

**Depends on Part 3.** The export currently cuts a sixteen-column selection from the JSON by slug.
Once the row-text chunks carry the five missing fields, the export reads those instead and the JSON
has no remaining consumer. Dropping it takes ~31 MB off the published site and ~6.6 MB off every
build's permanent git history.

*Done when:* `test_catalogue_export.py` passes with the JSON deleted.

## What must not break

**Deep links.** Filter state lives in the URL fragment. A reader arriving on a fragment gets the
baked first screen, then the index, then the filtered result. **Nothing about the fragment's grammar
changes** — not in any of the four parts.

**Export byte-parity.** `raw-catalogue.csv` is `design.md` §9's named exception to the edition rule
and does not change at all. The filtered export must stay byte-identical to it with rows removed —
the BOM, the CRLF, the sixteen columns, all of it. `test_catalogue_export.py` is what says so.

**`raw-catalogue.csv` itself.** Untouched by every part of this.

## Go-live checks that belong with this work

The site going live changes what a mistake costs, and two things are worth confirming rather than
assuming on the day:

- **The retention rule is already correct for a live site** and needs no change: forward-only from
  2026-08-19, any fetch at all protects, a week's lag after supersession, and every uncertainty
  resolving towards keeping the file. What changes is only that "nobody downloaded it" starts
  meaning something. See `documentation/how-the-site-is-served.md`.
- **The `.com` redirects** are what keep over a thousand published PDFs' printed URLs alive. They
  work today; they are worth re-checking on the day, because that is the one thing here with no
  undo. `documentation/cloudflare.md` → *Confirming it all still works* has the two `curl` lines.

## Status

| Part | State |
|---|---|
| 1 — bake the first screen | starting 2026-09-08 |
| 2 — title and hero search shards | not started |
| 3 — filter index and row-text chunks | not started |
| 4 — drop `raw-catalogue.json` | not started |
