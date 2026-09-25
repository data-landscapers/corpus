---
type: decision
reader: cc
title: catalogue-serving-shape.md — how the catalogue is served at 40,000 records
last_reviewed: 2026-09-04
status: decided; carried out in full 2026-09-08 — see archived/catalogue-split-plan.md
---

# The serving shape of the catalogue

> **Done, 2026-09-08 — all four parts, in one day.** `documentation/archived/catalogue-split-plan.md`
> is the record of the work; this file is the decision and the argument for it.
>
> **What the numbers came out at.** The filter index is **0.68 MB gzipped at 20,267 records, so
> ~1.34 MB at 40,000** — measured, and it survives the hero column. A reader pays **0.73 MB gzipped
> before the first draw against 3.73 MB**, an 80% cut, and the first screen is in the markup so the
> page draws with JavaScript off entirely. `raw-catalogue.json` is gone from the site.

*(This resolves the first bullet of `design.md` §6, *Serving shape of the catalogue*, and supersedes both its projection and the instrument it reached for. Written 2026-09-04 against a catalogue of 16,730 records, to plan for 40,000.)*

## What was measured

Everything below is the built tree at 2026-09-04. The 40,000-record column is a straight ×2.39 scaling, fair because every file is a per-record structure with a fixed vocabulary alongside it.

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

§6 said *~23 MB at the 30,000 records projected for spring 2027*. The log showed **+7,323 records in the 22 days to 2026-09-04, or 333 a day**, which put 30,000 at mid-October 2026 and 40,000 at mid-November; the catalogue was already inside §6's *15–20k rows* band. **A projection written into a design record with no mechanism reading it back is a projection nobody re-checks.**

> **The rate above is a backfill rate, and it is ending — Bill, 2026-09-08.** The forward rate is
> **1,000–2,000 new items a month**. From 20,267 records on 2026-09-08 that puts **30,000 between
> February and July 2027**, and **40,000 between July 2027 and April 2028**. The dates in this note
> are superseded; the *ordering* of the three constraints is not.
>
> **Nothing in the decision changes and the work is already done.** The editions and the shard
> indexes moved to R2, so `site/` is **67 MB against the 1 GB ceiling** rather than 924 MB, and the
> eager payload is 0.73 MB gzipped rather than 3.73 MB: constraint 1 now binds on neither count.
> **This note is kept as the argument, not as a schedule**, and the next figure written into it
> should say what would make it re-checked.

## Three constraints, in the order they bind

They are three, with different deadlines, and the one usually discussed is the last to arrive.

**1. `site/` is 924 MB against a hard 1 GB ceiling.** [GitHub Pages caps a published site at 1 GB](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits) and recommends the source repository stay under the same. Reports (537 MB) and topics (277 MB) fill it — not the catalogue's 72 MB. But the catalogue wants roughly another 100 MB by mid-November against 76 MB of headroom. **This binds first, it binds hardest, and it is not a catalogue problem**: the editions layer needs its own answer, and `prune-editions.py` deleting only what nobody downloaded will not be it for long.

**2. Git history churn, which is invisible in `site/`.** All three catalogue files are rewritten wholesale on every render and committed. At 40,000 that is roughly 17 MB of new, permanently retained blob per build (zlib-compressed, so the gzip figures are the ones to add), plus whatever fraction of the ~114 MB names index churned that night. Call it 6 GB a year of history no prune can reach, because `prune-editions.py` deletes files from the tree and git keeps the blob — as `design.md` §9 says of editions.

**3. The eager payload — §6's problem, and the least urgent of the three.** At 40,000 the page ships 5.4 MB gzipped and then parses a 16.8 MB JavaScript source literal before it can draw anything. The bandwidth is survivable; the parse degrades badly on a mid-range phone, and `ROWS.forEach` then builds a second full-corpus string allocation (`r._s`, the per-row search blob of title + publisher + entity slugs) on top.

## Sharding by year is the wrong instrument

§6 reaches for year-shards because `raw/` is already sharded that way, so the boundary is nearly free.

The boundary is cheap; the *access pattern* makes it wrong. The page's core interaction is to filter and sort **across the whole corpus** — a place, a topic, an entity, a free-text string — and only then look at what came back. A year shard helps only a reader who has already chosen a year. Every other filter would fetch every shard, so the common case gets *worse*: the same bytes as N round trips with N parse steps. And a boundary is expensive to move once anything external consumes it.

Encoding alone does not rescue it either. A columnar re-encode — dictionaries for publisher, places, topics and hostname, dates as integer day-offsets, titles and URL paths as newline-joined blobs, slugs stripped of their date prefix — measured **5.08 MB raw / 1.74 MB gzip against the present 7.03 MB / 2.24 MB**: a 28% cut raw and 22% gzipped, and at 40,000 still 12.1 MB raw and 4.2 MB gzipped. **You cannot encode your way out of shipping 40,000 titles and 40,000 URLs**; those two columns plus the slug are 4.36 MB of the present 7.03 MB, and the redundancy the dictionaries exploit is redundancy gzip was already exploiting.

## Amendment, 2026-09-08 — the hero text, which did not exist when this was measured

**Everything above was measured with no `catalogue_hero` in the payload.** OSINT began filling it in
September: **0 of 13,264 July and August records carry it, and 2,384 of September's 5,630 do — 42%
of the month's intake against 16.9% of the corpus.** It is a one-line summary of the source, ~93
characters, on its way to being on everything.

**Measured, not projected** — the current payload with the field filled in for every record, from
the heroes already written:

| | raw | gzip |
|---|---|---|
| now, hero on 16.9% | 8.87 MB | 2.95 MB |
| same records, hero on 100% | 10.44 MB | 3.73 MB |
| **at 40,000, hero on 16.9%** | 17.55 MB | 5.83 MB |
| **at 40,000, hero on 100%** | **20.65 MB** | **7.38 MB** |

