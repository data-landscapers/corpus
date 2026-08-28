---
type: spec
title: report-layer.md — what every Corpus report process shares
last_reviewed: 2026-08-28
status: in force; Corpus-owned
---

# report-layer.md — what every report process shares

**One layer, several processes.** Country reports, region reports (six `X__` codes, which are first-class places) and topic reports are all built and publishing. This file holds what all of them call, so a new process costs a run procedure and a skeleton rather than a re-derivation. Each process owns its unit, its outstanding list, its section layout, its skeleton and its initialisation shell; everything below is common and lives here in one copy.

**A process may issue fewer than three documents.** A region issues the **progress report** only, and `scripts/report-render.py` refuses the other two for an `X__` unit rather than making every caller branch.

---

## 1. The ledger is the record layer

`outputs/reports/{unit}/ledger.csv` — one row per **system or instrument** (a payment rail, a statute, a registry, a programme, a policy draft). `{unit}` is an ISO-3 code, a region code, or a taxonomy slug. It is **maintained, never rebuilt**: each run updates rows and adds new ones, and git holds every prior state.

**A row is a named object with a position that can move, not a topic the news covered.** *National Radio Frequency Plan 2026* is a row; *cybersecurity of state information systems* is not. The test before adding a row: could a reader name the thing, and could its position be different next quarter? If either answer is no, the material belongs in the prose, not the ledger. This is the difference between a report on systems and an audit of news stories.

| Column | Meaning |
|---|---|
| `row_id` | Stable handle, `{unit}-{subject}-{short-slug}` — never reissued, never renamed. Published at launch. |
| `place` | ISO-3 or `X__` from `countries.csv`. A topic ledger carries the place per row; a country ledger repeats its own. |
| `subject` | One `taxonomy.md` slug. |
| `section` | **Derived, not authoritative.** A country report's section is the `subject`'s Level-1 chapter in `lookups/taxonomy.csv`, computed by the renderer; a region's comes from `report-region-sections.csv` by the same subject lookup. `normalise_ledger()` keeps the column in step so the file reads on its own terms; it is not overridable per row. |
| `kind` | `instrument` (default) — a named system or instrument, in both the status inventory and the movement ledger. `measure` — a dated measure of one (a breach notification rate, delivered data-centre load), which moves and so belongs in the **progress report only**; it carries no status and is never listed as current state. |
| `name` | The system or instrument as a reader would name it. Short enough to scan — a qualifying clause belongs in `note` or the prose. |
| `status` | A status stem from §3, optionally followed by a comma and a qualifying clause: `Implemented, under appeal`. |
| `published` | The publication date of the most recent record the row cites — read off the `raw/` slug — and the field every period selects on. Not an event date: what fixed the position goes in `milestone`. |
| `milestone` | What the status table prints in its third column: the **event that fixed the position**, never a bare date — `Gazetted 2026-07-24`, `Submissions close 2026-08-21`, `No appropriation line found`, `Since 1998`. No fallback: a row without one prints an em-dash. |
| `position_start`, `position_end` | What the progress table prints at each end of the window: **the substance of the position, not its label** — `30 branches, five banks (2025-08)` against `296 branches, four banks`. Where the base establishes the thing did not exist at the start, say so: `Did not exist`, `None published`, `No date`. |
| `since` | The date the base first puts the row in its **current** status, where that is earlier than `published` — a row whose latest source only refreshes a figure has not moved. Empty means the cited record is the first to report this position. |
| `movement` | A movement stem from §3, optionally with a qualifying clause: `Advanced, slipped`. |
| `sources` | Source slugs, `\|`-separated, resolved to URLs at render time through `outputs/catalogue/raw-catalogue.csv`. |
| `probe_at` | For a ***Not held*** row: the date the gap was last searched for (§4). Empty on a held row. |
| `note` | One clause, only where the row needs a caveat a reader would otherwise ask for. |

**A row's `published` is a fact about a source, not about the run.** A run that reads twenty sources and changes no row is a correct and normal outcome. `published` is also what ages a row out of a report: the ledger is the one place the monthly and the progress report are aged from, and month turnover is the window moving past a value already held.

**The file is kept sorted by taxonomy Level-1, then Level-2, then name.** `report-render.py`'s `resort_ledger()` re-orders on every load, rewriting only when the order changes; content, `row_id`s and column order are untouched, which keeps `ledger.csv` diff-readable.

