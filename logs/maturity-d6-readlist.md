---
type: log
title: Maturity D6 — what to read, and the calls CC flagged while vetting
date: 2026-09-24
---

# D6 read list

*(CC, 2026-09-24, for Bill's read of the July and August runs (task D6). A stage that looks wrong is fixed as a rubric change (C2, flagged `reassessed` on rerun) or as an assessor fix (D1), never by hand.)*

**Reading the files.**

- **The monthly edition**, `outputs/reports/{ISO3}/maturity/2026-07.csv` (and `2026-08.csv`): one row per indicator with evidence. Its columns are defined in `site/metadata/maturity-metadata.csv`.
- **Stages**: 1 Absent (a cited absence) · 2 Nascent · 3 Established · 4 Operating · 5 Leading. An empty `stage` is **unplaced**: evidence is held but meets no rung. An indicator with no row is **No evidence**.
- **What each stage needs for one indicator**: `lookups/maturity-rubric.csv`, five anchors per indicator. The norm behind them is in `lookups/maturity-norms.csv`.
- **Why a row is at its stage**: `stage_rows` names the ledger rows (in `outputs/reports/{ISO3}/ledger.csv`), and `qualifier` says what is missing for the next stage.
- **The drafter's input**: `logs/maturity-verdicts/{ISO3}-{YYYY-MM}.csv`. It is the same columns plus `cause`. Measures a drafter left out are filled in by the script from Corpus's own figures or the reference data (`reference/measures.csv`).
- **The movement list**, `logs/maturity-movements-2026-08.csv`: `july` and `august` are the stages; `movement` is one of:
  - `up` or `down`: staged in both months;
  - `placed`: unplaced in July, staged in August;
  - `unplaced`: staged in July, unplaced in August;
  - `newly assessed`: no July row, staged in August;
  - `newly unplaced`: no July row, unplaced in August.

  `moved_by` is the dated source.

**Countries to read**, the status report beside `outputs/reports/{ISO3}/maturity/2026-07.csv` and `2026-08.csv`:

- **thin: GNQ.** 51 of 104 unplaced in August, the most of any country; it tests whether unplaced reads as honest or as empty.
- **thick: NGA.** The most August movement (three moves up, three first placements), and its data-protection law moved from 3 to 4 on the first damages award.
- **with a read budget year: GHA.** `finance.sustain` computes, at 86.7 % domestic, from `budgets/GHA/2026.csv`.

**The movement list**: `logs/maturity-movements-2026-08.csv`. 19 up, 1 down (MUS, open discussion 3 to 2, on a restated false-information offence), 35 placed from unplaced, 84 newly assessed, 157 newly unplaced.

**Calls CC let stand but would like a second pair of eyes on:**

- KEN broadband strategy at 4, with no plan document held (the anchor asks for an adopted plan, funded).
- ETH statistics strategy at 1: the old strategy is cited as expired, but "no successor" is an absence of evidence, not a citation.
- SDN and SLE ID registration (88.8 % and 90 %) on the authorities' own figures, the population base unstated; stage 3 either way.
- ZAF revenue collection at 2 on VAT e-invoicing papers, when SARS eFiling payment has run for years: the base's evidence is thin, not the country.
- GHA access to information placed at 3 while the commission has fined 254 bodies, which arguably meets 4.
- ETH authentication 3 to 4 on 194m eKYC checks, with no PKI (the anchor allows an online verification API instead).
- NGA cloud strategy: `moved_by` records the latest-dated source (a GITEX article) rather than the cloud guidelines that crossed the anchor. F1's movement note should cite the source that crossed it.

**Calls CC changed while vetting**, each named in its commit message: bandwidth counts taken from rows held (AGO, GMB); population bases that differ (AGO registration); multi-tenant centres per Corpus's dataset (CPV, MRT); stage 1 contradicted by evidence elsewhere (NAM satellite); stages resting on another indicator's rows (AGO, SOM data protection); channels that are not the state's (CAF, ERI feedback portals); systems of another body or domain (LBY customs, KEN social protection, SSD education); a procurement taken for the thing (TCD AI strategy, TUN hubs); DPA operations not on record (GMB); survey fieldwork taken for results (UGA).

**Mapping gaps the drafters found**, for the next re-read (D4 re-verdicts but never re-maps): DZA's law 18-07 not mapped to data-protection readiness; MUS InfoHighway not mapped to the data exchange; NAM OneWeb service under bandwidth, not satellite; GIN's 2016 law's transfer rules not on cross-border transfers; SWZ Computer Crime Act under discourse, not cybersecurity legislation.
