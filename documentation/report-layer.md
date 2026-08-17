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
| `published` | **The publication date of the most recent record the row cites** *(Bill, 2026-08-14)*, and the field every period selects on. `raw/` names sources by publication date, so it is read off the slug. It is not an event date: what fixed the position goes in `milestone`. |
| `milestone` | What the status table prints in its third column: the **event that fixed the position**, not a bare date — `Gazetted 2026-07-24`, `Submissions close 2026-08-21`, `Deferred to 2028/29`, `No appropriation line found`, `Since 1998`. **This is where the event date lives.** It has no fallback: a row without one prints an em-dash, because `published` is when a source reported the position and printing it here would claim it was when the position was fixed. |
| `position_start`, `position_end` | What the progress table prints at each end of the window: **the substance of the position, not its label** — `30 branches, five banks (2025-08)` against `296 branches, four banks`. Where the base establishes the thing did not exist at the start, say so: `Did not exist`, `None published`, `No date`. |
| `since` | The date the base first puts the row in its **current** status, where that is earlier than `published` — a row whose latest source only refreshes a figure has not moved. Empty means the cited record is the first to report this position. |
| `movement` | A movement stem from §3, optionally followed by a comma and a qualifying clause: `Advanced, slipped`. |
| `sources` | Source slugs, `\|`-separated, resolved to URLs at render time through `outputs/catalogue/raw-catalogue.csv` (Corpus's own, built in stage 2 from `raw/`). |
| `probe_at` | For a ***Not held*** row: the date the gap was last searched for (§4). Empty on a held row. |
| `note` | One clause, only where the row needs a caveat a reader would otherwise ask for. |

**A row's `published` is a fact about a source, not about the run.** A run that reads twenty sources and changes no row is a correct outcome, and it is the normal one.

**`published` is what ages a row out of a report.** A report is a curated selection of `raw/` records, period-selected by publication date; putting that date on the row makes the ledger the one place both the monthly and the progress report are aged from, and month turnover a matter of the window moving past a value already held. It replaced `as_at`, an event date the drafter wrote by hand and left empty on 744 rows, every one of which fell out of every window however recently it had been reported.

**The file is kept sorted by taxonomy Level-1 then Level-2, then name.** `scripts/report-render.py`'s `resort_ledger()` re-orders it on every load, rewriting only when the order actually changes. Content, `row_id`s and column order are untouched; only row position moves, which is what makes `ledger.csv` diff-readable and scannable in the taxonomy's own order rather than in whatever order a run happened to add rows.

**`since` is what stops a first build reading as a year of upheaval.** Without it, every row whose newest source falls inside the window renders as ***Baseline not held***, and a progress report says nothing about the place — only about the date the ledger was cut. A row is only baseline-less when the base genuinely carries no position for it before the window opened.

**The three documents are renderings of this file, not drafts.** *Status* renders the current rows, *monthly* renders the rows whose `published` falls in the window, *progress* compares each row's `position_start` against its `position_end`. That is why a monthly update carries everything needed to refresh the other two, and why the same ledger sliced the other way is a different report at no extra reading.

## 2. Cadence — the windows slide, and a document changes only when the ledger moves

**The ledger is updated whenever the base moves; a document changes only when the ledger moved.**

- **At initialisation, all three are issued together.** The first build is the one run that reads the whole base for a unit; it establishes the current position, the position a year back and the month's events in a single pass, and the second and third documents are then a render each. Issuing only the status report saves nothing — it defers the same reading to a run that has to do it under time pressure, on a unit whose baseline was never cut. **The expensive thing is reading the base, and it is paid once.** *(Initialisation is a deferred stage in Corpus — BUILD.md → Deferred stages. The current ledgers are the accepted baseline.)*
- **On every build**, at BUILD.md stage 4: `report-scan.py` names the initialised units holding sources the layer has not looked at, a model reads only those sources against the ledger, and any row they move is moved. A unit with nothing unconsidered is skipped without being read; a place with no ledger is skipped whatever arrived, because this pass never initialises. **The set of unconsidered sources is a set difference over slugs, not a date window**, so an interrupted build resumes cleanly and nothing is re-read.
- **The status report is refreshed on any build where a row moved.** Its filename carries no period and it answers *where is this now*, so leaving it stale while the ledger moves underneath it is the failure the layer exists to prevent — and re-rendering costs a render, because the tables rebuild from the ledger and only the moved sections' prose is edited.
- **The monthly and the progress report move with their windows**, on every build. The monthly's window opens on the first of the last closed month; the progress report's opens twelve months before that. Both close on the day the document last changed. New sources that move nothing change nothing — the file is left untouched. This is what makes the full set affordable: a typical month is ~500 country-tagged sources across ~51 places, a median of 8–10 each, most of which report activity rather than movement.
- **A month in which nothing moved still issues a monthly, and the monthly says so** *(Bill, 2026-08-14)*. The run used to record `nil, unchanged` and write nothing, which was right while a monthly was a dated issue nobody was obliged to cut. It is wrong for a living document: writing nothing leaves the *previous* month's update on disk under its own heading, so a quiet place publishes a stale page instead of the finding that it was quiet. The renderer writes the absence in its own voice and mints no narrative block, because an absence of movement is a finding the ledger settles and not an empty box to hand a drafter.

**Both windows open on a month boundary and run to the present.** The base is swept nightly upstream, and being current to the day is the thing these reports have that a quarterly review does not — a monthly that stopped at the month's last day would sit on evidence it already held. **The monthly therefore always spans a month boundary**: on 14 August it covers 1 July to 14 August, which is what "this month and last month" means. The header prints the true window rather than a month's name, because the window is what the document actually covers.

**Nothing is ever closed to new evidence** *(Bill, 2026-08-14)*. A record belongs in the window its **publication date** falls in, whenever it is ingested — a record published in July and ingested in mid-August is July's news and goes into the monthly while July is still in the window. Once a window has slid past that date the record still moves the ledger, and still shows in the status report and in the progress report's twelve months; the monthly is simply no longer the document that covers it.

**The scan is a labour-saving gate, not the limit of BUILD's authority.** `report-scan.py`'s set difference exists so a build need not re-read what it has already read. It does not define what BUILD may revisit. BUILD authors this layer and holds editorial control over it: where a document can be made better — a narrative never written, a section that reads badly, a row the prose does not serve — BUILD revises it, whether or not a script nominated the unit that day. A pass that only ever touches what the gate hands it is a pass that cannot improve anything it has already been past.

**`compiled:` changes only when the record changes** *(Bill, 2026-08-14)*. It is the date the document last **changed**, never the date the build last **ran**. A render that changes nothing leaves the file alone: the old date stands, the mtime does not move, and nothing enters the diff. This is the same discipline as `period:` above, applied to the other dated field, and **making the date true is BUILD's whole obligation here** — what reads it afterwards is not BUILD's concern.

**The date is judged against a stored digest, `record:`, not against the file on disk.** Comparing the render to the file looks sufficient and is not, because the renderer carries the narrative across *from that same file*: a drafter who writes prose into a block and re-renders produces output identical to what is already there, so a file-to-render comparison sees nothing and the date stands still while the document changes. `record:` is a short hash of the document with `compiled:` and `record:` themselves taken out, written at the same moment the date is; the prose is part of the content, so prose entering a block changes the digest whoever wrote it and by whatever route.

This is the failure the field exists to prevent, and it has happened: on 2026-08-13, 116 dated PDFs were overwritten in place because their bodies had moved while `compiled:` had not (`scripts/render.py`). A date that can stand still through a change is worse than no date, because everything downstream trusts it.

**A document with no stored digest is stamped with the date of the build that gives it one** *(Bill, 2026-08-14)*. There was briefly a migration rule here that kept the existing date wherever the fresh render matched the file on disk, so that introducing the field would neither back- nor forward-date anything. It could not work. With no digest to compare against, it fell back to comparing the render with the file — the exact mistake the paragraph above rejects, since the renderer carries the prose across *from that file*, so hand-written prose reproduces itself and the comparison sees nothing. It was caught on `SLE-progress.md`, whose prose was edited on 2026-08-14 and which kept a compiled date of the 10th, and it would have swallowed the whole drafting backlog: writing prose into a narrative block is precisely the change it could not see, and that is BUILD's main work. Stamping the build date is exact from the following build onward and wrong only in the safe direction, on the single build where the field arrives.

**The window's closing date is a property of the last change, not of the last build** *(Bill, 2026-08-14)*. A document that did not change keeps the window it already prints, even where the build ran days later — so `period:` and `compiled:` move together or not at all. The alternative is worse: the close is printed in six places (`period:`, the title, the heading, the opening paragraph and, in the progress report, every movement table's header), and letting it track the build date would move the digest daily and stamp a new `compiled:` on every document every night, which is the churn this section exists to prevent. **Selection still runs to today** — a record published this morning is in scope, and anything it moves brings both dates forward together — so a frozen close can only ever *understate*. It never claims evidence the document does not hold.