**`since` is what stops a first build reading as a year of upheaval.** A row is only baseline-less when the base genuinely carries no position for it before the window opened.

**The three documents are renderings of this file, not drafts.** *Status* renders the current rows, *monthly* renders the rows whose `published` falls in the window, *progress* compares `position_start` against `position_end`. The same ledger sliced another way is a different report at no extra reading.

## 2. Cadence — the windows slide, and a document changes only when the ledger moves

**The ledger is updated whenever the base moves; a document changes only when the ledger moved.**

- **At initialisation, all three are issued together.** The expensive thing is reading the base, and it is paid once; the second and third documents are then a render each.
- **On every build**, at BUILD.md stage 4: `report-scan.py` names the initialised units holding sources the layer has not looked at, a model reads only those sources against the ledger, and any row they move is moved. A unit with nothing unconsidered is skipped unread; a place with no ledger is skipped whatever arrived, because this pass never initialises. The set of unconsidered sources is a **set difference over slugs, not a date window**, so an interrupted build resumes cleanly.
- **The status report is refreshed on any build where a row moved.** Its filename carries no period and it answers *where is this now*; leaving it stale while the ledger moves is the failure the layer exists to prevent.
- **The monthly and the progress report move with their windows.** The monthly's window opens on the first of the last closed month; the progress report's opens twelve months before that. Both close on the day the document last changed. New sources that move nothing change nothing.
- **A month in which nothing moved still issues a monthly, and the monthly says so.** The renderer writes the absence in its own voice and mints no narrative block: an absence of movement is a finding the ledger settles, not an empty box for a drafter.

**Both windows open on a month boundary and run to the present**, so the monthly always spans a month boundary: on 14 August it covers 1 July to 14 August. The header prints the true window, not a month's name.

**Nothing is ever closed to new evidence.** A record belongs in the window its **publication date** falls in, whenever it is ingested. Once a window has slid past that date the record still moves the ledger, and still shows in the status report and the progress report; the monthly is simply no longer the document that covers it.

**The scan is a labour-saving gate, not the limit of BUILD's authority.** BUILD authors this layer and holds editorial control: where a document can be made better — a narrative never written, a section that reads badly — BUILD revises it, whether or not the scan nominated the unit that day.

**`compiled:` is the date the document last changed, never the date the build last ran.** A render that changes nothing leaves the file alone: the old date stands, the mtime does not move, nothing enters the diff. Making the date true is BUILD's whole obligation here.

**The change is judged against a stored digest, `record:`, not against the file on disk.** A file-to-render comparison cannot work, because the renderer carries the narrative across *from that same file* — prose written into a block reproduces itself, so the comparison sees nothing while the document changes. `record:` is a short hash of the document with `compiled:` and `record:` taken out, written at the same moment as the date; prose entering a block changes the digest whoever wrote it. A document with no stored digest is stamped with the date of the build that gives it one — wrong only in the safe direction, once.

**The window's closing date is a property of the last change, not of the last build.** A document that did not change keeps the window it prints, so `period:` and `compiled:` move together or not at all. Selection still runs to today, so a frozen close can only ever *understate* — it never claims evidence the document does not hold. The printed window is the period the document **draws on**; `compiled:` is the day it last changed; neither claims nothing happened afterwards. `considered.txt` is the record of what was read. The close comes back into line at every month turnover.

**The build must never become a chronology.** The report layer moves *positions*; events live in the dated source pages that cite them.

**Significance is a ledger question, not an editorial one.** "Not significant enough to change the report" means *no row's status, date or figure changed* — a test a script applies.

## 3. The two vocabularies

**Status** — *Implemented* (in operation or in force) · *Piloting* (limited user group or controlled environment) · *In development* (build or drafting under way, not operating) · *Planned* (announced or provided for, nothing on record being built) · *Enacted* (an instrument passed into law — pair with a qualifying clause for its in-force date) · *Under review* (a law or policy being reconsidered) · *Discontinued* (closed or superseded) · ***Not held*** (the base carries no reliable statement).

**Movement** — *Advanced* (a system entered service, a stage completed, an instrument was made) · *Stalled* (a stated target passed without delivery) · *Regressed* (an instrument withdrawn or neutralised, or a measured position worsened) · *Closed* (the programme ended) · *No change* (the position at both ends is the same, and that is a finding) · ***Baseline not held*** (the base carries no position at the start of the period).

