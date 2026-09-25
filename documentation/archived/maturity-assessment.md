---
type: design-note
reader: cc
title: maturity-assessment.md — the country maturity assessment that replaces the progress report
last_reviewed: 2026-09-22
status: ruled — design agreed by Bill 2026-09-22; build plan in §12, nothing built yet. Supersedes progress-report-redesign.md.
---

# The country maturity assessment

*(Written 2026-09-22 in Cowork from a design conversation with Bill, and revised the same day after his ruling on the first draft. Decisions marked (Bill) are his and are not reopened here. The companion `maturity-assessment-norms.md` holds the research this rests on — one anchoring norm per indicator — and was written first, because what it found shapes the rubric. Two indicators are added to the frame and six leave it; `adding-an-indicator.md` is the procedure and `indicator-digital-sovereignty.md` and `indicator-financial-sustainability.md` are the two additions. CC has not been asked to do anything yet; §12 is the order in which it would be.)*

## 1. What it is

**A five-stage assessment of each assessed indicator in `lookups/indicators.csv` — 117 after the frame change in §2 — for each of the 54 countries, taken as at the end of every month and kept.** The stage says where the country stands on that indicator against a stated continental norm. The monthly series says how that has moved. The assessment is a *stock*; everything Corpus records today is a *flow*.

That is the gap it fills. The progress vocabulary — *Movement · Stalled · Regressed · Mixed · No change · No evidence* — says which way an indicator moved inside a window and never where it is. The status report says where it is, in prose, so it cannot be counted or compared. The assessment is the status report made countable: a position, assessed against a norm a reader can look up, stored so that the next month's position can be set beside it.

**It replaces the progress report** *(Bill, 2026-09-22)*. The three-document set becomes **status · monthly · maturity**. What the progress report did well — the fixed frame, the mapped rows, the summary and developments prose, the visible *No evidence* — the assessment keeps; what it did badly — a direction with no level behind it, a word budget that had to be defended document by document — goes.

**It is called the Maturity Assessment, not an index** *(Bill)*. It is not a country score, a ranking, or a chapter average *(Bill: resist even chapter averages for starters)*. The only arithmetic it does is counting — how many indicators sit at each stage, per kind, per country. It is not the status report and does not derive from it (§9). The level is called a *stage*, so that *Corpus stage 3* never reads as a score.

## 2. Decisions taken

Recorded here so the build does not relitigate them. All Bill, 2026-09-22, in two rounds, and the last two 2026-09-23.

- **The assessment replaces the progress report** rather than sitting beside it.
- **Measures are in, and are the point.** Instruments and systems are what everyone else assesses; measures are what they avoid, because the figures are stale, self-reported and defined differently source to source. Corpus can carry a figure with its date, its source and who says so, and that is what makes a banded measure publishable where a bare number is not.
- **No aggregation.** No country score, no chapter average, no ranking. Counts only.
- **Status and assessment are two exercises, side by side.** The status report keeps a qualitative narrative in Corpus's own voice; the assessment quantifies against continental norms. They must not contradict each other, and neither is derived from the other.
- **Norms are continental first.** AU instruments wherever possible; where none exists, the origin of the norm is searched for and defined; every indicator is anchored. The exercise is `maturity-assessment-norms.md`, and its anchors and kind assignments are agreed.
- **The five `geopol.*` indicators leave the assessment.** They record a relationship, not maturity. A **digital sovereignty** indicator is added to the Geopolitics chapter in their place — `indicator-digital-sovereignty.md`.
- **`finance.mou--strategic-relationships` leaves** for the same reason and a **financial sustainability** indicator takes its place — `indicator-financial-sustainability.md`.
- **Rural police stations get a Corpus rubric**, on the pattern of the other three `digital.rural` rows.
- **No evidence flag.** The qualifier already carries *on the ministry's own figures*; a second column would duplicate it.
- **Baseline as at 2026-07-31; first snapshot as at 2026-08-31.** The month-end assessment is run on the 5th of the following month, to let late arrivals in.
- **Measure bands without an African number use Africa-only quintiles.**
- **The financial sustainability indicator gets its own subject, `finance.sustain`** *(Bill, 2026-09-23)*. `finance.budget` is for the facts of actual budgets; `finance.sustain` covers efforts to make the digital estate financially sustainable. It travels to OSINT in one patch with `geopol.sovereignty`.
- **Africa-only quintiles are cut at the baseline and recut each July** *(Bill, 2026-09-23)*, with the year of the cut named in the rubric row — never recut on an ordinary snapshot.
- **`finance.new--development-partner-project-financing` measures the on-budget share of partner digital finance** *(Bill, 2026-09-24)*: the share printed in the state's own budget document, not the external share of the digital budget, which is the sustainability row's figure seen from the other side. The indicator stays assessed.
- **A global dataset used as a norm is a reference, not the record.** Corpus's own collected figure takes precedence where it exists; most global datasets are out of date against what the base holds. `maturity-assessment-norms.md` §7 is the rule.

