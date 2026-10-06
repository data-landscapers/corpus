---
type: procedure
reader: cc
title: maturity-study-method.md — how one indicator is studied, staged and written up, in two phases around OSINT's ingest
last_reviewed: 2026-10-06
status: proposed by Cowork with Bill's rulings of 2026-10-06, for CC's operational review; first used by maturity/health/maturity-study-health.md; not yet run
---

# A maturity study: one indicator, worked whole

*(Bill, 2026-10-06: the assessment is rebuilt topic by topic, indicator by indicator. The scale, the null and the as-at rule of `documentation/archived/maturity-assessment.md` §3 and §7 still hold.)*

## 0. What a study is

**One indicator, all 54 countries, two phases with OSINT's ingest between them.** Phase 1 defines, reviews, searches and hands over. Phase 2 re-reads, stages and writes: a stage, a short summary and a long summary per country per sub-indicator. Triggers: "**run maturity study {id}**" and "**run maturity study {id} phase 2**".

**Where things live** *(Bill)*:

| What | Where |
|---|---|
| This method and anything generic | `maturity/documentation/` |
| A study's file and its working files | `maturity/{id}/` |
| What a study issues | `outputs/maturity/{id}/` |

## 1. Typology before anything is compared

**Settle what the thing is, then classify every system the evidence names.** The study file lists the classes: assessed, noted and not assessed, or out of scope. Where one label hides two things, the indicator splits into sub-indicators, each with its own ladder.

**A country's label is the country's; the class is Corpus's.** Nor is a product a class: classify the deployment by what the source says it does. A system named with no description stays unclassified, a gap for §5.

Output: `systems.csv`, one row per named system per country — `iso3, system, country_label, class, platform, owner, tiers, sources`.

## 2. Aspects

**Each sub-indicator is assessed on a fixed list of aspects, each with one role and a closed list of values.** A **coverage** aspect sets the stage; a **qualifier** can cap or flag it and never raises it.

## 3. How a stage is defined

The rules a study's ladder is written to:

1. **A rung is a coverage test.** The existence of a named system, a strategy or a launch places nothing above Nascent.
2. **Each rung states a value for every coverage aspect**, as a table of rung by aspect, and is met only when every aspect meets it. A drafter decides it from a dated source without interpretation.
3. **Between two rungs, take the lower** and name the missing fact in the short summary.
4. **Stage 1 needs a cited, dated absence.** Evidence that states no coverage aspect leaves the cell unplaced; nothing held is *No evidence*.
5. **Stage 5 is reachable.** A coverage level on a published figure, set from the norm's target where it has one; a statement of alignment is not a test.
6. **A threshold is a share of a stated denominator.** A count without a denominator is a floor and places by the lower rung.
7. **A qualifier carries at most one cap rule and a closed list of flags.**
8. **A coverage fact carries its year**; one older than three years at the as-at still places the country and prints its year in the short summary.
9. **The ladder is drafted before the review, tested on the review's evidence and fixed before Phase 2.** A rung nothing reaches, or one drafters read two ways, is rewritten then; a later change restages every country.

## 4. Phase 1: review what is held

**The reading list is selected by a script and read whole by a drafter.** `scripts/study-select.py {id}` writes `maturity/{id}/evidence/{ISO3}/readlist.csv` from:

- the status report's sub-sections for the study's subjects;
- `ledger.csv` rows and `considered.txt` entries on those subjects;
- every `raw/` document whose `places:` holds the country and whose `topics:` holds a study subject, or whose title or body matches the study's term list;
- regional and continental documents that name the country.

**One drafter per country reads every listed document, not its ledger line**, and writes `evidence.csv` beside the list, one row per stated fact: `row_id, iso3, sub_indicator, aspect, value, fact, as_of, date_precision, system, class, source_slug, url`. A row holds only what its own source states. The event date is not the publication date.

`scripts/study-profile.py` then writes `profile.csv`: per sub-indicator and aspect, the best-evidenced value, its sources and a `gap` cell saying what is not established. Where sources disagree the newest value stands and both are kept.

**The parent verifies files, not tallies**: slugs resolve in `raw/` and sampled facts match the body.

## 5. Phase 1: search for what is missing

**A gap is a coverage aspect with no dated fact inside three years, or a qualifier aspect with nothing in its window.**

**One Exa brief per country per sub-indicator that has a gap.** It names the gaps, gives the held facts as context, and asks in the country's working language for the study's source types, ranked.

**Fetch, capture, dedup, frontmatter and delegation are PROGRESS-FILLER's** (`documentation/archived/PROGRESS-FILLER.md` §0 and §3 to §6). Its cap (§4a) and its folders (§5) are replaced:

