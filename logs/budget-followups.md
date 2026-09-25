# Budget extraction — follow-ups found during the 2026-09-24 sprint

Work a sitting surfaced but did not settle. Each item names what to do. Strike an item in the commit that settles it.

- **Share with mixed stages.** GHA FY2024-26, SLE FY2025, MDG FY2024-25, LSO FY2024, BWA FY2024 and SWZ FY2024-25 have no domestic share, because some rows carry only a proposed figure (the Act does not print the line) or only an actual (own-source fund accounts). `budget_source.share` is right to refuse a mixed-stage sum. The maturity assessment's financial-sustainability measure must say what it shows for these years.
- **Partial lines swing the share.** `budget_source.share` counts partial lines at full value, so one large mixed programme moves a country's share: CPV FY2025 (CVE 5.43bn state-modernisation, 96.0%) and CMR FY2026 (XAF 146.7bn partial). Decide whether the figure of record is taken over whole lines, with partial reported beside it, in `documentation/indicator-financial-sustainability.md`.
- **NGA: lines under ₦250m were not scanned.** The 2026-09-25 sitting checked every line of ₦250m or more by hand and counted the rest in the log; a later sitting completes the scan below that floor.
- **NGA FY2026 appropriated figures cite the bill's records.** They are read from the April 2026 Act (Details), not yet catalogued; it is on `africa-acquire.csv`. When OSINT catalogues it, re-point the rows' `source_slug`.
- **NGA: add NASRDA at partial.** Rule settled 2026-09-25 in `documentation/budget-extract.md` → *Scope* (geospatial data body whole; space agency with mixed mandate partial). LBY and EGY already comply; NGA dropped NASRDA and must add it.
- **AGO FY2026 is still the migrated placeholder (9 rows).** OSINT holds only the 2026 *fundamentação* (a summary); the OGE 2026 volume is on `africa-acquire.csv`. Sit it when it lands.
