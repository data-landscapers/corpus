---
type: tasks
title: Maturity assessment — the build, as sequential tasks with owners
date: 2026-09-22
source: documentation/maturity-assessment.md §12 (expanded here); maturity-assessment-norms.md; adding-an-indicator.md; indicator-digital-sovereignty.md; indicator-financial-sustainability.md
status: in progress; A, B1–B3, C1, C2 (instruments and systems), C4 done 2026-09-23
---

# Maturity assessment — tasks

*(Written 2026-09-22 in Cowork at Bill's request, expanding `maturity-assessment.md` §12 into the order the work is done in and who does each piece. Owners: **Bill** decides; **Cowork** drafts and designs; **CC** builds, runs and reviews; **OSINT** applies what is delivered to it. Every task names what it depends on and what *done* looks like, so that a fresh CC session can pick the next one up from this file alone. Sizes are Cowork's estimate and unverified: **S** under an hour, **M** a sitting, **L** more than one.)*

**The clock.** The baseline is as at 2026-07-31 and the first snapshot as at 2026-08-31, both constructed retrospectively. The first *live* snapshot is September's, due on 2026-10-05. Phases A–E have to be complete by then for that to happen; if they are not, September is taken retrospectively with the other two and the first live run is October's on 2026-11-05. Phases F and G are not on the clock: the assessment can exist in `outputs/` before it is rendered, and the progress report can keep printing until its replacement is on the site.

**Commit discipline throughout**: one commit per task or per numbered step inside a task, pushed at the end of the sequence it belongs to; every reader-visible change carries a `content/changelog.md` entry in the same commit.

## Where this stands