The cost is worth stating plainly, because it is what the site has to explain: a build that reads new sources and finds that **nothing moved** is the normal outcome, and it leaves the close where it was. The printed window therefore understates not only what exists but what was *read* — a reader could take a development published after the close to have been out of scope when it was in fact considered and judged not to have moved a position. `considered.txt` is the record of what was read. The window is the period the document **draws on**; `compiled:` is the day it last changed; neither is a claim that nothing happened afterwards. The close comes back into line at every month turnover, since a window that has slid onto a new month is a different document and re-renders on its own.

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

**Every table row carries its citation on the cell that makes the claim** — the status cell in a status table, the end-position cell in a progress table — hyperlinked to the first of the row's `sources` that resolves through the catalogue. Not the name: the name is the object, the status is the claim, and the claim is what a reader checks. A ***Not held*** or ***Baseline not held*** cell is never linked: there is nothing behind it, which is what the marker says.

**The narrative carries its own citations, including where the same source is already linked in the table above it** *(Bill's ruling, 2026-08-05)*. A dated claim in prose is linked on the claim, not left to a reader to match against a row. The duplication is the point: **prose is read on its own** — quoted, extracted into the published work, or reached by someone who scrolled past the table — and a paragraph whose evidence lives only in a table it no longer sits beside is a paragraph nobody can check. Link the claim, not the sentence: one link where the fact is asserted, not a citation after every clause.

**The monthly update carries no table.** It is prose by section, each paragraph a run of dated and cited developments. A table of rows that moved restates the ledger without telling a reader what happened, and it is what turns a monthly into an audit.

**Within a section, every process sub-groups by taxonomy Level-2 subject, in the taxonomy's own order.** Status and progress print one small table per subject, each preceded by a `###` sub-heading carrying that subject's taxonomy label — a section's rows are never combined into one table across subjects. Monthly prints one narrative block per subject, keyed `{section-key}--{subject-slug}` (dots become hyphens: `dpi--dpi-pay`), each under its own `###` sub-heading.

**An empty section or sub-section is not printed at all, and the status report is the only exception** *(Bill, 2026-08-14)*. A subject with no rows — or, for monthly, none that moved in the window — gets no sub-heading and no block; a **section** with nothing in it gets no heading either, in the monthly and the progress report. The drafter is never handed an empty box, and a reader is never given a heading with nothing under it.

The status report alone states the absence, in a sentence the renderer writes: *"The base holds no {section} rows for {place}. A thin evidence base is a finding, not a gap in this document."* That is the difference the exception turns on. In a status report "nothing on this subject" is a finding **about the place**, and a known vacuum is worth publishing. In a monthly it is a finding about the **window** — nothing moved this month — which is not news, and in a progress report it is a statement about the ledger's coverage rather than about progress. *(The status report is due a major overhaul, which may revisit this.)*

**Changing a section's marker granularity is not free on a document that already exists.** Status and progress keep a per-section marker id (`{section-key}`), so a re-render carries their prose across exactly as this section promises. Monthly's marker id is per-subject, which is not backward-compatible with the older per-section scheme: rebuilding a monthly written under the old scheme finds no existing block under the new keys and mints empty ones, orphaning the old prose. Migrating the pre-existing monthlies is drafting work, not a script, and is registered as a housekeeping job.

**Figures are script-emitted from the ledger.** A number written by hand inside a narrative block is a defect, and check H catches it. A table refresh must never touch prose, and a prose refresh must be a clean diff. It is also what lets a **format change re-render every existing report without re-reading the base** — narrative blocks are carried across by marker id.

## 6. Verification

**The old `REPORT-LINT` splits along a seam already inside it** *(Bill, 2026-08-13)*: **checks A–F stay in OSINT**, next to what they verify — they reconcile the finance and hub compiles against `raw/`, and a check belongs beside the records it reads, not beside the export it produced. **Checks G–K travel here**, because they verify the report layer, which is Corpus's. Verification never compiles.

Every check the layer claims is now implemented: G, I, J, L and M in `report-render.py --check`, H and K in `report-register-check.py`.

- **G. Every link is held.** Each URL in a rendered report must be present in `outputs/catalogue/raw-catalogue.csv` — the published catalogue of everything `raw/` holds, which is Corpus's own committed artefact and the same file a reader can download. *(2026-08-14: this used to resolve through OSINT's `index/`. The catalogue is built from that index in stage 2 and the two were verified identical — 9,404 URLs, over all 5,189 slugs the 57 ledgers cite — so what changed is which copy the layer trusts, not what it accepts. `report-render.py` refuses to resolve against a catalogue `raw/` has moved past, counted as well as timed, since a deletion moves no mtime.)* **Non-optional, and re-run after every edit pass, not once at the end** — a URL synthesised from a remembered pattern is indistinguishable from a real one by inspection, and exactly that happened while the first three reports were drafted. Set membership is the only test that catches it.
- **H. A figure in narrative prose has a source.** `report-register-check.py` reports any narrative block that carries a substantive figure — money, a percentage, a count of a thousand or more — and no citation at all. **It asks only that a source exists** *(Bill, 2026-08-14)*. It does not open the source, does not compare the figure against it, and does not ask which sentence a given citation belongs to. Provenance, not fact-checking. The block is the unit: a block carrying citations is sourced prose, and working out which one covers which figure is the fact-check this deliberately is not. It reports and a person rules, as K does.

  **This replaced a rule that could not have worked.** §6 used to require that every figure and status word in a block appear in that section's ledger rows. Three things were wrong with it. It was an unscoped copy of a check OSINT ran and retired — `LINT.md` records the line-level money scan running *"~90% false-positive"* until it *"stopped being read"*, and `REPORT-LINT.md`'s check E refuses the domestic block for the same reason, *"nearly every honest sentence in it holds a figure that sits in no single record cell"*. It contradicted §2 below: the build must never become a chronology, so a monthly's prose carries event detail — a launch, an outage, a count — that is deliberately **not** a ledger position, and the old rule made every such sentence a defect while complying with it would have promoted events into rows. And its own reference-study exemption already conceded the principle, exempting that figure precisely because it carries its own citation. **The ledger is one route to a source, not the definition of one.** OSINT's settled definition is the one used here: a wikilink to a dated `raw/` slug, or an inline URL.

  Scope follows the same reasoning: check the prose that has no provenance machinery of its own. The tables have theirs — M that a row cites something, G that what it cites is real. On the current corpus this reports **67 blocks**, against 1,601 carrying prose.
