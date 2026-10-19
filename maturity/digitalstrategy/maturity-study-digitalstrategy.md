---
type: task
reader: cc
title: maturity-study-digitalstrategy.md — the seventh maturity study and the first of an instrument: the national digital transformation strategy
last_reviewed: 2026-10-11
status: CC's proposal, run on Bill's word of 2026-10-11; staged, written and on the soft-launch map as at 2026-09-30; awaiting Bill's acceptance
---

# Maturity study: digitalstrategy — the national strategy

*(Commissioned by Bill on 2026-10-11, under `maturity/documentation/maturity-study-method.md`. CC's proposal throughout. Trigger: "**run maturity study digitalstrategy**".)*

## 1. The question, and the row it redraws

**Does the country have a national digital strategy in force, and does it publish what the strategy has delivered?** `gov.policy--digital-transformation-strategy` stages 45 cells: 26 at stage 3, 19 at 2, none at 1, 4 or 5, and 9 unplaced. Two things cause that.

- **No settled subject.** Cells hold national strategies, public-service plans, a development plan's pillar, an agency's plan, a ministerial roadmap and a connectivity strategy as one thing.
- **A fourth rung asking for four things at once**: a costed plan, a mandated body, a progress report and budget lines.

**This is the first study of an instrument.** The method's rule that a strategy places nothing above stage 2 was written for systems. Here it becomes: **adoption alone places no higher than 3**; above that the test is published reporting.

**One sub-indicator replaces the row**:

| Sub-indicator | Indicator text | Id |
|---|---|---|
| National strategy | Digital transformation strategy: national strategy | `gov.policy--digital-transformation-strategy` |

**`gov.policy--ict-strategy` is not redrawn.** It stages on the same document as this row in at least 14 countries; that is its own study's to settle.

## 2. Typology

| Class | What it is | Treatment |
|---|---|---|
| `national` | **The government's own strategy for digital change across the economy and the state**: adopted, or to be adopted, by the government as a whole | Assessed |
| `government` | A strategy for digitalising the state's own administration and services, and nothing beyond them | Noted, not assessed; flagged |
| `development-plan` | A digital pillar or chapter of a national development plan or vision | Noted, not assessed; flagged |
| `ministry-plan` | A ministry's, regulator's or agency's own strategic plan or roadmap | Noted, not assessed |
| `directive` | A law, decree, ordinance or order to digitalise, with no strategy behind it | Noted, not assessed |
| `programme` | A financed project or programme, donor or domestic | Noted, not assessed; read for finance |
| `sector-ict` | An ICT or telecommunications sector policy | Logged for `gov.policy--ict-strategy` |
| `thematic` | A strategy for one technology or layer: broadband, AI, data, cloud, cybersecurity, public infrastructure | Out of scope: its own row |
| `regional` | A strategy of a regional community or the African Union | Out of scope |

**The test: is it the whole government's strategy, and does it cover both the economy and the state?** Read from the text or from a source describing its pillars. A *digital economy strategy*, *digital agenda* or *master plan* is `national` where it passes; the label is the country's.

**The whole government.** Adopted by the cabinet, the head of state or government, or parliament. A ministry's own roadmap is `ministry-plan`, whatever it is called.

## 3. Aspects

| # | Aspect | Role | Values |
|---|---|---|---|
| 1 | Governance and finance | qualifier | Body: a named body `mandated` to deliver or coordinate it, or `none`. Finance: a `domestic` budget line a source ties to the strategy, `donor` only, or `not-stated` |
| 2 | Standing | coverage | `adopted`. `validated`: complete and awaiting adoption. `drafting`. `announced`. `none` |
| 3 | Text | coverage | `public`: held, or linked or quoted by a source from an official site. `unpublished`: a source says there is none |
| 4 | Period | coverage | `to:YYYY`, the year its stated period ends, or `open` |
| 5 | Delivery plan | coverage | `costed`: an implementation or action plan stating what it costs. `actions`: dated actions or targets with no cost. `none` |
| 6 | Reporting | coverage | `results-all`: a published report, review or evaluation giving progress against the strategy's own targets or actions, on every pillar. `results`: the same on some. `activity`: implementation claimed, measured against nothing in the strategy. `none` |
| 7 | Last twelve months | qualifier | Advancing, no change on record, or regressing, with the dated event |

**Aspects 2 to 6 set the stage; 1 and 7 cap or flag it and never raise it.**

**The cap rule.** Without a mandated body and a domestic budget line, stage 4 or 5 is capped at 3 and flagged *no budget or body*.

**Flags that never change the stage.** *Government only* and *in the national plan*, for the noted class held instead; *lapsed*; *text unpublished*.

**One instrument, one name.** `instruments.csv` gives every named instrument its class, its name and its period's end; a cell is staged on the instrument in force, never on a mix.

## 4. The ladders

Staged as at 2026-09-30: 18 at stage 3, 27 at 2, 2 at 1, 5 unplaced, 2 with no evidence. **Rungs 4 and 5 are unreached and stand**: no government report against a strategy's own targets is held.

**National strategy**

| Stage | Standing | Text | Period | Delivery plan | Reporting |
|---|---|---|---|---|---|
| 1 Absent | A dated statement that there is no national digital strategy, with none on record as adopted, launched or in preparation | | | | |
| 2 Preparing | `announced`, `drafting` or `validated`; or `adopted` | For an adopted strategy: not public | Or ended, with a successor in preparation | Any | Any |
| 3 Establishing | `adopted` | `public` | Not ended, or `open` | Any | Any |
| 4 Operating | `adopted` | `public` | Not ended | `costed` or `actions` | `results` or `results-all`, published within three years |
| 5 Leading | `adopted` | `public` | Not ended | `costed` | `results-all`, published within two years |

**A noted class never places a country above stage 1.** A country holding only noted classes is unplaced.

**An expired strategy** with no successor in preparation leaves the cell unplaced and flagged *lapsed*.

**An open strategy stops at stage 3. Stage 5 has no alignment test**: method §3 rule 5.

**Fixed at D3** (`corrections.csv`):

- **Adoption is the source's own word**: *approved*, *adopted*, *enacted* or *gazetted*; the act named is not required. A launch by a ministry alone is `announced`.
- **A text the government has published, and no source calls a draft, is read as adopted.** A text that calls itself a proposal, or asks to be approved, is not; nor is a proposal the text of the strategy later approved.
- **A published rate of execution of the strategy's own actions is `results`.**
- **A fact is kept for a named strategy whose scope its document does not describe**; the class comes from the documents that do.

## 5. The norm

The norm is the African Union's Digital Transformation Strategy for Africa 2020-2030. Under its enabling-environment pillar it asks states to "develop and implement national and sectorial digital strategies". Its monitoring section covers the continental strategy itself.

**The norm names the subject and measures nothing.** The ladder takes one thing from it: *develop and implement*, so adoption is not the top.

## 6. What the review reads and the search asks for

- **Subjects and term list**: in `study.json`.
- **Source types for the briefs**, ranked: the strategy's own text and its action plan; the adopting act in the official gazette or a cabinet communiqué; the government's implementation or mid-term reports on it; budget and audit reports naming it; evaluations by the World Bank, UNDP and the ITU; dated news, for aspect 7.

## 7. Tasks, in order

- [x] **D0. Prepare the criteria** (method step 1): this file and `study.json`, 2026-10-11.
- [x] **D1. Bill's rulings**: the seven proposals stand, 2026-10-11.
- [x] **D2. Review all 54 countries**, method §4: 3,433 documents, 89 slices, 143 read twice; 725 facts.
- [x] **D3. Test and fix the ladder**: 289 corrections.
- [x] **D4. Search and hand over**, method §5: 54 searches, 67 documents for 34 countries, `notes-for-osint` 226.
- [x] **D5. Re-read and stage**, method §7: 61 of 67 admitted, 90 documents read, 867 facts; agreement 19 of 20.
- [x] **D6. Write, render and lint.** **D7. Report to Bill.**

**The rulings of D1**, run unamended:

1. Adoption with a public, current text is stage 3 and no higher; stages 4 and 5 are set by published reporting against the strategy's own targets.
2. An adopted strategy with no public text is stage 2.
3. A strategy for government services only is noted, not assessed.
4. A digital chapter of a national development plan is noted, not assessed.
5. Without a mandated body and a domestic budget line, stage 4 or 5 is capped at 3.
6. Alignment with the African Union's strategy is not a test at any stage.
7. Only this row is redrawn; the ICT strategy row waits for its own study.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
