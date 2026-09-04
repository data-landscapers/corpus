---
type: decision
title: catalogue-serving-shape.md — how the catalogue is served at 40,000 records
last_reviewed: 2026-09-04
status: decided; implementation deferred to the end of the freeze (2026-09-28)
---

# The serving shape of the catalogue

*(This resolves the first bullet of `design.md` §6, *Serving shape of the catalogue*, and supersedes both its projection and the instrument it reached for. §6's bullet should be struck and replaced with a pointer here. Written 2026-09-04 against a catalogue of 16,730 records, at Bill's request to plan for 40,000.)*

## What was measured

Everything below is the built tree at 2026-09-04, not an estimate. The 40,000-record column is a straight ×2.39 scaling, which is fair for these files: every one of them is a per-record structure with a fixed vocabulary alongside it, so nothing in them grows faster or slower than the row count.

| file | how it loads | now (16,730) | gzip | at 40,000 | gzip |
|---|---|---|---|---|---|
| `catalogue-data.js` | **blocking `<script src>`** | 7.0 MB | 2.24 MB | 16.8 MB | 5.4 MB |
| `raw-catalogue.json` | lazy, first export click | 13.0 MB | 2.75 MB | 31.2 MB | 6.6 MB |
| `raw-catalogue.csv` | download only | 7.0 MB | 2.23 MB | 16.8 MB | 5.3 MB |
| `names/` (4,655 shards) | lazy, one shard per search | 47.6 MB | — | 113.9 MB | — |
| **`site/catalogue/`** | | **72 MB** | | **~172 MB** | |

Where the browse payload's bytes actually are, per column, uncompressed:

| column | MB | distinct values |
|---|---|---|
| `url` | 1.75 | 3,670 hostnames |
| `title` | 1.59 | — |
| `slug` | 1.02 | — |
| `topics` | 0.66 | 38 |
| `publisher` | 0.60 | 6,046 |
| `published` | 0.20 | — |
| `places` | 0.14 | 62 |

## The projection in §6 was wrong, and not by a little

§6 says *~23 MB at the 30,000 records projected for spring 2027*. `logs/log.md` says catalogue 9,407 on 2026-08-13, 15,324 on 2026-09-03 and 16,730 on 2026-09-04 — **+7,323 records in 22 days, or 333 a day**, with +1,406 on the last day alone.

At the 22-day average, 30,000 arrives around **mid-October 2026** and 40,000 around **mid-November 2026**. Spring 2027 was out by about five months, and the number it was pointed at was the smaller one. §6's other clause — that a single fetch *stops being defensible around 15–20k rows* — is not a future condition either: the catalogue entered that band in the last week of August and is inside it now.

The lesson worth keeping is not that the arithmetic slipped. It is that a projection written into a design record with no mechanism reading it back is a projection nobody re-checks. `RENDER.md` Step 5 carries the same defect independently — *Expect ~10,700 records*, a statement that has been wrong for weeks and that a render prints past every night.

## Three constraints, in the order they bind

They are usually discussed as one problem. They are three, they have different deadlines, and the one everybody talks about is the last to arrive.

**1. `site/` is 924 MB against a hard 1 GB ceiling.** [GitHub Pages caps a published site at 1 GB](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits) and recommends the source repository stay under the same. Reports (537 MB) and topics (277 MB) are what fills it — the catalogue's 72 MB is not the cause and never was. But the catalogue wants roughly another 100 MB by mid-November, and there is 76 MB of headroom in total. **This binds first, it binds hardest, and it is not a catalogue problem**; the catalogue is merely the tenant that notices the building is full. Whatever is decided here, the editions layer needs its own answer, and `prune-editions.py` deleting only what nobody downloaded is not going to be it for much longer.