Both lists are the authoritative statement of `report-render.py`'s `STATUSES` and `MOVEMENTS` tuples; a change to one is a change to the other.

**Both vocabularies are stems, not fixed strings.** A value may take a comma and a short qualifying clause where the plain stem would mislead: *Implemented, under appeal* · *Planned, not proceeding* · *Advanced, slipped*. Check I tests the stem. Without the qualifier, real progress against a moved deadline reads as either success or failure, and both are wrong.

**A system that did not exist at the start of the window is *Advanced*, not a special value** — the fact goes in `position_start`, where a reader can see it. Reserve ***Baseline not held*** for what the base genuinely cannot say.

**A dated, searched absence is `**Not held**, searched {probe_at} — {what looked and found nothing}`, not a bare `Not held`.** The bare stem means a gap in the record, which is the opposite of the finding when a probe has confirmed the thing does not exist. The row still counts as `Not held` for the gaps tally — no document is held either way.

Both are **closed vocabularies**, restated in each document immediately before first use, because no reader can infer the boundary between *Planned* and *In development*. The not-held markers are set in bold italic so they read as a different kind of value: their function is to be counted, published and chased. **Publish the not-held count** — it tells the reader how much weight the document bears.

## 4. Gaps — a ***Not held*** row is a research brief

A gap is an **absence**, and it is a named question — the best possible input to a sweep.

1. The run writes every ***Not held*** row to `outputs/reports/{unit}/gaps.csv` — the row's `name`, `subject` and one line on what would settle it.
2. **The run does not probe.** It records the gap and stops. Corpus does not fetch and does not write to OSINT: a gap that names a document Corpus wants becomes a row in the exchange feed, `africa-acquire.csv` in `C:\corpus-osint-xfer\` (`status_lib.EXCHANGE`), which OSINT drains on Bill's schedule. Two sources found disagreeing are a contradiction for OSINT's queue, not a gap. Nothing published at all is a dated absence stated on the page it bears on, which is a finding.
3. **`probe_at` records the date a gap was last searched for.** A ***Not held*** row whose `probe_at` is empty has been noticed and not yet searched — a true statement of the record.
4. Whatever the feed brings back enters OSINT's `raw/` through its own ingest; Corpus's next scan sees the new source and settles the gap itself. Nothing is written into a report from a source Corpus has not seen in `raw/`.
5. An unfilled gap is not re-raised while its feed row stands open, and is re-raised only **when that unit's base moves** — a re-search over an unchanged base returns the same nothing at full price.

That is the closed loop: report → gaps → exchange feed → OSINT sweep → ingest → `raw/` → ledger → next report. **Nothing in a Corpus build blocks on OSINT having acted.**

## 5. The marked blocks

Everything a script owns is outside the markers; everything a model owns is inside them:

```markdown
<!-- narrative: {section-key} -->
Prose here. Every interpretive sentence carries its citation.
<!-- /narrative -->
```

**No document carries an unwritten narrative block, in any form.** An unwritten block is emitted **empty**, and empty is not a licence: check L fails on it, because it says a section was published with nothing said about it. Where a block has no prose, BUILD.md → *Narrative integrity* governs: remove the section, or write the sentence that explains why there is no suitable narrative. There is no third option.

**Every table row carries its citation on the cell that makes the claim** — the status cell in a status table, the end-position cell in a progress table — hyperlinked to the first of the row's `sources` that resolves through the catalogue. The name is the object; the status is the claim; the claim is what a reader checks. A ***Not held*** or ***Baseline not held*** cell is never linked: there is nothing behind it.

**The narrative carries its own citations, including where the same source is already linked in the table above it.** Prose is read on its own — quoted, extracted, or reached by someone who scrolled past the table — and a paragraph whose evidence lives only in a table it no longer sits beside is a paragraph nobody can check. Link the claim, not the sentence: one link where the fact is asserted.

**The monthly update carries no table.** It is prose by section, each paragraph a run of dated and cited developments. A table of rows that moved restates the ledger without telling a reader what happened.

**A country report's sections are the taxonomy's Level-1 chapters, in `lookups/taxonomy.csv`'s order** — ten chapters, opening on Governance, the same ten in the same order in all three documents and in the bulletin. `documentation/report-country-skeleton.md` → *Sections* carries the table. A region is different: `report-region-sections.csv` is a grouping of the region's own objects, not a view of the taxonomy.

**Within a section, every process sub-groups by taxonomy Level-2 subject, in the taxonomy's own order.** Status and progress print one small table per subject under a `###` sub-heading carrying the subject's `taxonomy.csv` label; a section's rows are never combined into one table across subjects. Monthly prints one narrative block per subject, keyed `{section-key}--{subject-slug}` (dots become hyphens: `dpi--dpi-pay`), each under its own `###` sub-heading.

