---
type: task
reader: cc
title: maturity-study-ictstrategy.md — the eighth maturity study and the second of an instrument: the ICT and telecommunications sector policy
last_reviewed: 2026-10-11
status: CC's proposal; step 1 done, awaiting Bill's rulings at step 2
---

# Maturity study: ictstrategy — the sector policy

*(Commissioned by Bill on 2026-10-11, under `maturity/documentation/maturity-study-method.md`. CC's proposal throughout. Trigger: "**run maturity study ictstrategy**".)*

## 1. The question, and the row it redraws

**Does the country have a policy in force for its ICT and telecommunications sector, and does it publish what the policy has delivered?** `gov.policy--ict-strategy` stages 42 cells: 30 at stage 3, 11 at 2, one at 4, none at 1 or 5, and 12 unplaced. Three things cause that.

- **No settled subject.** Cells hold sector policies, national digital strategies, a development plan, a communications law, a regulator's decision, a tender and a minister's dismissal as one thing.
- **The same instrument staged twice.** At least 14 cells stand on the national digital strategy that `digitalstrategy` has already staged; eight share a staging row with it.
- **A fifth rung that is another row.** Stage 5 asks for the sector strategy to be superseded by a national digital transformation strategy, which is the neighbouring indicator.

**One sub-indicator replaces the row**:

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Sector policy | ICT strategy: sector policy | `gov.policy--ict-strategy-sector-policy` |

## 2. Typology

| Class | What it is | Treatment |
|---|---|---|
| `sector` | **The government's policy or strategy for the ICT and telecommunications sector**: its networks, market, regulation, access and industry | Assessed |
| `national` | The national digital strategy, as `maturity/digitalstrategy/instruments.csv` classes it | Noted, not assessed; flagged; staged on its own row |
| `law` | A communications or telecommunications act, code or decree that regulates the sector and states no policy | Noted, not assessed |
| `institution-plan` | A ministry's or regulator's plan for its own work | Noted, not assessed |
| `development-plan` | An ICT pillar or chapter of a national development plan or vision | Noted, not assessed; flagged |
| `programme` | A financed project or programme, donor or domestic | Noted, not assessed; read for finance |
| `subsector` | A policy for one part of the sector: broadband, universal access, spectrum, postal, broadcasting, outsourcing | Out of scope: its own row where there is one |
| `government` | A strategy for digitalising the state's own administration | Out of scope |
| `regional` | A policy of a regional community or the African Union | Out of scope |

**The test: does it set the government's policy for the sector as a whole?** Read from a source describing what it covers. A *national ICT policy*, *ICT4D policy*, *white paper*, *politique sectorielle* or *sector strategic plan* is `sector` where it passes; the label is the country's.

**One instrument, one row.** An instrument `digitalstrategy` staged as `national` is `national` here and is not staged twice, whatever it says of the sector.

**Adopted by the government or by the minister responsible for the sector.** A regulator's own plan is `institution-plan`.

## 3. Aspects

| # | Aspect | Role | Values |
|---|---|---|---|
| 1 | Governance and finance | qualifier | Body: a ministry, regulator or agency `mandated` to deliver it, or `none`. Finance: a `domestic` budget line a source ties to the policy, `donor` only, or `not-stated` |
| 2 | Standing | coverage | `adopted`. `validated`: complete and awaiting adoption. `drafting`. `announced`. `none` |
| 3 | Text | coverage | `public`: held, or linked or quoted by a source from an official site. `unpublished`: a source says there is none |
| 4 | Period | coverage | `to:YYYY`, the year its stated period ends, or `open` |
| 5 | Delivery plan | coverage | `costed`: an implementation or action plan stating what it costs. `actions`: dated actions or targets with no cost. `none` |
| 6 | Reporting | coverage | `results-all`: a published report, review or evaluation giving progress against the policy's own targets or actions, on every objective. `results`: the same on some. `activity`: implementation claimed, measured against nothing in the policy. `none` |
| 7 | Last twelve months | qualifier | Advancing, no change on record, or regressing, with the dated event |

**Aspects 2 to 6 set the stage; 1 and 7 cap or flag it and never raise it.**

**The cap rule.** Without a mandated body and a domestic budget line, stage 4 or 5 is capped at 3 and flagged *no budget or body*.

**Flags that never change the stage.** *Under the national strategy* and *in the national plan*, for the noted class held instead; *lapsed*; *text unpublished*; *dated*, for an open policy adopted more than ten years before the as-at.

**A regulator's market or annual report is `activity`** unless it reports against the policy's own targets.

**One instrument, one name**, in `instruments.csv`; a cell is staged on the instrument in force, never on a mix.

## 4. The ladders

**Sector policy**

| Stage | Standing | Text | Period | Delivery plan | Reporting |
|---|---|---|---|---|---|
| 1 Absent | A dated statement that there is no ICT or telecommunications sector policy, with none on record as adopted or in preparation and no national digital strategy held | | | | |
| 2 Preparing | `announced`, `drafting` or `validated`; or `adopted` | For an adopted policy: not public | Or ended, with a successor in preparation | Any | Any |
| 3 Establishing | `adopted` | `public` | Not ended, or `open` | Any | Any |
| 4 Operating | `adopted` | `public` | Not ended | `costed` or `actions` | `results` or `results-all`, published within three years |
| 5 Leading | `adopted` | `public` | Not ended | `costed` | `results-all`, published within two years |

**A noted class never places a country.** A country holding a national digital strategy and no sector policy in force is unplaced and flagged *under the national strategy*.

**An expired policy** with no successor in preparation leaves the cell unplaced and flagged *lapsed*. **Only a sector policy counts as its successor**: where the national digital strategy follows it, the cell is unplaced, *lapsed* and *under the national strategy*.

**An open policy stops at stage 3**, and its year prints in the short summary (method §3 rule 8).

**The four readings `digitalstrategy` fixed at its D3 carry over**: adoption is the source's own word; a text the government has published, and no source calls a draft, is read as adopted; a published rate of execution of the policy's own actions is `results`; a fact is kept for a named policy whose scope its document does not describe.

## 5. The norm

The frame's anchor (`lookups/maturity-norms.csv`) is the African Union's Digital Transformation Strategy for Africa 2020-2030 with the Smart Africa Manifesto. The first asks states for "national and sectorial digital strategies".

**The norm names the subject and measures nothing**, and it treats a sector policy as subsumed in a digital strategy. The old fifth rung, supersession by a national strategy, becomes the flag.

## 6. What the review reads and the search asks for

- **Subjects and term list**: in `study.json`.
- **The review starts from what is already read.** `digitalstrategy` logged 109 `sector-ict` rows for 37 countries in its `systems.csv`; D2 carries them into this study's `systems.csv` before a drafter runs, and its `instruments.csv` settles `national`.
- **Read by rung** (method §4): dated news and official notices settle standing, text and period. The policy's own text is opened only for a cell at stage 3 with a source naming a report against it.
- **Source types for the briefs**, ranked: dated news and ministry or regulator notices of the policy's adoption, launch, review or replacement; the adopting act in the official gazette or a cabinet communiqué; the ministry's or regulator's report against it; ITU and World Bank sector assessments; the policy's own text.

## 7. Tasks, in order

- [x] **D0. Prepare the criteria** (method step 1): this file and `study.json`, 2026-10-11.
- [ ] **D1. Bill's rulings**, below.
- [ ] **D2. Review all 54 countries**, method §4.
- [ ] **D3. Test and fix the ladder.**
- [ ] **D4. Search and hand over**, method §5.
- [ ] **D5. Re-read and stage**, method §7.
- [ ] **D6. Write, render and lint.** **D7. Report to Bill.**

**The rulings asked at D1**:

1. Only a sector policy is assessed. A country run on its national digital strategy alone is unplaced and flagged *under the national strategy*, not staged a second time.
2. A communications law is noted, not assessed.
3. A sector policy adopted by the responsible minister counts as adopted.
4. An open-ended policy stays at stage 3 however old; past ten years it is flagged *dated*.
5. The ladder above stage 3 is `digitalstrategy`'s: published results against the policy's own targets, capped at 3 without a mandated body and a domestic budget line.
6. Broadband and universal access policies stay out, on their own rows.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
