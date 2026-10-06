---
type: procedure
reader: cc
title: maturity-study-method.md — how one indicator is studied, staged and written up, in two phases around OSINT's ingest
last_reviewed: 2026-10-06
status: proposed by Cowork at Bill's request, for CC's operational review; first used by maturity-study-health.md; not yet run
---

# A maturity study: one indicator, worked whole

*(Bill, 2026-10-06: the assessment is rebuilt topic by topic and, within a topic, indicator by indicator. This is the generic procedure; a study file answers it for one indicator, §9. The five-stage scale, the null and the as-at rule of `archived/maturity-assessment.md` §3 and §7 still hold.)*

## 0. What a study is

**One indicator, all 54 countries, two phases with OSINT's ingest between them.** Phase 1 defines, reviews, searches and queues; Phase 2 re-reads, stages and writes. Triggers: "**run maturity study {id}**" and "**run maturity study {id} phase 2**".

**It issues three things per country per sub-indicator**: a stage, a short summary and a long summary.

## 1. Typology before anything is compared

**Settle what the thing is, then classify every system the evidence names.** The study file lists the classes: assessed, noted and not assessed, or out of scope. Where one label hides two things, the indicator splits into sub-indicators, each with its own ladder.

**A country's label is the country's; the class is Corpus's.** Nor is a product a class: classify the deployment by what the source says it does. A system named with no description stays unclassified, a gap for §5.

Output: `systems.csv`, one row per named system per country — `iso3, system, country_label, class, platform, owner, tiers, sources`.

## 2. Aspects

**Each sub-indicator is assessed on a fixed list of aspects, and each aspect has one role.** A **coverage** aspect sets the stage. A **qualifier** aspect can cap a stage or flag it and never raises it. Every aspect takes a closed list of values, so findings compare across countries.

## 3. How a stage is defined

The study file's ladder is written to these rules.

1. **A rung is a coverage test.** The existence of a named system, a strategy or a launch places nothing above Nascent.
2. **Each rung states a value for every coverage aspect**, as a table of rung by aspect. A drafter decides it from a dated source without interpretation.
3. **Rungs are cumulative**: a rung is met only when every coverage aspect meets it.
4. **Between two rungs, take the lower** and name the missing fact in the short summary.
5. **Stage 1 needs a cited, dated absence.** Evidence on the subject that states no coverage aspect at all leaves the cell unplaced; nothing held is *No evidence*.
6. **Stage 5 is reachable.** A coverage level on a published figure, set from the norm's target where it has one; a statement of alignment is not a test.
7. **A threshold is a share of a stated denominator.** A count without a denominator is a floor and places by the lower rung.
8. **A qualifier carries at most one cap rule and a closed list of flags.**
9. **A coverage fact carries its year.** One older than three years at the as-at still places the country, and its year prints in the short summary.
10. **The ladder is drafted before the review, tested on the review's evidence and fixed before Phase 2.** A rung nothing reaches, or one drafters read two ways, is rewritten then; a later change restages every country.

**The norm is discussed, not taken on trust**: the study file says whether it measures what the sub-indicators measure, and what the ladder borrows from it.

## 4. Phase 1: review what is held

**The reading list is selected by a script and read whole by a drafter.** `scripts/study-select.py {id}` writes `prep/study/{id}/{ISO3}/readlist.csv` from:

- the status report's sub-sections for the study's subjects;
- `ledger.csv` rows and `considered.txt` entries on those subjects;
- every `raw/` document whose `places:` holds the country and whose `topics:` holds a study subject, or whose title or body matches the study's term list;
- regional and continental documents that name the country.

It reads `raw/` and `wiki/` through `scripts/.workroot/` and nothing of OSINT's process material.

**One drafter per country reads every listed document, not its ledger line**, and writes `evidence.csv`, one row per stated fact: `iso3, sub_indicator, aspect, value, fact, as_of, date_precision, system, class, source_slug, url`. A row holds only what its own source states. The event date is not the publication date.

`profile.csv` then holds, per sub-indicator and aspect, the best-evidenced value, its sources and a `gap` cell saying what is not established. Where sources disagree the newest value stands and both are kept.

**The parent verifies files, not tallies**: every `source_slug` resolves in `raw/`, and sampled facts are checked against the body.

## 5. Phase 1: search for what is missing

**A gap is a coverage aspect with no dated fact or none inside three years, a governance aspect with nothing, or a twelve-month aspect with nothing in the window.**

**One Exa brief per country per sub-indicator that has a gap.** It names the gaps, gives the held facts as context, states the date range, uses the country's working language, and asks for the study's source types, ranked.

