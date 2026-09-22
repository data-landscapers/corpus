---
type: plan
title: Data work to completion — who does what
opened: 2026-09-22
---

# Data work to completion — who does what

*(Written 2026-09-22 at Bill's request, from the share's register, housekeeping register, notes and `new-queue/`, and Corpus's `budgets/` and logs. **Run in order; tick each box in the commit that completes it**, with the date. Standing items have no box.)*

## The division of labour

| | Does | Limit |
|---|---|---|
| **OSINT** | Collection: the nightly sweep cycle, ingest, the backfill lane, document acquisition, wiki housekeeping, fixes to its own records and `lookups/` | **The weekly quota.** Anything beyond the sweep cycle runs only on a morning when usage is under that day's line in the share's `osint-daily-usage-targets.md` |
| **CORPUS** | Processing: budget extraction (`budgets/`), the datasets, the compile; then rendering and publishing the site | None that matters: work is paced by Bill, not by quota |
| **Bill** | Decisions, delivering notes to OSINT, anything outward-facing, Cowork sessions | — |

**OSINT's order of work is fixed:** the sweep cycle first, then the data-centre backfill (automatic, in the backfill lane), then housekeeping. **OSINT's budget work waits until the backfill and housekeeping are both clear.** Corpus's budget work does not wait: it fetches documents from the publisher and needs OSINT only when a document cannot be found.

## Where things stand

| Area | State | What remains |
|---|---|---|
| Data-centre dataset | Live on `/datasets/data-centres/`; T1–T9 done; *finalising* notice removed by Bill | T10's upstream link on the main site; 233 source documents still to ingest (batches 11–16) |
| Data-centre backfill | ZAF and batches 01–10 pulled and ingested | Batches 11–16 (233 items) sit on the share **without `READY`**, so nothing is moving — Corpus's step |
| Housekeeping | 42 open jobs (143–186), ~3,170 min ≈ **53 hours** of OSINT sessions | All of it; almost all are wiki-page merges and mints, which only OSINT may write |
| Acquisition feed | `africa-acquire.csv` holds 2 rows (Madagascar LFR tomes) | Those 2 |
| Non-state finance | Current; OSINT's latest records compiled into `outputs/` but not yet rendered | One BUILD and RENDER with a change-log entry |
| Budgets | 54 countries: **5 read against the spec** (CAF and ZAF all three years; GHA, MDG, NER one year each), **23 hold only migrated rows** (370 rows, plus 2 in GHA), **26 have nothing** | See Phase 2 |
| Notes to OSINT | 159, 160, 161 (small record and FX fixes); 162, 163 (budget catalogue pages and South African Acts) | Delivery by Bill |

## Phase 1 — now until the backfill and housekeeping are clear

### CORPUS

- [ ] **1.** **Write `READY` on the last data-centre batches** (note 47's pace of about 190 a night), then close `notes-for-corpus` 47 when the last is pulled. *This is what the backfill is waiting on.*
  - [x] Batches 11–14 (160) — 2026-09-22
  - [ ] Batches 15–16 (73) — 2026-09-23
- [ ] **2.** **Run BUILD and RENDER** to publish OSINT's new finance records (Côte d'Ivoire, Ghana, Nigeria, South Africa and the Sahel regional rows), with the change-log entry.
- [ ] **3.** **Budget sittings, one country-year each (R58)**, in this order — the countries with most structure gaps first, then those complete on structure. Each sitting fetches the publisher's copy; where it cannot, it writes an `africa-acquire.csv` row for Phase 2 and moves on. A year is struck through when its sitting commits; the country's box is ticked when all its years are.
  - [ ] ETH — 2024, 2025, 2026
  - [ ] KEN — 2024, 2025, 2026
  - [ ] NGA — 2024, 2025, 2026
  - [ ] BDI — 2024, 2025, 2026
  - [ ] AGO — 2025, 2026
  - [ ] BFA — 2024, 2025, 2026
  - [ ] BWA — 2024, 2025, 2026
  - [ ] BEN — 2024, 2025, 2026
  - [ ] SEN — 2024, 2026
  - [ ] COG — 2024, 2025, 2026
  - [ ] COM — 2024, 2025, 2026
  - [ ] EGY — 2025
  - [ ] ZMB — 2026
  - [ ] ZWE — 2026
  - [ ] CIV — 2024, 2025, 2026
  - [ ] CPV — 2024, 2025, 2026
  - [ ] RWA — 2024, 2025, 2026
  - [ ] CMR — 2024, 2025, 2026
  - [ ] COD — 2024, 2025, 2026
  - [ ] MOZ — 2026
  - [ ] DZA — 2026
  - [ ] TZA — 2025, 2026
  - [ ] SLE — 2026
  - [ ] GHA — 2024
- [ ] **4.** **ZAF harmonisation pass:** the three years hold slightly different line sets; Vote 30 was restated in FY2026; one Stats SA 2024/25 outturn is unexplained.
- [ ] **5.** **T10 upstream edit** in `data-landscapers` (one line on the v2 post pointing to the Corpus dataset) and the *dataset complete* change-log entry — **when Bill says go**.

### OSINT

- **6.** *(standing)* **Sweep cycle nightly** — unchanged, always first.
- [ ] **7.** **Pull and ingest data-centre batches 11–16** as they turn `READY`: automatic in the backfill lane, about two nights.
- [ ] **8.** **Housekeeping, oldest first** (jobs 143 → 186): one job on the Day B night, plus the extra sessions Bill runs each day while usage is under that day's line in `osint-daily-usage-targets.md`.
- [ ] **9.** **Notes 159, 160, 161** — small: two finance-record corrections and the ZWG exchange-rate rows. They fit a housekeeping slot.

### Bill

- **10.** *(standing)* **Run OSINT's extra sessions daily against the usage targets**, as now. The quota sets the pace, so no fixed rate is set. At about 75 minutes a job, clearing the 42 jobs by the end of next week needs about six a day. Phase 2 starts when the register reads zero.
- [ ] **11.** **Deliver notes 159–161** to OSINT now; hold 162 and 163 for Phase 2.
- [ ] **12.** **Answer the two open blocks in `logs/messages-for-bill.md`**: the non-state summary bucketing by publication year, and the US$4bn Botswana MoU summed as committed finance.
- [ ] **13.** **Say when to announce the data-centre dataset** — that releases task 5.
- **14.** *(standing)* **Keep budget CSVs closed in Excel while sittings run** — an open file locks the rewrite (it stopped two today).

## Phase 2 — once the backfill and housekeeping are clear

### OSINT

- [ ] **15.** **R55:** stage the documents in `new-budget/` (GHA, LBY, MDG, NER, ZWE) into `new/`.
- [ ] **16.** **Notes 162 and 163:** companion pages for the CAR and South African budget volumes, and the three South African Appropriation Acts. Corpus then re-points the stand-in citations.
- [ ] **17.** **Acquire what Corpus's sittings could not fetch**, from `africa-acquire.csv`.
- [ ] **18.** **R57:** retire OSINT's domestic-state budget layer. It is safe once no Corpus file carries a migrated row that still leans on those records.

### CORPUS

- [ ] **19.** **The 26 countries with no budget rows**, three years each: DJI, ERI, GAB, GIN, GMB, GNB, GNQ, LBR, LBY, LSO, MAR, MLI, MRT, MUS, MWI, NAM, SDN, SOM, SSD, STP, SWZ, SYC, TCD, TGO, TUN, UGA. Where a document exists it is read; where none is published, the sitting logs the absence.
- [ ] **20.** **Re-point stand-in citations** as 162 and 163 land.

### Bill

- [ ] **21.** **R64:** when the housekeeping register and `africa-acquire.csv` both read zero, take out the Day B row and call review 5.

## Phase 3 — publishing budgets

- [ ] **22.** **Budgets return to the Finance page** — CORPUS, on Bill's go. Proposed bar: every migrated row replaced by a read one (the structure-gap ceiling at zero and no `origin_record` left), so nothing published is a stand-in.
- [ ] **23.** **The continental budget dataset in US$** — CORPUS. The conversion happens at build time from `lookups/fx-imf-annual.csv` (`finance_lib.fx_rate`), recording the rate, the rate's year and a flag where another year's rate was used; source rows stay in local currency. Needs note 161's ZWG rates.

## Sizing

| Work | Owner | Estimate |
|---|---|---|
| Data-centre backfill | OSINT (automatic) | ~2 nights after `READY` |
| Housekeeping | OSINT | ~53 hours of sessions |
| Budget sittings, migrated countries (~60 country-years) | CORPUS | 15–75 min each; about 30 hours |
| Budget sittings, unstarted countries (~78 country-years) | CORPUS | about 40 hours, less where nothing is published |
| Acquisition for missing budget documents | OSINT | unknown until the sittings have run |
