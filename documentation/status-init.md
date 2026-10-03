---
type: doc
reader: cc
title: Status initialisation — why the procedure is shaped as it is
last_reviewed: 2026-10-03
---

# Status initialisation — why the procedure is shaped as it is

*(Spec for `STATUS-INIT.md`. The runbook says what to run; this holds the reasoning and the history behind it, moved here by housekeeping job 1 on 2026-10-03 as R92 did for the other runbooks.)*

## Where the campaign stands

**All 54 countries carry an authored baseline** (`logs/status-init-progress.csv`; a country counts because its report carries `built_by: STATUS-INIT`, which `scripts/status-progress.py` counts in the reports themselves, so the question cannot be talked out of its answer). The last fourteen — BDI, BWA, COM, DJI, ERI, GMB, GNB, GNQ, LSO, MDG, MLI, MRT, NER, STP — ran on 2026-09-04. Two earlier statements of where the campaign stood were wrong, both written away from the checklist: a docs pass on 2026-08-28 claimed completion at 40, and a later paragraph said it had stopped there.

**Four of the last fourteen were written while their evidence sat in the hand-carry queue.** NER, MRT, STP and MLI had 581 files uningested in `new-queue\` on the day they ran, and they are the four thinnest units. GNQ's queue, drained the same morning, took its catalogued records from 101 to 222. These four are the first candidates for a re-baseline.

The two data inputs stay in `prep/` and are gitignored deliberately: working material for initialisation, so a clean checkout cannot run status-init and does not need to.

## Status is a baseline, and sits outside the collection perimeter

The wiki's machinery — ingest, index membership, the acquisition queue — assumes material is news arriving now. A status report is the baseline the news is read against: it has to be able to say a 1990 law is in force from a source the wiki will never hold, and there is no intention of ingesting ten years of material to make that possible. Two of the wiki's rules therefore do not reach it, and neither is a conflict:

- **The ledger** carries movement over a rolling thirteen months. Status has no window, so this process neither reads nor writes `ledger.csv`.
- **Index membership** (report-layer check G) protects reports compiled from the wiki. Status draws on sources the wiki does not hold by design, so check A widens the set to the evidence the process read.

**Keeping the baseline current is BUILD's job** (`REPORT-UPDATE.md` → *Maintaining the status baseline*). From the moment this process has run on a unit, `report-render.py` drops `status` from that unit's document set: a ledger render of an authored baseline is a total loss reported as a successful build.

## Why borderline evidence is dropped

**The asymmetry is the whole argument.** A gap in the baseline is visible and gets filled the first time someone asks; an error is invisible and propagates into every comparison made against it, indefinitely. The two are not comparable costs, which is why the rule outranks the news and why two equal-tier sources that disagree yield neither figure.

## Why the run fans out by intersection

An intersection's `topics:` span several chapters, so chapter-shaped extraction agents would each re-read most of the base; the intersection is one file, one agent, read exactly once. Writers then work per chapter from pooled facts, never raw wiki text, which is what makes *no link, no claim* enforceable: a writer cannot cite anything not in its slice.

**The harness caps concurrent subagents at 20, and the refusal is silent in the sense that matters.** On the BDI run (2026-09-04) a country with 28 intersections needed 32 extraction agents; the twelve over the cap came back as an error beside nineteen successes, and a run that fires and forgets would have assembled from two thirds of the evidence. Hence the count of `facts/` files against agents before pooling.

**Extraction is where errors get baked in**: a writer never sees a verbatim body, only a fact someone drew from it. Stage 1 therefore returns facts with caveats and dates attached — an internal handoff, never report content.

## The fact schema

Fixed because ten writers consuming an improvised shape is this design's likeliest failure. The extract brief (`documentation/archived/status-init-extract.md`) carries it to the agents.

| Field | Contents |
| --- | --- |
| `fact` | One sentence, plain, statable on the page as written. |
| `as_at` | The date the fact is true of, or `structural`. |
| `slugs` | Every Level-2 slug the fact answers. |
| `url` | The resolved link. A fact without one is not returned. |
| `published` | The source's own publication date — this alone drives the 2024 rule. |
| `publisher`, `title` | Enough to write an acquire line without going back. |
| `origin` | `wiki`, `dpi` or `finance`. |
| `tier` | `primary`, `official`, `reported` or `syndicated` — the kind of source. |
| `caveat` | The qualification the fact cannot safely be stated without. Internal. |
| `confidence` | `solid` or `borderline`, judged with the body in front of the agent. Kept apart from `tier`: a primary source can carry a weak claim. |
| `news` | `true` where an informed reader of this country would not already know it. |

**Pooling** (`status-pool.py`): two facts are one when they state the same thing about the same object; the survivor is `solid` over `borderline`, then better tier, then later `published`, taking the union of the losers' slugs. Every fact gets an owner — the chapter of the first slug listed — and only the owner states it in full, or one coverage number appears four times in four voices. A sub-section that owns nothing has its six best-evidenced shared facts promoted into it; a promoted fact arrives `mine: true` and is stated in full.

**Why the draft path is fixed**: `status-assemble.py` globs `draft/*.md`, and a chapter written anywhere else is invisible to it — the assemble then fails naming all 39 sub-sections as uncarried, and the cause is not in the message. Writers are also handed every sub-section's label and slug comment, including those the pool left empty, which they would otherwise silently drop.

## Inputs, in more detail

- **The hub** (`wiki/places/{ISO3}.md`): frontmatter `topics:`, `## Active topics` and `## Record not held` are the map; `## Recent developments` is chronology, read only to date a claim; `## Financing` is an uncited aggregate. Never read whole (NGA is 301KB).
- **Intersections** are selected on frontmatter `place:`, never by constructed filename — several countries use unexpected prefixes. A thin country (Eritrea: none) is a real outcome.
- **The catalogue, not the index**, resolves slugs: the catalogue is the published set; the index also carries wiki concept pages with a `url:`, which are not sources.
- **The AfDB dataset** (`prep/africa-dpi-data.csv`, about 462 rows a country): only `Variable Id`, `Value Name`, `Year`, `Comments`, `Source urls` matter. The `govtech-*` family resolves to one landing page; some cells concatenate conflicting answers; mojibake is repaired, not described; a sourceless negative is not evidence of absence. Fuller record: `documentation/archived/dpi-data-defects.md`.
- **The Ibrahim Index profiles** (`lookups/iiag-profiles.csv`) are verified against each PDF's cover by `scripts/iiag-profiles.py`; the dataset's `iiag-*` rows carry no URL and are read against the profile.

## Sources: why *held* is the test

Framing acquisition on whether the catalogue holds a URL makes it checkable — set membership, which `status-check.py` performs. A source dated before 2024 that is not held is baseline material outside the perimeter; one from 2024 on is a gap in the sweep. `africa-acquire.csv` is one file for all of Africa; a run rewrites only its own country's rows, and the `status` and `notes` columns are Bill's and survive every rewrite — a file that loses working state on regeneration is a report, not a worksheet. OSINT's worked rows live in `acquire-done.csv`, and a row is in exactly one of the two files, so both are read; answering a line does not un-find the gap that produced it.

## Writing: who it is for

Someone who follows this country, skimming for what they did not already know. A section that walks the checklist in order and reports what everyone knows has failed, however accurate. A hedged sentence is worse than a missing one: it costs the reader the same attention and pays nothing.

## Context budget

The fan-out removes the ceiling: an extraction agent's context is bounded by the largest single file (about 55KB), and writers see extracted facts. The parent holds the map, the lists, the pooled facts and the assembled file. **What fills the parent is reading the finished report**, which check H requires; combine countries in one session only where the reports are short enough to read properly.

## Why A, B and G are gates

A synthesised link is undetectable by eye, so set membership (A) is the only test that catches one; `report-render.py --check` applies the same widened set through one implementation in `scripts/status_lib.py`, so the two cannot drift. B and G fail a report that hedges or talks about its own evidence, because such a report has stopped being skimmable, which is the only thing it is for.
