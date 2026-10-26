---
type: task
reader: cc
title: maturity-study-customs.md — customs declarations processed electronically, in four questions
last_reviewed: 2026-10-16
status: first pass run 2026-10-16; staged, written and on the soft-launch map; waits for Bill's acceptance
---

# Maturity study: customs

*(Commissioned by Bill on 2026-10-16 as `dpi.mis--customs`, a first pass under `maturity/documentation/first-pass-batch.md`, in one batch with socialprotection, justice, taxadmin, customs and landadmin: the topic Sectoral management information systems.)*

## 1. What is assessed

**The system customs processes declarations on**: lodging, assessing and clearing goods electronically, and the single window that joins the other border agencies to it. What clears goods electronically counts, whatever it is called.

The study redraws `dpi.mis--customs`, which as at 2026-08-31 puts 34 countries at stage 3, 11 at 2 and nine unplaced. It touches no other row.

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Customs | Customs: customs | `dpi.mis--customs` |

Anything else the evidence names is `other`, noted and never staged: a port's own terminal system, a cargo tracking seal with no clearance, a tariff or trade agreement, a business one-stop shop.

## 2. The questions

Asked in order. Each is answered with a date and a link.

| # | Question | A yes is |
|---|---|---|
| 1 | Is an automated customs system under way? | A source from the last three years says a customs management system is procured, being installed, piloted at some posts or upgraded |
| 2 | Are declarations processed electronically? | A source from the last three years says customs declarations are lodged and processed in an automated system at the main port, airport or border posts |
| 3 | Is there a single window for other agencies? | A source from the last three years says a trade single window is in service, joining customs and other border agencies |
| 4 | Does it exchange data across its regional community? | A source from the last three years says the customs system exchanges declaration or transit data through a system open to every country of its regional economic community, such as ECOWAS's SIGMAT or the EAC single customs territory, even where not every member yet reciprocates |

## 3. The ladders

**Customs**

| Stage | Answers |
|---|---|
| 1 Paper | A source from the past three years says customs declarations are processed on paper. |
| 2 Under way | Yes to 1 |
| 3 Automated | Yes to 2 |
| 4 Single window | Yes to 3 |
| 5 Regional exchange | Yes to 4 |

A later yes answers the earlier ones (method §3.3). **Rung 5 rewritten** *(Bill, 2026-10-26, message 39)*: a link with one or a few neighbours is no longer a yes; eight such facts were removed (`corrections.csv`), and Cameroon falls to 4, Chad and the Central African Republic to 3. **Dated by the source**: a standing state answers when a source from the last three years states it (`source_dated`), and a year-only fact of the as-at's year counts from its source's date. **A government statement is a fact** (Somalia to 3); **a guide is preparation, not implementation** (Mauritania to 2). `study.json` holds this as three aspects: `system` (`inservice`, `underway`, `none`) for stage 1 and questions 1 and 2, `window` (`window`) for 3 and `exchange` (`exchange`) for 4.

## 4. The norm

The AfCFTA Protocol on Trade in Goods asks for customs automation, a single window connecting border agencies and electronic exchange with trading partners. This study asks the four questions above; it does not measure a country against the norm.

## 5. What the run reads

- **Carried**: nothing; no earlier study holds facts on these questions.
- **Read**: **104 story readings about the subject**, published since October 2023, in at most 20 stories a country: 12 in the batch's three shared calls (13 stories), read once for every study that lists them, and 92 in 38 calls of its own. A story published before the three-year window can set no stage, and the twenty are each country's best ranked across the batch (`study-calls.py --batch … --cap 20`).
- **Not read**: the rest of the 852 documents this study lists, instruments, long reports, passing mentions and the documents the row's current cells cite. A question nothing answers is printed as *Not held*.

## 6. Token ceiling

**8 million** for this study; **40 million** for the batch, checked with `study-tokens.py` after every fan-out.

## 7. Tasks, in order

- [x] **D0. Prepared**: this file, `study.json` and the reading lists, 2026-10-16.
- [x] **D1. Read**, 2026-10-16: the batch's shared calls and this study's own, Sonnet drafters; 84 facts after the parent's corrections (`corrections.csv`).
- [x] **D2. Staged** as at 2026-09-30: 4 at 5, 9 at 4, 13 at 3, 5 at 2; unplaced 1, no evidence 22. Every cell is a first pass; no second drafter.
- [x] **D3. Written, rendered and linted**, by `study-first-write.py`; on the soft-launch map. Reported to Bill.

- [x] **Rebuild reassess**, 2026-10-26: the second-drafter check agreed on 20 of 20 cells (`agreement.csv`); the 51 first-pass cells were read afresh and four moved. The ECOWAS SIGMAT launch Guinea stood on names Cote d'Ivoire and Liberia equally, so both took it as a fact and stage 5; Libya fell to 2, its full ASYCUDA launch still announced; Mauritania's 2026 clearance guide set 3.

**Decided in the run**: Nothing removed at the top-stage check.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