**The machinery is PROGRESS-FILLER's** (`archived/PROGRESS-FILLER.md` §0, §3–§6 and §8), unchanged except:

- **Cap: three documents per country per sub-indicator.** A maximum, never a quota; a nil is a finding.
- **Staging: `C:\corpus-osint-xfer\new-queue\study-{id}-{XUNIT}\`**, flat, one folder per region. `sweep_batch: study-{id}-{ISO3}-YYYY-MM-DD`, `places: [{ISO3}]`, the study's subject first in `topics:`.
- **Records in `logs/study/{id}/`**: `searched.csv` (country, sub-indicator, gaps, briefs, staged, held, nil), `staged.csv` (url, file, country, sub-indicator, aspects) and the unselected register.

**Corpus runs the searches and never writes to `raw/`** *(Bill, 2026-10-06)*. A found document reaches the study only by returning through ingest; delivery is not admission.

Then `python scripts/lint-staged-queue.py`, `READY` written last in each folder, the share committed and pushed, and one `[FYI]` note in `notes-for-osint.md` giving the label, the count and the cap.

**A `study-` batch takes OSINT's backfill lane.** Until `study-` is among the backfill prefixes `scripts/ingest-lane.py` reads, a batch is staged without `READY`. The change is a patch cut by `scripts/osint-patch.py`, delivered once with an `[ACT]` note.

**Phase 1 ends** with a commit, a log line and the counts for Bill: countries reviewed, gaps searched, staged and nil. Phase 2 waits on ingest.

## 6. Between the phases

**Phase 2 opens by asking what came back.** `scripts/study-returned.py {id}` checks every row of `staged.csv` against the mirror's `lookups/raw-url-index.csv` and `rejected-urls.csv`: admitted, rejected or still queued. Phase 2 proceeds when no `study-{id}-…` folder remains in `new-queue/` and the mirror's `cycle-manifest.json` is later than the pull. A document not admitted is not held, and its gap stands.

## 7. Phase 2: stage

1. **Re-read.** Admitted documents are read whole and added to `evidence.csv`; the profiles are refreshed.
2. **Fix the as-at**: the last day of the month before Phase 2 opens.
3. **Stage from the ladder**: the coverage aspects pick the rung, the cap rule is applied, the flags are set. `stage_sources` names the rows that set the stage.
4. **Check that two drafters agree.** A second drafter restages 20 randomly drawn cells blind from `evidence.csv`. Below 16 in agreement, the rung that split them is rewritten and every country restaged. The count is recorded.

## 8. Phase 2: write

**Short summary: one line, 25 words at most, no link.** The fact that sets the stage with its year, then what is not established.

**Long summary: one paragraph per aspect, in the study's order, each opening with the aspect's name in bold; 120 to 250 words.** `STATUS-INIT.md`'s hard rule and its borderline rule apply whole: every fact carries a link on the claim to its source, and a borderline fact is coarsened or dropped. Figures are dated. A country's own label is attributed to it. Two closing lines: ***Noted, not assessed*** and ***Not held***. `house-style.md` and `AI-speak.md` govern the prose.

Files, in `outputs/maturity/studies/{id}/`:

| File | Holds |
|---|---|
| `assessment.csv` | One row per country per sub-indicator: `iso3, sub_indicator, as_at, stage, one column per aspect, cap, flags, short, stage_sources, gaps` |
| `systems.csv` | The typology, §1 |
| `{ISO3}.md` | The long summaries |
| `{sub-indicator}.md` | Cross-country page: norm, ladder, then stage, short summary and linked evidence per country |

`scripts/study-render.py` writes the pages from the CSVs. `scripts/lint-study.py` holds them: every country and sub-indicator has a row, every stage is 1 to 5 or empty with a reason, every source slug and link is held in `raw/`, the short summary is inside its cap, and the cap rule is applied wherever it fires.

**Nothing is published to `site/` and the frame is not touched until Bill accepts the study.** On acceptance, rows are retired and minted under `adding-an-indicator.md` §2 and §10, and the study's CSV is the baseline edition.

## 9. The study file

`documentation/maturity-study-{id}.md` answers, for one indicator: the question and the frame rows it redraws; the classes and sub-indicators; the aspects, their roles and values; the ladder and cap rule; the norm; the subjects and term list; the source types to search for; and what is Bill's to rule.

## Boundary

Nothing here writes to `C:\OSINT`: a missing document is a candidate in `new-queue/`, a script change a patch OSINT applies.