- **Relevance selects; there is no numeric cap** *(Bill)*. A fetched document is kept when its body states a dated fact, on an aspect with a gap, that nothing held states; one such fact is enough. Anything else goes to the unselected register.
- **Delivery is a handover in `prepared\`, not a `new-queue\` batch** *(Bill)*: maturity evidence is not general ingest, and OSINT is told so. Candidates are written to `C:\corpus-osint-xfer\prepared\maturity-study-{id}\`, flat with no country folders, each with `sweep_batch: maturity-study-{id}-{ISO3}-YYYY-MM-DD`, `places: [{ISO3}]` and the study's subject first in `topics:`.
- **OSINT's cycle pulls the folder once it carries `READY`, written last** (`notes-for-corpus` 78); file names are unique against `raw/`. One `[ACT]` note in `notes-for-osint.md`, titled *Maturity study {id}: evidence to ingest*, with `Affects: outputs/maturity/{id}/`. The folder's `BRIEF.md` opens by saying it is evidence for maturity study {id} and not general ingest, then gives the count by country, the selection rule, the lane asked for, the lint result and `Closed by: notes-for-osint NNN`.
- **Records in `maturity/{id}/search/`**: `searched.csv` by country and sub-indicator, `staged.csv` by file handed over, and `unselected.csv`. Candidate bodies are never committed in Corpus.

Before the note is written, `python scripts/lint-staged-queue.py` passes over the folder; then the share is committed and pushed.

**Maturity batches take OSINT's backfill lane**: `maturity-study-` is among the prefixes its `scripts/ingest-lane.py` reads.

**Corpus runs the searches and never writes to `raw/`** *(Bill)*. A found document reaches the study only by returning through ingest; delivery is not admission.

**Phase 1 ends** with a commit, a log line and the counts for Bill.

## 6. Between the phases

**Phase 2 waits until the note has moved to `notes-for-osint-resolved.md`** and the mirror's `cycle-manifest.json` is later than the move. `scripts/study-returned.py {id}` then checks every row of `staged.csv` against the mirror's `lookups/raw-url-index.csv` and `rejected-urls.csv`. A document not admitted is not held, and its gap stands. The spent handover is deleted in the same commit.

## 7. Phase 2: stage

1. **Re-read**: admitted documents are read whole into `evidence.csv` and the profiles refreshed.
2. **Fix the as-at**: the last day of the month before Phase 2 opens.
3. **Stage from the ladder**: the coverage aspects pick the rung, then the cap rule and the flags; `stage_sources` names the `row_id`s that set it, and `cap` the rung a capped cell had reached.
4. **Check that two drafters agree.** A second drafter restages 20 cells, drawn by `study-profile.py --draw`, blind from `evidence.csv`. Below 16 in agreement, the rung that split them is rewritten and every country restaged.

## 8. Phase 2: write

**Short summary: one line, 25 words at most, no link.** The fact that sets the stage with its year, then what is not established.

**Long summary: one paragraph per aspect, in the study's order, each opening with the aspect's name in bold; 120 to 250 words.** `STATUS-INIT.md`'s hard rule and borderline rule apply whole: a link on every claim, and a borderline fact coarsened or dropped. Figures are dated and a country's own label is attributed. Two closing lines: ***Noted, not assessed*** and ***Not held***. `house-style.md` and `AI-speak.md` govern the prose.

Files, in `outputs/maturity/{id}/`:

| File | Holds |
|---|---|
| `assessment.csv` | One row per country per sub-indicator: `iso3, indicator_id, as_at, stage, one column per aspect, cap, flags, short, stage_sources, gaps` |
| `systems.csv` | The typology, §1 |
| `{ISO3}.md` | The long summaries |
| `{indicator_id}.md` | Cross-country page: norm, ladder, then stage, short summary and linked evidence per country |

`scripts/study-render.py` writes the pages from the CSVs. `scripts/lint-study.py` holds them: a row for every cell, a stage or a reason, every source and link held in `raw/`, the short summary inside its cap, and the cap rule applied wherever it fires.

**Nothing is published to `site/` and the frame is not touched until Bill accepts the study.** On acceptance, rows are retired and minted under `adding-an-indicator.md` §2 and §10, and the study's CSV is the baseline edition.

## 9. The study file

`maturity/{id}/maturity-study-{id}.md` answers §1 to §5 for one indicator, names the frame rows it redraws, and says whether the norm measures what the sub-indicators measure. `study.json` beside it restates its lists as data for the scripts.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
