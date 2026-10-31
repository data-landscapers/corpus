---
type: task
reader: cc
title: maturity-study-digitalskills.md — digital skills taught to the public and measured, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: digitalskills

*(Commissioned by Bill on 2026-10-16 as `capacity.literacy--digital-literacy-general-population`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with civilserviceskills, digitalskills, policyresearch, schoolinternet, stemgraduates and ictjobs: the chapter Capacity.)*

## 1. What is assessed

**Digital skills of the public**: a national programme that teaches digital skills to the public, and a measured share of people who have them. What teaches the public digital skills, or measures how many have them, counts, whatever it is called.

The study redraws `capacity.literacy--digital-literacy-general-population`, which as at 2026-08-31 puts one country at stage 2 and 53 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Digital skills of the public | Digital literacy (general population): digital skills of the public | `capacity.literacy--digital-literacy-general-population` |

Anything else the evidence names is `other`, noted and never staged: a course for civil servants only, computing in the school curriculum, a university degree, a one-off workshop or hackathon, a company's training for its own staff, a device giveaway with no training.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is a national digital-skills programme under way? | A source from the last three years says the government, alone or with partners, has launched, piloted or is preparing a programme to teach digital skills to the public |
| 2 | Is one in service and counted? | A source from the last three years says a government digital-skills programme for the public, alone or with partners, is in service in more than one location and has trained a stated number of people |
| 3 | Is the share of people with digital skills measured? | A source from the last three years gives a measured share of adults or of the population with basic digital skills, from a survey |
| 4 | Is that share half or more? | A source from the last three years gives a measured share of half or more of adults, or of the population, with basic digital skills |

## 3. The ladders

**Digital skills of the public**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the past three years says no programme teaches the public digital skills. |
| 2 Under way | Yes to 1 |
| 3 Programme | Yes to 2 |
| 4 Measured | Yes to 3 |
| 5 Half skilled | Yes to 4 |

**A share of the population counts at question 4** *(Bill, 2026-10-31, messages-for-bill 62, borderline)*: a survey share of individuals, or of everyone above a stated age, of half or more is a yes. BWA, MUS 4→5.

**A programme need not be shown national** *(Bill, 2026-10-31, messages-for-bill 61)*: question 2 is met by a government programme, alone or with partners, with a stated count, shown in more than one location. KEN, SWZ, BDI 2→3; a count from one site (MOZ's Matola pilot) or with no location (BFA) is not enough.

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `training` (`inservice`, `underway`, `none`) for stage 1 and questions 1 and 2, `measured` (`measured`) for 3 and `half` (`half`) for 4.

## 4. The norm

The Digital Transformation Strategy asks for 300 million Africans a year trained in e-skills; Agenda 2063's second ten-year plan asks for 80 per cent of primary completers digitally proficient by 2033. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **327 story readings about the subject**, published since October 2023, in at most 20 stories a country: 268 in the batch's shared calls (49 calls over 243 stories), read once for every study that lists them, and 59 in 46 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the 4,461 documents this study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**20 million** for this study; **70 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: Sonnet drafters, self-contained calls; corrections in `corrections.csv`.
- [x] **D2. Staged** as at 2026-09-30: 5 at 4, 11 at 3, 28 at 2; unplaced 1, no evidence 9. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**; on the soft-launch map. Reported to Bill.
- [x] **D4. Second drafter**, 2026-10-31, after the rebuild (housekeeping 46): 20 of 44 staged cells drawn and restaged blind from `evidence.csv`. 19 of 20 agree; `agreement.csv`. The split is Djibouti, 2 against 3: the second drafter reads DJI-007, 226 people given digital skills under the Digital Foundations Project by August 2024, as a programme in service and counted.

**Decided in the run**: Mauritius's 62.2 per cent is people aged 5 and over able to use a computer, revalued to `measured`; Malawi's 12.5 per cent, a minister's statement with no survey, removed.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