**2. Git history churn, which is invisible in `site/`.** All three catalogue files are rewritten wholesale on every render and committed. At 40,000 that is roughly 17 MB of new, permanently-retained blob per build — git stores them zlib-compressed, so the compressed figures are the right ones to add up — plus whatever fraction of the ~114 MB names index churned that night. The log shows renders on consecutive days. Call it 6 GB a year of history that no prune can reach, because `prune-editions.py` deletes files from the tree and git keeps the blob; `design.md` §9 already says so about editions and it is equally true here. `du` on `.git` did not complete in 100 seconds over the Cowork mount, which is not a measurement but is a signal.

**3. The eager payload — §6's problem, and the least urgent of the three.** At 40,000 the page ships 5.4 MB gzipped and then parses a 16.8 MB JavaScript source literal before it can draw anything. The bandwidth is survivable; the parse is not the kind of thing that degrades gracefully on a mid-range phone, and `index.html` line 185 then builds a second full-corpus string allocation (`r._s`, the per-row search blob of title + publisher + entity slugs) on top of the array it just parsed.

## Sharding by year is the wrong instrument

§6 reaches for year-shards on the grounds that `raw/` is already sharded that way, so the boundary is nearly free.

The boundary is cheap; the *access pattern* is what makes it wrong. The catalogue page's core interaction is to filter and sort **across the whole corpus** — a place, a topic, an entity, a free-text string — and only then to look at what came back. A year shard only helps a reader who has already chosen a year, and there is no year facet in the sidebar that is not a filter over everything. Every other filter would have to fetch every shard, so the common case gets *worse*: the same total bytes, now as N round trips with N parse steps. And §6 is right that the boundary is expensive to move once anything external consumes it, which argues for not choosing a bad one quickly.

There is also a measured reason to expect little from encoding alone. A columnar re-encode of the whole payload — dictionaries for publisher, places, topics and hostname, dates as integer day-offsets, titles and URL paths as newline-joined blobs, slugs stripped of their redundant date prefix — was prototyped and measured at **5.08 MB raw / 1.74 MB gzip against the present 7.03 MB / 2.24 MB**. That is a 28% cut raw and 22% gzipped: real, worth having, and nowhere near enough. At 40,000 it still lands at 12.1 MB raw and 4.2 MB gzipped. **You cannot encode your way out of shipping 40,000 titles and 40,000 URLs**, and those two columns plus the slug are 4.36 MB of the present 7.03 MB. The redundancy the dictionaries exploit is redundancy gzip was already exploiting.

## The decision: split the payload where the work splits

**The line to cut along is not the year. It is the difference between the rows the page must *filter* and the rows it must *display*.**

Filtering and sorting need no text at all. Date, place, topic, entity, publisher, artefact flag and body-completeness are all small closed vocabularies or integers, and the entity column is already dictionary-encoded for exactly this reason. Displaying needs title, URL and slug — but only for the hundred rows actually on screen.

Measured on the present catalogue, the two halves are of completely different orders:

| half | now | gzip | at 40,000 | gzip |
|---|---|---|---|---|
| **filter index** — dates, places, topics, entities, publisher, artefact, completeness, plus every vocabulary | 1.26 MB | **0.33 MB** | 3.0 MB | **0.79 MB** |
| **row text** — title, URL, slug | 4.29 MB | 1.47 MB | 10.3 MB | 3.5 MB |

So:

- **Ship the filter index up front**, fetched rather than `<script src>`. 0.79 MB gzipped at 40,000, and integers parse in milliseconds where a source literal does not. Every facet, every combination of facets and every sort runs against it with no text in memory. This is the number that makes the decision: **it is still under a megabyte at 40,000, and it would still be tractable at 100,000.**
- **Fetch row text in fixed chunks**, in the stored order (date-descending), only for rows about to be drawn — about 128 KB raw per 500 rows. A reader who filters to eleven results fetches the chunks those eleven live in and nothing else.
- **Move title search onto the `names/` mechanism.** This is the part that already exists. Free-text search is the one operation that appears to need every title in the browser, and the answer is the machinery running today for 208,000 entity names: tokenise titles at build time into prefix shards posting document ids, fetch one shard per query. `build-names-index.py` and the page's `refreshNames()` are the working model, down to the degradation behaviour when a fetch fails. Titles are a smaller problem than names were.
- **Render the first screen at build time.** The newest ~100 rows and the facet menus are known when `catalogue.py` runs; bake them into `index.html` and upgrade to live filtering when the index lands. This is the move that matters most for the long run, because it **decouples time-to-useful from corpus size permanently** rather than setting a second threshold to be rediscovered at 80,000.

