---
type: task
reader: cc
title: maturity-study-localrecords.md — the sixth maturity study: digitalisation of local government records, as the revenue record
last_reviewed: 2026-10-10
status: CC's proposal, run unamended on Bill's word of 2026-10-10; staged, written and rendered; awaiting acceptance
---

# Maturity study: localrecords — revenue records

*(Commissioned by Bill on 2026-10-10, under `maturity/documentation/maturity-study-method.md`. CC's proposal, modelled on the localgov and registry studies. Trigger: "**run maturity study localrecords**".)*

## 1. The question, and the row it redraws

**Does the local government keep its own revenue record digitally: who owes it, and what was paid?** `digital.localgov--digitalisation-of-local-government-records` has no settled subject. Its 40 staged cells hold civil registration, revenue software, treasury platforms, document systems and payroll checks as one thing.

**Why revenue.** Of the record types the localgov study logged, it is the one a local government makes itself and that sources report by local government: 100 named systems in 34 countries. Civil registration is the registry study's and land is `dpi.registry--land-register`; accounts run in the treasury's system; document systems are named in 27 countries and described in few.

**One sub-indicator replaces the row**:

| Sub-indicator | Indicator text | Id |
|---|---|---|
| Revenue records | Digitalisation of local government records: revenue records | `digital.localgov--digitalisation-of-local-government-records-revenue-records` |

The id enters `lookups/indicators.csv` at acceptance. `dpi.pay--revenue-collection`, `dpi.registry--tax-register` and `dpi.mis--tax` stage the national tax authority and are not redrawn.

## 2. Typology

| Class | What it is | Treatment |
|---|---|---|
| `revenue` | A system in which **the local government's own staff record, as routine, its payers and what they pay**: property rates, business licences, market and parking fees, local taxes | Assessed |
| `survey` | A one-off count that builds a register and no system to keep it: a property census, a valuation roll, an addressing exercise | Noted, not assessed; flagged, below |
| `central` | The national tax authority or treasury assesses or collects the local government's revenue, and holds the record | Noted, not assessed; stated in the long summary |
| `accounts` | Budget, accounting, payroll and procurement systems, the treasury's extended to local governments or their own | Noted, not assessed |
| `documents` | Document, archive, correspondence and minutes systems | Noted, not assessed |
| `permits` | Building permits and licensing workflows that state no bill or payment | Noted, not assessed |
| `web` | A portal or payment channel for residents, with no record behind it stated | Noted, not assessed |
| `upper-tier` | The revenue systems of a state, province or region | Noted, not assessed; stated in the long summary |
| `civil` | Civil registration | Out of scope: the registry study |
| `land` | Land titles and the cadastre, unless the source says the local government bills from it | Out of scope |
| `enabling` | Connection and equipment | Out of scope: the localgov study |

**The test: does the local government's own staff enter the payer and the payment in the system, as routine?** A register built by a project and not said to be billed from is `survey`. A payment channel alone, mobile money or a bank counter, is `web` until a source says the local government's record is made from it.

**Classified by what the source says the system does**; a name alone is unclassified.

**A private collector.** Where a firm collects under contract in its own system, the class is `revenue` and the owner is `vendor`: the cap rule holds the cell at 3.

**Local governments.** The basic tier, as the localgov study defines it (its §2), elected or appointed. The denominator is the country's own count of them.

**Two flags that never change the stage.** *Register survey*: a `survey` is under way or done. *Centrally collected*: a `central` body collects a main local revenue.

## 3. Aspects

| # | Aspect | Role | Values |
|---|---|---|---|
| 1 | Governance, planning, finance | qualifier | Owner: the state, central or local; partner or vendor. Plan: a current strategy or costed plan naming the system, or none. Finance: domestic budget line, donor only, or not stated |
| 2 | What is recorded | coverage | `register`: the payers and each bill and payment against them. `receipts`: payments only, by electronic receipt or point-of-sale device, with no register of payers. `none` |
| 3 | Where the record is held | coverage | `shared`: in a national or shared system, or one that reports to the centre. `local`: in a system that stays in the local government. `paper` |
| 4 | Last twelve months | qualifier | Advancing, no change on record, or regressing, with the dated event |
| 5 | Local governments recording | coverage | Share of basic-tier local governments, with numerator, denominator, year and who says so; else `equipped`, a share given the system or trained on it; else a count; else *not published* |

**Aspects 2, 3 and 5 set the stage; 1 and 4 cap or flag it and never raise it. The cap rule and aspect 4 are the health study's, unchanged** (its §3).

## 4. The ladders

**Revenue records**

| Stage | What is recorded | Where held | Local governments |
|---|---|---|---|
| 1 Absent | A dated statement that local governments keep their revenue records on paper | `paper` | |
| 2 Preparing | A system is being prepared or piloted; or a `survey` only; or only the capital city or the upper tier records | Any, or not stated | Pilot local governments, or none |
| 3 Establishing | `register` or `receipts`: past its pilot and live in some local governments outside the capital | `shared` or `local` | A minority, a count with no total, or not published |
| 4 Operating | `register` | `shared` or `local` | More than half, on a share or a count with a denominator |
| 5 Leading | `register` | `shared` | 90 per cent or more, on a figure published within two years |

**Pilot or live, and preparation, are read as the schools study reads them** (its §4). **A noted class never places a country above stage 1**, as in the police study (its §4).

**The localgov study's fixes hold** (its §4): a share *equipped*, *trained* or *covered* is `equipped` and places at stage 3 only where the system is live; a count of sites is a floor without its total; a system announced is preparation; a law places nothing.

**Receipts alone stop at stage 3**: without a register of payers a local government cannot say who has not paid.

**Fixed at R3** (`ladder-test.csv`, `corrections.csv`): A system in use in a counted local government, with what it records not stated, is read as `receipts`. Staff trained on a system, or a system made available, is `equipped`. Paper in some local governments does not unsay a count of others recording.

**Fixed at R5.** Where the record is held, left unstated, does not keep a country from stage 3 where a system is in use outside the capital. *Centrally collected* is flagged only where a source says a central body collects a local revenue; a national tax system alone is not that.

## 5. The norm

The frame's anchor (`lookups/maturity-norms.csv`) is the African Union's Digital Transformation Strategy, with the decentralisation charter's Article 16. The Strategy asks states to "establish electronic government registers or digitalise existing ones, starting with an electronic population registry, eBusiness register and Land Use register", and to let organisations "reuse core registers".

**Neither measures what the sub-indicator measures.** The Strategy names national registers and no local government; Article 16 sets a duty and no measure. The ladder takes one thing from the Strategy: stage 5 needs `shared`, a record the centre can reuse. *(Read 2026-10-10.)*

## 6. What the review reads and the search asks for

- **Subjects and term list**: in `study.json`. **The terms are revenue terms**, not the localgov study's names for a local government.
- **Source types for the briefs**, ranked: audit reports on local governments; annual reports of the ministry of local government and of local finance bodies; budget reports and parliamentary answers; donor project documents and evaluations on local revenue; local government association surveys; dated news, for aspect 4.

## 7. Tasks, in order

- [x] **R1. Bill's rulings**: the six proposals stand, 2026-10-10.
- [x] **R2. Review all 54 countries**, method §4: 566 documents, 117 facts, 20 countries with evidence.
- [x] **R3. Test and fix the ladder**: 3 facts withdrawn.
- [x] **R4. Search and hand over**, method §5: 127 documents, `notes-for-osint` 225.
- [x] **R5. Re-read and stage**: 111 of 127 admitted; as at 2026-09-30; agreement 20 of 20.
- [x] **R6. Write, render and lint**: clean; on the soft-launch map.
- [x] **R7. Report to Bill.** Awaiting acceptance.

**The rulings of R1**, CC's proposals, run unamended: the revenue record only; only this row redrawn; receipts with no register stop at stage 3; a private collector's system counts, capped at 3; revenue the centre collects is flagged and places nothing; stage 5 needs a shared system.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
