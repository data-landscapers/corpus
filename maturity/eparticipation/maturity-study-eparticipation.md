---
type: task
reader: cc
title: maturity-study-eparticipation.md — the public's part in making policy and law online, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: eparticipation

*(Commissioned by Bill on 2026-10-16 as `include.access--citizen-participation-in-policy`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with feedbackportals, eparticipation, gendergap, disabilityaccess, refugees and digitaldivides: the chapter Inclusion.)*

## 1. What is assessed

**Online participation in making policy and law**: a government channel through which the public takes part in policy or law-making over the internet: a draft posted online for public comment, an online consultation or survey on a named policy, a consultation portal or an e-petition system. What lets the public take part in making policy online counts, whatever it is called.

The study redraws `include.access--citizen-participation-in-policy`, which as at 2026-08-31 puts two countries at stage 3, 19 at 2, one at 1 and 30 unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Online participation in policy | Citizen participation in policy: online participation in policy | `include.access--citizen-participation-in-policy` |

Anything else the evidence names is `other`, noted and never staged: a consultation held only in person, a channel for complaints about a service, a workshop of officials and donors, a social-media post announcing a policy with no call for views, an internet governance forum, an election or referendum.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Has the government asked the public for views online? | A source from the last three years says a ministry, parliament or regulator posted a named draft law, policy or regulation online for public comment, or ran an online consultation or survey on one |
| 2 | Is a standing online channel in service? | A source from the last three years says a government consultation portal, e-petition system or online platform for comments on drafts is in service and open to the public for more than one draft |
| 3 | Is what the public said published? | A source from the last three years says the government published the comments it received in an online consultation, a report of one, or its answer to them |
| 4 | Is online consultation required? | A source from the last three years says a consultation was held online because a law, decree or published procedure requires drafts to be put online for public comment |

## 3. The ladders

**Online participation in policy**

| Stage | Answers |
|---|---|
| 1 Absent | A source from the past three years says laws and policies are adopted with no public consultation and no way for citizens to take part. |
| 2 Asked online | Yes to 1 |
| 3 Standing channel | Yes to 2 |
| 4 Answers published | Yes to 3 |
| 5 Required | Yes to 4 |

A later yes answers the earlier ones (method §3.3). `study.json` holds this as three aspects: `online` (`standing`, `asked`, `none`) for stage 1 and questions 1 and 2, `published` (`published`) for 3 and `required` (`required`) for 4.

**A site posting drafts with comments by email is not an online platform for comments** *(Bill, 2026-10-26)*: question 2 needs a portal taking comments online, so Mozambique stays at 2.

## 4. The norm

The African Charter on Democracy, Elections and Governance asks for citizen participation in the development process; the UN E-Participation Index measures it online. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing. The publicconsultation study holds consultation on digital policy by any channel; its facts do not say whether the public took part online, so none answers these questions.
- **Read**: **57 story readings about the subject**, published since October 2023, in at most 20 stories a country: 3 in the batch's shared calls (4 calls over 17 stories), read once for every study that lists them, and 54 in 31 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the 1,184 documents this study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**15 million** for this study; **90 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: Sonnet drafters, self-contained calls; corrections in `corrections.csv`.
- [x] **D2. Staged** as at 2026-09-30: 1 at 4, 2 at 3, 11 at 2; unplaced 0, no evidence 40. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**; on the soft-launch map. Reported to Bill.

**Decided in the run**: Nothing removed.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
