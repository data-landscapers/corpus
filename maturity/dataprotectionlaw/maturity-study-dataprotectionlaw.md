---
type: task
reader: cc
title: maturity-study-dataprotectionlaw.md — the ninth maturity study and the first of a law: the general data protection law
last_reviewed: 2026-10-11
status: CC's proposal, run on Bill's word of 2026-10-11; staged, written and on the soft-launch map as at 2026-09-30; awaiting Bill's acceptance
---

# Maturity study: dataprotectionlaw — the general law

*(Commissioned by Bill on 2026-10-11, under `maturity/documentation/maturity-study-method.md`.)*

## 1. The question, and the row it redraws

**Does the country have a general data protection law in force, and is it applied?** `gov.legislate--data-protection-legislation` stages 52 cells as at 2026-08-31: 42 at stage 3, five at 2, three at 4, two at 1, none at 5, and two unplaced. Three things cause that.

- **A third rung that holds everything.** A law of 2001 with an authority fining controllers and a law of 2026 with nothing under it are both stage 3.
- **A fourth rung set by which row a fact was filed on.** It asks for regulations, a constituted authority and an enforcement act together.
- **A fifth rung that is a statement of alignment.** It asks for a law "aligned with Malabo's principles", which method §3 rule 5 does not accept as a test.

**This is the first study of a law.** The instrument studies' rule carries over: **enactment alone places no higher than 3**; above that the test is that the law is applied.

**One sub-indicator replaces the row**:

| Sub-indicator | Indicator text | Id |
|---|---|---|
| General law | Data protection legislation: general law | `gov.legislate--data-protection-legislation` |

**`gov.protect--data-protection-authority` is not redrawn**: its own study. **`gov.protect--national-data-protection-readiness` is not touched**: a composite of this row, the authority row and ratification, proposed for retirement with the authority study.

## 2. Typology

| Class | What it is | Treatment |
|---|---|---|
| `general` | **A law that sets the country's rules for protecting personal data, standalone or part of a larger law**, or a bill for one | Assessed |
| `sectoral` | Data protection provisions inside a law on another subject: telecommunications, banking, health, identity, electronic transactions, cybercrime, consumer protection | Noted, not assessed; flagged |
| `constitutional` | A constitutional right to privacy or habeas data | Noted, not assessed |
| `regulation` | A regulation, decree, order or guideline | Under a general law, that law's aspect 3; otherwise noted |
| `authority` | The supervisory authority, commission, office or regulator | Logged for `gov.protect--data-protection-authority`; shows the law's aspects 1 and 4 |
| `treaty` | Ratification of the Malabo Convention, Convention 108+ or a regional community's act | Noted, not assessed; flagged |
| `policy` | A data protection or data governance policy or strategy | Noted, not assessed |
| `adjacent` | A law on cybercrime, access to information, electronic transactions or artificial intelligence, with no general data protection regime in it | Out of scope: its own row |
| `regional` | A regional or African Union model law or act | Out of scope |

**The test: does the country have a law setting data protection rules?** Its title, and what else the law covers, do not matter.

**Every fact is classed `general`**, whichever body or instrument it names: the other classes are for `systems` rows.

**A cell is staged on the law in force; a bill to replace it is the flag *under revision*.**

## 3. Aspects

| # | Aspect | Role | Values |
|---|---|---|---|
| 1 | Authority | qualifier | `constituted`: its head or members are appointed, or an existing body is designated and acting. `provided`: named in the law and not constituted. `none` |
| 2 | Standing | coverage | `in-force`. `transition`: in force with a compliance period running or parts not commenced. `enacted`: promulgated or assented and not commenced. `passed`: voted and not promulgated. `tabled`: before parliament. `drafting`: a draft, a consultation or a bill the cabinet has approved. `announced`. `none` |
| 3 | Regulations | coverage | `issued`: at least one regulation, decree or order made under the law is in force. `none`: a source says none is |
| 4 | Application | coverage | `reported`: a published count of decisions, sanctions or complaints settled under the law, for a stated year. `applied`: a named and dated sanction, order, decision or judgment under the law. `activity`: registrations, guidance, training or warnings, with no decision. `none` |
| 5 | Last twelve months | qualifier | Advancing, no change on record, or regressing, with the dated event |

**Aspects 2 to 4 set the stage; 1 and 5 cap or flag it and never raise it.**