## 3. The scale: five stages and a null

One scale for every indicator, so that a reader who has learned what stage 3 means on one row can read every other row. The labels are chosen to hold across the three kinds in §4.

| stage | label | instruments and systems | measures |
|---|---|---|---|
| 1 | **Absent** | Nothing of the kind exists, and the base holds a citation that says so | Far below the norm's target, on a dated figure |
| 2 | **Nascent** | Announced, drafted, tabled, piloted — an intention with an instrument or a pilot behind it | Below the norm |
| 3 | **Established** | Enacted, or in service — but limited in scope, coverage or use | Approaching the norm |
| 4 | **Operating** | In service at scale: funded, regulated, used, maintained | Meets the norm's target |
| 5 | **Leading** | Embedded: interoperable, reviewed, measured, sustained; at or beyond the continental instrument's end state | Exceeds the target |

**The null is not a stage.** An indicator with no mapped row is *unassessed*, prints as ***No evidence*** exactly as it does today, and is never stage 1. *Absent* is a position the base can cite — Starlink listing no launch date, the cable registry showing no landing; *unassessed* is a position the base has not looked at. Collapsing the two would make the assessment say things the base does not know, and the mapping conventions already keep them apart (a *Not held* row with a source is mapped; one without is not).

**Stages are ordinal.** 4 is above 3; it is not twice 2. That is why §1 forbids averages and why the only aggregate is a count at each stage.

## 4. Three kinds, one scale

Every assessed indicator is one of three kinds, and the kind picks the rubric family and the columns the assessment carries. `lookups/indicators.csv` gains a `kind` column; the register's §3 carries the agreed assignment (44 instruments, 51 systems, 22 measures).

- **instrument** — a strategy, law, regulation, institution, standard or agreement. The ladder is the instrument's own life: absent → drafted or tabled → enacted or constituted → operating with a mandate and a budget → aligned with or ratifying the continental instrument. For the legal indicators the AU instrument supplies the rungs directly.
- **system** — an operating digital system or piece of infrastructure: an ID system, a registry, an MIS, an exchange layer, a backbone, an IXP. The ladder is service: absent → piloted → in service, limited → in service at scale → interoperable and sustained.
- **measure** — a quantity: penetration, affordability, bandwidth, electrification, literacy, account ownership, the domestic-state share of digital expenditure. The ladder is bands over the value against the norm's target (§5).

**The kinds are never counted together.** A measure's stage 3 and a law's stage 3 are the same rung on the same ladder only in the sense that both are *Established*; adding them tells a reader nothing. What the three-kinds-one-scale design buys is the juxtaposition: a country at 4 on instruments and 2 on measures is *policy ahead of reality*; one at 2 on instruments and 4 on measures is *the market got there without the state*. Nobody else can draw that contrast because nobody else does the measures column. Three separate assessments would put the two halves of it in different tables.

**Measures carry a figure of record.** Where the progress report's §6 forbade asserting a level as current state, the assessment asserts one — with its provenance beside it. A measure row carries `value`, `unit`, `value_year` and `value_source` alongside the stage, and the stage is a band over the value. A reader sees the band, the number behind it, and that the number is from 2023. **This is a ruling against `progress-report-redesign.md` §6 and against the *reference studies are cited, not absorbed* line as it applies to this document only**: the assessment is the one place a figure is promoted to current position, and the columns are what make that defensible. The status report and the monthly keep the old rule.

**Which figure is the figure of record** *(Bill)*: Corpus's own, where the base holds a cited primary figure — a regulator's statistics, a census, an audited count — and the global dataset's only where the base holds nothing or holds only a claim the global figure contradicts. `value_source` says which; the qualifier records a material disagreement between the two, because the disagreement is itself a finding. Africa-only quintiles are computed from the figures the assessment carries, not from the global dataset's column.

Two consequences for measures. They step, not drift: a new figure arrives once a year, so a measure sits flat for eleven months and then moves, and the grid must show the data year or a flat row reads as *nothing happening* when it means *no new figure*. And the qualifier matters most here: *band 3, on the regulator's 2024 figure* and *band 3, on the ministry's own claim, untested* are different findings and print differently.