- **I. Vocabulary.** No status or movement value outside §3; every ***Not held*** row present in `gaps.csv`; the not-held count in the document equals the ledger's.
- **J. As-of honesty.** `report-render.py --check`. Two things, and only the first can fail. **A document compiled before the newest `published` on its ledger is stale** — BUILD moved a row and did not rebuild, so the document renders a position the base has already moved past. That is the same question OSINT's check C asks of a hub, asked of a report, and answered against the data rather than a file mtime, which does not survive a clone. It fails because the fix is a re-render. **And every progress report must carry its shape check** (§7), which `render_progress()` emits unconditionally, so this asserts that it stayed.

  **The direction this rule was written in is now governed at the cause, and is reported rather than judged** *(2026-08-14)*. "No document dated ahead of its newest source" was aimed at the old behaviour where every build stamped `compiled:` with the render date — a document could claim today while holding nothing since July, and the gap widened by a day, every day. The window-close rule in §2 ended that: the close and the date move only when the document does. What is left is a real but truthful lag, since a document can change for a structural reason without new evidence, and a window running to a quiet tail is a true statement about a real period. The check prints the gap and rules on nothing, because any threshold on it would be invented.
- **L. No unwritten narrative.** `report-render.py --check` fails on any narrative block that is empty or still carries the old placeholder. Unlike K this **fails rather than reports**: a register hit can be a quoted source and needs a person to rule, but there is no reading of an unwritten block under which the document is finished. BUILD owns this, because BUILD owns what is fit to publish.
- **M. Every piece of evidence has a source, and the source resolves.** `report-render.py --check` fails on any ledger row that states a position and cites nothing, on any row citing a slug the base does not hold, and on any row where no cited slug carries a URL a reader could follow. **A source has to resolve, not merely be typed** *(Bill, 2026-08-14)*: testing the field for emptiness repeated the same mistake one level down, and passed a row citing a slug with a doubled word that the base does not hold — which rendered exactly as an unsourced row would, no link for G to test and a populated field for M to be satisfied by. The two resolution failures are reported apart because they belong to different people: a slug the base does not hold is a mistake in the ledger, while a slug held without a `url:` is an uncitable record and OSINT's to fix (§8). **This is the rule the layer rests on, not a lint on the ledger** *(Bill, 2026-08-14)*: the base publishes nothing it cannot show the reader where it got. ***Not held*** is the only exemption and is barely one — the marker's meaning *is* that no position is held, so there is nothing to cite and the row carries no link for that reason. **Measures are in scope**: a figure is evidence like any other claim, and check I skips a `kind: measure` row only because it has no status to test against a vocabulary. Neither G nor I could see this gap — an unsourced `Implemented` is inside the vocabulary, and a row with no source emits no link for G to test, so it passed by contributing nothing. It renders as a bare status with no hyperlink, indistinguishable from ***Not held*** while asserting the opposite, which is the one confusion the marker exists to prevent.
- **K. Register and budget.** `python scripts/report-register-check.py` reads the narrative blocks — never the tables, where a ledger `name` is the object's name and not the report's prose — and reports register terms, any surviving `## Comment` heading, and any document outside its skeleton's word budget. **It reports; a person rules.** Under the Corpus register a connecting sentence is not a defect, so this check informs rather than gates. The budget is read from the skeleton so there is one knob, and the script exits 2 rather than pass silently if that line is reworded past it.

