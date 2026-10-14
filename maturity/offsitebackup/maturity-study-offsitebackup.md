---
type: task
reader: cc
title: maturity-study-offsitebackup.md — the forty-seventh maturity study: off-site backup for government systems, in four questions
last_reviewed: 2026-10-14
status: prepared 2026-10-14; waits for Bill's word on the questions
---

# Maturity study: offsitebackup

*(Commissioned by Bill on 2026-10-14 as `infra.store--off-site-backup-capacity`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**A separate site that keeps a public body's systems and data recoverable when its main site fails**, whatever it is called: a backup site, disaster-recovery site, secondary data centre, mirror or alternative site. A public body is a ministry, an agency or the central bank; a state-owned company's own redundancy is not.

The study redraws `infra.store--off-site-backup-capacity`, which as at 2026-08-31 puts 9 countries at stage 3, 24 at stage 2 and 1 at stage 1, none at 4 or 5, and 17 without a stage; three countries have no cell. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Off-site backup for government systems | Off-site backup capacity: a separate site that keeps the government's systems and data recoverable | `infra.store--off-site-backup-capacity-off-site-backup-for-government-systems` |

Anything else the evidence names is `other`, noted and never staged: backup equipment or a site tendered, financed or under construction; a commercial provider selling backup or disaster recovery, unless a source states it holds government systems; a second network link or satellite route, which is redundancy of connection, not of data; backup power.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Does a public body have a backup site in service? | A source states that a ministry, agency or the central bank keeps its systems or data at a second site, in service, separate from its main one |
| 2 | Does one serve the government's shared systems? | A source states that the backup site in service is for the national or government data centre, the government cloud, or systems run for the government as a whole |
| 3 | Is a recovery plan or test on record for it? | A source states that a disaster-recovery or continuity plan covers the government's backup, or that a failover test or recovery exercise was held |
| 4 | Are the main and backup sites both Tier III or above? | Sources state that the government's main data centre and its backup site are each Tier III or IV, by certification, a TIA-942 rating or the operator's own statement |

## 3. The ladders

**Off-site backup for government systems**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the past three years says government systems have no off-site backup or disaster-recovery site |
| 2 Preparing | Yes to 1: one public body's backup site in service |
| 3 Establishing | Yes to 2: a backup site for the government's shared systems |
| 4 Operating | Yes to 3: a recovery plan or test on record for it |
| 5 Leading | Yes to 4: main and backup sites both Tier III or above |

- **Questions 1, 2 and 4 have no window.** A site in service stands until a later source says it has closed. **Question 3 has the usual three years**: a plan or a test older than that is not a yes.
- **Stage 2 changes.** The row put procurement, a planned site and one institution's own site at stage 2. Procurement and plans are now `other`; one institution's site in service is stage 2. Most of the row's 24 countries at stage 2 stand on tenders, so many will fall to unplaced unless the reading finds a site in service.
- **Stage 3 changes.** The row let a commercial or satellite provider's redundancy under contract stand at stage 3. A contract counts only where a source says it holds government systems; a satellite link does not.
- **Stage 5 is the row's end state, asked as a fact**: the Blueprint's Tier-classified primary and secondary site. Its continuity standard and published availability are not asked: ISO 22301 certification of a government estate is rare and availability is seldom published, so either would leave stage 5 empty.
- **Stage 1 needs a statement of absence**, as in every study.

`study.json` holds this as three aspects: `site` (`shared`, `service`, `none`) for questions 1 and 2, `plan` (`tested`, `plan`) for question 3, and `tier` (`both`) for question 4.

## 4. The norm

The Smart Africa Data Center and Cloud Blueprint asks for 24/7 availability of e-government on a Tier-classified primary and secondary site, with disaster recovery and continuity management. This study asks whether a public body keeps a backup site, whether one serves the government's shared systems, whether its recovery is planned or tested, and whether both sites are built to Tier III; it does not measure capacity, recovery times or how many systems are covered.

## 5. What the run reads

- **Carried first**: the frame's cells for the row, and the datacentres and nationaldatacentres studies' facts, matched to the questions from their own text; 14 of those facts speak of backup or disaster recovery.
- **Read**: **137 news and frame readings**, in 44 countries: 45 the frame's cells cite (29 stories, 16 longer documents), in 25 countries; 34 on the subject that no study has read, in 25; and 58 stories the two data-centre studies read that pass the same test on backup terms, reopened because their carried facts were filed for other questions (`reopen.csv`).
- **Not read**: other long texts, reports and passing mentions. **No web search and no handover to OSINT.**

## 6. Token ceiling

**30 million**, about two-thirds of the nationaldatacentres study's 40.2 million: 137 readings against its 194. Within the usual share of the week.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file, `study.json`, the reading lists and `reopen.csv`, 2026-10-14.
- [ ] **D1. Bill's word** on the questions.
- [ ] **D2. Carry and read.**
- [ ] **D3. Stage** as at 2026-09-30, the parent's corrections and the agreement draw.
- [ ] **D4. Write, render and lint**; the soft-launch map. **D5. Report to Bill.**

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
