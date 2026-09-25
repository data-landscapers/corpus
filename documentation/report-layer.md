---
type: spec
reader: cc
title: report-layer.md — what every Corpus report process shares
last_reviewed: 2026-08-28
status: in force; Corpus-owned
---

# report-layer.md — what every report process shares

**One layer, several processes.** Country, region (six `X__` codes, first-class places) and topic reports share everything below; each process owns its unit, outstanding list, section layout, skeleton and initialisation shell.

**A process may issue fewer than three documents.** A region issues a **monthly update and a progress report, never a status**; `scripts/report-render.py` refuses the status for an `X__` unit.

---

## 1. The ledger is the record layer

`outputs/reports/{unit}/ledger.csv` — one row per **system or instrument**. `{unit}` is an ISO-3 code, a region code, or a taxonomy slug. It is **maintained, never rebuilt**; git holds every prior state.

**A row is a named object with a position that can move, not a topic the news covered.** *National Radio Frequency Plan 2026* is a row; *cybersecurity of state information systems* is not. The test: could a reader name the thing, and could its position be different next quarter? If either answer is no, it belongs in the prose.

| Column | Meaning |
|---|---|
| `row_id` | `{unit}-{subject}-{short-slug}` — never reissued, never renamed. Published. |
| `place` | ISO-3 or `X__` from `countries.csv`; a country ledger repeats its own. |
| `subject` | One `taxonomy.md` slug. |
| `section` | **Derived, not authoritative**: the `subject`'s Level-1 chapter in `lookups/taxonomy.csv` (country), or its group in `report-region-sections.csv` (region). `normalise_ledger()` keeps it in step; not overridable per row. |
| `kind` | `instrument` (default) — in the status inventory and the movement ledger. `measure` — a dated measure of one (a breach notification rate, delivered data-centre load): **progress report only**, no status, never listed as current state. |
| `name` | As a reader would name it, short; qualifiers go in `note` or prose. |
| `status` | A status stem from §3, optionally with a qualifying clause: `Implemented, under appeal`. |
| `published` | Publication date of the most recent record the row cites, read off the `raw/` slug — the field every period selects on. Not an event date. |
| `milestone` | Status table's third column: the **event that fixed the position**, never a bare date — `Gazetted 2026-07-24`, `Submissions close 2026-08-21`, `No appropriation line found`, `Since 1998`. None prints an em-dash. |
| `position_start`, `position_end` | The progress table's two ends: **the substance of the position, not its label** — `30 branches, five banks (2025-08)` against `296 branches, four banks`. Where the thing did not exist at the start: `Did not exist`, `None published`, `No date`. |
| `since` | Date the base first puts the row in its **current** status, where earlier than `published` — a source that only refreshes a figure has not moved the row. Empty: the cited record is the first to report it. |
| `movement` | A movement stem from §3, optionally qualified: `Advanced, slipped`. |
| `sources` | Slugs, `\|`-separated, resolved to URLs at render time through `outputs/catalogue/catalogue-internal.csv`. |
| `probe_at` | ***Not held*** rows: date the gap was last searched for (§4). Empty on a held row. |
| `note` | One clause, only for a caveat a reader would otherwise ask for. |

**A row's `published` is a fact about a source, not about the run.** A run that changes no row is normal. `published` also ages a row out of the monthly and progress report.

**But a source naming something the ledger holds nothing on mints a row.** A named system shown to exist and be live opens at `movement: Baseline not held`. Not minting it is the error `documentation/considered-not-carried.md` records: the indicator frame then reports ***No evidence***, true of the ledger and false of the base.

**The file is kept sorted by taxonomy Level-1, then Level-2, then name.** `resort_ledger()` re-orders on every load, rewriting only when the order changes; content, `row_id`s and column order are untouched.

**`since` is what stops a first build reading as a year of upheaval.** A row is baseline-less only when the base genuinely has no position for it before the window opened.

**The three documents are renderings of this file, not drafts.** *Status* renders the current rows, *monthly* the rows whose `published` falls in the window, *progress* compares `position_start` against `position_end`.

## 2. Cadence — the windows slide, and a document changes only when the ledger moves

**The ledger is updated whenever the base moves; a document changes only when the ledger moved.**

- **At initialisation, all three are issued together** — the base is read once.
- **On every build**, at BUILD.md stage 4: `report-scan.py` names initialised units holding sources the layer has not looked at; a model reads only those against the ledger and moves any row they move. Places with no ledger are skipped — this pass never initialises. The unconsidered set is a **set difference over slugs, not a date window**, so an interrupted build resumes cleanly.
- **The status report is refreshed on any build where a row moved.** Its filename carries no period.
- **The monthly and the progress report move with their windows.** The monthly's opens on the first of the last closed month, the progress report's twelve months earlier; both close on the day the document last changed.
- **A month in which nothing moved still issues a monthly, and the monthly says so**, in the renderer's voice, with no narrative block.

**Both windows open on a month boundary and run to the present**: on 14 August the monthly covers 1 July–14 August, and says so.