**The cap rule.** Without a constituted authority, stage 4 or 5 is capped at 3 and flagged *no authority*.

**Flags that never change the stage.** *Sectoral only*, for the noted class held instead; *Malabo ratified*; *under revision*; *regulations pending*, where a source says the law's regulations are not issued.

**Application is the law's, whoever applies it**; the authority row keeps the body.

## 4. The ladders

**General law**

| Stage | Standing | Regulations | Application |
|---|---|---|---|
| 1 Absent | A dated statement that the country has no general data protection law, with none on record as enacted or in preparation | | |
| 2 Preparing | `announced`, `drafting`, `tabled` or `passed` | Any | Any |
| 3 Establishing | `enacted`, `transition` or `in-force` | Any | Any |
| 4 Operating | `in-force` | Any | `applied` or `reported`, dated within three years |
| 5 Leading | `in-force` | Any | `reported`, for a year ending within two years |

**A noted class never places a country.** A country holding sectoral or constitutional provisions and no general law or bill is unplaced and flagged *sectoral only*, unless a dated source states the absence.

**A dated decision under a law is evidence that the law is in force.**

**Stage 5 has no alignment test**, and a count without the year it covers is `applied`.

**Fixed at D3** (`corrections.csv`, `scripts/study-ladder-dataprotectionlaw.py`):

- **The country is placed, not the instrument**: the strongest standing stated is the country's, and authority, regulations and application are the law's, whatever body the source names.
- **`applied` is an identified decision on one controller's conduct**, named or not. A general deliberation, rule, opinion or authorisation, an investigation opened or a referral is `activity`.
- **`reported` counts decisions, sanctions or complaints settled**, for a stated period of a quarter or more. Complaints or breaches received are `activity`.
- **Stage 5 needs no regulation** *(Bill, 2026-10-31, messages-for-bill 55)*: a law that allows enough action without regulations is rewarded. Benin's count of complaints treated is enough for 5, and so are authorisation decisions. GAB, MAR and SEN 4→5.

## 5. The norm

The norm is the African Union's Malabo Convention: Article 8(1) commits each party to a legal framework for personal data, Article 13 sets the principles and Articles 16 to 19 the rights. **It names the subject and measures nothing**: it sets no test of whether a law is applied, and matching its principles is a reading of two texts, not a dated fact. Ratification is the flag.

## 6. What the review reads and the search asks for

- **Subjects and term list**: in `study.json`.
- **The review starts from the August assessment** *(Bill, 2026-10-11)*: this row's and the authority row's cells, with the sources they cite, are carried into `evidence.csv` before a drafter runs. **A drafter reads only for a cell the carried facts leave short of a rung test**, and a search is briefed only for those cells.
- **Source types for the briefs**, ranked: dated news and the authority's own notices of a sanction, order or decision; the authority's annual report; the gazette notice of promulgation, commencement or a regulation; a court judgment under the law; the trackers (Data Protection Africa, UNCTAD, Law Lab Africa) for standing and a dated absence; the law's text.

## 7. Tasks, in order

- [x] **D0. Prepare the criteria**: this file and `study.json`, 2026-10-11.
- [x] **D1. Bill's rulings**: ruling 1 amended, the rest stand, 2026-10-11.
- [x] **D2. Review all 54 countries**, method §4: the 369 documents the frame's cells cite, and eight more, in 116 calls; 769 facts.
- [x] **D3. Test and fix the ladder**: 13 corrections.
- [x] **D4. Search and hand over**: 47 searches, 47 documents for 28 countries, note 228.
- [x] **D5. Re-read and stage**, method §7: 26 of 47 admitted and read; 4 at stage 5, 10 at 4, 31 at 3, 7 at 2, 1 at 1, one with no evidence; agreement 20 of 20.
- [x] **D6. Write, render and lint.** **D7. Report to Bill.**

**The rulings of D1**:

1. The subject is the law that sets data protection rules, standalone or part of a larger law.
2. Enactment is stage 3 and no higher; stage 4 is a dated decision under the law, stage 5 a published year's figures.
3. Application is staged on this row, whoever applies it; the authority row is not redrawn and waits for its own study.
4. Without a constituted authority, stage 4 or 5 is capped at 3.
5. Regulations are required at stage 5 only.
6. Malabo ratification is a flag; alignment with the Convention is not a test at any stage.
7. The readiness row is left alone and proposed for retirement with the authority study.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
