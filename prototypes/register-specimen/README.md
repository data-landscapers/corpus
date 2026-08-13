---
type: doc
title: Register specimen — South Africa status report
last_reviewed: 2026-08-13
---

# Register specimen — ZAF status report

*(A specimen, for developing the Corpus editorial register (`MIGRATION-REPORT-LAYER.md` → v0.2) dialectically. Not authoritative output.)*

`ZAF-status.md` is a South Africa status report built by the ported toolchain from the frozen OSINT `raw/` snapshot: the tables are script-rendered from `outputs/reports/ZAF/ledger.csv` (92 status rows, 11 *Not held*); the seven narrative blocks are authored under the light-touch register.

What the light touch adds over the OSINT (register-neutral) original, all of it checkable against the rows:

- **Selection through the lens.** Each section foregrounds who owns the infrastructure, who holds the data and under whose jurisdiction, and where dependency sits — using the same dated, cited facts.
- **A few restrained connecting sentences**, one per section at most: e.g. the SITA agency "the state relies on to build its own systems is one of the reform's slowest legs"; the breach-penalty ceiling that "sits below the average cost of the harm it sanctions"; PayShap's "deliberately domestic ownership of the country's core payment rail".
- **No new figures, no charge, no thesis.** Every number is one the OSINT original already carried and cited; the editorial hand is in emphasis and connection, not in adjectives.

Verification: `report-render.py --check` → check G (every link held in `index/`) PASS, check I (vocabulary) PASS. Full G–K + register-check is a Phase 2c step.

Compare against the OSINT original to see the delta: `C:\OSINT\outputs\reports\ZAF\ZAF-status.md` (read-only).