**Nothing is ever closed to new evidence.** A record belongs in the window its **publication date** falls in, whenever ingested; past that window it still moves the ledger.

**A pile of new sources earns a whole re-read of what it touches** *(review 5, R76)*. Over 15 sources touching a unit's status sub-sections since its last whole read (unit review, status initialisation or last such re-read) and those sub-sections are re-read whole that build, by the unit review's method. `report-scan.py --sections` names them and `--sections-read` resets the clock. The drift measure is `unit-review.py`'s rolling mean of sections revised, which should fall under two.

**The scan is a labour-saving gate, not the limit of BUILD's authority.** BUILD revises any document that can be made better, nominated or not.

**`compiled:` is the date the document last changed, never the date the build last ran.** A render that changes nothing leaves the file alone.

**The change is judged against a stored digest, `record:`, not against the file on disk**, from which narrative is carried across. `record:` hashes the document without `compiled:` and `record:`, written with the date. A document with no digest is stamped with the date of the build that gives it one.

**The window's closing date is a property of the last change, not of the last build.** `period:` and `compiled:` move together or not at all; a frozen close can only understate. The printed window is the period the document **draws on**; `considered.txt` records what was read. The close comes back into line at every month turnover.

**The build must never become a chronology.** The layer moves *positions*; events live in the source pages.

**Significance is a ledger question, not an editorial one.** "Not significant enough to change the report" means *no row's status, date or figure changed* — a test a script applies.

## 3. The two vocabularies

**Status** — *Implemented* (in operation or in force) · *Piloting* (limited user group or controlled environment) · *In development* (build or drafting under way, not operating) · *Planned* (announced or provided for, nothing on record being built) · *Enacted* (an instrument passed into law — pair with a qualifying clause for its in-force date) · *Under review* (a law or policy being reconsidered) · *Discontinued* (closed or superseded) · ***Not held*** (the base carries no reliable statement).

**Movement** — *Advanced* (a system entered service, a stage completed, an instrument was made) · *Stalled* (a stated target passed without delivery) · *Regressed* (an instrument withdrawn or neutralised, or a measured position worsened) · *Closed* (the programme ended) · *No change* (the position at both ends is the same, and that is a finding) · ***Baseline not held*** (the base carries no position at the start of the period).

Both lists are the authoritative statement of `report-render.py`'s `STATUSES` and `MOVEMENTS` tuples; a change to one is a change to the other.

**The region progress report prints *Advanced* as *Movement*, under a column headed *Progress*** *(Bill, 2026-09-11)*. The ledger keeps *Advanced*; `as_progress()` translates, and check I accepts either.

**Both vocabularies are stems, not fixed strings.** A value may take a comma and a short qualifying clause where the plain stem would mislead: *Implemented, under appeal* · *Planned, not proceeding* · *Advanced, slipped*. Check I tests the stem.

**A system that did not exist at the start of the window is *Advanced*, not a special value** — the fact goes in `position_start`. ***Baseline not held*** is for what the base genuinely cannot say.

**A dated, searched absence is `**Not held**, searched {probe_at} — {what looked and found nothing}`, not a bare `Not held`**, which means a gap in the record. It still counts as `Not held` for the gaps tally.

Both are **closed vocabularies**, restated in each document before first use; not-held markers in bold italic. **Publish the not-held count** — it tells the reader how much weight the document bears.

## 4. Gaps — a ***Not held*** row is a research brief

1. The run writes every ***Not held*** row to `outputs/reports/{unit}/gaps.csv` — `name`, `subject` and one line on what would settle it.
2. **The run does not probe.** Corpus does not fetch or write to OSINT: a gap naming a document Corpus wants becomes a row in `africa-acquire.csv` in `C:\corpus-osint-xfer\` (`status_lib.EXCHANGE`). Two sources disagreeing are a contradiction for OSINT, not a gap. Nothing published at all is a dated absence stated on the page it bears on.
3. **`probe_at` records the date a gap was last searched for.** Empty means not yet searched.
4. What the feed brings back enters OSINT's `raw/` through its own ingest, and Corpus's next scan settles the gap. Nothing is written into a report from a source Corpus has not seen in `raw/`.
5. An unfilled gap is not re-raised while its feed row stands open, and only **when that unit's base moves**.

**Nothing in a Corpus build blocks on OSINT having acted.**

## 5. The marked blocks

Everything a script owns is outside the markers; everything a model owns is inside them:

```markdown
<!-- narrative: {section-key} -->
Prose here. Every interpretive sentence carries its citation.
<!-- /narrative -->
```

**No document carries an unwritten narrative block, in any form.** An unwritten block is emitted **empty**, and check L fails on it. BUILD.md → *Narrative integrity* governs: remove the section, or write the sentence explaining why there is no suitable narrative.

**Every table row carries its citation on the cell that makes the claim** — status, or progress end-position — linked to the first of the row's `sources` that resolves through the catalogue. A ***Not held*** or ***Baseline not held*** cell is never linked.

**The narrative carries its own citations, even where the table above links the same source.** Link the claim, not the sentence: one link where the fact is asserted.

**The monthly update carries no table** — prose by section, of dated, cited developments.

**A country report's sections are the taxonomy's Level-1 chapters, in `lookups/taxonomy.csv`'s order** — ten, opening on Governance, the same in all three documents and the bulletin (`report-country-skeleton.md` → *Sections*). A region's `report-region-sections.csv` groups its own objects, not the taxonomy.

**Within a section, every process sub-groups by taxonomy Level-2 subject, in the taxonomy's own order.** Status and progress print one table per subject under a `###` sub-heading carrying its `taxonomy.csv` label. Monthly prints one narrative block per subject, keyed `{section-key}--{subject-slug}` (dots become hyphens: `dpi--dpi-pay`), each under its own `###` sub-heading.

