---
type: plan
title: Data work to completion — who does what
opened: 2026-09-22
---

# Data work to completion — who does what

*(Written 2026-09-22 at Bill's request, from the share's register, housekeeping register, notes and `new-queue/`, and Corpus's `budgets/` and logs. Tick or strike as tasks close; when a phase is empty, delete it.)*

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

1. **Write `READY` on data-centre batches 11–14 tonight and 15–16 tomorrow** (note 47's pace of about 190 a night). Close `notes-for-corpus` 47 when the last is pulled. *This is what the backfill is waiting on.*
2. **Run BUILD and RENDER** to publish OSINT's new finance records (Côte d'Ivoire, Ghana, Nigeria, South Africa and the Sahel regional rows), with the change-log entry.
3. **Budget sittings, one country-year each (R58)**, in this order:
   - **The migrated countries with most gaps first:** ETH (19), KEN (17), NGA (11), BDI (10), AGO (9), BFA (8), BWA (6), BEN (4), then SEN, COG, COM, EGY, ZMB, ZWE.
   - **Then the migrated countries already complete on structure:** CIV, CPV, RWA, CMR, COD, MOZ, DZA, TZA, SLE, and GHA's two 2024 rows.
   - Each sitting fetches the publisher's copy. Where it cannot, it writes an `africa-acquire.csv` row for OSINT's Phase 2 and moves on.
4. **ZAF harmonisation pass:** the three years hold slightly different line sets; Vote 30 was restated in FY2026; one Stats SA 2024/25 outturn is unexplained.
5. **T10 upstream edit** in `data-landscapers` (one line on the v2 post pointing to the Corpus dataset) and the *dataset complete* change-log entry — **when Bill says go**.

### OSINT

6. **Sweep cycle nightly** — unchanged, always first.
7. **Pull and ingest data-centre batches 11–16** as they turn `READY`: automatic in the backfill lane, about two nights.
8. **Housekeeping, oldest first** (jobs 143 → 186), on days under the quota line.
9. **Notes 159, 160, 161** — small: two finance-record corrections and the ZWG exchange-rate rows. They fit a housekeeping slot.

### Bill

10. **Set the housekeeping rate.** At the Day B rate of one job a night, 42 jobs take about six weeks. Finishing next week needs about six a day, which means extra *run housekeeping* sessions on low-usage mornings. The rate is yours to set against the quota; nothing else in Phase 1 depends on it except when Phase 2 starts.
11. **Deliver notes 159–161** to OSINT now; hold 162 and 163 for Phase 2.
12. **Answer the two open blocks in `logs/messages-for-bill.md`**: the non-state summary bucketing by publication year, and the US$4bn Botswana MoU summed as committed finance.
13. **Say when to announce the data-centre dataset** — that releases task 5.
14. **Keep budget CSVs closed in Excel while sittings run** — an open file locks the rewrite (it stopped two today).

## Phase 2 — once the backfill and housekeeping are clear

### OSINT

15. **R55:** stage the documents in `new-budget/` (GHA, LBY, MDG, NER, ZWE) into `new/`.
16. **Notes 162 and 163:** companion pages for the CAR and South African budget volumes, and the three South African Appropriation Acts. Corpus then re-points the stand-in citations.
17. **Acquire what Corpus's sittings could not fetch**, from `africa-acquire.csv`.
18. **R57:** retire OSINT's domestic-state budget layer. It is safe once no Corpus file carries a migrated row that still leans on those records.

### CORPUS

19. **The 26 countries with no budget rows**, three years each: DJI, ERI, GAB, GIN, GMB, GNB, GNQ, LBR, LBY, LSO, MAR, MLI, MRT, MUS, MWI, NAM, SDN, SOM, SSD, STP, SWZ, SYC, TCD, TGO, TUN, UGA. Where a document exists it is read; where none is published, the sitting logs the absence.
20. **Re-point stand-in citations** as 162 and 163 land.

### Bill

21. **R64:** when the housekeeping register and `africa-acquire.csv` both read zero, take out the Day B row and call review 5.

## Phase 3 — publishing budgets

22. **Budgets return to the Finance page** — CORPUS, on Bill's go. Proposed bar: every migrated row replaced by a read one (the structure-gap ceiling at zero and no `origin_record` left), so nothing published is a stand-in.
23. **The continental budget dataset in US$** — CORPUS. The conversion happens at build time from `lookups/fx-imf-annual.csv` (`finance_lib.fx_rate`), recording the rate, the rate's year and a flag where another year's rate was used; source rows stay in local currency. Needs note 161's ZWG rates.

## Sizing

| Work | Owner | Estimate |
|---|---|---|
| Data-centre backfill | OSINT (automatic) | ~2 nights after `READY` |
| Housekeeping | OSINT | ~53 hours of sessions |
| Budget sittings, migrated countries (~60 country-years) | CORPUS | 15–75 min each; about 30 hours |
| Budget sittings, unstarted countries (~78 country-years) | CORPUS | about 40 hours, less where nothing is published |
| Acquisition for missing budget documents | OSINT | unknown until the sittings have run |
