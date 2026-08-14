---
type: spec
title: report-layer.md — what every Corpus report process shares
last_reviewed: 2026-08-14
status: in force; Corpus-owned. Adapted from OSINT's `wiki/report-layer.md` on migration (documentation/migration-report-layer.md)
---

# report-layer.md — what every report process shares

*(Corpus owns the report-and-analysis layer. This file is the spec BUILD.md's stage 4 works to, and the record layer the report scripts implement. It was adapted from OSINT's `wiki/report-layer.md` when the layer moved — the ledger, the vocabularies, the gaps rule and the marked blocks are carried across substantially unchanged, because they are what the scripts already enforce; OSINT's §2 nightly-and-hub framing and its §10 register are not, and what replaced them is noted where they stood.)*

**One layer, several processes.** Country reports and region reports (six `X__` codes, which are first-class places) are built; the topic layer is not yet written. This file holds what all of them call, so a second and third process cost a run procedure and a skeleton rather than a re-derivation.

**A process may issue fewer than three documents.** A region issues the **progress report** only, and `scripts/report-render.py` refuses the other two for an `X__` unit rather than making every caller branch. Nothing else here changes: one ledger, one cadence, one register, one set of checks.

Each process owns: its unit, its outstanding list, its section layout, its skeleton, and its initialisation shell. Everything below is common and lives here in **one copy**.

---

## 1. The ledger is the record layer

`outputs/reports/{unit}/ledger.csv` — one row per **system or instrument**, which is the unit these reports are actually about (a payment rail, a statute, a registry, a programme, a policy draft). `{unit}` is an ISO-3 code, a region code, or a taxonomy slug. It is **maintained, never rebuilt**: each run updates rows and adds new ones, and git holds every prior state.

**A row is a named object with a position that can move, not a topic the news covered.** *National Radio Frequency Plan 2026* is a row; *cybersecurity of state information systems* is not. *Blocked identity numbers* is a row, because it is a dated measure of a named register and both ends can be stated; *device affordability* is not. The test before adding a row: could a reader name the thing, and could its position be different next quarter? If the answer to either is no, the material belongs in the prose, not the ledger. **This is the difference between a report on systems and an audit of news stories**, and it is the failure the format was rebuilt to prevent.

| Column | Meaning |
|---|---|
| `row_id` | Stable handle, `{unit}-{subject}-{short-slug}` — never reissued, never renamed. Published at launch. |
| `place` | ISO-3 or `X__` from `countries.csv`. A topic ledger carries the place per row; a country ledger repeats its own. |
| `subject` | One `taxonomy.md` slug. |
| `section` | Report section, from the process's own section map (overridable per row). |
| `kind` | `instrument` (default) — a named system or instrument, which appears in both the status inventory and the movement ledger. `measure` — a dated measure of one (blocked identity numbers, a breach notification rate, delivered data-centre load), which moves and so belongs in the **progress report only**; it carries no status and is never listed as current state. |
| `name` | The system or instrument as a reader would name it. **Short enough to scan** — no qualifying clause, which belongs in `note` or in the prose. |
| `status` | A status stem from §3, optionally followed by a comma and a qualifying clause: `Implemented, under appeal`. |
| `as_at` | The date the status is asserted *from* — the event date in the source, never the publication or compile date. |
| `milestone` | What the status table prints in its third column: the **event that fixed the position**, not a bare date — `Gazetted 2026-07-24`, `Submissions close 2026-08-21`, `Deferred to 2028/29`, `No appropriation line found`, `Since 1998`. Falls back to `as_at` when empty, which should be rare. |
| `position_start`, `position_end` | What the progress table prints at each end of the window: **the substance of the position, not its label** — `30 branches, five banks (2025-08)` against `296 branches, four banks`. Where the base establishes the thing did not exist at the start, say so: `Did not exist`, `None published`, `No date`. |
| `since` | The date the base first puts the row in its **current** status, where that is earlier than `as_at` — a row whose latest source only refreshes a figure has not moved. Empty means `as_at` is the first record of this position. |
| `prior_status`, `prior_as_at` | The last different position, with its date. **One prior only** — supersession is not contradiction. |
| `movement` | A movement stem from §3, optionally followed by a comma and a qualifying clause: `Advanced, slipped`. |
| `sources` | Source slugs, `\|`-separated, resolved to URLs at render time through OSINT's `index/` (read-only). |
| `probe_at` | For a ***Not held*** row: the date the gap was last searched for (§4). Empty on a held row. |
| `note` | One clause, only where the row needs a caveat a reader would otherwise ask for. |

**A row's `as_at` is a fact about a source, not about the run.** A run that reads twenty sources and changes no row is a correct outcome, and it is the normal one.

**The file is kept sorted by taxonomy Level-1 then Level-2, then name.** `scripts/report-render.py`'s `resort_ledger()` re-orders it on every load, rewriting only when the order actually changes. Content, `row_id`s and column order are untouched; only row position moves, which is what makes `ledger.csv` diff-readable and scannable in the taxonomy's own order rather than in whatever order a run happened to add rows.

**`since` is what stops a first build reading as a year of upheaval.** Without it, every row whose newest source falls inside the window renders as ***Baseline not held***, and a progress report says nothing about the place — only about the date the ledger was cut. A row is only baseline-less when the base genuinely carries no position for it before the window opened.

**The three documents are renderings of this file, not drafts.** *Status* renders the current rows, *monthly* renders what changed in the window, *progress* renders `prior_*` against current. That is why a monthly update carries everything needed to refresh the other two, and why the same ledger sliced the other way is a different report at no extra reading.

## 2. Cadence — the calendar names the issue, change decides whether there is one

**The ledger is updated whenever the base moves; a document is issued only when the ledger moved.**

- **At initialisation, all three are issued together.** The first build is the one run that reads the whole base for a unit; it establishes the current position, the position a year back and the month's events in a single pass, and the second and third documents are then a render each. Issuing only the status report saves nothing — it defers the same reading to a run that has to do it under time pressure, on a unit whose baseline was never cut. **The expensive thing is reading the base, and it is paid once.** *(Initialisation is a deferred stage in Corpus — BUILD.md → Deferred stages. The current ledgers are the accepted baseline.)*
- **On every build**, at BUILD.md stage 4: `report-scan.py` names the initialised units holding sources the layer has not looked at, a model reads only those sources against the ledger, and any row they move is moved. A unit with nothing unconsidered is skipped without being read; a place with no ledger is skipped whatever arrived, because this pass never initialises. **The set of unconsidered sources is a set difference over slugs, not a date window**, so an interrupted build resumes cleanly and nothing is re-read.
- **The status report is refreshed on any build where a row moved.** Its filename carries no period and it answers *where is this now*, so leaving it stale while the ledger moves underneath it is the failure the layer exists to prevent — and re-rendering costs a render, because the tables rebuild from the ledger and only the moved sections' prose is edited.
- **The monthly update and the progress report are issued on the first build after a month closes**, for the month just closed. Both carry a period in their filename, and a document a reader can cite by date must not be rewritten for the month it is still inside. New sources that move nothing produce **no issue** — the run records `nil, unchanged` and stops. This is what makes the full set affordable: a typical month is ~500 country-tagged sources across ~51 places, a median of 8–10 each, most of which report activity rather than movement.

**Both dated windows open on a month boundary and close on the day of issue.** A monthly runs from the first of the month just closed to the date it is cut; a progress report runs from twelve months before that same opening to the same date. The base is swept nightly upstream, and being current to the day is the thing these reports have that a quarterly review does not — a July monthly issued on 4 August that stopped at 31 July would sit on four days of evidence it already held and release them a month later, in a document about August. **The days between the month's close and the issue therefore appear in two consecutive monthlies**, in the one that was current enough to carry them first and again in the one whose month they belong to. That is the intended cost, and it is why the header prints the true period rather than the month's name alone.

**A late issue widens its window; it does not stale.** Lateness is still worth avoiding — a monthly that runs six weeks is a monthly in name only — but the failure mode is a mislabelled document, not an out-of-date one.

**An issued document's period is fixed at the moment it is cut.** The renderer reads back the `period:` line of a document that already exists, so a re-render for a format change, or a re-run of an interrupted build, never widens a document a reader may already have cited. `--end` overrides, and is for re-cutting a period that was printed wrong.

**`compiled:` changes only when the record changes** *(Bill, 2026-08-14)*. It is the date the document last **changed**, never the date the build last **ran**. A render that would produce a document identical to the one on disk therefore leaves the file alone: the old date stands, the mtime does not move, and nothing enters the diff. `report-render.py` compares the two with the date masked, so the date can never itself be the thing that makes a document look changed.

This is the same discipline as `period:` above, applied to the other dated field. While every render rewrote every file the date was true of the run and false of the document, which put 165 files into every commit and left nothing downstream able to tell which of them had actually moved. **Making the date true is BUILD's whole obligation here**; what reads it afterwards is not BUILD's concern.

**What the build must never become is a chronology.** The report layer moves *positions*; events live in the dated source pages that cite them.

**Significance is a ledger question, not an editorial one.** "Not significant enough to change the report" means *no row's status, date or figure changed* — a test a script applies, not a judgement made afresh each run.

## 3. The two vocabularies

**Status** — *Implemented* (in operation or in force) · *Piloting* (limited user group or controlled environment) · *In development* (build or drafting under way, not operating) · *Planned* (announced or provided for, nothing on record being built) · *Enacted* (an instrument passed into law — pair with a qualifying clause for its in-force date, e.g. *Enacted, in force 2027-01-23*) · *Under review* (a law or policy currently being reconsidered) · *Discontinued* (closed or superseded) · ***Not held*** (the base carries no reliable statement).

**Movement** — *Advanced* (a system entered service, a stage completed, an instrument was made) · *Stalled* (a stated target passed without delivery) · *Regressed* (an instrument withdrawn or neutralised, or a measured position worsened) · *Closed* (the programme ended) · *No change* (the position at both ends is the same, and that is a finding) · ***Baseline not held*** (the base carries no position at the start of the period, so no movement can be stated).

Both lists are the authoritative statement of `report-render.py`'s `STATUSES` and `MOVEMENTS` tuples, and a change to one is a change to the other.

**Both vocabularies are stems, not fixed strings.** A value may be followed by a comma and a short qualifying clause where the plain stem would mislead: *Implemented, under appeal* · *Enacted, in force 2027-01-23* · *Planned, not proceeding* · *Advanced, slipped* · *Advanced, marginal* · *Advanced in scope, regressed in access*. Check I tests the stem. Without the qualifier, real progress against a moved deadline gets recorded either as success or as failure and both are wrong.

**A system that did not exist at the start of the window is *Advanced*, not a special value** — the fact goes in `position_start` as `Did not exist` or `None published`, where a reader can see it. Reserve ***Baseline not held*** for what the base genuinely cannot say. Putting a coverage fact into the movement column makes it read as a finding about the country rather than about the record.

**A dated, searched absence is `**Not held**, searched {probe_at} — {what looked and found nothing}`, not a bare `Not held`.** The bare stem reads as "the base carries no reliable statement" — a gap in the record — which is the opposite of the finding when a probe has actually confirmed the thing does not exist. No new closed value is needed: the qualifying-clause mechanism above covers it, and the row still counts as `Not held` for the gaps tally, which is correct — no document is held either way.

Both are **closed vocabularies**, restated in each document immediately before first use, because no reader can infer the boundary between *Planned* and *In development*. The not-held markers are set in bold italic so they read as a different kind of value: their function is to be counted, published and chased. **Publish the not-held count** — it tells the reader exactly how much weight the document bears.

## 4. Gaps — a ***Not held*** row is a research brief, and it is the one thing that crosses the boundary

A gap is an **absence**, and it is a named question — the best possible input to a sweep. It is also the only Corpus→OSINT channel there is.

1. The run writes every ***Not held*** row to `outputs/reports/{unit}/gaps.csv` — the row's `name`, `subject` and one line on what would settle it.
2. **The run does not probe.** It records the gap and stops. Corpus does not fetch, and it does not write to OSINT: a gap that names a document Corpus wants goes to the machine-readable request feed, `logs/requests-for-osint.csv`, which OSINT reads on its own schedule. Two sources found disagreeing are not a gap at all — they are a contradiction, and belong in OSINT's queue by the same feed. **Nothing published at all** is a dated absence stated on the page it bears on, which is a finding.
3. **`probe_at` records the date a gap was last searched for**, and it is what makes a published absence one that was searched on a date. A ***Not held*** row whose `probe_at` is empty has been noticed and not yet searched, which is a true statement of the record and reads correctly in the gaps file. *(Ownership of `probe_at` moves to Corpus with the ledger at Phase 3 — migration-report-layer.md. Until the request feed is stood up, it is filled from what OSINT stamped.)*
4. Whatever the feed brings back enters OSINT's `raw/` through its own ingest, and Corpus's next scan sees the new source arrive and settles the gap itself. Nothing is written into a report from a source Corpus has not seen in `raw/`.
5. An unfilled gap is not re-raised while its request stands open, and is re-raised only **when that unit's base moves** — a re-search over an unchanged base returns the same nothing at full price.

That is the closed loop: report → gaps → request feed → OSINT sweep → ingest → `raw/` → ledger → next report. **Nothing in a Corpus build blocks on OSINT having acted.**

## 5. The marked blocks

Everything a script owns is outside the markers; everything a model owns is inside them:

```markdown
<!-- narrative: {section-key} -->
Prose here. Every interpretive sentence carries its citation.
<!-- /narrative -->
```

**No document carries an unwritten narrative block, in any form** *(Bill, 2026-08-14)*. The renderer no longer mints `_(narrative not yet written)_` — it emitted readable prose into a document a reader may download, which is a note-to-self escaping into the deliverable — and an unwritten block is now emitted **empty**. Empty is not a licence: check L fails on an empty block exactly as it fails on the old placeholder, because both say a section was published with nothing said about it. Where a block has no prose, BUILD.md → *Narrative integrity* governs: remove the section, or write the sentence that explains why there is no suitable narrative. There is no third option and no circumstance in which one is available.

**Every table row carries its citation on the cell that makes the claim** — the status cell in a status table, the end-position cell in a progress table — hyperlinked to the first of the row's `sources` that resolves through `index/`. Not the name: the name is the object, the status is the claim, and the claim is what a reader checks. A ***Not held*** or ***Baseline not held*** cell is never linked: there is nothing behind it, which is what the marker says.

**The narrative carries its own citations, including where the same source is already linked in the table above it** *(Bill's ruling, 2026-08-05)*. A dated claim in prose is linked on the claim, not left to a reader to match against a row. The duplication is the point: **prose is read on its own** — quoted, extracted into the published work, or reached by someone who scrolled past the table — and a paragraph whose evidence lives only in a table it no longer sits beside is a paragraph nobody can check. Link the claim, not the sentence: one link where the fact is asserted, not a citation after every clause.

**The monthly update carries no table.** It is prose by section, each paragraph a run of dated and cited developments. A table of rows that moved restates the ledger without telling a reader what happened, and it is what turns a monthly into an audit.

**Within a section, every process sub-groups by taxonomy Level-2 subject, in the taxonomy's own order.** Status and progress print one small table per subject, each preceded by a `###` sub-heading carrying that subject's taxonomy label — a section's rows are never combined into one table across subjects. Monthly prints one narrative block per subject, keyed `{section-key}--{subject-slug}` (dots become hyphens: `dpi--dpi-pay`), each under its own `###` sub-heading.

**An empty section or sub-section is not printed at all, and the status report is the only exception** *(Bill, 2026-08-14)*. A subject with no rows — or, for monthly, none that moved in the window — gets no sub-heading and no block; a **section** with nothing in it gets no heading either, in the monthly and the progress report. The drafter is never handed an empty box, and a reader is never given a heading with nothing under it.

The status report alone states the absence, in a sentence the renderer writes: *"The base holds no {section} rows for {place}. A thin evidence base is a finding, not a gap in this document."* That is the difference the exception turns on. In a status report "nothing on this subject" is a finding **about the place**, and a known vacuum is worth publishing. In a monthly it is a finding about the **window** — nothing moved this month — which is not news, and in a progress report it is a statement about the ledger's coverage rather than about progress. *(The status report is due a major overhaul, which may revisit this.)*

**Changing a section's marker granularity is not free on an already-issued document.** Status and progress keep a per-section marker id (`{section-key}`), so a re-render carries their prose across exactly as this section promises. Monthly's marker id is per-subject, which is not backward-compatible with the older per-section scheme: re-rendering a monthly issued under the old scheme finds no existing block under the new keys and mints empty ones, orphaning the old prose. Migrating the pre-existing monthlies is drafting work, not a script, and is registered as a housekeeping job.

**Figures are script-emitted from the ledger.** A number written by hand inside a narrative block is a defect, and check H catches it. A table refresh must never touch prose, and a prose refresh must be a clean diff. It is also what lets a **format change re-render every existing report without re-reading the base** — narrative blocks are carried across by marker id.

## 6. Verification

Corpus takes the checks that verify its own outputs — **A** (finance CSVs rebuild from records), **D** (financier display names), and **G–K** below. The hub checks (B, C, E, F) verify OSINT's private wiki and stay there. Verification never compiles.

- **G. Every link is held.** Each URL in a rendered report must be present in `index/`. **Non-optional, and re-run after every edit pass, not once at the end** — a URL synthesised from a remembered pattern is indistinguishable from a real one by inspection, and exactly that happened while the first three reports were drafted. Set membership is the only test that catches it.
- **H. Prose agrees with the ledger.** Every figure and status word in a narrative block must appear in the ledger rows of that section. **Two figures are exempt and only two**: a count the renderer itself emits (row totals, the shape check), because restating it cannot disagree with it; and a figure attributed inline to a named reference study, which is cited and **not** absorbed — putting it in a row would promote a survey into current state.
- **I. Vocabulary.** No status or movement value outside §3; every ***Not held*** row present in `gaps.csv`; the not-held count in the document equals the ledger's.
- **J. As-of honesty.** No document dated ahead of its newest source, and no period comparison issued without the shape check recorded.
- **L. No unwritten narrative.** `report-render.py --check` fails on any narrative block that is empty or still carries the old placeholder. Unlike K this **fails rather than reports**: a register hit can be a quoted source and needs a person to rule, but there is no reading of an unwritten block under which the document is finished. BUILD owns this, because BUILD owns what is fit to publish.
- **K. Register and budget.** `python scripts/report-register-check.py` reads the narrative blocks — never the tables, where a ledger `name` is the object's name and not the report's prose — and reports register terms, any surviving `## Comment` heading, and any document outside its skeleton's word budget. **It reports; a person rules.** Under the Corpus register a connecting sentence is not a defect, so this check informs rather than gates. The budget is read from the skeleton so there is one knob, and the script exits 2 rather than pass silently if that line is reworded past it.

**A report that fails G is not published, ever.** The others report and are fixed.

## 7. Shape check before any period comparison

Count the unit's sources per month across the window **before** promising a comparison. **Where the earlier half is thin, either narrow the window or say plainly in the document that it is a shorter comparison wearing a longer label** — with the counts, once, near the top. Each process's initialisation shell prints this and flags the cliff; the check is worthless run after drafting.

## 8. Byproducts — the pass is a defect detector

Forcing every claim through a resolution step finds what nothing else looks for: a source held twice under two slugs, an artefact with no `url:` and therefore uncitable, a closed contradiction confirmed still closed. **Emit them in the run** — as numbered notes in `logs/notes-for-osint.md`, since the defects are in OSINT's evidence and Corpus cannot fix them there. They cost nothing to collect while passing and are never found by going looking.

## 9. Files and versions

```
outputs/reports/{unit}/ledger.csv                  # the record layer, maintained
outputs/reports/{unit}/gaps.csv                    # not-held rows, with probe dates
outputs/reports/{unit}/{unit}-status.md            # current position — stable name, git holds prior issues
outputs/reports/{unit}/{unit}-monthly-YYYY-MM.md   # one dated issue per month, never overwritten
outputs/reports/{unit}/{unit}-progress-YYYY-MM.md  # one dated issue per window, never overwritten
outputs/reports/{unit}/considered.txt              # slugs the ledger has looked at — the set difference §2 works over
```

**The status report keeps a stable filename and the dated issues are immutable.** A published status page needs a URL that does not move and its history is in git; a monthly *is* an issue. Nothing here is a source: reports are derived views, never cited by a wiki page, never re-ingested into OSINT.

These constraints bind **from public launch**, not retroactively — nothing in `outputs/` was ever public before the migration, so the layer was free to be re-cut clean (migration-report-layer.md → *What we agreed*).

## 10. The register

**The Corpus editorial register governs the prose, and it is stated once, in `documentation/migration-report-layer.md` → *Corpus editorial register* (v0.3, light touch).** It is not restated here, because a register in two files is a register that drifts from the day the second is written.

What sits here is only the boundary it does not move. The **evidential spine stays exactly as disciplined as OSINT's**: the ledger, the tables, every dated figure, the published *Not held* count — script-emitted, cited, honest about gaps. A reader must always be able to **take the facts and refuse the reading**. A declared position raises the cost of an unchecked figure; it does not lower it.

**No document in this layer carries a comment section.** The argument belongs downstream, in the published work these reports feed. A labelled comment section also acts as a licence: prose written towards a verdict at the end leaks the verdict into the body.

**The prose never narrates the ledger.** "Twenty-three rows moved this month" and "58 entered the record" are facts about the document, not about the unit, and they are what turn a report into an audit of its own sources. Write about the systems.