**An empty section or sub-section is not printed at all, and the status report is the only exception.** A subject with no rows — or, for monthly, none that moved in the window — gets no sub-heading and no block; a section with nothing in it gets no heading either, in the monthly and the progress report. The status report alone states the absence, in a sentence the renderer writes: *"The base holds no {section} rows for {place}. A thin evidence base is a finding, not a gap in this document."* In a status report "nothing on this subject" is a finding **about the place**; in a monthly it is a finding about the window, which is not news; in a progress report it is a statement about the ledger's coverage.

**Figures are script-emitted from the ledger.** A number written by hand inside a narrative block is a defect, and check H catches it. A table refresh must never touch prose, and a prose refresh must be a clean diff. This is also what lets a format change re-render every existing report without re-reading the base — narrative blocks are carried across by marker id.

## 6. Verification

Checks A–F live in OSINT, beside the records they reconcile. Checks G–M are Corpus's, because they verify the report layer: G, I, J, L and M in `report-render.py --check`, H and K in `report-register-check.py`. Verification never compiles.

- **G. Every link is held.** Each URL in a rendered report must be present in `outputs/catalogue/raw-catalogue.csv` — Corpus's own committed catalogue of everything `raw/` holds, the same file a reader can download. `report-render.py` refuses to resolve against a catalogue `raw/` has moved past, counted as well as timed. **Non-optional, and re-run after every edit pass, not once at the end** — a URL synthesised from a remembered pattern is indistinguishable from a real one by inspection; set membership is the only test that catches it.
- **H. A figure in narrative prose has a source.** Reports any narrative block that carries a substantive figure — money, a percentage, a count of a thousand or more — and no citation at all. **It asks only that a source exists**: provenance, not fact-checking. The block is the unit; working out which citation covers which figure is the fact-check this deliberately is not. It reports and a person rules. A source is OSINT's settled definition: a wikilink to a dated `raw/` slug, or an inline URL — the ledger is one route to a source, not the definition of one.
- **I. Vocabulary.** No status or movement value outside §3; every ***Not held*** row present in `gaps.csv`; the not-held count in the document equals the ledger's. A `kind: measure` row is skipped only because it has no status to test.
- **J. As-of honesty.** A document compiled before the newest `published` on its ledger is stale — BUILD moved a row and did not rebuild — and fails, because the fix is a re-render. Every progress report must carry its shape check (§7), which `render_progress()` emits unconditionally. The check also prints the gap between compile date and newest evidence, and rules on nothing — any threshold on a truthful lag would be invented.
- **L. No unwritten narrative.** Fails on any narrative block that is empty or carries a placeholder. Unlike K it **fails rather than reports**: there is no reading of an unwritten block under which the document is finished. BUILD owns this, because BUILD owns what is fit to publish.
- **M. Every piece of evidence has a source, and the source resolves.** Fails on any ledger row that states a position and cites nothing, on any row citing a slug the base does not hold, and on any row where no cited slug carries a URL a reader could follow. **A source has to resolve, not merely be typed.** The two resolution failures are reported apart because they belong to different people: a slug the base does not hold is a ledger mistake; a slug held without a `url:` is an uncitable record and OSINT's to fix (§8). ***Not held*** is the only exemption, and barely one — the marker's meaning *is* that no position is held. **Measures are in scope**: a figure is evidence like any other claim.
- **K. Register and budget.** `report-register-check.py` reads the narrative blocks — never the tables, where a ledger `name` is the object's name, not the report's prose — and reports register terms, any surviving `## Comment` heading, and any document outside its skeleton's word budget. **It reports; a person rules** — under the Corpus register a connecting sentence is not a defect. The budget is read from the skeleton so there is one knob, and the script exits 2 rather than pass silently if that line is reworded past it.

**A report that fails G or M is not published, ever.** The others report and are fixed.

**G and M are two halves of one rule: every piece of evidence has a source.** M is that a stated position cites something; G is that what it cites is real. Together they are the whole of the layer's claim to be evidence-led, and they are not negotiable against any other consideration, including a drafting deadline.

## 7. Shape check before any period comparison