**An empty section or sub-section is not printed at all, and the status report is the only exception.** In the monthly (nothing moved) and the progress report, it gets no heading and no block. The status report states the absence in a renderer sentence: *"The base holds no {section} rows for {place}. A thin evidence base is a finding, not a gap in this document."*

**Figures are script-emitted from the ledger**; a hand-written number in a narrative block is a defect (check H). A table refresh never touches prose; blocks carry across by marker id.

## 6. Verification

Checks A–F live in OSINT. G, I, J, L and M are in `report-render.py --check`; H and K in `report-register-check.py`. Verification never compiles.

- **G. Every link is held.** Each URL in a rendered report must be in `outputs/catalogue/catalogue-internal.csv`, Corpus's catalogue of everything `raw/` holds, with the `slug` a citation resolves by (`build-catalogue.py` → `CSV_COLS`). `report-render.py` refuses a catalogue `raw/` has moved past, counted as well as timed. **Non-optional, and re-run after every edit pass.**
- **H. A figure in narrative prose has a source.** Reports any narrative block carrying a substantive figure — money, a percentage, a count of a thousand or more — and no citation. **It asks only that a source exists**, per block: provenance, not fact-checking. A person rules. A source is a wikilink to a dated `raw/` slug or an inline URL.
- **I. Vocabulary.** No status or movement value outside §3; every ***Not held*** row in `gaps.csv`; the document's not-held count equals the ledger's. `kind: measure` rows are skipped.
- **J. As-of honesty.** A document compiled before the newest `published` on its ledger fails. Every progress report carries its shape check (§7), emitted by `render_progress()`. J also prints, and does not rule on, the lag to the newest evidence.
- **L. No unwritten narrative.** **Fails** on any empty or placeholder narrative block. BUILD owns this.
- **M. Every piece of evidence has a source, and the source resolves.** Fails on any row that states a position and cites nothing, cites a slug the base does not hold (a ledger mistake), or cites no slug carrying a `url:` (OSINT's to fix, §8) — the two reported apart. ***Not held*** is the only exemption. **Measures are in scope.**
- **K. Register and budget.** Reads narrative blocks, never tables; reports register terms, any `## Comment` heading, and any document outside its skeleton's word budget. **It reports; a person rules.** The budget is read from the skeleton; the script exits 2 if that line is reworded past it.

**A report that fails G or M is not published, ever.** The others report and are fixed.

**G and M are two halves of one rule: every piece of evidence has a source** — M that a position cites something, G that what it cites is real. Neither yields to any other consideration, including a deadline.

## 7. Shape check before any period comparison

Count the unit's sources per month across the window **before** promising a comparison. Where the earlier half is thin, narrow the window or say it is a shorter comparison wearing a longer label, with the counts, once, near the top. Each initialisation shell prints this and flags the cliff.

## 8. Byproducts — the pass is a defect detector

Resolving every claim finds duplicate slugs, artefacts with no `url:`, contradictions confirmed closed. **Emit them in the run** as numbered notes in `C:\corpus-osint-xfer\notes-for-osint.md`.

## 9. Files and versions

```
outputs/reports/{unit}/ledger.csv                  # the record layer, maintained
outputs/reports/{unit}/gaps.csv                    # not-held rows, with probe dates
outputs/reports/{unit}/{unit}-status.md            # current position
outputs/reports/{unit}/{unit}-monthly.md           # the monthly report; `period:` states its window
outputs/reports/{unit}/{unit}-progress.md          # the progress report; `period:` states its window
outputs/reports/{unit}/considered.txt              # slugs the ledger has looked at — the set difference §2 works over
```

Every document carries `compiled:` and `record:` in its frontmatter, never written by hand.

**There are no issues.** Each unit has one monthly and one progress report whose windows slide; an earlier state is an earlier commit. **No markdown filename carries a period.** RENDER dates the PDF and CSV, which citations point at; the HTML is always current.

**Narrative always carries across.** Moving a window on is an **edit** — BUILD removes what has aged out and writes in what has arrived, including any sentence still describing a period that has moved on — never a fresh composition.

**A build that discards prose says so.** The renderer names every block that held prose and was not asked for.

Reports are never a source: never cited by the wiki or re-ingested into OSINT.

## 10. The register

**The register lives in `documentation/report-layer-register.md`** — the two styles, the *Corpus editorial register*, *Plain English* and the standing hits — and binds every narrative block in full.