## 5. The rubric: norms and anchors

**Every indicator is assessed against a named norm**, and the norm is a citation, not a sentence in a rubric. `maturity-assessment-norms.md` is the register, ruled on; CC cuts `lookups/maturity-norms.csv` from it once the register's §6 items are confirmed, with one row per indicator: `indicator_id, kind, tier, instrument, adopting_body, adopted, status, provision, fixes, reference, url, vintage, notes`.

**What the register found** shapes the rest of this section. Of the 117 assessed indicators, 105 anchor on an AU organ instrument and a further seven on a continental agency or alliance; four fall through to a global body and one (rural police stations) to Corpus's own rubric. No REC instrument is the anchor anywhere, because an AU instrument always sits above it. The DTS 2020–2030 is the anchor or co-anchor for 48 indicators and Agenda 2063's Second Ten-Year Implementation Plan supplies most of the dated numbers the DTS lacks. Twenty-seven rows carry a numeric target.

**Seventy-three anchors fix the top of the ladder and nothing below it.** Malabo says what compliance looks like; it does not say what stage 2 is. So for most indicators the norm fixes stage 5 (or 4) and stages 2–4 are Corpus's interpolation. The rubric says so per row, in a column, and the published methodology says how many rows are interpolated. This is the same discipline as the datasets rule — *a classification rubric is ours and says so* — applied at the rung.

**The fallback order is written once and applied uniformly**: AU organ instrument → continental agency or alliance (Africa CDC, Smart Africa, ATU, AMCOMET, APAI-CRVS, PIDA) → REC instrument → global body → Corpus-defined. A Corpus-defined row carries a sentence saying what was searched and not found. The count of Corpus-defined rows is published: it is one.

**Vintage is frozen.** Each norm is the instrument as adopted. If the AU revises a target — the DTS mid-term review, a SHaSA 3 — the assessment records a rubric change, flagged `reassessed` on every row it touches, never fifty-four countries moving in one month.

**The rubric itself** is a second lookup, `lookups/maturity-rubric.csv`, with one row per indicator per stage: `indicator_id, stage, anchor, interpolated`. The `anchor` is what evidence satisfies the stage for that indicator — *stage 3 for `dpi.id--registration-of-entire-population`: a national ID system issuing credentials to the public, coverage cited, below the 99.9 % target* — so that an assessment cites the rows that meet it rather than asserting a feeling. Five rows for 117 indicators is 585 anchors, and drafting them is the largest single piece of work in §12.

**Measure bands** are set against the norm's target where one exists (the ITU's 2 %-of-GNI affordability line, the STYIP's 80 % electrification, the DTS's 99.9 % legal identity), as absolute values: *meets the norm* in 2026 means the 2030 or 2033 target value, not a time-adjusted trajectory towards it. Countries will mostly sit at 2 and 3 on measures for years, and that is the truthful picture. Where the norm states no number, bands are **Africa-only quintiles** *(Bill)* of the figures the assessment carries, at a named year, and the rubric says which reference dataset fills the gaps.

## 6. The assessment file

`outputs/reports/{unit}/indicators.csv` is kept, and the expensive work in it — the mapping, `summary`, `developments`, `row_ids` — is reused as is. One column changes meaning and a few are added:

| column | meaning |
|---|---|
| `stage` | 1–5; replaces `progress`. Absent from the file ⟺ *No evidence*, as today |
| `value, unit, value_year, value_source` | measures only; the figure of record (§4) |
| `next_milestone, due` | optional; a dated target the cited instrument itself states, from which *stalled* is derived (§8) |
| `assessed_on` | the date the stage was last set or confirmed |
| `reassessed` | 1 when the stage changed because the rubric changed or a re-read corrected it, not because an event occurred |
| `qualifier` | free text, as today: *on the ministry's own figures*. This is where who-says-so lives; there is no separate evidence flag *(Bill)* |

**Rules that keep the series stable.** These are the load-bearing part of the design, because a level diff is now the only source of indicator-level movement and drift from re-reading would print as movement.