**A report that fails G or M is not published, ever.** The others report and are fixed.

**Checks G and M are two halves of one rule: every piece of evidence has a source** *(Bill, 2026-08-14)*. M is that a stated position cites something; G is that what it cites is real. Neither is sufficient alone — a row citing nothing passes G, and a row citing a plausible invention passes M — and together they are the whole of the layer's claim to be evidence-led. This is not negotiable against any other consideration in the layer, including a drafting deadline or a unit the scan did not nominate.

## 7. Shape check before any period comparison

Count the unit's sources per month across the window **before** promising a comparison. **Where the earlier half is thin, either narrow the window or say plainly in the document that it is a shorter comparison wearing a longer label** — with the counts, once, near the top. Each process's initialisation shell prints this and flags the cliff; the check is worthless run after drafting.

## 8. Byproducts — the pass is a defect detector

Forcing every claim through a resolution step finds what nothing else looks for: a source held twice under two slugs, an artefact with no `url:` and therefore uncitable, a closed contradiction confirmed still closed. **Emit them in the run** — as numbered notes in `osint-corpus-exchange/notes-for-osint.md`, since the defects are in OSINT's evidence and Corpus cannot fix them there. They cost nothing to collect while passing and are never found by going looking.

## 9. Files and versions

```
outputs/reports/{unit}/ledger.csv                  # the record layer, maintained
outputs/reports/{unit}/gaps.csv                    # not-held rows, with probe dates
outputs/reports/{unit}/{unit}-status.md            # current position
outputs/reports/{unit}/{unit}-monthly.md           # the monthly report; `period:` states its window
outputs/reports/{unit}/{unit}-progress.md          # the progress report; `period:` states its window
outputs/reports/{unit}/considered.txt              # slugs the ledger has looked at — the set difference §2 works over
```

