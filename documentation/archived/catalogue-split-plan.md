---
type: plan
title: catalogue-split-plan.md — how the catalogue split gets done, in four shippable parts
last_reviewed: 2026-09-08
status: archived 2026-09-08 — all four parts done; the R2 upload and Worker deploy Part 2 needs are in `logs/messages-for-bill.md`
---

# Doing the catalogue split

> **Archived 2026-09-08. All four parts landed the day this was written.** What the page ships
> now: the first screen baked into the markup, title and hero search on prefix shards, the payload
> split into a filter index and 41 row chunks, and no second published copy of the catalogue.
> **A reader pays 0.73 MB gzipped before the first draw, against 3.73 MB.** The decision this
> carried out is `documentation/catalogue-serving-shape.md`; the one thing still owed is Part 2's
> R2 upload and Worker deploy, which is in `logs/messages-for-bill.md` rather than here, because
> an open action in an archived file is an action nobody reads.

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

> **Amended 2026-09-08, doing Part 1: the first of those is not true on this machine.** There is no
> `node` on the PATH here, so `test_catalogue_export.py` does not fail loudly — it prints `skipped`
> and returns 0, and has been doing so for however long node has been absent. The safety net the
> paragraph above leans on is not under the work; `RENDER.md` reaches for node and jsdom for the
> datatable test in the same way and has the same hole. **So the browser is the check, not the
> backstop**, and Parts 3 and 4 should plan on driving the real page rather than on a test run
> catching them — Part 4's *done when* is `test_catalogue_export.py` passing with the JSON deleted,
> and on this machine that sentence currently means nothing. Installing node would fix both tests
> at once and is Bill's call; nothing here is blocked on it, because the same comparisons can be
> run in the browser and were for Part 1.

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

> **Done, 2026-09-08.** Both, and the second is checked rather than asserted:
> `scripts/test_catalogue_firstscreen.py` lifts the page's own `rowHTML` and `optsHTML` out of the
> built file — the lift `test_catalogue_export.py` already uses — runs them over the payload the
> page ships, and compares the result to the markup baked into the same file. Verified in the
> browser as well, which is what actually settled it here: node is not on this machine, so that
> test skipped, and the check that ran was a `DOMParser` over the fetched page against the live
> DOM after redraw. **Results, facets, count and note came back character for character
> identical** — 103,033 characters of rows and 18,959 of facets. The page renders complete with
> every `<script>` stripped, and a `<noscript>` paragraph says what is missing and points at the
> whole-catalogue downloads.
>
> **Two things changed that the plan did not name.** The facet sidebar was built with
> `createElement` and `appendChild`, a shape only a browser can produce; it is now two pure
> functions returning strings, which is what let the builder write the same markup. And entity
> display names are decided at build time instead of in the reader's browser — the prettifier
> moved to `catalogue.py`, because the baked rows have to carry the same labels the page draws and
> two copies of that rule would have been the thing that drifted. The page ships `entpretty`
> alongside `entnames` for it: **+217 KB raw on a 9.1 MB payload**, against 3,758 label
> computations removed from every page load, and both maps land in the fetched half at Part 3.
> `index.html` goes from 37 KB to 160 KB, which is the whole point of the exercise.

### Part 2 — Title and hero search shards

**No dependencies; can go before or after Part 1.** Tokenise title *and* `catalogue_hero` at build
time into prefix shards posting document ids, on the `build-names-index.py` model. The shards live
in R2 with `names/`.

**Hero must be tokenised alongside title, not after it.** `index.html` folds hero into the
per-row search blob (`r._s = r[0] + r[1] + r[12] + r[7] + …`), so it is searched today. Missing it
would silently narrow what search finds — the results just look thinner and nobody reports that.

*Done when:* a search that matches only on hero text returns the same rows it does today.

