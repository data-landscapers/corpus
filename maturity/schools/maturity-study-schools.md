---
type: task
reader: cc
title: maturity-study-schools.md — the second maturity study: rural primary schools, as EMIS
last_reviewed: 2026-10-09
status: proposed by CC on Bill's commission of 2026-10-09, for his rulings; not yet run
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

The id is CC's, after the health pair, and enters `lookups/indicators.csv` only at acceptance, when both old rows are retired. **The census gets no ladder of its own**; that is CC's reading of Bill's line and his to reverse.

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

**A learner register is `emis`, and tops out at stage 3.** Unique learner numbers filled in once a year at enrolment are a record per learner, and are not daily use.

**Higher and vocational education are out of scope.**

**Levels.** P primary, with pre-primary where it is taught in the same school; S secondary. The country's own cycle names are mapped in `systems.csv`. Where basic education runs nine years in one school, that school is P.

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

## 4. The ladder

Tested and fixed at S3.

| Stage | Levels | How the record is kept | Primary schools |
|---|---|---|---|
| 1 Absent | A dated statement that primary schools keep learner records on paper only | | |
| 2 Nascent | Secondary schools only, or some districts; or a national system contracted or in preparation | Any, or not stated | None, or pilot schools |
| 3 Established | P: a national system holds a record for each primary learner | `enrolment` or `keyed-elsewhere` | Routine entry in a minority, or not published |
| 4 Operating | P | `routine` | More than half enter attendance or results during the year, on a share or a count with a denominator |
| 5 Leading | P | `routine`, with attendance entered daily | 90 per cent or more, on a figure published within two years that gives the rural share |

**A census never places a country above stage 1.** A country holding only noted classes is unplaced, or stage 1 where a source states that learner records are on paper; what it holds prints under *Noted, not assessed*.

**Stage 2 takes preparation** *(Bill, 2026-10-09)*, as the health study's §4 defines it.

**A share of all schools is read as the share of primary schools**, and the short summary says which. A share of schools *registered on* or *given* a system is not a share entering data: it places by the lower rung.

## 5. The norm

The African Union's Digital Education Strategy (2022): devices for 20 per cent of students and half of teachers by 2027; half of institutions connected; and, under its fourth objective, a move from *EMIS 1.0* to an individual-level, ID-linked *EMIS 2.0*.

**It does not measure what the sub-indicator measures, and it carries the trap.** Its device and connection targets count `enabling`. Its *EMIS 1.0*, as the first run read it, is the census under the EMIS name. *EMIS 2.0* is nearest, and describes a record and its links, not whether a school uses it. The ladder borrows nothing from it: the 90 per cent line is the health study's. The pages say so.

## 6. What Phase 1 reads and searches for

- **Subjects**: `dpi.mis`, `digital.rural`, `dpi.exchange`.
- **Term list**, in `study.json`: EMIS, SIGE, OpenEMIS, StatEduc, school census, recensement scolaire, censo escolar, annuaire statistique, learner identifier, school management system, and their French and Portuguese forms. **Census terms are searched on purpose**: a census document is where a ministry says what else it runs.
- **Source types for the briefs**, ranked: ministry EMIS manuals, user guides and circulars, which say who enters what and when; education sector plans and joint sector reviews; World Bank and GPE appraisal and implementation reports; UNESCO, UIS and UNICEF EMIS diagnostics; statistical yearbooks, for their method chapter only; dated news of a rollout, an outage or a withdrawal, for aspect 4.

## 7. Tasks, in order

- [ ] **S1. Bill's rulings** on §1 to §4: the single sub-indicator and its id, the retirement of `dpi.mis--education`, the learner register at stage 3, the *rural gap* flag.
- [ ] **S2. Review all 54 countries in one run**, method §4. `study-ladder-health.py` is the health study's own; write its counterpart, with tests.
- [ ] **S3. Test and fix the ladder** on the profiles, method §3 rule 9. Read the Strategy's fourth objective whole and correct §5 if it does not say what the first run took it to.
- [ ] **S4. Search, select and hand over**, method §5. Tell Bill the count before the note is written.
- [ ] **S5. Phase 2, on Bill's trigger**, method §6 and §7.
- [ ] **S6. Write, render and lint**, method §8. Write `study.json`'s `criteria` again from the fixed ladder and set `criteria_of`. Commit.
- [ ] **S7. Report to Bill**: countries per stage; unplaced and *No evidence*; countries holding only a census, by the name each gives it; *rural gap* flags; the agreement count; what OSINT did not admit; every country the cap held at 3.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
