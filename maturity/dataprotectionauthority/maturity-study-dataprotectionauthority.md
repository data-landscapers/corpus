---
type: task
reader: cc
title: maturity-study-dataprotectionauthority.md — the tenth maturity study and the first of a body: the data protection authority
last_reviewed: 2026-10-11
status: CC's proposal; criteria prepared, awaiting Bill's rulings (method step 2)
---

# Maturity study: dataprotectionauthority — the supervisory authority

*(Commissioned by Bill on 2026-10-11, under `maturity/documentation/maturity-study-method.md`.)*

## 1. The question, and the row it redraws

**Does the country have a body that supervises data protection, and does it work?** `gov.protect--data-protection-authority` stages 50 cells as at 2026-08-31: 31 at stage 3, 16 at 2, three at 1, none at 4 or 5, and four unplaced. Three things cause that.

- **A third rung that holds everything**: a commission ten years into publishing sanctions and one sworn in last month.
- **A fourth rung nothing reaches.** It asks for independence by statute, a budget line and enforcement together, and the first is a reading of a text.
- **A fifth rung that is a statement of alignment**, "Malabo Arts 11–12 met", which method §3 rule 5 does not accept.

**This is the first study of a body. Constitution alone places no higher than 3**; above that the test is what the body does.

**One sub-indicator replaces the row**:

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Supervisory authority | Data protection authority: supervisory authority | `gov.protect--data-protection-authority-supervisory-authority` |

**`gov.protect--national-data-protection-readiness` is not touched.** Which indicators the frame holds is Bill's decision alone.

## 2. Typology

| Class | What it is | Treatment |
|---|---|---|
| `authority` | **The body a law or decree charges with supervising data protection across controllers**: a commission or office of its own, an existing regulator or commission designated for it, or a ministry unit so charged | Assessed |
| `informal` | A ministry unit or regulator handling data protection with no law or decree giving it the job | Noted, not assessed; flagged |
| `sectoral` | A regulator supervising personal data in its own sector only: the central bank, the telecommunications or health regulator | Noted, not assessed; flagged |
| `law` | The general data protection law or bill | The law row's; read for aspect 1 |
| `court` | A court applying the law | The law row's; not assessed |
| `network` | Membership of a network of authorities: NADPA-RAPDP, AFAPDP, the Global Privacy Assembly | Noted, not assessed; flagged |
| `adjacent` | A cybersecurity agency, a computer emergency team or an access-to-information commission with no data protection mandate | Out of scope: its own row |
| `regional` | A regional or African Union body | Out of scope |

**The test: is there a body charged with supervising data protection?** Its name, and what else it regulates, do not matter.

## 3. Aspects

| # | Aspect | Role | Values |
|---|---|---|---|
| 1 | Standing | coverage | `constituted`: its head or members are appointed, or an existing body is designated and acting. `lapsed`: constituted before, and a dated source says it now has no head or members, or is suspended or dissolved. `provided`: named in a law that is enacted or in force, and not constituted. `proposed`: named in a bill or an announcement. `none` |
| 2 | Operations | coverage | `reported`: the body publishes a count of its decisions, sanctions or complaints settled, for a stated period of a quarter or more. `enforcing`: a named and dated decision of the body on one controller's conduct. `active`: registrations, authorisations, guidance, opinions, training, warnings, or an investigation opened. `none` |
| 3 | Resources | coverage | `published`: a budget allocation, spending or staff figure for the body, for a stated year. `none`: a source says it has no budget or no staff |
| 4 | Seat | qualifier | `own`: a body of its own. `hosted`: an existing regulator or commission designated. `ministry`: a unit of a ministry |
| 5 | Last twelve months | qualifier | Advancing, no change on record, or regressing, with the dated event |

**Aspects 1 to 3 set the stage; 4 and 5 cap or flag it and never raise it.**

**The cap rule.** A body seated in a ministry, or whose seat no source states, does not reach stage 5: it is capped at 4 and flagged *ministry unit*.