> **Done, 2026-09-08 — with one step left that is not CC's to take: see *What is not live yet*
> below.** `scripts/build-title-index.py` writes `outputs/titles/`, 23,682 titles and hero lines
> over **1,675 shards, 9.22 MB gzipped, median 0.9 KB a query and 17.6 KB at the ninetieth
> percentile**. Title and hero have come *out* of the page's per-row blob, so this is a switch and
> not an addition: the page searches them through a shard fetch now, and a reader who browses
> without searching never touches either.
>
> **The machinery is shared, not copied.** `scripts/shard_lib.py` was lifted out of
> `build-names-index.py` — doc ids, bucketing, splitting, writing, the size profile — and both
> builders sit on it. The names index rebuilt **byte-identical across all 5,682 shards and its
> manifest** after the lift, which is what says the refactor changed nothing.
>
> **Three things the plan did not anticipate, all of them found by measuring:**
> - **Accents.** 5,028 of 23,739 texts tokenise differently with the accents on, in a corpus a
>   fifth French and Portuguese. The shard *key* is folded and the text and the match are not, so
>   `côte` still matches Côte and `cote` still does not — exactly as the blob behaved.
> - **457 texts no word can key**, nearly all Arabic titles. They live in one fallback shard the
>   page asks for when a query yields no key of its own; without it they would have been reachable
>   by facet and by nothing else, silently.
> - **The page must compute its key the way the builder does, padding and all.** Slicing the bare
>   query word tried `sa`, found it had been re-cut into `sa_`/`sab`/`sac`, and gave up. And the
>   key is taken from the first word of the query that *could* be one, so `the digital` reaches
>   what `digital` reaches — the stopword narrowing this plan would have shipped is not there.
>
> **The one real narrowing is a query that starts mid-word**: `ercafes` no longer finds
> `Cybercafes`. That is the price of not shipping 20,000 titles to every visitor, and it is stated
> in `build-title-index.py`, in `RENDER.md` and in the test.
>
> *Proof.* `scripts/test_title_index.py` lifts `shardKeyFor` and `hitsFrom` out of the built page
> and runs **9,948 word-aligned queries cut from the corpus's own text, 1,441 of them from hero
> lines**: every one returned the record it came from, and all 855,167 records returned hold the
> query. Node is still absent here (see *The risk*), so it ran in the browser with `fs` and
> `process` shimmed onto synchronous XHR. The page itself was then driven: `escrow payments` — a
> phrase in one hero and in no title — returns that one record, which is the done-when in the
> literal form it was written in.
>
> **What is not live yet.** The shards are derived data and go to R2 with `names/`, which needs
> **`python scripts/r2-sync.py --apply`** and **a deploy of `workers/download-log/worker.js`**,
> whose `R2_PREFIX` now carries `catalogue/titles/`. Both are in this commit as source; neither
> has been run. Until they are, `site/catalogue/titles/` exists only locally and untracked, so a
> Pages deploy would 404 every title shard and search would return publishers and slugs only.
> **Nothing else in Part 2 is waiting on anything.**

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
- **The slug has to join the title index when it leaves the payload.** Part 2 left it in the
  in-memory blob because it was still there to leave; Part 3 takes it out. A record whose `url:`
  is a documented absence is cited *to this page* by slug (`report-render.slug_offline()`,
  notes-for-corpus 22), so an unsearchable slug lands those citations on nothing. It is one word
  in `build-title-index.py`'s `FIELDS`, and the date prefix keys on nothing, so a pasted slug
  finds its shard through the first real word in it. *(Done: `FIELDS` carries it, the index went
  from 1,675 shards to 2,283, and a pasted slug returns its one record.)*

**State in `catalogue.py` that the chunk files are internal and carry no stability promise**, and
that `raw-catalogue.csv` is the supported way to consume this data. Say it in the file that writes
them, or the boundary acquires a second consumer the way the last one did.

*Done when:* every facet, every combination and every sort returns what it returns today, and a
deep link from before the change resolves to the same result set.

