---
type: task
reader: cc
title: maturity-study-cybersecuritylaw.md — the twelfth maturity study: the cybercrime and cybersecurity law, in four questions
last_reviewed: 2026-10-11
status: run on Bill's word of 2026-10-11; staged, written and on the soft-launch map as at 2026-09-30; awaiting Bill's acceptance
---

# Maturity study: cybersecuritylaw

*(Commissioned by Bill on 2026-10-11 as `gov.legislate--cybercrime-legislation`, under `maturity/documentation/maturity-study-method.md`. The frame holds no row of that name: its row is `gov.legislate--cybersecurity-legislation`, whose ladder reads "cybercrime or cybersecurity law" at every stage, and this study is of that row.)*

## 1. What is assessed

**The law that makes attacks on computers and data a crime, or that sets duties and a body to protect systems**, whatever it is called: an act of its own, or a chapter of a penal code or a digital code.

The study redraws `gov.legislate--cybersecurity-legislation`, which as at 2026-08-31 puts 42 countries at stage 3 and 10 at stage 2, none above 3, and leaves two unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Cybercrime and cybersecurity law | Cybersecurity legislation: cybercrime and cybersecurity law | `gov.legislate--cybersecurity-legislation` |

Anything else the evidence names is `other`, noted and never staged: a cybersecurity strategy or policy, an agency or response team, a treaty.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is there a cybercrime or cybersecurity bill or law? | A bill drafted, before parliament or passed, or a law |
| 2 | Is the law in force? | A law promulgated and in force, standing alone or as part of a larger code. A bill is not a yes |
| 3 | Has the law been used in the last three years? | A dated arrest, charge, prosecution or conviction under it, or a penalty or order imposed under it by the body it sets up. The source must name the law or an offence only it creates |
| 4 | Is the law in regular use? | Sources from the last two years showing it used again and again: a count of cases under it, a run of cases, or a source stating repeated use. Judged case by case; two or three cases are not regular use |

**A private criminal complaint is not use of the law** *(Bill, 2026-10-27)*: question 3 needs the state to act, by arrest, charge, prosecution, conviction or penalty. Equatorial Guinea's complaint leaves it at 3.

**A count that does not name the law is not use of it** *(Bill, 2026-10-30)*: a police or cybercrime-unit tally of complaints, cases or arrests is valued `unnamed` and stages nothing. **Stage 5 is regular use, not published figures** *(Bill, 2026-10-30)*: no number of cases is set, and the stager judges each country from all its rows.

## 3. The ladders

**Cybercrime and cybersecurity law**

| Stage | Answers |
|---|---|
| 1 Absent | A dated source says the country has no cybercrime or cybersecurity law and no bill for one |
| 2 Preparing | Yes to 1: a bill, and no law in force |
| 3 Establishing | Yes to 1 and 2: a law in force |
| 4 Operating | Yes to 1, 2 and 3: the law has been used |
| 5 Leading | Yes to all four: the law is in regular use |

- **A yes to a later question answers the earlier ones**: a conviction under the law shows it is in force.
- **Questions 1 and 2 have no time limit**; a law stands, with its year, until a dated source says it is repealed or struck down.
- **A statement that there is no law counts for three years.**
- **Who the law is used against is not judged.** A prosecution of a journalist or a critic under it is a use of the law, and the summary says who was prosecuted.
- **Ratifying the Budapest or the Malabo Convention is noted and does not change the stage**, as on the data protection law row.
- **Incidents handled by a response team are not a use of the law**: they belong to the cybersecurity readiness row.

`study.json` holds this as two aspects: `standing` (`in-force`, `bill`, `none`) for questions 1 and 2, and `use` (`regular`, `used`, `unnamed`, `none`) for 3 and 4.

## 4. The norm

The Malabo Convention's third chapter commits each party to legal measures against cybercrime: Article 25 on legislation and Articles 29 to 31 on the offences. It names what a law should cover and sets no test of whether one is used. This study asks whether the law exists, is in force and is used.

## 5. What the run reads

- **Read first**: **128 news stories about a cybercrime or cybersecurity law**, across 35 countries, 119 of them from the last three years. No study has read them.
- **Then, only for a country those leave short of an answer to question 1 or 2**: the news stories its current cell cites, at most 138 across all countries.
- **Not read**: the texts of the laws, 53 of them, and stories that mention a law in passing. A law's text is opened only for a country with nothing else.
- A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**40 million.** The run stops and reports if it reaches it. This study has no earlier study's facts to start from, so it reads more than the last two.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file and `study.json`, 2026-10-11.
- [x] **D1. Bill's word**: run on it, 2026-10-11.
- [x] **D2. Read**: the 128 `about` stories; then the cited news for the 24 countries those left short; then what was held for six still short; then the cited documents of six countries that had come out below the frame's stage. 200 facts.
- [x] **D3. Staged**: 10 at stage 4, 36 at 3, 6 at 2, one unplaced, one with no evidence, none at 1 or 5, as at 2026-09-30; three corrections and one fact added by the parent; agreement 20 of 20.
- [x] **D4. Written, rendered and linted**; on the soft-launch map. **D5. Reported to Bill**, 2026-10-11.

**Decided in the run**: arrests or files handled by a cybercrime unit count as use of the law where the source does not name the law (Benin, Cote d'Ivoire), and do not count as published figures.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