**As of 2026-09-24.** Phase A is done. B1–B3 are done: OSINT applied note 164 on 2026-09-23, and the frame holds 123 rows, 117 assessed. C1 is done (117 norms rows) and so is C4 (`budgets/{ISO3}/external.csv`). C2 has cut every instrument and system, 95 of 117 with 347 interpolated rungs. **D1–D4 done 2026-09-24** (D3's render-side checks come with F); the July baseline is applied. **C3 cut 2026-09-24** (three rows owed), **C5 built**. **Open on the critical path**: D5 (August), then D6 (Bill reads the two runs). B4 done 2026-09-24.

---

## Phase A — decisions and confirmations (nothing built until A1 is done)

### A1. Rule on the two open placements — **Bill** — S — *done 2026-09-23: `finance.sustain`; July recut*

Two questions in `maturity-assessment.md` §13: whether the financial sustainability indicator sits under `finance.budget` (no taxonomy change) or gets its own `finance.sustain` subject (travels to OSINT with `geopol.sovereignty`); and whether the Africa-quintile cadence is *cut at the baseline, recut each July*. Done when both are written into `maturity-assessment.md` §2 as rulings. Everything below assumes `finance.sustain` and the July recut.

### A2. Confirm the register's not-verified items — **CC** (research, not code) — M, runs in parallel with everything through Phase C — *done 2026-09-23: §6 closed save three status lines (DES organ, DTP ratification count, DAS period), none a provision; corrections in §3–§4*

`maturity-assessment-norms.md` §6: decision numbers (DTS, DPF, AI Strategy, Compact, Interop. Framework, STYIP, PIDA PAP 2, DES, DAS, CESA, STISA), current ratification counts on the AU treaty status lists, Malabo article numbering and the Art. 14 paragraph, DTP article numbers against the deposited text, the CAMCR declaration texts, the ACHPR Model Law URL, the land-policy F&G provisions, ATU-R Report 004-0, STISA's R&D benchmark, ARSO's and PAQI's provisions, and whether the DTS mid-term review has revised any target. Each item is either confirmed in the register (with the source) or left flagged with what was tried. Done when §6 is empty or every remaining line says why it cannot be closed. **Nothing in C1 is cut as fact while its line is still in §6.**

### A3. Tell CC the shape of the work — **Bill** — S — *done 2026-09-23: the unnamed wiring and two scope calls are in `maturity-assessment.md` §10*

Point CC at this file and the five documents. Done when CC has read them and logged any wiring the retirement list (`maturity-assessment.md` §10) does not name — that list is from a Cowork read of the tree and is expected to be incomplete.

---

## Phase B — the frame change (`adding-an-indicator.md`)

### B1. Cut the taxonomy patch for OSINT — **CC** → **OSINT** — S to cut, then blocked — *done 2026-09-23: `prepared/note-164/`, `notes-for-osint` 164, applied by OSINT the same day*

`scripts/osint-patch.py prepare`; in the clone add `geopol.sovereignty` — Digital sovereignty and `finance.sustain` — Financial sustainability to OSINT's `lookups/taxonomy.md` and to `lookups/report-region-sections.csv`; `cut`; deliver to `prepared/` on the share with the base commit named; write the `[ACT]` note in `notes-for-osint.md` asking OSINT to apply it and mint the two concept pages (wiki prose, which a patch may not carry), `Affects: lookups/indicators.csv, the maturity assessment's Geopolitics and Finance chapters`; commit and push the share. (Corpus's `lookups/taxonomy.csv` is its own display copy and gains the two rows at B3.) Run `lint-prepared.py`, `lint-notes.py`, `lint-preambles.py`. Done when the job is on the share and `git log` on the share shows it pushed. **B3 is blocked until the mirror shows the subjects**; B2 is not.

### B2. Add `kind` and `assessed` to the frame; flag the six that leave — **CC** — S — *done 2026-09-23: 115 assessed of 121 (43 I, 51 S, 21 M; B3's two make it 44, 51, 22); progress render unchanged*

`lookups/indicators.csv`: two new columns, `kind` from `maturity-assessment-norms.md` §3 (44 I, 51 S, 22 M — the register is the source, not this file), `assessed = 1` for all except the five `geopol.*` rows and `finance.mou--strategic-relationships`, which get `assessed = 0` and `retired = 2026-09-22` in a third new column. `indicators_lib.frame()` learns the three columns and exposes `assessed()`; `test_indicators.py` gains a case that the frame reads with the new columns and that an `assessed = 0` row is not returned by the assessed view. The `Progress indicator` column keeps its name for now. Done when the tests pass and `report-render.py` still renders the progress report unchanged (it must not notice `assessed` yet — the progress report keeps printing all 121 until G1).

### B3. Mint the two new frame rows — **CC** — S, blocked on B1 — *done 2026-09-23: 40 subjects, 123 rows, 117 assessed; `finance.sustain` inserted at 8 so Finance stays one group; progress and topic documents re-rendered; `progress.py` prints an indicator with no evidence anywhere unlinked*

Add the two subjects to Corpus's `lookups/taxonomy.csv` (`finance.sustain` at 8 inside Finance, `geopol.sovereignty` at 40), then `geopol.sovereignty--digital-sovereignty` and `finance.sustain--financial-sustainability-of-digital-systems`, per §3 of each indicator document. `indicators_lib.ids()` shows no collision. The frame count is now 117 assessed of 123 rows. **Grep `scripts/` for `121`** and fix every docstring, description and comment that states it (`progress.py`, `report-render.py`, `rebuild.py` are known); none may be in logic. Done when the tests pass and the grep is clean. If B1 is still blocked when Phase D is ready to run, run the baseline without the two, and add them later under `adding-an-indicator.md` §8 with the July and August rows flagged `added`.

### B4. Status outline — **Cowork** drafts, **CC** commits — S — *done 2026-09-24: 40 sub-sections, the two new ones on the DPI ids CC listed*

`status-outline.md`: the `### geopol.sovereignty — Digital sovereignty` sub-section with its question and bullets (`indicator-digital-sovereignty.md` §6, with CC checking which DPI variable ids exist); a new `### finance.sustain — Financial sustainability` sub-section with the sustainability bullet (`indicator-financial-sustainability.md` §6). Done when the outline's own counts at the top are updated and the file says 40 sub-sections.

**The DPI ids for Cowork's draft** *(CC, 2026-09-24, read from `prep/africa-dpi-data.csv`, 453 variables)*. **No `reg-data-*` variable exists.** Hosting: `ict-storage-govcloud`, `ict-storage-dcpresence`, `ict-storage-cloudadoption` (weak proxies, as §6 says). Classification and localisation: `ict-storage-datalocalisation`, `govtech-cloud-1.6` (hosting policy), `reg-cyber-cloud`, `reg-egov-cloudpolicy`. **`exchange-uptake-sovereignty`** (*Data Sovereignty Provisions*) is the closest variable to the question, and §6 does not name it. Vendor dependence and the terms of agreements have no variable, so the wiki answers them. `finance.sustain` cites no DPI variable, by design.

---

## Phase C — the lookups and the rubric

### C1. Cut `lookups/maturity-norms.csv` from the register — **CC** — S, after A2 has closed the lines it can — *done 2026-09-23: 117 rows (105 AU, 7 continental, 4 global, 1 corpus) by `scripts/maturity-norms-cut.py`; `--check` says whether the lookup is still the register's cut; 8 rows carry `not verified`*

One row per assessed indicator (117), columns `indicator_id, kind, tier, instrument, adopting_body, adopted, status, provision, fixes, reference, url, vintage, notes`, cut by script from `maturity-assessment-norms.md` §3 and §4 rather than retyped, so the register stays the source until the lookup exists and the two cannot disagree at birth. A row whose §6 item is still open carries `provision not verified` in `notes`. A check (D3) will require a row per assessed id. Done when the lookup has 117 rows, one tier value from the five, and `lint-structured-data.py` (or its successor) reads it clean.

### C2. Draft the rubric, chapter by chapter, with a review after each — **Cowork** drafts, **CC** reviews — L, the longest task — *Every instrument and system accepted and cut 2026-09-23 (95 of 117, 347 interpolated rungs); the 22 measures are C3; checker `lint-maturity-rubric.py`, cut `maturity-rubric-cut.py`, reviews in `maturity-rubric-review.md`*

`lookups/maturity-rubric.csv`: `indicator_id, stage, anchor, interpolated` — 585 rows. The order is the one `maturity-assessment.md` §12 gives: **instruments first** (Governance and Finance chapters, 44 rows × 5 = 220), because the AU instruments supply their rungs; then **systems** (DPI, Infrastructure, Digitalisation, Technology, Inclusion, Data); **measures last**, because each needs its value definition, unit, reference dataset, target or Africa-quintile cut and the cut's year (C3). Cowork drafts one chapter and stops; CC reviews it against the mapping conventions, the generic scale (`maturity-assessment.md` §3) and the two indicator documents' worked rubrics, and either commits it or sends it back with what to change; only then is the next chapter drafted. Each `anchor` names evidence a mapped row can satisfy, never a feeling; each `interpolated` is honest to the register's *fixes* column (a *top*-only anchor has four interpolated rungs). Done when 117 × 5 rows exist, every `interpolated` value matches the register, and the count of interpolated rungs is written into the methodology draft (F4).

### C3. Define the measures: value, unit, source, band — **Cowork** drafts, **CC** checks the datasets exist — M, inside C2's last leg — *accepted and cut 2026-09-24: 22 measures, `lookups/maturity-measures.csv`; partner financing is the on-budget share (Bill); items 6–8 (10+ ownership, 5 GB basket, `tech.industry`) owed by Cowork and re-cut on arrival. C2 is therefore complete: 117 × 5 rows*

For each of the 22 measures: the figure's definition; the unit; the reference dataset named in the register and its latest vintage; the target value where the norm has one (as an absolute, not time-adjusted); otherwise *Africa quintiles, cut at 2026-07-31, recut each July*; and the precedence rule restated per row (Corpus's cited figure over the dataset's — `maturity-assessment-norms.md` §7). The financial sustainability row carries the provisional absolute bands and the fifteen-country trigger (`indicator-financial-sustainability.md` §5). Done when every measure row in the rubric has all of these and CC has confirmed each dataset is reachable and its latest year recorded.

### C5. Pull the reference datasets into Corpus — **CC** — M, after C3's vintages — *added 2026-09-24; built the same day: `scripts/maturity-reference.py`, 9 measures and 2 denominators from WDI, the SDG API, UIS, ILOSTAT and Data360; affordability, `tech.industry` and the urban–rural ratio wait on C3 items 7–8 and wiring*

A measure is assessed for every country, from the reference dataset where the base holds nothing (`maturity-assessment.md` §4). But a country whose only figure is ITU's has no ledger row, so the figures have to be in Corpus as data. `scripts/maturity-reference.py` fetches each measure's reference series for the 54 countries, by API where one exists and by the published file otherwise, into `reference/measures.csv` and `reference/denominators.csv` (tracked, beside `budgets/`; `prep/` is the untracked alpha workspace). Each fetch is dated, and the release date is what `ref:{dataset}@{date}` cites. It also supplies GDP and population as denominators. Done when every reference named in `lookups/maturity-measures.csv` is held with its release date, and the packet shows the reference figure for each measure beside anything the base holds.

### C4. Extend the budget extract for the sustainability denominator — **CC** — M, can run any time after A1 — *done 2026-09-23: `budgets/{ISO3}/external.csv` for nine read country-years (not four), `budget_source.py --share`, BUDGET-EXTRACT step 4a, the conventions exception*

`indicator-financial-sustainability.md` §5 and §7: record the externally financed digital total per read country-year (CC chooses `budgets/{ISO3}/external.csv` or a column on `logs/budget-extract.csv`), backfill it for GHA, MDG, NER and CAF from the log notes and the documents, add the step to `BUDGET-EXTRACT.md`'s sitting, and write the one-sentence exception into `indicator-mapping-conventions.md` (a measure may cite a `budgets/` country-year as `value_source`; `row_ids` may then be empty for this indicator alone). Done when the four shares compute from the files and the sitting procedure carries the step.

---

## Phase D — the assessment pass and its checks

### D1. The assessor: write `stage` and the new columns — **CC** — L — *done 2026-09-24: `scripts/maturity-assess.py` (`packet`, `apply`) and `documentation/maturity-assessor-brief.md`; STP assessed end to end in a scratch copy, 88 staged or unplaced, checks N–S clean; measures pending C3*

Extend the stage-4 mapping pass (BUILD.md → *Stage 4*) so that a mapped indicator row is assessed against `maturity-rubric.csv` and carries `stage, value, unit, value_year, value_source, next_milestone, due, assessed_on, reassessed, qualifier` per `maturity-assessment.md` §6 — `progress` is not written any more, though it is not removed from existing files until G1. The pass reads the ledger and the mapped rows as today, cites the rows that satisfy the anchor, and records the stage with the qualifier. `UNIT_FIELDS` in `indicators_lib.py` grows accordingly and `load_unit()` reads both old and new shapes until G1. Done when a single unit can be assessed end to end and its file round-trips through `load_unit()`.

### D2. The as-at rule and the stability rule — **CC** — M, inside D1 — *done 2026-09-24, in `apply`; a change no dated row supports is held at the prior stage and reported*

The assessor takes an `--as-at YYYY-MM-DD` and reads only rows dated on or before it; a stage may differ from the previous snapshot's only if a cited row is dated inside the window (previous as-at, as-at] or `reassessed = 1`; otherwise the prior stage carries forward. This is the load-bearing rule and is implemented in the pass, not left to the model. **One named exception** (rubric review, 2026-09-23): any anchor keyed to *the 12 months to the as-at date* (four rows in the rubric: open discussion, open data stage 4, citizen participation, sovereignty) may move when an event leaves the period; the ageing-out is the dated cause, dated the day it leaves, and is logged like any other. Done when a unit assessed twice against the same rows yields identical stages, and a unit assessed with one new dated row moves only the indicators that row is mapped to.

### D3. The checks — **CC** — M — *done 2026-09-24 in part: `scripts/lint-maturity.py` N–T, unit checks under `report-render.py --check`; R fails on the 22 measures until C3. Cross-kind counts, published counts and status agreement come with F1/F3/F4, which make the outputs they check*

The list in `maturity-assessment.md` §11, as checks in the report-lint sequence with the next free letters: stage domain and the `assessed = 0` rule; change ⇒ dated row or `reassessed`; stage 1 ⇒ citation (or `value_source` for the budget measure); measure ⇒ four value columns and `value_year` ≤ as-at year; no cross-kind count; a norms row and five rubric rows per assessed id; published counts match the lookups; status/assessment agreement reported not blocking; edition byte-identity on rebuild; no hard-coded frame count. Each check has a case in `test_indicators.py` or a new `test_maturity.py`. Done when the suite passes on the D1 unit and fails on a deliberately broken copy of it.

### D4. Run the baseline as at 2026-07-31 over all 54 countries — **CC** — L (model authoring; budget it like a filler run) — *done 2026-09-24: 54 editions `maturity/2026-07.csv`, 5,440 cells staged or unplaced (1 282 · 2 1,881 · 3 1,854 · 4 212 · 5 10 · unplaced 1,201); verdicts in `logs/maturity-verdicts/`; seven quintile rows cut; checks N–T clean*

The two new indicators are mapped in the same pass from rows already held (`indicator-digital-sovereignty.md` §7: the 260 `geopol.*` rows and the four related indicators' rows; `indicator-financial-sustainability.md` §7: the four read country-years). Every previously mapped row is re-verdicted, none re-mapped. Expect, and record, the stage distribution per kind and the *No evidence* count; expect most countries at 2–3 on measures and the sustainability indicator assessable in four. Done when all 54 units carry stages, D3 is clean, and `logs/` holds the run's one-line record.

**How to run it** *(CC, 2026-09-24; the machinery is D1–D3 and C5)*:

1. `python scripts/maturity-reference.py` if the reference is more than a month old. Commit `reference/` if it changed.
2. **Per unit, the drafting**: `python scripts/maturity-assess.py packet {UNIT} --as-at 2026-07-31 --out <scratch>/{UNIT}-2026-07.md`. A subagent drafts from it under `documentation/maturity-assessor-brief.md` and writes `logs/maturity-verdicts/{UNIT}-2026-07.csv`. The verdicts are kept and committed: they are the drafter's judgement, and the edition is not the only record of it. Instruments and systems need a verdict. Measures need one only where the base holds a primary figure or a condition decides. Batch the units six at a time; STP took about 130k tokens.
3. **The cut**, once every unit is drafted: `python scripts/maturity-assess.py cut --as-at 2026-07-31 --verdicts-dir logs/maturity-verdicts` as a dry run. Read the band counts. The guard (`maturity-rubric.md`, *How to read a measure*) applies before `--write`.
4. **Per unit, the apply**: `python scripts/maturity-assess.py apply {UNIT} --as-at 2026-07-31 --verdicts logs/maturity-verdicts/{UNIT}-2026-07.csv`. A refusal is fixed in the verdicts and re-run, never forced.
5. `python scripts/lint-maturity.py`: every unit N–S clean, R and T pass. Record the stage distribution per kind, and the *No evidence* and unplaced counts, in the run's log line. Commit per batch and push.

### D5. Run the 2026-08-31 snapshot — **CC** — M

Same pass, `--as-at 2026-08-31`, over the baseline; only rows dated 1–31 August 2026 may move a stage. The packet marks the in-window sources (▲). The drafter writes verdicts only for indicators that have one, or whose look-back anchor may have aged out. Everything else carries forward, which makes August far cheaper than July. Done when D3 is clean and the movement list (moved up / down / stalled / reassessed) is written to the log for inspection.

### D6. Read the two runs — **Bill** with **CC** — S

Bill reads two or three countries' assessed files and the August movement list against the status reports; anything that looks wrong is a rubric change (C2, flagged `reassessed` on rerun) or an assessor fix (D1), never a hand edit of a stage. Done when Bill says the baseline stands.

---

## Phase E — snapshots, history, the monthly runbook

### E1. Editions and history — **CC** — M — *the edition writer is in D1's `apply` (write-once, byte-identical on rerun, `--replace` only before publication); the history file and the render-side byte check remain*

`outputs/reports/{unit}/maturity/{YYYY-MM}.csv` written once per snapshot under the editions rule (`design.md` §9; the CR-only churn trap in `global-claude.md` applies — check before committing a rebuild); `outputs/reports/maturity-history.csv` appended per snapshot and rebuildable from the editions; `outputs/reports/{unit}/indicators.csv` stays the current position. Write the July and August editions and the history from D4 and D5. Done when the byte-identity check passes on a second render and the history file has 54 × (assessed rows) × 2.

### E2. `MATURITY.md` — the monthly runbook at the root — **Cowork** drafts, **CC** finishes — M

In the shape of `BUDGET-EXTRACT.md` and `STATUS-INIT.md`: trigger phrase (*run the maturity snapshot*), the as-at rule, the 5th-of-the-month schedule and where it sits in `CYCLE.md`, the pass, the checks, the editions, the movement list, the one-line log, the commit-and-push, and what to do when a run is late or a month is missed (take it retrospectively; never skip a month-end). `BUILD.md` gets a stage pointer, not a copy. Done when a fresh CC session can take the September snapshot from `MATURITY.md` alone.

### E3. The September snapshot, live, on 2026-10-05 — **CC** — S if E2 holds

The first run that is not retrospective. Done when the edition, the history row and the log line exist and D3 is clean. If A–E are not complete on the day, note it in the log, take September retrospectively when they are, and the first live run is 2026-11-05.

---

## Phase F — rendering and the site

### F1. The maturity document per country — **CC** — L

`outputs/reports/{unit}/{unit}-maturity.md`, rendered like status and monthly: a renderer-emitted explanatory paragraph (what a stage is, what *No evidence* means, that the assessment is against continental norms, and the published counts); the current stage table per chapter grouped by kind, with summary and the developments expander as the progress table had them; the monthly movement note — prose only for moved cells, each with its citing row, one sentence when nothing moved; a `reassessed` section when there is one. Word budget: set by the count of moved cells, on the monthly's per-row form. PDF edition per the editions rule. Done when a unit renders, `report-register-check.py` reads its prose columns, and the register check's bands are stated in `report-country-skeleton.md`.

### F2. The country grid — **Cowork** designs, **CC** builds — M

Indicators × months, grouped by chapter and kind, cell colour by stage, a mark on every changed cell, the data year on measure rows; static SVG at build; house palette and the design-consistency rules (`house-style.md`, `design.md`). Two months of columns is a thin grid — design for twenty-four and let it fill. Done when the SVG renders at 390px and 1366px without overflow and the audit script is clean.

### F3. The stage counts, the one-indicator view, the DPI cross-check — **CC** — M

Stacked bars per chapter and kind per month; one indicator across 54 countries as a distribution and over time; the monthly comparison of external scores (GTMI, EGDI, GCI from the DPI dataset) against Corpus stage, feeding `gaps.csv` where the external is high and Corpus is 1 or unassessed. Done when each is a page or a section on the assessment page and none prints a mean, a score or a rank.

### F4. The methodology page and the changelog — **Cowork** drafts, **CC** publishes — S

`/methodology/` gains the assessment: the scale, the kinds, the norm tiers with the counts (117 assessed; 105 AU, 7 continental, 4 global, 1 Corpus-defined; interpolated rungs from C2), the figure-of-record rule, the as-at and 5th-of-month rule, what *No evidence* means, and the retirement of the progress report. Changelog entries (two terse sentences each) for the assessment's arrival and for the two new indicators, as drafted in the indicator documents. Done when the counts on the page equal the lookups (D3 checks this).

### F5. `/maturity/` replaces `/progress/` — **CC** — M

The estate page: the six progress counts retire; the assessment's counts and the cross-country views take the URL's place; `/progress/` redirects. Done when the sitemap, the nav and the redirects are updated and `lint-external-links.py` is clean.

---

## Phase G — retirement

### G1. Retire the progress report — **CC** — M, one commit

Per `maturity-assessment.md` §10, including CC's read of 2026-09-23 under it (topic progress reports go; region ones stay): the progress document and its PDF edition stop being written; `progress` is dropped from `UNIT_FIELDS` and from the 54 files (a migration script, run once, that removes the column and nothing else); the vocabulary-closure and *Mixed* checks retire; `progress-narrative-archive.md`, `logs/progress-report-log.csv`, `progress-filler` and `progress-filler-gaps.py` go; `scripts/progress.py` goes with `/progress/`; `documentation/progress-report-redesign.md` moves to `archived/` with a pointer to `maturity-assessment.md`. Done when nothing in `scripts/` reads `progress` as an indicator value and the render is clean.

### G2. Amend the three documents that describe the layer — **Cowork** drafts, **CC** commits — S

`report-country-skeleton.md` (the three-document table; *what goes in each*; the word-budget section; *no maturity verdicts — that is the assessment's job*); `indicator-mapping-conventions.md` (*Choosing the value* rewritten for stages; the budget-measure exception from C4); `report-layer.md` (a paragraph saying the indicator layer now carries stages and the ledger's `movement` is unchanged). Done when `lint-preambles.py` and the doc-reading checks are clean and no document still says a country has three documents named status, monthly and progress.

---

## Phase H — verification (after everything above)

### H1. Verification pass — **CC**, report read by **Bill**

Re-run the whole suite (`test_indicators.py`, `test_maturity.py`, `test_editions.py`, `report-lint.py`, `lint-structured-data.py`, `lint-external-links.py`, `lint-shared-assets.py`, the design audit script). Rebuild and confirm the July, August and September editions are byte-identical. Pick three countries — one thin, one thick, one with a read budget year — and read the maturity document, the grid and the status report side by side; every disagreement the soft check reports is either a rubric issue logged for the next recut or an assessor issue fixed in D1. Confirm `/progress/` redirects and nothing in the built site still carries the word *Progress* as a column heading. Write *Where this stands* at the top of this file in CC's voice, as the design-consistency tasks file does, naming the commits.

---

## Dependencies at a glance

A1 → everything. A2 → C1 (partial). B1 → B3 (both new rows) → D4 (both assessed). B2 → B3 → D1. C1, C2, C3 → D1 → D2 → D3 → D4 → D5 → D6 → E1 → E2 → E3. C4 → D4 (sustainability assessed). E1 → F1 → F2, F3, F4, F5 → G1 → G2 → H1. B4 has no dependants and can be done any time after A1.

The critical path to the live September snapshot is A1 → B2 → C1 → C2 → D1 → D2 → D3 → D4 → D5 → D6 → E1 → E2 → E3, and C2 is where the time goes.
