---
type: task
reader: cc
title: maturity-study-cybersecurity.md — the fifty-third maturity study: whether a country has a working national cyber response, in four questions
last_reviewed: 2026-10-14
status: run 2026-10-14; on the soft-launch map; waits for Bill to accept
---

# Maturity study: cybersecurity

*(Commissioned by Bill on 2026-10-14 as `infra.cybersec--national-cybersecurity-readiness`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**The national body that watches for cyber attacks on the country's systems, warns of them and helps respond, and the strategy that sets it up.**

Who counts is whoever does the job for the country as a whole, whatever it is called and wherever it sits: a national CERT, CSIRT or CIRT, a cybersecurity agency or authority, or a response team inside the telecom regulator or the ICT agency.

The study redraws `infra.cybersec--national-cybersecurity-readiness`, which as at 2026-08-31 puts one country at stage 4, 7 at stage 3, 42 at stage 2 and one at stage 1, and leaves three unplaced. It touches no other row: the cybercrime and cybersecurity law, and prosecutions under it, stay with `gov.legislate--cybersecurity-legislation` and its study.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| National cyber response | National cybersecurity readiness: national cyber response | `infra.cybersec--national-cybersecurity-readiness` |

Anything else the evidence names is `other`, noted and never staged: a cybercrime law, an arrest or a prosecution; a police cybercrime unit; a team serving one sector only, such as banks; a company's security centre; training, awareness campaigns, conferences and drills; an attack on its own; a cooperation memorandum; ratifying the Malabo or Budapest Convention; a rank in an index.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Does the country have a national cybersecurity strategy or a national cyber body? | A source states a strategy was adopted, or a national agency or response team was created by law, decree or order |
| 2 | Has the national body responded to an incident in the last three years? | A source from October 2023 or later states it handled an incident or issued a public alert |
| 3 | Has the country named its critical information infrastructure? | A source states the systems that count as critical were designated, or their operators required to report incidents to the national body |
| 4 | Does the national body publish evidence of dealing with incidents? | The body's own account of incidents it acted on (responded to, contained, neutralised, investigated or notified to those hit), for a period of a quarter or more ending within the last year. A count of complaints, cases recorded or threats detected is not a yes: recording a case is not acting on it |

## 3. The ladders

**National cyber response**

| Stage | Answers |
|---|---|
| 1 Absent | A source from 2023 or later says the country has no cybersecurity strategy and no national body or response team |
| 2 Nascent | Yes to 1: a strategy adopted or a body created |
| 3 Established | Yes to 2: the body has responded to an incident |
| 4 Operating | Yes to 3: critical information infrastructure designated |
| 5 Leading | Yes to 4: the body publishes evidence of dealing with incidents in the last year |

- **Stage 2 changes.** The row put an announced or drafted strategy at stage 2. Only an adopted strategy or a created body is a yes now; a draft is noted and the cell stays where the rest of its evidence puts it.
- **Stage 3 changes.** The row asked for a strategy and a law and a constituted body, and no record. A body that has handled an incident or issued an alert is the first fact that shows it works, so that is stage 3. The law moves out: it is its own row.
- **Stage 4 keeps the row's critical-infrastructure regime** as one fact a notice states. Its enforcement and prosecutions go to the law's row.
- **Stage 5 keeps the row's "reporting published"** as an account of incidents dealt with *(Bill, 2026-10-30: a count of complaints or detections shows recording, not action)*. Malabo ratification, regional cooperation and a recognised assessment go: the first is noted as on the law's row, and the other two are not a fact a story states.
- **Windows**: a strategy counts while its period runs, and a body until a source says it was dissolved; question 2 is three years; question 3 has none; question 4 is one year. A statement that there is nothing counts for three years.
- **A later yes answers the earlier ones**: published figures show a body that responds, and a designation names the body operators report to.

`study.json` holds this as four aspects, which head the long summary's paragraphs: `foundation` (`body`, `strategy`, `none`) for question 1, `response` (`responded`) for question 2, `cii` (`designated`) for question 3 and `figures` (`published`, or `recorded` for a count that shows no action, which never stages) for question 4. **For the drafter**: a body's name goes in `country_label`; an alert counts only when the national body issued it, not a bank or a ministry.

## 4. The norm

The Malabo Convention, chapter III, asks each party for a national cybersecurity policy and strategy (Art. 24) and a body that governs cybersecurity (Art. 27). It sets no test of whether the body works. The ITU Global Cybersecurity Index and the Oxford capacity model are not read.

## 5. What the run reads

- **Read**: **587 stories** in all 54 countries: 341 about a national cyber strategy, body or response team that no study has read, in 53 countries, and 246 more that the frame's cells for the row cite, in 53. Eight of the 322 stories are regional, read once each.
- **No earlier study is carried**: the cybersecurity law study holds the law, which this study does not stage.
- **Not read**: the long texts, reports and passing mentions the listing also holds.

## 6. Token ceiling

**55 million**: itcapacity read 544 stories in 150 drafters and 51.2 million; this plans 167.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file, `study.json` and the reading lists, 2026-10-14.
- [x] **D1. Bill's word**, 2026-10-14, the questions as prepared.
- [x] **D2. Read**: 167 drafters over 587 readings, nine regional stories read once; 398 facts after 14 rows removed by the parent (`corrections.csv`). Gabon's count covers two months and its sector mapping designates nothing; Senegal's authority law is passed but not promulgated; South Sudan's and Zambia's acts bind only systems not yet designated; Zambia's and Guinea's alerts are on disinformation, not an attack.
- [x] **D3. Staged** as at 2026-09-30: stage 5 seven, 4 six, 3 four, 2 thirty-one, unplaced two, no evidence four; none at 1, the two statements of absence held (Eritrea 2015, Lesotho March 2023) being older than three years. The second drafter agreed on 18 of 20; its two readings (Guinea, Sao Tome) were right and are corrected, so 20 of 20.
- [x] **D4. Written, rendered and linted**, by `study-cybersecurity-write.py`; on the soft-launch map. **D5. Reported to Bill.** Tokens 57.3M of 55M, step 1's thread counted.

**Decided in the run**: a duty to report that binds only systems a minister or agency has yet to designate is not a yes to question 3; a duty laid directly on named categories or on public bodies is. A strategy whose stated period has ended counts no longer, which leaves Mauritania (2022-2025) unplaced.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