So the third constraint arrives sooner and larger — **37% more than the 16.8 MB / 5.4 MB measured**
— and the three keep their order.

**The decision does not change, because hero text lands entirely on the fetched half of the
split.** It is not a facet, so the filter index is still **~1.3 MB gzipped at 40,000** with it
filled in. Hero joins title, URL and slug in the row-text chunks, taking them from ~128 KB to
**~177 KB per 500 rows**, paid only for rows a reader looks at. **The hero text is an argument for
the split**: unsplit, it is 0.8 MB of gzip every visitor pays before the page draws; split, 50 KB
more on a chunk.

**One correction to the plan below.** Hero is searched as well as shown — `site/catalogue/index.html`
folds it into the per-row search blob (`r._s = r[0] + r[1] + r[12] + r[7] + …`) — so free-text
search on the `names/` mechanism must tokenise **hero alongside title**, not title alone. That is
more text per shard and no change of shape. Missing it would silently narrow what search finds.

**Timing:** hero removed the option of deferring the split again — the payload was growing on two
axes at once, records and columns.

## The decision: split the payload where the work splits

**The line to cut along is not the year. It is the difference between the rows the page must *filter* and the rows it must *display*.**

Filtering and sorting need no text at all. Date, place, topic, entity, publisher, artefact flag and body-completeness are all small closed vocabularies or integers, and the entity column is already dictionary-encoded for exactly this reason. Displaying needs title, URL and slug — but only for the hundred rows actually on screen.

Measured on the present catalogue, the two halves are of completely different orders:

| half | now | gzip | at 40,000 | gzip |
|---|---|---|---|---|
| **filter index** — dates, places, topics, entities, publisher, artefact, completeness, plus every vocabulary | 1.26 MB | **0.33 MB** | 3.0 MB | **0.79 MB** |
| **row text** — title, URL, slug | 4.29 MB | 1.47 MB | 10.3 MB | 3.5 MB |

So:

- **Ship the filter index up front**, fetched rather than `<script src>`. 0.79 MB gzipped at 40,000, and integers parse in milliseconds where a source literal does not. Every facet, combination and sort runs against it with no text in memory. This is the number that makes the decision: **it is still under a megabyte at 40,000, and it would still be tractable at 100,000.**
- **Fetch row text in fixed chunks**, in the stored order (date-descending), only for rows about to be drawn — about 128 KB raw per 500 rows. A reader who filters to eleven results fetches the chunks those eleven live in and nothing else.
- **Move title search onto the `names/` mechanism**, which already exists: tokenise titles at build time into prefix shards posting document ids, fetch one shard per query. `build-names-index.py` and the page's `refreshNames()` are the working model, down to the degradation behaviour when a fetch fails.
- **Render the first screen at build time.** The newest ~100 rows and the facet menus are known when `catalogue.py` runs; bake them into `index.html` and upgrade to live filtering when the index lands. This matters most for the long run, because it **decouples time-to-useful from corpus size permanently** rather than setting a second threshold to be rediscovered at 80,000.

**Deep links must survive unchanged.** Filter state travels in the URL fragment and those URLs are citable; a reader arriving on a fragment gets the baked first screen, then the index, then the filtered result. The fragment's grammar does not change.

## What happens to the other three files

**`raw-catalogue.csv` does not change at all.** It is the citable public artefact and `design.md` §9's named exception to the edition rule — undated, republished wholesale, the column set `build-catalogue.py` defines. The export's byte-parity with it (`test_catalogue_export.py`, the BOM, the CRLF) stays exactly as it is.

**`raw-catalogue.json` should go.** It existed so the export could cut a whole-record selection by slug, because packing the missing fields into the payload would tax every visitor. Once the payload is chunked those fields ride the row-text chunks, fetched only for rows the reader has. Dropping it takes ~31 MB off the published site and ~6.6 MB off every build's permanent git history, and removes the second consumer §6 was worried about pinning the format.

**`names/` should move off GitHub Pages to R2, behind the Worker that is already there.** At 40,000 it is ~114 MB and ~7,000 files of pure derived data: fetched, never cited, never linked, reproducible from `outputs/` in one command, and about to be joined by a title index of the same shape. `documentation/cloudflare.md` has the account, the zone and a Worker in production. **That one move returns more headroom against the 1 GB ceiling than everything else in this note combined.**

## What is a defect and what is a feature

**Everything architectural above was missing, not wrong**: nothing on the site stated something false because of it, so it was a feature, decided early so it would not be decided in a hurry.

**The two things that were wrong** — `RENDER.md` Step 5's fixed record-count expectation and `design.md` §6's spring-2027 projection — are fixed: `RENDER.md` states counts as facts about the last build, and §6 points here.

## What this leaves open

**The editions layer, which is the real ceiling problem.** 814 MB of the site's 924 MB was `reports/` and `topics/`, and this note does nothing about it.

> **Resolved, 2026-09-08 — `documentation/editions-serving-shape.md`.** The same move as for
> `names/`, built together with it: the dated editions and the names shards go to R2 behind the
> Worker at the URLs they already have.

**Whether the browse payload's chunk boundary is a public commitment.** It is not: the chunk files are internal and carry no stability promise, and the whole-catalogue CSV is the supported way to consume this data — stated or the boundary acquires a second consumer, as `raw-catalogue.json` did.

> **Said, 2026-09-08.** `catalogue.py` carries it where it writes them, and `RENDER.md` repeats the
> pointer. The export no longer reads a published file — it rebuilds each record from the chunks —
> so nothing outside the page depends on their shape.
