---
type: task
reader: cc
title: maturity-study-health.md — the first maturity study: rural health clinics, as HMIS and EMR
last_reviewed: 2026-10-06
status: proposed by Cowork with Bill's rulings of 2026-10-06, for CC's operational review; not yet run
---

# Maturity study: health — HMIS and EMR

*(Commissioned by Bill on 2026-10-06, the first study under `maturity/documentation/maturity-study-method.md`. Lines marked (Bill) are his rulings of that day; the rest is Cowork's proposal. Study id `health`. Triggers: "**run maturity study health**", then "**run maturity study health phase 2**".)*

## 1. The question, and the rows it redraws

**How far is health data digital, from the ministry down to the primary clinic?** Two frame rows ask that today: `dpi.mis--health` and `digital.rural--digitalisation-of-rural-health-clinics`. Their stages read reporting systems, stock systems, community apps, patient trackers and satellite kits as one thing.

**One study redraws both rows, as two sub-indicators** *(Bill)*:

| Sub-indicator | Indicator text | Id |
|---|---|---|
| HMIS | Digitalisation of rural health clinics: HMIS | `digital.rural--digitalisation-of-rural-health-clinics-hmis` |
| EMR | Digitalisation of rural health clinics: EMR | `digital.rural--digitalisation-of-rural-health-clinics-emr` |

The ids are Bill's. They enter `lookups/indicators.csv` only at acceptance, when both old rows are retired.

`dpi.exchange--interoperability-of-health-systems` is not redrawn. Its evidence is logged in `maturity/health/exchange.csv` and left.

## 2. Typology

| Class | What it is | Treatment |
|---|---|---|
| `hmis` | Routine aggregate reporting of a facility's operations and logistics, usually monthly. **The bottom line: it reports how many patients were treated, and for what** *(Bill)* | Assessed as HMIS |
| `emr` | The digital, transportable record of a patient's health history and dealings with the health service *(Bill)*, kept for general care | Assessed as EMR |
| `single-function` | Aggregate reporting for one function only: stock, surveillance, laboratory | Noted, not assessed *(Bill)* |
| `tracker` | Patient-level, one programme: immunisation, HIV, TB, maternal | Noted, not assessed *(Bill)* |
| `community` | Systems used by community health workers | Noted, not assessed; integration is a plus *(Bill)*, below |
| `enabling` | Connectivity, devices, power, telemedicine kits | Noted, not assessed |
| `exchange` | Interoperability layers, client and facility registries | Logged for `dpi.exchange` |

**DHIS2 is classified by module, never by name**. Aggregate reporting of patients treated is `hmis`; a Tracker or Capture programme is `tracker`. A source that says only "DHIS2" is `hmis` where it describes that reporting and unclassified otherwise.

***Africa, we have a data problem* is excluded as evidence** *(Bill, 2026-10-06)*: an AI-assisted compilation, named in `study.json`.

**A hospital management system is `emr` only where the source says it holds the clinical record**; billing and administration alone are out of scope.

**A community system that exchanges data with the HMIS or the EMR earns the flag *community integrated*** on that sub-indicator. It prints in both summaries and does not change the stage.

**Tiers.** T1 national and referral hospitals; T2 regional and district hospitals; T3 health centres; T4 health posts, dispensaries and clinics. **Primary clinics are T3 and T4**, every facility below the first referral hospital; the country's own tier names are mapped in `systems.csv`. Community health workers are never counted as primary clinics.

## 3. Aspects *(Bill)*

| # | Aspect | Role | Values |
|---|---|---|---|
| 1 | Governance, planning, finance | qualifier | Owner: ministry unit, partner or vendor. Plan: a current strategy or costed plan naming the system, or none. Finance: domestic budget line, donor only, or not stated |
| 2 | Tiers in use | coverage | Which of T1 to T4 use it routinely |
| 3 | Where data is digitised | coverage | HMIS: at the facility, at the district from paper, or nationally. EMR: at the point of care, or keyed afterwards |
| 4 | Last twelve months | qualifier | Advancing, no change on record, or regressing, with the dated event |
| 5 | Primary clinics doing the digital input | coverage | Share of primary clinics, with numerator, denominator, year and who says so; else a count; else *not published* |

**Aspects 2, 3 and 5 set the stage; 1 and 4 cap or flag it and never raise it** *(Bill)*.

**Cap rule, on aspect 1** *(Bill: agreed for now, reconsidered after the first run)*. Stage 4 or 5 needs the ministry named as owner and either a domestic budget line or a current plan covering the system. Without both the stage is capped at 3 and flagged *externally run*. Read `outputs/budgets/{ISO3}-budget.csv` for the budget line before searching.

**Aspect 4 flags only**, and is where small anecdotal pieces belong: each dated event is its own evidence row. A regression that removes coverage is restaged on what still runs.

## 4. The ladders

Thresholds agreed *(Bill)*; wording fixed at H4 on 2026-10-06, against `ladder-test.csv`.

**HMIS**

| Stage | Tiers | Where digitised | Primary clinics |
|---|---|---|---|
| 1 Absent | A dated statement that routine reporting has no digital entry at any level | | |
| 2 Nascent | Hospitals only, or some districts; or a national rollout contracted | Anywhere, or not stated | None, or pilot sites |
| 3 Established | Any: a system keyed at district takes the clinics' reports | At the district, from clinics' paper forms | Facility entry in a minority, or not published |
| 4 Operating | The primary tier, T3 or T4 | At the facility | More than half enter their own reports, on a share or a count with a denominator |
| 5 Leading | The primary tier | At the facility | 90 per cent or more, on a figure published within two years, with reporting completeness published |

**EMR**

| Stage | Tiers | Where digitised | Primary clinics |
|---|---|---|---|
| 1 Absent | A dated statement that patient records are on paper at every tier | | |
| 2 Nascent | Some hospitals or pilot facilities; or a national system procured | Anywhere | None, or pilot sites |
| 3 Established | Most T1 and T2 hospitals, or primary clinics in some districts | Either; the record stays in the facility | A minority, or not published |
| 4 Operating | The primary tier | `shared`: at the point of care, on a unique patient identifier, retrievable at another facility | More than half |
| 5 Leading | The primary tier | As 4, across the public network | 90 per cent or more, on a figure published within two years |

**A country holding only noted classes is unplaced on that sub-indicator**, or stage 1 where a source states the paper position; what it does hold prints under *Noted, not assessed*.

**H4 changed three wordings and no threshold** (`h4-ladder-test.md`): the primary tier at stages 4 and 5, HMIS stage 3's district test, and the value `shared` for EMR stage 4. **A share of all health facilities is read as the share of primary clinics**, and the short summary says which. Stage 5 is unreached and stands.

## 5. The norm

Africa CDC's Digital Transformation Strategy (2023) and PHC Digitalisation Framework (2025–26): 100,000 facilities connected by 2030 and 90 per cent digitally enabled primary care by 2035.

**It does not measure what either sub-indicator measures.** It counts connection and *digitally enabled*, which a clinic with a tablet and paper registers meets. **The review bears this out**: most of the 15 coverage shares it found count facilities where a system is deployed, not clinics entering their own data. Countries publish the norm's kind of figure. The ladders borrow only the 90 per cent line, for stage 5, and the pages say so.

## 6. What Phase 1 reads and searches for

- **Subjects**: `dpi.mis`, `digital.rural`, `dpi.exchange`.
- **Term list**, to narrow those to health and to catch untagged documents: DHIS2, HMIS, SNIS, SIS, health information system, système d'information sanitaire, sistema de informação de saúde, EMR, EHR, electronic medical record, dossier médical, dossier patient, processo clínico, OpenMRS, eLMIS.
- **Source types for the briefs**, ranked: ministry HMIS bulletins and reporting-rate tables; digital health strategies and costed plans; facility assessments (HHFA, SARA, SPA); World Bank appraisal and implementation reports; Global Fund and Gavi grant documents; WHO country reports; peer-reviewed data-quality studies; dated news of a rollout, an outage or a withdrawal, for aspect 4.

## 7. Tasks, in order

- [x] **H1. Build the scripts**, with tests.
- [x] **H2. Open the lane.** Done by OSINT (`notes-for-corpus` 78); no patch sent.
- [x] **H3. Review all 54 countries in one run** *(Bill: no pilot)*, method §4.
- [x] **H4. Test and fix the ladders**, §4 and §5.
- [x] **H5. Search, select and hand over**, method §5. *245 delivered, note 218.*
- [ ] **H6. Phase 2, on Bill's trigger**, method §6 and §7.
- [ ] **H7. Write, render and lint** (method §8). Commit.
- [ ] **H8. Report to Bill**: countries per stage for each sub-indicator; unplaced and *No evidence*; countries holding only noted classes; *community integrated* flags; the agreement count; what OSINT did not admit; and every country the cap rule held at 3, for his reconsideration.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`.
