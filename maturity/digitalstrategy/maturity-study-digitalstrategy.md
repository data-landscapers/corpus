---
type: task
reader: cc
title: maturity-study-digitalstrategy.md — the seventh maturity study and the first of an instrument: the national digital transformation strategy
last_reviewed: 2026-10-11
status: CC's proposal, run unamended on Bill's word of 2026-10-11; step 3 under way
---

# Maturity study: digitalstrategy — the national strategy

*(Commissioned by Bill on 2026-10-11, under `maturity/documentation/maturity-study-method.md`. CC's proposal throughout. Trigger: "**run maturity study digitalstrategy**".)*

## 1. The question, and the row it redraws

**Does the country have a national digital strategy in force, and does it publish what the strategy has delivered?** `gov.policy--digital-transformation-strategy` stages 45 cells: 26 at stage 3, 19 at 2, none at 1, 4 or 5, and 9 unplaced. Two things cause that.

- **No settled subject.** Cells hold national strategies, public-service plans, a development plan's pillar, an agency's plan, a ministerial roadmap and a connectivity strategy as one thing.
- **A fourth rung asking for four things at once**: a costed plan, a mandated body, a progress report and budget lines. Every stage 3 cell reads *no costed plan or M&E report on record*.

**This is the first study of an instrument.** The method's rule that a strategy places nothing above stage 2 was written for systems. Here it becomes: **adoption alone places no higher than 3**; above that the test is published reporting.

**One sub-indicator replaces the row**:

| Sub-indicator | Indicator text | Id |
|---|---|---|
| National strategy | Digital transformation strategy: national strategy | `gov.policy--digital-transformation-strategy-national-strategy` |

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

**Classified by what the source says the document covers**; a name alone is unclassified.

**The whole government.** Adopted by the cabinet, the head of state or government, or parliament. A ministry's own roadmap is `ministry-plan`, whatever it is called.

**Two strategies.** Where a strategy in force and a successor in drafting are both on record, the cell is staged on the one in force.

## 3. Aspects

| # | Aspect | Role | Values |
|---|---|---|---|
| 1 | Governance and finance | qualifier | Body: a named body `mandated`, by the strategy or by an act, to deliver or coordinate it, or `none`. Finance: a `domestic` budget line or allocation a source ties to the strategy, `donor` only, or `not-stated` |
| 2 | Standing | coverage | `adopted`, by a named act or a launch by the head of state or government. `validated`: technically complete and awaiting adoption. `drafting`. `announced`. `none` |
| 3 | Text and period | coverage | `current`: the text is public and the as-at falls inside its stated period. `open`: public, with no end stated. `expired`: the period has ended. `unpublished`: no public text |
| 4 | Delivery plan | coverage | `costed`: an implementation or action plan stating what it costs. `actions`: dated actions or targets with no cost. `none` |
| 5 | Reporting | coverage | `results-all`: a published report, review or evaluation giving progress against the strategy's own targets, on every pillar. `results`: the same on some pillars. `activity`: implementation claimed, measured against nothing in the strategy. `none` |
| 6 | Last twelve months | qualifier | Advancing, no change on record, or regressing, with the dated event |

**Aspects 2 to 5 set the stage; 1 and 6 cap or flag it and never raise it.**

**The cap rule.** Without a mandated body and a domestic budget line, stage 4 or 5 is capped at 3 and flagged *no budget or body*.

**Public text.** Held, or linked or quoted by a source from an official site. A press report of a launch is not the text.

**Reporting is published.** A minister's count of services or a project's progress report is `activity` unless it reports against the strategy's stated targets.

**Flags that never change the stage.** *Government only* and *in the national plan*, for the noted class held instead; *lapsed*; *text unpublished*.

## 4. The ladder

Proposed; tested and fixed at D3 (method §3 rule 9).

**National strategy**

| Stage | Standing | Text and period | Delivery plan | Reporting |
|---|---|---|---|---|
| 1 Absent | A dated statement that the country has no national digital strategy, or that the last one lapsed and none is being prepared | | | |
| 2 Preparing | `announced`, `drafting` or `validated`; or `adopted` | For an adopted strategy: `unpublished`; or `expired` with a successor in preparation | Any | Any |
| 3 Establishing | `adopted` | `current` or `open` | Any | Any |
| 4 Operating | `adopted` | `current` | `costed` or `actions` | `results` or `results-all`, published within three years |
| 5 Leading | `adopted` | `current` | `costed` | `results-all`, published within two years |

**A noted class never places a country above stage 1**, as in the police study (its §4). A country holding only noted classes is unplaced.

**An expired strategy.** With a successor in preparation it is stage 2. On a dated statement that none is, stage 1. With neither, the cell is unplaced and flagged *lapsed*.

**An open strategy stops at stage 3.**

**Stage 5 has no alignment test**: method §3 rule 5.

**Adoption is read from the fact's words.** *Approved*, *adopted* or *gazetted*, with the act or body named, is `adopted`; *launched* by a ministry alone is `announced` until an act is on record.

## 5. The norm

The frame's anchor (`lookups/maturity-norms.csv`) is the African Union's Digital Transformation Strategy for Africa 2020-2030. Under its enabling-environment pillar it asks states to "develop and implement national and sectorial digital strategies". Its monitoring section covers the continental strategy itself. *(Read 2026-10-11, from the held PDF.)*

**The norm names the subject and measures nothing.** It sets no date, no content and no reporting duty for a national strategy. The ladder takes one thing from it: *develop and implement*, so adoption is not the top. The OECD recommendation the lookup offers for rungs was not read; nothing is borrowed from it.

## 6. What the review reads and the search asks for

- **Subjects and term list**: in `study.json`.
- **Source types for the briefs**, ranked: the strategy's own text and its action plan; the adopting act in the official gazette or a cabinet communiqué; the government's implementation or mid-term reports on it; budget and audit reports naming it; evaluations and readiness assessments by the World Bank, UNDP and the ITU; dated news, for aspect 6.

## 7. Tasks, in order

- [x] **D0. Prepare the criteria** (method step 1): this file and `study.json`, 2026-10-11.
- [x] **D1. Bill's rulings**: the seven proposals stand, 2026-10-11.
- [ ] **D2. Review all 54 countries**, method §4. **D3. Test and fix the ladder.**
- [ ] **D4. Search and hand over**, method §5.
- [ ] **D5. Re-read and stage**, method §7. **D6. Write, render and lint.**
- [ ] **D7. Report to Bill.**

**The rulings of D1**, CC's proposals, run unamended:

1. Adoption with a public, current text is stage 3 and no higher; stages 4 and 5 are set by published reporting against the strategy's own targets.
2. An adopted strategy with no public text is stage 2.
3. A strategy for government services only is noted, not assessed.
4. A digital chapter of a national development plan is noted, not assessed.
5. Without a mandated body and a domestic budget line, stage 4 or 5 is capped at 3.
6. Alignment with the African Union's strategy is not a test at any stage.
7. Only this row is redrawn; the ICT strategy row waits for its own study.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
