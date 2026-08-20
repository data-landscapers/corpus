---
type: doc
title: Known defects in prep/africa-dpi-data.csv
last_reviewed: 2026-08-20
---

# Known defects in `prep/africa-dpi-data.csv`

*(**Moved here from the OSINT notes queue on 2026-08-20**, where it had been sitting as note 11 and part of note 15 since 2026-08-15. It was never OSINT's: `prep/africa-dpi-data.csv` is a **Corpus** file holding a third-party dataset, OSINT keeps no copy, and there was nothing there to repair. Recording it here is what the misfiling should have been from the start — `STATUS-INIT` reads this file on every country, so the defects want stating where the next run will meet them.)*

**This is not a defect list to fix.** The data is a third party's and Corpus does not correct it; a correction would be an unsourced claim wearing a dataset's authority. What this file does is tell a `STATUS-INIT` run what it is looking at, so a run neither trusts a bad cell nor spends a second country rediscovering the same fault. Confirmed across **eight countries** — NGA, SEN, TZA, CIV, MAR, EGY, SWZ and one more — which is what makes them structural rather than incidental.

## The `govtech-*` family — 149 rows a country, one URL

**Every `govtech-*` row resolves to the GTMI 2025 update landing page**, not to anything country-specific, and the `Comments` column repeats the same boilerplate — *"Selected data from the World Bank GovTech Maturity Index &lt;row-id&gt;"* — rather than reasoning about the country. That is a third of the dataset's rows for a country yielding facts that can be linked only to a page which does not itself state them. In CIV's cut the boilerplate is misspelled in the source as *"GovTech Matutiy Index"*.

Under `STATUS-INIT`'s check A — every link is held and resolves — and check B — every claim is linked — a `govtech-*` value can be used only where the run is content to cite the landing page for a fact the landing page does not carry. **The standing treatment is not to.**

### Three cell-level defects beneath it

- **Concatenated answers.** A cell holds two or three mutually exclusive answers run together into one value, most often *"Yes (via separate interfaces) Yes (via Government Service Bus)"*. Recurring ids: `customs-8.8`, `debt-14.6`, `procure-12.6`, `financial-5.13`, `hr-9.7`, `taxmanage-7.7`, `socialinsure-11.9`, `taxportal-20.2`, `taxportal-20.3` (three answers), `startup-48.5`. Counts run four to eight cells a country.
- **Repeated ids carrying conflicting values.** A single sub-indicator id appears on several rows with different answers, with nothing in the row to say which is the country's reading. Recurring: `govtech-socialinsure-11.1`, `govtech-skills-45.5`, `govtech-publicinnov-46.4`, `govtech-publicinnov-47.5`.
- **Outright self-contradiction.** On MAR, `govtech-skills-45.5` and `govtech-publicinnov-46.4` each appear as both *"Yes"* and *"No"* inside the one country's cut. Both were marked borderline and neither reached `MAR-status.md`, which is the correct outcome: `STATUS-INIT` → *When the evidence is borderline* rules that a source which merely disagrees with itself settles nothing.

**The same six ids have now recurred on five countries**, so a run meeting them should recognise rather than re-investigate them.

## The sourceless negatives — and several of them are false

*(Found on the MAR run, 2026-08-15; the third finding of what was note 15.)*

**Thirty-eight of Morocco's 462 rows carry an empty `Source urls`, and 24 of those state a flat "No"** — all in the `reg-*` families. Those 24 are exactly the absences a baseline most wants to state: no data-protection law, no digital-ID law, no right-to-information instrument, no cloud or CIIP framework, no payments law, no fintech sandbox or open banking, no e-government or open-data policy, no AI strategy, no broadband, spectrum or infrastructure-sharing instrument. None could reach `MAR-status.md`, because a claim with no link fails check B.

**What makes this worse than a gap is that the wiki contradicts several of them outright.** `reg-id-dplaw` reads "No" against **loi 09-08 of 2009**, which the base holds and the report itself cites; `reg-egov-strategy` reads "No" against **Digital Morocco 2030**; `reg-connect-spectrum` reads "No" against the **ANRT 5G spectrum tender of July 2025**.

**So a sourceless negative in this dataset is not evidence of absence and must never be read as one.** Nothing in the cut distinguishes the true absences from the false ones, and a false negative that reaches a baseline is a published statement that a country has no data-protection law when it has had one since 2009. Where the dataset is the only thing saying a country lacks an instrument, the finding is ***Not held***, with a `gaps.csv` line — not an absence.

## What this costs, and why the dataset is still used

The `govtech-*` third is largely unusable and the sourceless negatives are unusable in the direction that matters most. What remains — the `iiag-*`, `odin-*`, `stats-*`, `rural-*` families and the sourced `reg-*` rows — carries real, citable, country-specific evidence, and `STATUS-INIT` stage 0's three-agent split (`STATUS-INIT.md` step 5) already partitions the families so a run reads each once. The dataset earns its place on the sourced rows; this file exists so that the rest is skipped knowingly rather than trusted by default.
