---
type: task
reader: cc
title: maturity-study-dataprotectionauthority.md — the tenth maturity study: the data protection authority, in four questions
last_reviewed: 2026-10-11
status: run on Bill's word of 2026-10-11; staged, written and on the soft-launch map as at 2026-09-30; awaiting Bill's acceptance
---

# Maturity study: dataprotectionauthority

*(Commissioned by Bill on 2026-10-11, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**The body the law gives the job of supervising data protection**, whatever it is called and wherever it sits: a commission of its own, or a regulator or information commission given the job as well as its own.

The study redraws `gov.protect--data-protection-authority`, which as at 2026-08-31 puts 31 countries at stage 3, 16 at 2, three at 1, none above 3, and leaves four unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Supervisory authority | Data protection authority: supervisory authority | `gov.protect--data-protection-authority` |

Anything else the evidence names is `other`, noted and never staged: a regulator that watches personal data in its own sector only, a ministry unit with no law behind it, a court, a cybersecurity agency.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is an authority named in law? | A law, enacted or in force, that names the body. A bill is not a yes |
| 2 | Has it been appointed? | Its head or members are appointed, or an existing body given the job is doing it. An acting head counts |
| 3 | Has it ruled against a named organisation in the last three years? | A dated decision, fine or order of the authority on one organisation's conduct. General guidance, an opinion, a registration or an investigation opened is not a yes |
| 4 | Does it publish yearly figures for its rulings? | A published count of its decisions, fines or complaints settled, for a period of a quarter or more ending within the last two years. Complaints received are not a yes |

## 3. The ladders

**Supervisory authority**

| Stage | Answers |
|---|---|
| 1 Absent | A dated source says the country has no data protection authority and none named in law |
| 2 Preparing | Yes to 1 |
| 3 Establishing | Yes to 1 and 2 |
| 4 Operating | Yes to 1, 2 and 3 |
| 5 Leading | Yes to all four |

- **A yes to a later question answers the earlier ones**: a ruling shows the authority is appointed.
- **An authority whose members have all left and not been replaced is a no to question 2**, from the date a source says so.
- **A country with a bill and no law is stage 1 only if a source states the absence**; otherwise it has no evidence, and the long summary notes the bill.
- **Only the authority's own rulings count.** A court's judgment belongs to the law row.
- **Question 4 is a regular publication of the authority's decisions** *(Bill, 2026-10-31, messages-for-bill 54)*: a numbered bulletin counts even where its figures are running totals, and the cell returns to 4 if no later edition is found. A register listing decisions one by one is not a count; Angola stays at 4.
- **Questions 1 and 2 have no time limit**: an appointment stands, with its year, until a dated source says the authority has gone. A later source that only describes the law does not undo it.
- **A statement that there is no authority counts for three years.**
- **The stage is counted by `scripts/study-ladder-dataprotectionauthority.py`**; what the parent's reading of the ruling facts changed is in `corrections.csv`.

`study.json` holds this as two aspects: `standing` (`constituted`, `provided`, `none`) for questions 1 and 2, and `rulings` (`reported`, `ruled`, `none`) for 3 and 4.

## 4. The norm

The African Union's Malabo Convention, Articles 11 and 12, commits each party to an independent authority with stated duties and powers, and the Union's Data Policy Framework asks for authorities that are "independent, funded, and effective". Neither sets a test of whether an authority works. This study asks whether it exists, whether it rules and whether it publishes what it has done; it does not judge independence.

## 5. What the run reads

- **Carried, no document opened**: the law study's facts on the authority (264) and on application (176), and the frame's cells for this row, matched to the four questions from their own text.
- **Read**: **128 news stories about an authority that no study has read**, across 41 countries, 116 of them from the last three years.
- **Not read**: laws, reports and stories that mention an authority in passing.
- A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**40 million.** The run stops and reports if it reaches it. The figure is an estimate from the law study's cost per call, which took 133 million in all.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file and `study.json`, 2026-10-11. **The four questions agreed by Bill, 2026-10-11.**
- [x] **D1. Built**: `study-select.py`'s passes `about` and `carried`, and `study-carry.py`.
- [x] **D2. Carried and read**: 326 facts carried from the law study, 112 from the 128 stories, in 47 calls.
- [x] **D3. Staged**: 5 at stage 5, 8 at 4, 21 at 3, 11 at 2, 4 at 1, three unplaced, two with no evidence, as at 2026-09-30; 13 corrections; agreement 20 of 20.
- [x] **D4. Written, rendered and linted**; on the soft-launch map. **D5. Reported to Bill**, 2026-10-11.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
