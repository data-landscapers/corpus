---
type: spec
title: report-country-skeleton.md — the shape and drafting contract for country reports
last_reviewed: 2026-08-14
status: in force; Corpus-owned. Ported from OSINT's `wiki/` on migration; the register now points at the Corpus one
---

# report-country-skeleton.md — the shape and drafting contract for country reports

**This is the knob for what a country report looks like.** Section order, front matter, word budget and the instructions given to a drafting agent live here, in one file, so tuning the shape is one edit rather than fifty. **The register is not here** — house style is the Corpus editorial register (`documentation/report-layer.md` → §10 *The register*), in one copy, because a region or topic report is the same kind of document about a different unit and three copies of a style guide drift. `REPORT-COUNTRY.md` governs the process and `documentation/report-layer.md` the record layer all three report processes share. `documentation/report-region-skeleton.md` was written from this one and inherits the register rather than restating it; the topic skeleton will do the same.

**Change it, then `python scripts/report-render.py --unit {ISO3} --rerender`** (the renderer is shared by all three processes and reads this process's section map) — tables rebuild from `ledger.csv`, narrative blocks are carried across by marker id, and nothing is re-read from the base. A format change costs a render, not a redraft. *(Until the renderer exists — task 31 — a change here applies to the next report written.)*

---

## Front matter

```yaml
---
title: {Place or subject} — {document type}{, period}
compiled: YYYY-MM-DD          # the render date
period: YYYY-MM-DD to YYYY-MM-DD   # monthly and progress only
place: ISO3                   # or subject: slug, for a topic report
ledger_rows: N                # script-emitted
not_held: N                   # script-emitted; the count a reader is owed
---
```

## Sections, in this order

**The sections are the taxonomy's ten Level-1 chapters, in `lookups/taxonomy.csv`'s sort order** *(Bill, 2026-08-25: "re-order as per lookups\\taxonomy.csv")*. There is no section map to consult and none to maintain: a row's subject has exactly one Level-1 parent, and that parent is the chapter it prints under.

| # | Heading | Holds |
|---|---|---|
| — | Summary of position / of the month / of the period | The three or four things a reader who stops here must have. Prose only, no table. |
| 1 | Governance | `gov.*` |
| 2 | Finance | `finance.*` |
| 3 | ICT Infrastructure | `infra.*` |
| 4 | DPI | `dpi.*` |
| 5 | Digitalisation | `digital.*` |
| 6 | Technology | `tech.*` |
| 7 | Capacity | `capacity.*` |
| 8 | Inclusion | `include.*` |
| 9 | Data | `data.*` |
| 10 | Geopolitics | `geopol.*` |
| — | Gaps to fill / Where the record is thin | The ***Not held*** rows, with what would settle each. Status and progress only. |

**What this replaced, and why the replacement is not merely a re-sort.** Until 2026-08-25 the renderer read `lookups/report-country-sections.csv`, a second grouping of the same 38 subjects into six sections of its own. Two groupings of one vocabulary is one too many, and the cost was not only that a country's three reports opened on a different chapter from the `STATUS-INIT` baseline sitting beside them on the same page. The two maps **disagreed about where a subject belonged**: `gov.legislate` printed under *Infrastructure* and `dpi.govtech` under *Governance and regulation*, and a subject the map named twice printed its sub-heading twice in one document. Deriving the section from the subject makes both unrepresentable. The `section` column survives in `ledger.csv` and is kept in step by `normalise_ledger()`, but nothing renders from it.

**The headings are identical across all three documents** so they read side by side, and an empty section in one of them is visible rather than hidden. **A section with no ledger rows is written as one sentence saying so** — never padded to parity with a thick one, and never silently dropped.

**Within a section, the renderer sub-groups by taxonomy Level-2 subject and prints a `###` sub-heading with that subject's `lookups/taxonomy.csv` label, in the taxonomy's own order** *(added 2026-08-10; the labels and the order both moved from `taxonomy.md` to `taxonomy.csv` on 2026-08-25)*. Status and progress get one small table per subject rather than one table for the whole section; monthly gets one narrative marker per subject, keyed `{section-key}--{subject-slug}` (dots replaced with hyphens). A subject with no rows, or no moved rows for that month, gets no sub-heading and no block — the drafter is never handed an empty box for a topic with no news. `ledger.csv` is kept sorted the same way (Level-1 then Level-2, then name) by the renderer on every load, so the file itself reads in taxonomy order.

**Four chapters arrived carrying no prose, and closing them is drafting work.** *Data*, *Digitalisation*, *Capacity* and *Geopolitics* had no section of their own under the six-section map — their subjects sat inside *Digital public infrastructure*, *Governance and regulation*, *Inclusion and capacity* and *AI and the technology sector*. The prose written under those headings crossed to the chapter it was written for (`report-render.py` → `LEGACY_SECTION_KEY`), which leaves **206 unwritten section blocks across 54 progress reports**, plus the equivalent on the fourteen ledger-rendered status reports. Check L counts them and BUILD closes them; nothing was lost, and splitting a paragraph between two chapters to pre-fill them would only have published the same sentences twice.

## What goes in each document, and what must not

- **Status** — state only. Each section opens with the **inventory table**: *system or instrument · status · as at*, where *as at* is the milestone that fixed the position (`Gazetted 2026-07-24`, `Submissions close 2026-08-21`, `Deferred to 2028/29`), never a bare date. Then prose on what the position *is* and why. **No chronology.** The test: a sentence that would read oddly six weeks from now belongs in the monthly.
- **Monthly** — events between the first of the month just closed and the date of issue, dated and cited. **No table**: a table of rows that moved restates the ledger without telling a reader what happened. **No maturity verdicts** — that is the status report's job.
- **Progress** — the **movement table**: *system or instrument · at {start} · at {end} · movement*, where the two middle cells carry the **substance** of the position rather than its label — `30 branches, five banks (2025-08)` against `296 branches, four banks`. Then prose on what moved. It is the only one of the three that can truthfully say nothing changed, and it must be willing to.

**Neither window stops at the month's close** (`documentation/report-layer.md` §2): both run to the day the issue is cut, so the document carries the nightly catch to the day it was written. Print the true period; never let the month in the title stand in for it.

Where one object belongs in more than one document: the monthly carries **what moved**, the status carries **what it means for the current position**, the progress report carries **the delta**. One deliberate repetition is allowed where the same fact is the hinge of two documents.

## Register

**The Corpus editorial register — `documentation/report-layer.md` → §10 *The register* — in one copy, and it binds every report the layer issues.** Nothing in it is country-specific: a region report and a topic report are the same kind of document about a different unit, and a register held per skeleton would be three copies drifting apart from the day the second is written. What stays here is what a country report does differently — its sections, its budget, its drafting contract.

## Word budget

**Prose only, tables excluded, settled here once so the argument does not recur per document: 1,000–1,450 words for a status report, 700–2,000 for a monthly.**

**The progress report is budgeted per indicator, not per document: 8–40 words for an indicator summary, 25–200 words for an indicator developments.** *(2026-08-26, with the indicator frame — `documentation/progress-report-redesign.md`.)* The 900–1,250 whole-document band it replaces cannot be stated any more, and not because the number moved. A country's progress prose is now one entry per indicator that carries evidence, and how many that is depends on what the base holds — five for a thin country and eighty for a thick one, both correct. A document band would have failed one of them for the state of the base rather than for the state of the writing, which is the one thing a word budget must never do.

The two bands are the two texts §5 of the redesign distinguishes. The **summary** is what the table shows in a column 46% of the page wide, so its ceiling is a layout constraint before it is an editorial one: "a clause or two, hyperlinked on the claim", and a summary running past forty words is a paragraph in a cell. The **developments** text sits behind the row's expander, where length costs the reader nothing until they ask for it, so the band is wide — enough for two to four dated events each carrying its own citation at the house rate of roughly thirty words an event, and generous at the top because an indicator in a year of real reform genuinely has more to say than one that moved once.

Neither band applies to a ***No evidence*** row, which carries no prose at all: the value is the statement.

*(Cut from 1,800–2,200 / 900–1,300 / 1,400–1,800 on 2026-08-04, when the inventory and movement tables took over the reference load. A status table of seventy-odd rows is itself ~900 words; prose that also recites the inventory is prose restating a table. The prose's job is what the table cannot carry — why a position is where it is, what is unreconciled, and what follows. Cut ~100 again the same day, with the `Comment` section and the framing sentences the register now rules out.)*

*(**The monthly's ceiling went to 2,000 on 2026-08-14** *(Bill)*. The 1,050 it replaced was calibrated against a monthly that selected on `as_at`; `published` selects roughly twice as many rows, so the document now carries a narrative block for about twice as many subjects — a median of 17, and 39 on Nigeria. At the house average of ~46 words a block the old ceiling was unreachable for any active unit: Nigeria's monthly stood at 962 words with 18 of its 39 blocks still empty. The choice was a higher ceiling or ~25 words a subject, and 25 words buys the fact of a movement while dropping the qualification that makes it evidence — that no lawful basis is stated, that the figure is the promoter's own. The ceiling is per document rather than per block because a quiet month should still be short.)*

Count prose with links reduced to their anchor text (`re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', body)`); counting raw markdown inflates a 1,950-word document to 2,350 by scoring URL path segments as words.

## Markers

```markdown
<!-- narrative: {section-key} -->
…model-authored prose…
<!-- /narrative -->
```

Everything outside the markers belongs to the renderer and is overwritten without warning. Everything inside belongs to the model and is never touched by a script. Same convention as `HUB-COMPILE.md`, for the same reason.

## The drafting contract — what a delegated agent is given and must return

Partition **by section**, not by file count: each agent takes one section, its subject slugs, and the intersection pages that carry them. Three to four agents in parallel is the practical ceiling; each runs 60–160k tokens.

Every agent prompt carries these six, verbatim in substance:

1. **The output shape, exactly** — a ledger row per system or instrument (`name | status | milestone | position_start | position_end | movement | source-slug`), then six to ten dated facts formatted `fact — [slug]`, then anything the wiki itself flags as unreconciled. Agents follow a format specification closely; a vague request comes back as an essay.
   - **`name` is a named object, short enough to scan** — *National Radio Frequency Plan 2026*, not *cybersecurity of state information systems*. Ask for the thing, not the topic.
   - **`milestone` is the event that fixed the position**, not the date it happened.
   - **`position_start` and `position_end` carry substance, not labels.** Where the base establishes the thing did not exist at the start, the cell says `Did not exist` — that is a fact, and it is not the same as ***Baseline not held***.
2. **Resolve slugs yourself** against `index/` (`scripts/vault_lib.py`), and **if a slug is not in the index, say so and drop the claim** — never reconstruct a plausible URL. A source with no `url:` field is correctly uncitable, not a bad slug.
3. **Report absence rather than filling it.** "Where the wiki holds little or nothing on a topic, say so explicitly — a thin or absent evidence base is a finding I want reported, not padded over." This produces the single most useful output of a run; the default behaviour without it is balanced-looking prose over nothing.
4. **Both ends dated, always** — even for a status report. Requiring a dated position at each end is what stops an agent inventing a baseline it does not have, and it costs the agent almost nothing. **Ask explicitly what the base said about each row twelve months ago**: the same status carried earlier is `since` and is *not* movement; a different status is `prior_*` and is; nothing at all is ***Baseline not held***. An agent that is not asked will return only the newest date, and the progress report then reports the ledger's build date as a year of change.
5. **No web search. Local files only.** An agent that helpfully fetches a fresh source has broken the sweep containment boundary and put unadmitted material into a deliverable.
6. **The Corpus editorial register — `documentation/report-layer.md` → §10 *The register* — in full**, wherever the agent writes narrative rather than ledger rows. An agent given a shape and no register writes to the register it thinks a report on Africa wants, which is the magazine one; pasting the rules costs a few hundred tokens and editing them out afterwards costs a redraft.