- **A stage changes between two month-ends only on a cited row dated inside the window.** Otherwise the prior stage carries forward, whatever the assessor's re-reading of the same rows would say this month. This is a hard check, not a convention.
- **A rubric correction or a re-read that changes a stage sets `reassessed`** and is reported in its own section, never as a country movement.
- ***No evidence* ⟺ zero mapped rows**, both directions — check I unchanged.
- **Stage 1 requires a citation.** An *Absent* with nothing behind it is *unassessed*.
- **Rows held that satisfy no rung leave the indicator *unplaced*** *(CC, 2026-09-24, from the first real unit: 12 of STP's 88)*. The stage is empty and the qualifier says why. The row stays in the snapshot so the finding is kept, and the indicator prints as unassessed. It is never stage 1, which would assert an absence the base cannot cite. Entering or leaving a stage from unplaced passes the stability rule like any other change. This refines the line above it and leaves check I alone: the mapping still has its rows.
- **A measure requires all four value columns.** A band with no figure behind it fails.
- **`Mixed` retires.** It existed because one indicator had several instruments moving different ways; the stage plus the qualifier carries that.

**The assessor** is the same model pass that maps rows today, reading the ledger and the mapped rows against `maturity-rubric.csv`, and recording the stage with the rows that satisfy its anchor. The stage is still a drafter's judgement, as the progress stem was; what changes is that the judgement has a stated anchor to be checked against, and a check that refuses a change no dated row supports.

## 7. Snapshots and history

**The as-at date is fixed: the last day of the month. The run date is the 5th of the following month** *(Bill)*. The two report windows deliberately run to the day the issue is cut; a time series cannot, because points cut on different days are not comparable. Running on the 5th lets sources published or ingested in the first days of the month, about events inside it, reach the assessment; a row dated after month-end still waits for the next snapshot, whenever it was ingested.

**The baseline is as at 2026-07-31 and the first snapshot as at 2026-08-31** *(Bill)*. Both are constructed retrospectively at build, from rows dated on or before the as-at date, with what the base holds *now* about those dates. That is a stated limitation of the first two points, not a defect: the as-at is by event date, so a source ingested in September about a July event belongs in the July position, and the rule going forward is the same. From September 2026 onward the snapshot is taken live on the 5th. The September 2026 snapshot is therefore due on 2026-10-05, which sets the build deadline in §12.

**Reference figures follow the same line** *(CC, 2026-09-24)*. The July and August snapshots see every reference figure Corpus holds, cited with its real release date. From September, a release after the as-at is invisible, exactly as a later source is to a ledger row. Gating the retrospective two by release would hide figures that were public long before July only because the fetch was later, and their first appearance in September would print as movement.

**Each month's assessment is an edition.** `outputs/reports/{unit}/maturity/{YYYY-MM}.csv` — the assessed rows as at that month-end — is written once and never revised, under `design.md` §9 exactly as the dated finance CSVs are. `outputs/reports/{unit}/indicators.csv` is the current position and is maintained; the monthly file is what it looked like on the day. The two retrospective editions are written once, at the build, and are then as fixed as any other.

**The estate history is the concatenation.** `outputs/reports/maturity-history.csv` — `unit, indicator_id, as_of, stage, value, value_year, reassessed` — is appended on every snapshot and is what the time-series renderers read. It is derived and can be rebuilt from the editions.

**Movement starts with the August snapshot**, since July is the baseline. No history before July is reconstructed.

## 8. Outputs

All derived from the history file and the current assessment; none drafted except the movement note's prose, and that only about cells that moved.

- **The monthly movement note, per country.** Three derived states — *moved up*, *moved down*, *stalled* (a `due` date passed with the stage unchanged) — plus a separate list of `reassessed` cells. Prose is written only for the cells that moved, each with its citing row; a month in which nothing moved says so in one sentence. This replaces the progress document's per-row prose and its word budget: the length is set by the count of moved cells, which is the same judgement the monthly's per-row budget already expresses.
- **The country grid.** Indicators down the side grouped by chapter and kind, months across, each cell coloured by stage, a mark on every cell where the stage changed, the data year printed on measure rows. One screen shows a country's whole trajectory and the movements stand out. Static SVG at build, consistent with how the site is served.
- **The stage count over time.** Per chapter and per kind, a stacked bar per month of how many indicators sit at each stage. This is the whole of the aggregation the assessment does.
- **One indicator across the continent.** For a chosen indicator, the 54 countries' stages as a distribution, and the distribution over time. This is the comparative view the fixed frame invites and probably the second most useful picture after the grid.
- **The DPI cross-check.** The 453 dataset variables include external maturity-style scores (GovTech Maturity Index, EGDI, GCI). A monthly comparison — external source high, Corpus stage 1 or unassessed — is a cheap gap-finder and feeds `gaps.csv` directly. The Corpus stage stays the base's own judgement; the cross-check never overwrites it.

Nothing on this list is a country score, a chapter average or a ranking.

## 9. Relationship to the status report and the monthly

**Status** keeps a qualitative narrative: what the position *is*, in Corpus's voice, why it is what it is. **The assessment** says where that position sits against a continental yardstick. They cannot be derived from each other — the narrative carries what the yardstick cannot, and the yardstick is what makes the narrative comparable — and they must not contradict.

**The check is soft.** A status section that describes a system in service while the assessment has its indicator at *Nascent* is a finding to reconcile, reported by the build, not a failure that blocks a render. This is a useful invariant the layer could not state before, because the status report had nothing countable to agree with.

**The monthly** is unchanged, except that `report-country-skeleton.md`'s *no maturity verdicts — that is the status report's job* becomes *that is the assessment's job*. The ledger's row-level `movement` vocabulary (*Advanced · Stalled · Regressed · Closed · No change · Baseline not held*) stays: it is the record layer's field, the monthly reads it, and — as `progress-report-redesign.md` §2 already ruled — the indicator layer does not.

## 10. What retires

The indicator-level progress vocabulary and everything downstream of it. CC enumerates the wiring at build; this is the list as far as a Cowork read of the tree goes:

- the progress document (`{unit}-progress.md`), its PDF edition, the `/progress/` page and its six counts (`scripts/progress.py`);
- the *Progress* column, the vocabulary closure checks and the *Mixed ⇒ qualifier* check; the Developments word bands in `report-country-skeleton.md` insofar as they served the progress document;
- `progress-narrative-archive.md`, `logs/progress-report-log.csv`, the `progress-filler` batches and `scripts/progress-filler-gaps.py`;
- `documentation/progress-report-redesign.md` → `archived/`, with a pointer here; its §2 (the ledger stays the record layer), §4 (*No evidence* is presented, not counted), §5 (terse in the table, full in the expander) and §8 (the coverage byproduct) carry over unchanged and are restated in this note by reference;
- `documentation/indicator-mapping-conventions.md` → *Choosing the value* rewritten for stages; the rest of that file stands;
- `documentation/report-country-skeleton.md` → the three-document table and the *what goes in each* section, amended for status · monthly · maturity;
- the six frame rows that leave the assessment stay in `lookups/indicators.csv` with `assessed = 0` (`adding-an-indicator.md` §7): ids are never deleted, and their 314 mapped rows across the 54 countries remain the coverage byproduct's and the sovereignty indicator's evidence.

What does **not** retire: the frame, the mapping, the per-unit `indicators.csv`, the coverage byproduct, the ledger's movement column, the status report, the monthly.

**CC's read of the tree, 2026-09-23 (task A3).** The list above is incomplete in two places of scope and about thirty files of wiring.

- **Topic progress reports retire too.** `outputs/topics/{slug}/{slug}-progress.md` (38) are built by `topic-render.py`'s `build_progress()` from the country *Progress* column, so they cannot outlive it; the one-indicator view (§8, task F3) takes their place, and `topic-page.py` loses the row.
- **Region progress reports stay** (CC's call, reversible). XAF, XSA, XWA and the other region units render `render_progress_movement` from the ledger's movement vocabulary, which §9 keeps, and the regions are not assessed. They keep printing until Bill says otherwise.
- **Wiring §10 does not name**, all for G1: `report-render.py` (`--doc progress`, the profiles, `PROGRESS_VOCAB`, `mark_progress`, `render_progress_indicators`, check J's progress branch, checks L and M over the indicator prose); `report-register-check.py` (progress word bands and its read of the indicator prose); `render.py` (label, badges, table classes, `meta-progress` keys, contents bar); `editions.py` and `test_editions.py` (progress stems); `country.py`, `home.py`, `chrome_lib.py` (the *Progress* nav item), `copy_lib.py`, `region.py`, `rebuild.py`; `indicators_lib.UNIT_FIELDS`; `lint-indicators-draft.py`, `lint-considered.py`, `reread-brief.py`, `filler-batch.py`, `lint-structured-data.py`, `lint-notes.py`; `test_indicators.py`, `test_report_register_check.py`; `report.css`, `progress.css`, `progress-sticky.js`; the `Progress indicator` header; `content/document.md`, `methodology-lookups.md` (*Progress Categories*), `country.md`, `home.md`, `topic.md`, `process-inventory.md`, `document-lifecycle.md`; `README.md`, `RENDER.md` (the render loop and Step 4a), `BUILD.md`, `REREAD.md`, `UNIT-REVIEW.md`, `STATUS-INIT.md`; `.gitignore`'s `logs/progress-filler/` rules; `report-layer.md`, `render.md`, `topic-reports.md`, `design.md`, `build.md`, `report-region-skeleton.md`, `considered-not-carried.md`, `baseline-filler.md`, `datasets.md`, `catalogue-serving-shape.md`; `logs/indicator-mapping-progress.md`; `prep/progress-*`; `prototypes/build-*-page.py`. Published `-progress` HTML and PDFs are editions and stay where they are; only new ones stop.

## 11. Checks

New, alongside the existing lettered checks; letters to be assigned by CC in sequence.

- stage ∈ {1..5} on every row present for an assessed indicator; a row absent ⟺ *No evidence* (check I, unchanged); a row present for an `assessed = 0` indicator carries no stage;
- stage change between consecutive snapshots ⇒ a cited row dated inside the window, or `reassessed = 1`;
- stage 1 ⇒ `row_ids` non-empty;
- kind = measure ⇒ all four value columns present, `value_year` ≤ as-at year;
- no count in any output crosses kinds;
- every assessed indicator in the frame has a row in `maturity-norms.csv` and five rows in `maturity-rubric.csv`;
- the number of Corpus-defined norms and of interpolated rungs is published on the methodology page and matches the lookups;
- status/assessment agreement: reported, not blocking (§9);
- a month's edition file, once written, is byte-identical on rebuild (the editions rule, applied to `maturity/{YYYY-MM}.csv`);
- the frame count is never hard-coded in logic — `scripts/progress.py` and `report-render.py` say *121* in prose and descriptions today, and the retirement commit removes or generalises every one.

## 12. Build sequence

Each step is a commit or a few, reviewable on its own; CC does the operational steps and Cowork the drafting ones, per the division of labour. The live September snapshot is due 2026-10-05, which is thirteen days from the ruling; steps 1–5 are what has to exist by then, and if they do not, the September snapshot is taken retrospectively like July's and August's and the first live one is October's on 2026-11-05.

1. **Confirm the *not verified* items** in the register's §6 against primary texts. Research, not code; runs in parallel with everything below.
2. **The frame change.** Per `adding-an-indicator.md`: the `geopol.sovereignty` subject goes to OSINT as a patch (`indicator-digital-sovereignty.md` §3); `lookups/indicators.csv` gains `kind` and `assessed`, the six leaving rows are flagged, the two new rows are minted once the subject exists; `status-outline.md` gains the two sub-section bullets.
3. **Lookups.** Cut `lookups/maturity-norms.csv` from the register. Draft `lookups/maturity-rubric.csv` — 585 anchors — in Cowork, chapter by chapter, and have CC review each chapter for consistency with the mapping conventions before the next is started. The instrument family goes first because the AU instruments supply its rungs; measures last, because each needs its reference dataset and its Africa-quintile year named.
4. **The assessment pass.** Extend the mapping pass to write `stage` and the new columns against the rubric; write the checks in §11; run the baseline as at 2026-07-31 over all 54 countries, which re-verdicts every mapped indicator row (about six and a half thousand) without re-mapping any; then the 2026-08-31 snapshot; the two new indicators are mapped in the same pass from the rows already held.
5. **Snapshots and history.** The month-end edition writer, the history appender, the editions check, and the 5th-of-the-month schedule in `BUILD.md`.
6. **Renderers.** The movement note, the grid, the stage counts, the one-indicator view, the DPI cross-check; the site pages; the methodology page with the published counts; the changelog entry.
7. **Retire the progress report** per §10, in one commit that also archives `progress-report-redesign.md` and amends the skeleton and the mapping conventions.

## 13. Still open

Nothing. Both questions left open on 2026-09-22 were ruled by Bill on 2026-09-23 and are in §2.

## What is and is not verified in this note

The norms were checked against live sources on 2026-09-22 by four research passes; where a provision, decision number or ratification count could not be read, the register says so and §6 there lists what is owed. The counts in §5 were computed from the register's rows by script after the frame change. The frame, the per-unit file layout, the mapping conventions and the three-document design were read from the tree; the count of mapped `geopol.*` and `finance.mou` rows (260 and 54) was counted from the 54 per-unit files; the retirement list in §10 is from that read and CC should expect to find wiring it does not name. No code has been written, no lookup cut, no indicator file touched, and nothing has been rendered.