Every document carries `compiled:` and `record:` in its frontmatter, and the pair is the layer's statement about identity: `record:` says *what this document is*, `compiled:` says *when it last became that*. Neither is ever written by hand.

**There are no issues** *(Bill, 2026-08-14)*. Each unit has one monthly report and one progress report — living documents whose windows slide, not a series of dated editions. Nothing is cut, replaced or superseded; there is no July monthly and no August monthly, only *the* monthly, covering this month and last. `period:` states the window the document now covers, and an earlier state of it is an earlier commit, which is what git is for.

**So no markdown filename carries a period.** All three documents have stable names. Versioning happens where a reader needs it: RENDER dates the PDF and the CSV, which are what a citation points at, and the HTML is not versioned because it is always the current document. A month in the markdown filename versioned the working file rather than the artefact, which is the wrong end.

**Narrative always carries across.** The renderer preserves every block so a rebuild costs a render rather than a redraft; deciding what of it still belongs is BUILD's. Moving a window on is an **edit** — BUILD removes what has aged out and writes in what has arrived — and never a fresh composition, because consecutive windows overlap heavily in both documents. The monthly runs from the first of the closed month to the day it was last built, so it always spans a month boundary; the progress report slides a twelve-month window one month at a time, keeping eleven.

What this leaves is a sentence still describing a period that has moved on: well-formed prose that no check can catch, because there is nothing malformed about it. Finding it is the point of the revision, and it is BUILD's.

