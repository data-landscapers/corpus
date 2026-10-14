---
type: task
reader: cc
title: maturity-study-offsitebackup.md — the forty-seventh maturity study: off-site backup for government systems, in four questions
last_reviewed: 2026-10-14
status: run 2026-10-14; on the soft-launch map, waits for Bill to accept
---

# Maturity study: offsitebackup

*(Commissioned by Bill on 2026-10-14 as `infra.store--off-site-backup-capacity`, under `maturity/documentation/maturity-study-method.md`.)*

## 1. What is assessed

**A separate site that keeps a public body's systems and data recoverable when its main site fails**, whatever it is called: a backup site, disaster-recovery site, secondary data centre, mirror or alternative site. A public body is a ministry, an agency or the central bank; a state-owned company's own redundancy is not.

**The backup site must be at least 200 km from the main site** *(Bill, 2026-10-14)*, so that one flood, fire or outage cannot take both. A site abroad counts at that distance, which keeps the test open to a country too small to hold two sites 200 km apart. The distance need not be stated: the parent measures it from the two places a source names, and records it in `sites.csv`. A site whose place no held source names, or one nearer than 200 km, is `other`, and the long summary says which.

The study redraws `infra.store--off-site-backup-capacity`, which as at 2026-08-31 puts 9 countries at stage 3, 24 at stage 2 and 1 at stage 1, none at 4 or 5, and 17 without a stage; three countries have no cell. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Off-site backup for government systems | Off-site backup capacity: off-site backup for government systems | `infra.store--off-site-backup-capacity-off-site-backup-for-government-systems` |

Anything else the evidence names is `other`, noted and never staged: backup equipment or a site tendered, financed or under construction; a commercial provider selling backup or disaster recovery, unless a source states it holds government systems; a second network link or satellite route, which is redundancy of connection, not of data; backup power; a backup site nearer than 200 km, or in no named place.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Does a public body have a backup site in service, 200 km or more from its main site? | A source states that a ministry, agency or the central bank keeps its systems or data at a second site, in service, in a named place at least 200 km from its main one |
| 2 | Does one serve the government's shared systems? | A source states that the backup site in service is for the national or government data centre, the government cloud, or systems run for the government as a whole |
| 3 | Is a recovery plan or test on record for it? | A source states that a disaster-recovery or continuity plan covers the government's backup, or that a failover test or recovery exercise was held |
| 4 | Are the main and backup sites both Tier III or above? | Sources state that the government's main data centre and its backup site are each Tier III or IV, by certification, a TIA-942 rating or the operator's own statement |

## 3. The ladders

**Off-site backup for government systems**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the past three years says government systems have no off-site backup or disaster-recovery site |
| 2 Preparing | Yes to 1: one public body's backup site in service, 200 km or more away |
| 3 Establishing | Yes to 2: a backup site for the government's shared systems |
| 4 Operating | Yes to 3: a recovery plan or test on record for it |
| 5 Leading | Yes to 4: main and backup sites both Tier III or above |

- **Questions 1, 2 and 4 have no window.** A site in service stands until a later source says it has closed. **Question 3 has the usual three years**: a plan or a test older than that is not a yes.
- **Stage 2 changes.** The row put procurement, a planned site and one institution's own site at stage 2. Procurement and plans are now `other`; one institution's site in service is stage 2. Most of the row's 24 countries at stage 2 stand on tenders, so many will fall to unplaced unless the reading finds a site in service.
- **Stage 3 changes.** The row let a commercial or satellite provider's redundancy under contract stand at stage 3. A contract counts only where a source says it holds government systems; a satellite link does not.
- **Stage 5 is the row's end state, asked as a fact**: the Blueprint's Tier-classified primary and secondary site. Its continuity standard and published availability are not asked: ISO 22301 certification of a government estate is rare and availability is seldom published, so either would leave stage 5 empty.
- **Every question asks about a site 200 km or more away.** A yes to questions 2 to 4 is a yes for the distant site; a backup in the same city answers none of them. The row set no distance, so countries the frame staged on a backup in the capital will fall.
- **Stage 1 needs a statement of absence**, as in every study.

`study.json` holds this as three aspects: `site` (`shared`, `service`, `none`) for questions 1 and 2, `plan` (`tested`, `plan`) for question 3, and `tier` (`both`) for question 4.

## 4. The norm

The Smart Africa Data Center and Cloud Blueprint asks for 24/7 availability of e-government on a Tier-classified primary and secondary site, with disaster recovery and continuity management. This study asks whether a public body keeps a backup site, whether one serves the government's shared systems, whether its recovery is planned or tested, and whether both sites are built to Tier III; it does not measure capacity, recovery times or how many systems are covered.

## 5. What the run reads

- **Carried first**: the frame's cells for the row, and the datacentres and nationaldatacentres studies' facts, matched to the questions from their own text; 14 of those facts speak of backup or disaster recovery.
- **Read**: **137 news and frame readings**, in 44 countries: 45 the frame's cells cite (29 stories, 16 longer documents), in 25 countries; 34 on the subject that no study has read, in 25; and 58 stories the two data-centre studies read that pass the same test on backup terms, reopened because their carried facts were filed for other questions (`reopen.csv`).
- **Drafters name the town of every main and backup site** in the fact, so the parent can measure the distance.
- **Not read**: other long texts, reports and passing mentions. **No web search and no handover to OSINT.**

## 6. Token ceiling

**30 million**, about two-thirds of the nationaldatacentres study's 40.2 million: 137 readings against its 194. Within the usual share of the week.

## 7. Tasks, in order

- [x] **D0. Prepare**: this file, `study.json`, the reading lists and `reopen.csv`, 2026-10-14.
- [x] **D0a. Distance**: the backup site 200 km or more from the main one, Bill, 2026-10-14.
- [x] **D1. Bill's word**: run on it, 2026-10-14.
- [x] **D2. Read**: 89 drafters over 146 readings (79 planned, 67 reopened); 23 facts in 21 countries. No carry: the two data-centre studies hold no fact on backup in this study's terms.
- [x] **D3. Staged** as at 2026-09-30: 3: 1, 2: 1, 1: 1, 16 unplaced, 35 without evidence; no correction; agreement 3 of 3, the only staged cells.
- [x] **D4. Written, rendered and linted**; on the soft-launch map. **D5. Reported to Bill**, 2026-10-14. Tokens 29.4M of 30M.

**Decided in the run**:

- **Distance is as the crow flies**, in `sites.csv`. Ghana's National Data Centre has its secondary site at KNUST, Kumasi, 194 km from Accra, so it is `near` and Ghana is unplaced; by road it is about 250 km.
- **A backup abroad counts though no country is named**: Sudan's traffic police keep vehicle-register backups outside the country, which sets stage 2.
- **Most backups held name no place**: Mali, Morocco, Mozambique, Mauritius, the Malawi Revenue Authority, Senegal, Eswatini and Tunisia's national backup centre. Each is unplaced, and the summary names the site under *Noted, not assessed*.
- **Angola, Cameroon and Egypt keep their backups within reach of the main site**: Luanda beside Camama, Zamengoe beside Yaoundé, the Sokhna road beside the New Capital.
- **Nigeria's Kano recovery centre was finished but not stated in service**, so its Tier IV fact sets nothing.
- **Ethiopia's statement of absence dates from February 2023**, outside the three years, so it does not set stage 1.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