> **Done, 2026-09-08.** `site/catalogue/data/` is the payload now: a **filter index of 2.29 MB,
> 0.68 MB gzipped**, fetched once, and **41 chunks of 500 rows at 154 KB / 53 KB gzipped**,
> fetched for the rows about to be drawn. A reader who opens the page pays **0.73 MB gzipped
> before the first draw against 3.73 MB today — an 80% cut** — and `catalogue-data.js` is deleted.
> Scaled to 40,000 records the filter index lands at **~1.34 MB gzipped**, which is the number
> `catalogue-serving-shape.md` said the whole decision rested on, measured rather than projected.
>
> **The encoding.** Dates are a **dictionary, not day offsets**: 284 records carry a published
> value that is not a whole date, and an offset would have to invent a day to store one and invent
> one back to show it. Publishers likewise; places, topics and actors are offsets into vocabularies
> the page shipped anyway; `lens` was dropped from the browse payload entirely, because nothing on
> the page had read it since the lens facet went.
>
> **The search blob is gone rather than shrunk.** `catalogue-serving-shape.md` named it as a defect
> in its own right — a second full-corpus string allocation on top of the array just parsed. What is
> matched in memory now is the two *vocabularies*, 7,697 publishers and 11,331 actors, once per
> query rather than once per record. The slug went to the title index with them
> (Part 2's `FIELDS`), which is why a pasted slug still finds its record.
>
> **A–Z had to become a build-time decision**, because the page cannot sort text it does not hold.
> One rank per record, from `coll()`. It approximates the browser's collation rather than
> reproducing it: measured against Chrome over all 20,267 titles, **1.6% of adjacent pairs sort the
> other way and the first A–Z screen shares 91 rows of 100**, the residue being how quotes and
> dashes order among themselves. Against that, `localeCompare` follows the reader's own locale, so
> a `#sort=az` link did not mean one thing before and does now. Two rounds of measurement went into
> that 1.6%: sorting by class before code point took the first screen from 64 to 91.
>
> *Proof.* **`scripts/test_catalogue_index.py`** reads the encoding back and compares it to
> `raw-catalogue.json` record by record — all 20,267, every field, every facet count, the year
> buckets and the A–Z permutation — and needs no node, so it runs here. Independently, expectations
> for 18 filter and sort combinations were computed in Python from the raw catalogue and replayed
> against the live page: **every count and every ordered first-100 matched**. The baked first
> screen is still character-for-character what the page draws, which after this change is an
> end-to-end check of the split — the bake reads the catalogue and the page reads an encoding of
> it. Search was driven over every path it now takes (hero, title, slug, publisher, actor, Arabic,
> sub-minimum), deep links resolve including entity-only ones, and the filtered CSV export comes
> out with its BOM, its CRLF and all seventeen columns.
>
> **Two things are not what the plan assumed.** The download has **seventeen** columns, not
> sixteen — that number was wrong in four places and is now stated nowhere, on the same grounds
> `RENDER.md` gives for not stating record counts. And the chunks are **tracked in git and served
> from Pages**, not moved to R2: the page cannot draw a row without them, and a `git push` should
> be enough to serve a working catalogue. They cost about what `catalogue-data.js` cost, so the
> churn is unchanged; moving them to R2 later is additive and is a decision on its own.
>
> **The worst case is worth stating.** A filter matching a hundred records spread evenly across the
> corpus fetches a hundred chunks — which is every chunk, about 2.2 MB gzipped, and therefore no
> worse than the payload every visitor pays today. Every other case is far better: the unfiltered
> screen is one chunk, and a dense filter a handful.

### Part 4 — Drop `raw-catalogue.json`

**Depends on Part 3.** The export currently cuts a whole-record selection from the JSON by slug.
Once the row-text chunks carry the five missing fields, the export reads those instead and the JSON
has no remaining consumer. Dropping it takes ~31 MB off the published site and ~6.6 MB off every
build's permanent git history.

*Done when:* `test_catalogue_export.py` passes with the JSON deleted.

> **Done, 2026-09-08.** `site/catalogue/raw-catalogue.json` is gone: **17 MB out of the published
> site, and out of every commit from here on.** The export rebuilds each record from the filter
> index and the row chunks instead — `itemOf` in the page — and the chunks gained the last column
> they were short, `artefact`, which the index carries only as a flag because a flag is all a row
> draws.
>
> *Proof, and it is the done-when in a stronger form than it was written.* The test used to lift
> `csvCell` and `toCSV` and run them over the published JSON, which proved the serialiser. It now
> lifts **`itemOf` as well** and rebuilds all 20,267 records from the payload the page actually
> fetches: **8,563,917 bytes, seventeen columns, byte for byte identical to `raw-catalogue.csv`.**
> That covers three things which used to be separate risks — the JavaScript port of
> `csv.DictWriter`, the encoding of every column into the split payload, and the reassembly of a
> record out of it.
>
> **The whole-catalogue JSON download survives the file.** Deleting the file would have taken the
> download with it, and that is a real loss for the audience most likely to want the catalogue as
> data. The button now cuts it in the browser from the same chunks the page draws from — 2.2 MB
> gzipped in, against 3.5 MB for the file it replaced — so the reader gets the same records and
> the site carries no second copy of them. **`raw-catalogue.csv` is untouched**: a published file
> at an undated URL, `design.md` §9's named exception, and still the thing to cite.
>
> **One field is deliberately not in the rebuilt record.** The published JSON carried `path`, the
> vault-relative filename of the source. It was never in the CSV, it means nothing to a reader,
> and keeping it would have cost about a megabyte across the chunks. Every column `csv_cols()`
> names is there, and `catalogue_hero` with them.

## What must not break

**Deep links.** Filter state lives in the URL fragment. A reader arriving on a fragment gets the
baked first screen, then the index, then the filtered result. **Nothing about the fragment's grammar
changes** — not in any of the four parts.

**Export byte-parity.** `raw-catalogue.csv` is `design.md` §9's named exception to the edition rule
and does not change at all. The filtered export must stay byte-identical to it with rows removed —
the BOM, the CRLF, the column set, all of it. `test_catalogue_export.py` is what says so.

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
| 1 — bake the first screen | **done 2026-09-08** |
| 2 — title and hero search shards | **built and proven 2026-09-08**; needs an R2 upload and a Worker deploy to be live |
| 3 — filter index and row-text chunks | **done 2026-09-08** |
| 4 — drop `raw-catalogue.json` | **done 2026-09-08** |
