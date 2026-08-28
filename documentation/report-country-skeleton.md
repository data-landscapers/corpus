---
type: spec
title: report-country-skeleton.md — the shape and drafting contract for country reports
last_reviewed: 2026-08-28
status: in force; Corpus-owned
---

# report-country-skeleton.md — the shape and drafting contract for country reports

**This is the knob for what a country report looks like.** Section order, front matter, word budget and the instructions given to a drafting agent live here, in one file, so tuning the shape is one edit rather than fifty. **The register is not here** — house style is the Corpus editorial register (`documentation/report-layer.md` → §10 *The register*), in one copy, because a region or topic report is the same kind of document about a different unit and three copies of a style guide drift. `documentation/report-region-skeleton.md` was written from this one and inherits the register rather than restating it.

**Change it, then `python scripts/report-render.py --unit {ISO3} --rerender`** — tables rebuild from `ledger.csv`, narrative blocks carry across by marker id, nothing is re-read from the base. A format change costs a render, not a redraft.

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

**The sections are the taxonomy's ten Level-1 chapters, in `lookups/taxonomy.csv`'s sort order.** There is no section map to consult and none to maintain: a row's subject has exactly one Level-1 parent, and that parent is the chapter it prints under. (A second grouping of the same vocabulary is one too many — two maps disagree about where a subject belongs, and deriving the section from the subject makes disagreement unrepresentable. The `section` column survives in `ledger.csv`, kept in step by `normalise_ledger()`, but nothing renders from it.)

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

**The headings are identical across all three documents** so they read side by side, and an empty section in one is visible rather than hidden. **A section with no ledger rows is written as one sentence saying so** — never padded, never silently dropped.

**Within a section, the renderer sub-groups by taxonomy Level-2 subject** — a `###` sub-heading with the subject's `taxonomy.csv` label, in the taxonomy's own order. Status and progress get one small table per subject; monthly gets one narrative marker per subject, keyed `{section-key}--{subject-slug}` (dots become hyphens). A subject with no rows, or no moved rows that month, gets no sub-heading and no block. `ledger.csv` is kept sorted the same way (Level-1, Level-2, name) by the renderer on every load.

The unwritten section blocks left by the six-section → ten-chapter migration are drafting work, counted by check L; `documentation/narrative-backlog-four-chapters.md` is the work list.

## What goes in each document, and what must not

- **Status** — state only. Each section opens with the **inventory table**: *system or instrument · status · as at*, where *as at* is the milestone that fixed the position, never a bare date. Then prose on what the position *is* and why. **No chronology.** The test: a sentence that would read oddly six weeks from now belongs in the monthly.
- **Monthly** — events between the first of the month just closed and the date of issue, dated and cited. **No table**: a table of rows that moved restates the ledger without telling a reader what happened. **No maturity verdicts** — that is the status report's job.
- **Progress** — the **movement table**: *system or instrument · at {start} · at {end} · movement*, the two middle cells carrying the **substance** of the position rather than its label. Then prose on what moved. It is the only one of the three that can truthfully say nothing changed, and it must be willing to.

**Neither window stops at the month's close** (`report-layer.md` §2): both run to the day the issue is cut. Print the true period; never let the month in the title stand in for it.

Where one object belongs in more than one document: the monthly carries **what moved**, the status **what it means for the current position**, the progress report **the delta**. One deliberate repetition is allowed where the same fact is the hinge of two documents.

## Register

`documentation/report-layer.md` → §10 *The register*, in one copy, binding every report the layer issues. What stays here is what a country report does differently — its sections, its budget, its drafting contract.

## Word budget

**Prose only, tables excluded: 1,000–1,450 words for a status report, 700–2,000 for a monthly.** The monthly's ceiling is per document rather than per block because a quiet month should still be short; the floor of a useful block is ~46 words — the fact of a movement *with* the qualification that makes it evidence.

**The progress report is budgeted per indicator, not per document: 8–40 words for an indicator summary, 25–200 for an indicator developments** (`documentation/progress-report-redesign.md`). A country's progress prose is one entry per indicator that carries evidence, and how many that is depends on what the base holds — five for a thin country and eighty for a thick one, both correct; a whole-document band would fail one of them for the state of the base rather than the state of the writing. The **summary** band is a layout constraint first — the table shows it in a cell, and a summary past forty words is a paragraph in a cell. The **developments** text sits behind the row's expander, where length costs the reader nothing until they ask — room for two to four dated events at roughly thirty words an event. Neither band applies to a ***No evidence*** row, which carries no prose: the value is the statement.

Count prose with links reduced to their anchor text (`re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', body)`); counting raw markdown scores URL path segments as words.

## Markers

```markdown
<!-- narrative: {section-key} -->
…model-authored prose…
<!-- /narrative -->
```

Everything outside the markers belongs to the renderer and is overwritten without warning. Everything inside belongs to the model and is never touched by a script.

## The drafting contract — what a delegated agent is given and must return

Partition **by section**, not by file count: each agent takes one section, its subject slugs, and the intersection pages that carry them. Three to four agents in parallel is the practical ceiling; each runs 60–160k tokens.

Every agent prompt carries these six, verbatim in substance:

1. **The output shape, exactly** — a ledger row per system or instrument (`name | status | milestone | position_start | position_end | movement | source-slug`), then six to ten dated facts formatted `fact — [slug]`, then anything the wiki itself flags as unreconciled. Agents follow a format specification closely; a vague request comes back as an essay.
   - **`name` is a named object, short enough to scan** — *National Radio Frequency Plan 2026*, not *cybersecurity of state information systems*. Ask for the thing, not the topic.
   - **`milestone` is the event that fixed the position**, not the date it happened.
   - **`position_start` and `position_end` carry substance, not labels.** Where the base establishes the thing did not exist at the start, the cell says `Did not exist` — a fact, and not the same as ***Baseline not held***.
2. **Resolve slugs yourself** against the index (`scripts/vault_lib.py`), and **if a slug is not there, say so and drop the claim** — never reconstruct a plausible URL. A source with no `url:` field is correctly uncitable, not a bad slug.
3. **Report absence rather than filling it.** A thin or absent evidence base is a finding to report, not to pad over — this produces the single most useful output of a run, and the default behaviour without it is balanced-looking prose over nothing.
4. **Both ends dated, always** — even for a status report. **Ask explicitly what the base said about each row twelve months ago**: the same status carried earlier is `since` and is *not* movement; a different status is movement; nothing at all is ***Baseline not held***. An agent not asked returns only the newest date, and the progress report then reports the ledger's build date as a year of change.
5. **No web search. Local files only.** An agent that helpfully fetches a fresh source has broken the sweep containment boundary and put unadmitted material into a deliverable.
6. **The Corpus editorial register (`report-layer.md` → §10), in full**, wherever the agent writes narrative. An agent given a shape and no register writes to the register it thinks a report on Africa wants, which is the magazine one; pasting the rules costs a few hundred tokens and editing them out afterwards costs a redraft.
