---
type: task
reader: cc
title: maturity-study-health.md — the first maturity study: health, as HMIS and patient records
last_reviewed: 2026-10-06
status: proposed by Cowork at Bill's request, for CC's operational review; not yet run
---

# Maturity study: health — HMIS and patient records

*(Commissioned by Bill on 2026-10-06, the first study under `maturity-study-method.md`. Lines marked (Bill) are his rulings of that day; the rest is Cowork's proposal. Triggers: "**run maturity study health**", then "**run maturity study health phase 2**".)*

## 1. The question, and the rows it redraws

**How far is health data digital, from the ministry down to the primary clinic?** Two frame rows ask that today: `dpi.mis--health` and `digital.rural--digitalisation-of-rural-health-clinics`. Their stages read reporting systems, stock systems, community apps, patient trackers and satellite kits as one thing.

**One study redraws both rows** *(Bill)*. It is assessed as two sub-indicators, under the working keys `health.hmis` and `health.records`. These are not frame ids; §8 has what happens to the frame.

`dpi.exchange--interoperability-of-health-systems` is not redrawn. Its evidence is logged in `logs/study/health/exchange.csv` and left.

## 2. Typology

| Class | What it is | Treatment |
|---|---|---|
| `hmis` | Routine aggregate reporting of a facility's operations and logistics, usually monthly: service counts, stock, staff, finance *(Bill)* | Assessed as `health.hmis` |
| `hmis-single` | Aggregate reporting for one function only: stock, surveillance, laboratory | Counts to `health.hmis`; alone, places no higher than stage 2 |
| `record` | The digital, transportable record of a patient's health history and dealings with the health service *(Bill)*, kept for general care | Assessed as `health.records` |
| `tracker` | Patient-level, one programme: immunisation, HIV, TB, maternal, community household | Noted, not assessed *(Bill)* |
| `enabling` | Connectivity, devices, power, telemedicine kits | Noted, not assessed |
| `exchange` | Interoperability layers, client and facility registries | Logged for `dpi.exchange` |

**DHIS2 is classified by module, never by name** *(Bill: some deployments include patient records and others do not)*. Aggregate reporting is `hmis`; a Tracker or Capture programme is `tracker`. A source that says only "DHIS2" is `hmis` where it describes aggregate reporting and unclassified otherwise.

**A hospital management system is `record` only where the source says it holds the clinical record**; billing and administration alone are out of scope.

**Tiers.** T1 national and referral hospitals; T2 regional and district hospitals; T3 health centres; T4 health posts, dispensaries and clinics. **Primary clinics are T3 and T4**, every facility below the first referral hospital; the country's own tier names are mapped in `systems.csv`. Community health workers are recorded as tier C and never counted as primary clinics.

## 3. Aspects *(Bill)*

| # | Aspect | Role | Values |
|---|---|---|---|
| 1 | Governance, planning, finance | qualifier | Owner: ministry unit, partner or vendor. Plan: a current strategy or costed plan naming the system, or none. Finance: domestic budget line, donor only, or not stated |
| 2 | Tiers in use | coverage | Which of T1 to T4 use it routinely |
| 3 | Where data is digitised | coverage | HMIS: at the facility, at the district from paper, or nationally. Records: at the point of care, or keyed afterwards |
| 4 | Last twelve months | qualifier | Advancing, no change on record, or regressing, with the dated event |
| 5 | Primary clinics doing the digital input | coverage | Share of primary clinics, with numerator, denominator, year and who says so; else a count; else *not published* |

**Aspects 2, 3 and 5 set the stage; 1 and 4 cap or flag it and never raise it** *(Bill)*.

**Cap rule, on aspect 1.** Stage 4 or 5 needs the ministry named as owner and either a domestic budget line or a current plan covering the system. Without both the stage is capped at 3 and flagged *externally run*. Read `outputs/budgets/{ISO3}-budget.csv` for the budget line before searching.

**Aspect 4 flags only.** A regression that removes coverage is restaged on what still runs.

## 4. The ladders

Proposed; fixed at task H4.

**`health.hmis`**

| Stage | Tiers | Where digitised | Primary clinics |
|---|---|---|---|
| 1 Absent | A dated statement that routine reporting is on paper end to end | | |
| 2 Nascent | Hospitals only, or some districts; or a national rollout contracted; or `hmis-single` alone | Anywhere | None, or pilot sites |
| 3 Established | Every district reports | At the district, from clinics' paper forms | Facility entry in a minority, or not published |
| 4 Operating | T1 to T4 | At the facility | More than half enter their own reports, on a share or a count with a denominator |
| 5 Leading | T1 to T4 | At the facility | 90 per cent or more, on a figure published within two years, with reporting completeness published |

**`health.records`**

| Stage | Tiers | Where digitised | Primary clinics |
|---|---|---|---|
| 1 Absent | A dated statement that patient records are on paper at every tier | | |
| 2 Nascent | Some hospitals or pilot facilities; or a national system procured | Anywhere | None, or pilot sites |
| 3 Established | Most T1 and T2 hospitals, or primary clinics in some districts | Either; the record stays in the facility | A minority, or not published |
| 4 Operating | T1 to T4 | At the point of care, on a unique patient identifier, retrievable at another facility | More than half |
| 5 Leading | T1 to T4 | As 4, across the public network | 90 per cent or more, on a figure published within two years |

**A country whose only patient-level system is a tracker is unplaced on `health.records`**, or stage 1 where a source states that general records are on paper; the tracker prints under *Noted, not assessed*.

## 5. The norm

Africa CDC's Digital Transformation Strategy (2023) and the PHC Digitalisation Framework (2025–26): 100,000 facilities connected and 2 million community health workers equipped by 2030; 90 per cent digitally enabled primary care by 2035. The row is in `lookups/maturity-norms.csv`.

**It does not measure what either sub-indicator measures.** It counts connection and *digitally enabled*, which a clinic with a tablet and paper registers meets. The ladders borrow only the 90 per cent line, for stage 5, and the pages say so. Argue this from the evidence at H4.

## 6. What Phase 1 reads and searches for

- **Subjects**: `dpi.mis`, `digital.rural`, `dpi.exchange`. On 2026-10-06 the mirror held 1,688 documents tagged `dpi.mis` and 842 tagged `digital.rural`, all sectors together.
- **Term list**, to narrow those to health and to catch untagged documents: DHIS2, HMIS, SNIS, SIS, health information system, système d'information sanitaire, sistema de informação de saúde, EMR, EHR, electronic medical record, dossier médical, dossier patient, processo clínico, OpenMRS, eLMIS, health facility, formation sanitaire, unidade sanitária. Add Arabic equivalents and national system names the review turns up.
- **Source types for the briefs**, ranked: ministry HMIS bulletins and reporting-rate tables; digital health strategies and costed plans; facility assessments (HHFA, SARA, SPA); World Bank appraisal and implementation reports; Global Fund and Gavi grant documents; WHO country reports; peer-reviewed data-quality studies, which usually say where the data is keyed.
- **Ceiling**: six staged documents a country, 324 overall.

## 7. Tasks, in order

Tick each box in the commit that completes it.

- [ ] **H1. Build the four scripts** the method names (`study-select.py`, `study-returned.py`, `study-render.py`, `lint-study.py`), with tests. `lint-interface.py` still passes.
- [ ] **H2. Open the lane.** Cut the patch adding `study-` to `BACKFILL_PREFIXES` in OSINT's `scripts/ingest-lane.py`; deliver it to `prepared/` with its `BRIEF.md` and an `[ACT]` note.
- [ ] **H3. Review all 54 countries in one run** *(Bill: no pilot)*, method §4. One drafter per country; the parent verifies files.
- [ ] **H4. Test and fix the ladders.** Count countries per rung on the Phase 1 profiles. Rewrite any rung nothing reaches or that drafters read two ways, record the change here, and write §5's paragraph.
- [ ] **H5. Search, stage and deliver**, method §5. `READY` waits on H2 being applied.
- [ ] **H6. Phase 2, on Bill's trigger**: what came back, the as-at, the stages, the agreement check (method §6 and §7).
- [ ] **H7. Write, render and lint** (method §8). Commit.
- [ ] **H8. Report to Bill**: countries per stage for each sub-indicator; unplaced and *No evidence*; tracker-only countries; the agreement count; what OSINT did not admit; the capped countries.

## 8. Bill's to rule, at acceptance

- **Where the two sit in the frame.** Proposed: two rows under `dpi.mis` — *Health management information system* and *Patient records* — with both old rows retired and the rural question carried by aspect 5. The alternative keeps a rural row as a view of aspect 5.
- **The `hmis-single` rule**, the **cap rule** and the **thresholds** (half, 90 per cent) are Cowork's, and each changes stages.

## Boundary

Nothing here writes to `C:\OSINT` or to `raw/`. Found documents go to `new-queue/` and count only once ingested.
