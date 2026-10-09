---
type: task
reader: cc
title: maturity-study-schools.md — the second maturity study: rural primary schools, as EMIS
last_reviewed: 2026-10-09
status: CC's proposal, agreed by Bill on 2026-10-09 with stages 2 and 3 reworded; run 2026-10-09
---

# Maturity study: schools — EMIS

*(Commissioned by Bill on 2026-10-09, the second study under `maturity/documentation/maturity-study-method.md`. Lines marked (Bill) are his; the rest is CC's proposal, modelled on `maturity/health/maturity-study-health.md`. Study id `schools`. Triggers: "**run maturity study schools**", then "**run maturity study schools phase 2**".)*

## 1. The question, and the rows it redraws

**Do primary schools keep their learners' records digitally, day to day?** Two frame rows ask near it. `digital.rural--digitalisation-of-rural-primary-schools` staged connectivity and devices, which are not data capture. `dpi.mis--education` put 18 countries at stage 3 for *EMIS 1.0: aggregate school returns and an annual census published*, which is the trap below.

**An annual school census is a facility survey. An EMIS is in use daily, recording attendance, learning outcomes and the rest. Some countries call their census an EMIS, and the study must not** *(Bill, 2026-10-09)*.

**One sub-indicator replaces both rows**:

| Sub-indicator | Indicator text | Id |
|---|---|---|
| EMIS | Digitalisation of rural primary schools: EMIS | `digital.rural--digitalisation-of-rural-primary-schools-emis` |

The id enters `lookups/indicators.csv` only at acceptance, when both old rows are retired. **The census gets no ladder of its own** *(Bill)*.

`dpi.exchange--interoperability-of-education-systems` is not redrawn. Its evidence is logged in `maturity/schools/exchange.csv`.

## 2. Typology

| Class | What it is | Treatment |
|---|---|---|
| `emis` | The ministry's system, or one that feeds it, holding **a record per learner that the school itself adds to during the school year** | Assessed |
| `census` | A questionnaire per school, once a year, returning counts: the annual school census, the statistical yearbook built on it, and the platform that collects it | Noted, not assessed *(Bill)* |
| `single-function` | One function only: examination registration, teacher payroll and deployment, inspection, school feeding, attendance totals sent by SMS | Noted, not assessed |
| `standalone` | A school's own package or a vendor's app that sends the ministry nothing | Noted, not assessed |
| `learning` | Content, e-learning platforms, digital classrooms | Noted, not assessed |
| `enabling` | Connectivity, devices, power | Noted, not assessed |
| `exchange` | Links to the national ID, examinations or payroll | Logged for `dpi.exchange` |

**The test that separates `emis` from `census`: does the school enter anything between one census day and the next?** If a source describes no entry but the yearly return, the system is `census`, whatever it is called, however the return is captured (paper, tablet or web form) and whoever keys it.

**Classified by what the source says the system does, never by name.** *EMIS*, *SIGE*, *OpenEMIS*, *StatEduc* and *DHIS2 for Education* each run as a census in one country and as learner records in another. A source that gives only the name is unclassified, a gap for the search.

**Nor by what it is built in** *(Bill, 2026-10-09)*: a spreadsheet the school keeps per learner and sends up is `emis` as much as a proprietary application.

**A learner register is `emis`, and tops out at stage 3.** Unique learner numbers filled in once a year at enrolment are a record per learner, and are not daily use.

**Levels.** Higher and vocational education are out. P primary, with pre-primary where it is taught in the same school; S secondary. The country's own cycle names are mapped in `systems.csv`.

## 3. Aspects

| # | Aspect | Role | Values |
|---|---|---|---|
| 1 | Governance, planning, finance | qualifier | Owner: ministry unit, partner or vendor. Plan: a current strategy or costed plan naming the system, or none. Finance: domestic budget line, donor only, or not stated |
| 2 | Levels in use | coverage | P, S, or none |
| 3 | How the record is kept | coverage | `routine`: at the school, during the year, attendance or assessment results per learner. `enrolment`: at the school, once a year or at registration. `keyed-elsewhere`: at the district or ministry, from the school's paper registers. `paper` |
| 4 | Last twelve months | qualifier | Advancing, no change on record, or regressing, with the dated event |
| 5 | Primary schools doing the digital input | coverage | Share of primary schools, with numerator, denominator, year and who says so; else a count; else *not published* |

**Aspects 2, 3 and 5 set the stage; 1 and 4 cap or flag it and never raise it. The cap rule and aspect 4 are the health study's, unchanged** (its §3): without the ministry as owner and a domestic budget line or current plan, stage 4 or 5 is capped at 3 and flagged *externally run*.

**Rural.** The stage reads primary schools nationally. Where a dated source says rural schools are outside the system, or enter less, the cell is flagged *rural gap* and the short summary gives the figure.

## 4. The ladders

Tested and fixed at S3, 2026-10-09 (`ladder-test.csv`): a register still at its pilot is stage 2, and a level is no longer required to be named.

**EMIS**

| Stage | Levels | How the record is kept | Primary schools |
|---|---|---|---|
| 1 Absent | A dated statement that primary schools keep learner records on paper only | | |
| 2 Preparing | An EMIS for primary schools is being prepared or piloted; or one runs in secondary schools only | Any, or not stated | Pilot schools, or none |
| 3 Establishing | P: past its pilot and live in some primary schools, for routine entry or as a learner register | `routine`, `enrolment` or `keyed-elsewhere` | A minority, a count with no total, or not published |
| 4 Operating | P | `routine` | More than half enter attendance or results during the year, on a share or a count with a denominator |
| 5 Leading | P | `routine`, with attendance entered daily | 90 per cent or more, on a figure published within two years that gives the rural share |

**Pilot or live is the source's word** *(Bill, 2026-10-09)*: a rollout, a phase after the pilot, or schools named as using it is live. Where the source does not say, it is a pilot.

**A census never places a country above stage 1.** A country holding only noted classes is unplaced, or stage 1 where a source states that learner records are on paper; what it holds prints under *Noted, not assessed*.

**Preparation is the health study's** (§4).

**A share of all schools is read as the share of primary schools, and a system for *schools* with no level named as P**; the short summary says which. A share of schools *registered on* or *given* a system is not a share entering data: it places by the lower rung.

## 5. The norm

The African Union's Digital Education Strategy (2022), fourth objective: a move from *EMIS 1.0*, "aggregate statistical data collection for generating annual reports", to *EMIS 2.0*, individual-level data on unique identifiers, in at least half of member states by 2027. Its device and connection targets (20 per cent of students and half of teachers by 2027; half of institutions connected) count `enabling`.

**It draws this study's line, and keeps one name for both sides of it.** Its *EMIS 1.0* is the school census, in its own words. Its *EMIS 2.0* is met by a learner register, this ladder's stage 3: it asks for a record per learner, not for a school that uses it during the year. The ladder borrows nothing from it; the 90 per cent line is the health study's. *(Read 2026-10-09: pages 10, 55 to 58.)*

## 6. What Phase 1 reads and searches for

- **Subjects**: `dpi.mis`, `digital.rural`, `dpi.exchange`.
- **Term list**: in `study.json`. Census terms are in it on purpose.
- **Source types for the briefs**, ranked: ministry EMIS manuals, user guides and circulars, which say who enters what and when; education sector plans and joint sector reviews; World Bank and GPE appraisal and implementation reports; UNESCO, UIS and UNICEF EMIS diagnostics; statistical yearbooks, for their method chapter only; dated news of a rollout, an outage or a withdrawal, for aspect 4.

## 7. Tasks, in order

- [x] **S1. Bill's rulings**: agreed, 2026-10-09.
- [x] **S2. Review all 54 countries in one run**, method §4: 1,105 documents, 302 facts.
- [x] **S3. Test and fix the ladder** on the profiles; §5 corrected from the Strategy's own text.
- [x] **S4. Search, select and hand over**, method §5. *130 delivered, note 220.*
- [x] **S5. Phase 2**: 124 of 130 admitted; 54 cells staged as at 2026-09-30; agreement 20 of 20.
- [x] **S6. Write, render and lint**: clean.
- [x] **S7. Report to Bill**, 2026-10-09. Acceptance is his.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