Count the unit's sources per month across the window **before** promising a comparison. Where the earlier half is thin, either narrow the window or say plainly in the document that it is a shorter comparison wearing a longer label — with the counts, once, near the top. Each process's initialisation shell prints this and flags the cliff; the check is worthless run after drafting.

## 8. Byproducts — the pass is a defect detector

Forcing every claim through a resolution step finds what nothing else looks for: a source held twice under two slugs, an artefact with no `url:` and therefore uncitable, a closed contradiction confirmed still closed. **Emit them in the run** — as numbered notes in `C:\corpus-osint-xfer\notes-for-osint.md`, since the defects are in OSINT's evidence. They cost nothing to collect while passing and are never found by going looking.

## 9. Files and versions

```
outputs/reports/{unit}/ledger.csv                  # the record layer, maintained
outputs/reports/{unit}/gaps.csv                    # not-held rows, with probe dates
outputs/reports/{unit}/{unit}-status.md            # current position
outputs/reports/{unit}/{unit}-monthly.md           # the monthly report; `period:` states its window
outputs/reports/{unit}/{unit}-progress.md          # the progress report; `period:` states its window
outputs/reports/{unit}/considered.txt              # slugs the ledger has looked at — the set difference §2 works over
```

Every document carries `compiled:` and `record:` in its frontmatter: `record:` says *what this document is*, `compiled:` says *when it last became that*. Neither is ever written by hand.

**There are no issues.** Each unit has one monthly and one progress report — living documents whose windows slide, not a series of dated editions. `period:` states the window the document now covers; an earlier state of it is an earlier commit. **So no markdown filename carries a period.** Versioning happens where a reader needs it: RENDER dates the PDF and the CSV, which are what a citation points at; the HTML is always the current document.

**Narrative always carries across.** The renderer preserves every block so a rebuild costs a render rather than a redraft. Moving a window on is an **edit** — BUILD removes what has aged out and writes in what has arrived — never a fresh composition, because consecutive windows overlap heavily. What this leaves is a sentence still describing a period that has moved on: well-formed prose no check can catch. Finding it is the point of the revision, and it is BUILD's.

**A build that discards prose says so.** A section with nothing in it is not printed, so a rebuild can legitimately drop a section that held writing — legitimately, but never silently. The renderer names every block that held prose and was not asked for; this is the one operation in the layer that destroys writing, and it reports the blocks **kept**, not the blocks found. Git holds the prose either way; knowing it went is the point.

Nothing here is a source: reports are derived views, never cited by a wiki page, never re-ingested into OSINT.

## 10. The register

**Corpus editorial register — light touch.** One principle: **the evidence speaks; the lens decides what gets noticed and connected, and then gets out of the way.**

- **The spine stays fully disciplined.** The ledger, the tables, every dated figure, the published *Not held* count — script-emitted, cited, explicit about gaps. Its neutrality is what makes any reading credible. A reader must always be able to **take the facts and refuse the reading**; that is the test the whole layer has to pass.
- **The prose stays factual first**: dated, attributed, no flash verbs, no staged reveals, no arguing a heading. A report may *connect* facts the lens brings together, and may name a pattern the evidence already shows, in a sentence a reader can check against the rows above it. It states the connection; it does not press it.
- **The lens is a quiet set of questions, asked by what gets included.** Who owns the infrastructure, who holds the data and under whose jurisdiction, what dependency a financing arrangement creates, who is vendor and who is regulator. These shape which facts a section foregrounds; they rarely need to be spoken.
- **Where a reading is offered, it is visibly a reading and rests on the dated facts beside it** — one sentence, not a paragraph, never a flourish. The polemical version is ruled out: no charge, no thesis. Worked contrast: *the circular of 24 July sets no implementation deadline; the estimates published the next day carry no budget line for the agency named to implement it* — then, at most, one plain connecting sentence: *the mandate names an implementing agency the same week's estimates do not fund.* The reader weighs it.

`report-register-check.py`'s tic-scanner reports rather than gates: a connecting sentence is not a defect. Checks G–M bind unchanged — a position, however light, raises the cost of an unchecked figure; it does not lower it.

**No document in this layer carries a comment section.** The argument belongs downstream, in the published work these reports feed. A labelled comment section is a licence: prose written towards a verdict at the end leaks the verdict into the body.

**The prose never narrates the ledger.** "Twenty-three rows moved this month" is a fact about the document, not about the unit. Write about the systems.