**Flags that never change the stage.** *Hosted*; *no statutory authority*, for the `informal` class held instead; *sectoral only*; *network member*; *vacant*, where the head's term has ended and a deputy or acting head runs the body.

**Operations are the body's own acts**; a court's judgment is the law row's.

**Independence is not staged**: it is a reading of a statute. The seat is the dated fact nearest to it, and it sets the cap.

## 4. The ladders

**Supervisory authority**

| Stage | Standing | Operations | Resources |
|---|---|---|---|
| 1 Absent | A dated statement that the country has no data protection authority, with none on record as provided for or proposed | | |
| 2 Preparing | `proposed`, `provided` or `lapsed` | Any | Any |
| 3 Establishing | `constituted` | Any | Any |
| 4 Operating | `constituted` | `enforcing` or `reported`, dated within three years | Any |
| 5 Leading | `constituted` | `reported`, for a period ending within two years | `published`, for a year ending within two years |

**The newest of `constituted` and `lapsed` is the standing.** A body with an acting head is `constituted` and flagged *vacant*.

**A noted class never places a country.** A country holding an `informal` or `sectoral` body and no authority provided for or proposed is unplaced and flagged, unless a dated source states the absence.

**The law study's fixes of D3 stand here**: `enforcing` is an identified decision on one controller, never a general deliberation, opinion, authorisation or referral; complaints or breaches received are `active`.

## 5. The norm

The frame's anchor (`lookups/maturity-norms.csv`) is the Malabo Convention, Articles 11 and 12, read with the African Union Data Policy Framework's call for authorities that are "independent, funded, and effective". **It supplies the checklist and no test.** The study takes *funded* as a published figure, *effective* as decisions on record and then a published count, and independence as the seat. Network membership is the flag.

## 6. What the review reads and the search asks for

- **Subjects and term list**: in `study.json`. A dry pass lists 1,959 documents and 2.6 million words, 514 and 282,000 in the first pass. The law study's terms listed 5,831.
- **The review starts from the law study's evidence**: its 264 authority facts, 176 application facts and 89 last-twelve-months facts are carried into `evidence.csv` and revalued to this study's aspects from the fact's own text, with no document opened.
- **A drafter reads only for a cell the carried facts leave short of a rung test**: standing where the law study holds `provided` or nothing, and the seat where no fact states it.
- **Resources are read and searched at the fifth rung only**: for a cell that has reached stage 4 on `reported`. Corpus's own budget extract (`budgets/`) is read first.
- **Source types for the briefs**: news and official notices first, then the authority's annual report.

## 7. Tasks, in order

- [x] **D0. Prepare the criteria** (method step 1): this file and `study.json`, 2026-10-11.
- [ ] **D1. Bill's rulings**, below.
- [ ] **D2. Carry and review all 54 countries**, method §4.
- [ ] **D3. Test and fix the ladder.**
- [ ] **D4. Search and hand over**, method §5.
- [ ] **D5. Re-read and stage**, method §7.
- [ ] **D6. Write, render and lint.** **D7. Report to Bill.**

**The proposals for D1**, each a yes or no:

1. Any body the law gives the job counts as the authority, including a telecoms regulator or an information commission given it as a second job.
2. Having an authority appointed is stage 3. Stage 4 needs a ruling against a named organisation in the last three years. Stage 5 needs published yearly figures for its rulings, and a published budget or staff number.
3. An authority whose members have all left and not been replaced drops to stage 2. One with an acting head keeps its stage.
4. We do not judge whether an authority is independent, because that means interpreting the law's text. We record where it sits instead. An authority that is a department of a ministry cannot reach stage 5.
5. We look for a budget or staff number only for authorities already at stage 4.
6. We start from the facts the law study collected and read new documents only where those leave a country's stage undecided.
7. Belonging to the African network of authorities is noted and does not change the stage.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