**A build that discards prose says so.** A section with nothing in it is not printed, so a rebuild can legitimately drop a section that had writing under it — legitimately, but never silently. The renderer names every block that held prose and was not asked for. This is the one operation in the layer that destroys writing, and it used to be reported as *"N narrative block(s) carried across"*, counting the blocks **found** rather than the blocks **kept**: a build that threw a paragraph away claimed to have preserved it. Git holds the prose either way; knowing it went is the point.

Earlier states live in git, and the dated artefacts RENDER writes are what a citation points at. Nothing here is a source: reports are derived views, never cited by a wiki page, never re-ingested into OSINT.

These constraints bind **from public launch**, not retroactively — nothing in `outputs/` was ever public before the migration, so the layer was free to be re-cut clean (migration-report-layer.md → *What we agreed*).

## 10. The register

**The Corpus editorial register governs the prose, and it is stated once, in `documentation/migration-report-layer.md` → *Corpus editorial register* (v0.3, light touch).** It is not restated here, because a register in two files is a register that drifts from the day the second is written.

What sits here is only the boundary it does not move. The **evidential spine stays exactly as disciplined as OSINT's**: the ledger, the tables, every dated figure, the published *Not held* count — script-emitted, cited, explicit about gaps. A reader must always be able to **take the facts and refuse the reading**. A declared position raises the cost of an unchecked figure; it does not lower it.

**No document in this layer carries a comment section.** The argument belongs downstream, in the published work these reports feed. A labelled comment section also acts as a licence: prose written towards a verdict at the end leaks the verdict into the body.

**The prose never narrates the ledger.** "Twenty-three rows moved this month" and "58 entered the record" are facts about the document, not about the unit, and they are what turn a report into an audit of its own sources. Write about the systems.