**Deep links must survive unchanged.** Filter state travels in the URL fragment and those URLs are citable in the same sense everything else here is; a reader arriving on a fragment gets the baked first screen, then the index, then the filtered result. Nothing about the fragment's grammar changes.

## What happens to the other three files

**`raw-catalogue.csv` does not change at all.** It is the citable public artefact and `design.md` §9's named exception to the edition rule — undated, republished wholesale, sixteen columns. Nothing here touches it, and the export's byte-parity with it (`test_catalogue_export.py`, the BOM, the CRLF) stays exactly as it is.

**`raw-catalogue.json` should go.** It exists for one purpose: the export cuts a sixteen-column selection from it by slug. `index.html`'s own comment weighs the three options and rejects packing the five missing fields into the payload on the grounds that it would tax every visitor to serve an export most never ask for. That objection dissolves once the payload is chunked — the five fields ride the row-text chunks, which are only fetched for rows the reader actually has. Dropping it takes ~31 MB off the published site and ~6.6 MB off every build's permanent git history, and removes the second consumer §6 was worried about pinning the format.

**`names/` should move off GitHub Pages to R2, behind the Worker that is already there.** At 40,000 it is ~114 MB and ~7,000 files of pure derived data: fetched, never cited, never linked, reproducible from `outputs/` in one command, and about to be joined by a title index of the same shape. It is the single largest thing on the site with no claim to be there. `documentation/cloudflare.md` has the account, the zone and a Worker in production; this is an extension of a thing that works, not a new dependency. **That one move returns more headroom against the 1 GB ceiling than everything else in this note combined.**

## What is a defect and what is a feature

The freeze runs to 2026-09-27 and the test is *wrong* against *missing* (`CLAUDE.md` → *The freeze*).

**Everything architectural above is missing, not wrong.** The page works, it will keep working through October, and nothing on the site is currently stating something false because of it. It is a feature and it waits for 2026-09-28. Deciding it now is the point of writing this down — the decision is the part that was blocking, and it should not be made in a hurry in November.

**Two things are wrong now and are fixable inside the freeze:**

- `RENDER.md` Step 5: *Expect ~10,700 records*. A stated expectation that cannot be right, printed past on every render.
- `design.md` §6, first bullet: the 30,000-by-spring-2027 projection, contradicted by this repo's own log. Strike it and point here.

`RENDER.md` line 141 is also drifting — *~208,000 names in ~1,900 shards* against 4,655 shards on disk — and should be restated as a fact about the last build rather than a fixed expectation, or dropped.

## What this leaves open

**The editions layer, which is the real ceiling problem.** 814 MB of the site's 924 MB is `reports/` and `topics/`, and this note does nothing about it. Retention is already conditional on somebody having downloaded the file (`design.md` §9, `prune-editions.py`), so the cheap move has been made. The next one is probably the same one recommended for `names/` — the dated PDFs are citable artefacts, but a citable artefact does not have to be served from the same origin as the page, and the Worker is already in the path of every download. That is a bigger decision than this one and wants its own note.

**Whether the browse payload's chunk boundary is a public commitment.** The chunks are fetched by the page and by nothing else, so on the face of it they are private and re-choosable. That was true of `raw-catalogue.json` too, right up until the export started reading it. State plainly, in `catalogue.py`, that the chunk files are internal and carry no stability promise — the whole-catalogue CSV is the supported way to consume this data — or the boundary will acquire a second consumer the same way the last one did.
