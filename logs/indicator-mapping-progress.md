---
type: log
title: Indicator mapping pass — progress and how to resume
---

# Mapping the country ledgers onto the indicator frame

*(Opened 2026-08-26. The decision record is `documentation/progress-report-redesign.md`; the drafting
conventions are `documentation/indicator-mapping-conventions.md` and this file amends neither. This is
only where the pass has got to and what the next session needs to know to carry it on.)*

**The state is on disk, not in this file.** A unit is done when `outputs/reports/{ISO}/indicators.csv`
exists. `ls outputs/reports/*/indicators.csv` is the authoritative count, and this note is a skim that
can go stale. The frame covers the 54 country units only — XAF, XSA and XWA keep the movement
document (`progress-report-redesign.md` §1) and are not in scope.

## Done

ERI and ZAF were the pilots. This pass has since added, in order: **GNB, AGO, BDI, BEN, BFA, BWA,
CAF** — 9 of 54, one commit each, all pushed.

Yields so far, as a sense of shape: 21 indicators from GNB's 25 ledger rows, 43 from BDI's 74, 52
from BWA's 107, 57 from BEN's 105, 64 from BFA's 131, 66 from AGO's 122, 43 from CAF's 92. Between
three quarters and nine tenths of ledger rows map; the rest are placeholders with no source, or real
instruments the frame has no question for (a telecoms statute, a broadcasting transition), and those
correctly stay on the ledger and out of the report.

## Remaining

45 country units: CIV, CMR, COD, COG, COM, CPV, DJI, DZA, EGY, ETH, GAB, GHA, GIN, GMB, GNQ, KEN,
LBR, LBY, LSO, MAR, MDG, MLI, MOZ, MRT, MUS, MWI, NAM, NER, NGA, RWA, SDN, SEN, SLE, SOM, SSD, STP,
SWZ, SYC, TCD, TGO, TUN, TZA, UGA, ZMB, ZWE.

## The loop, per unit

1. Read the ledger. Every field earns its place: `subject` says where the row was filed and **not**
   which indicator it answers, `movement` is the ledger's vocabulary and not this one, and `note`
   usually carries the qualification the prose needs.
2. Draft the rows and write `outputs/reports/{ISO}/indicators.csv` — columns
   `indicator_id, progress, summary, developments, row_ids`, CRLF, no BOM, ordered however you like
   (the renderer walks the frame, not the file).
3. From `scripts/.workroot`: `python scripts/report-render.py --unit {ISO} --check` — want checks I,
   L and M **(indicators)** all PASS. Then `python scripts/report-register-check.py --unit {ISO}` —
   want 0 register hits, 0 indicator cells outside band, check H 0.
4. Commit that one file and push.

**A `StaleCatalogue` error means the mirror has moved under you**: run
`python scripts/build-catalogue.py` from the workroot first. It happened three times in nine units,
so expect it rather than diagnosing it.

**Check L failing on `{ISO}-progress.md` and `{ISO}-status.md` is expected and gates nothing** — those
are the old documents, and the progress one is replaced the next time the renderer runs.

## What the checks actually catch, and what a drafting lint should test first

Running the two real checks per attempt is slow. Everything below can be tested locally before
writing the file, and every item on it was hit repeatedly during this pass:

- **Every sentence carrying a figure needs a citation in that same sentence.** Sentences split on
  `.` **and `;`** — a semicolon inside a link label splits the label away from its own target, which
  is how `200,000 biometric authentications a day;` came to read as uncited. Figures are 4+ digit
  runs, comma-grouped numbers, percentages and currency amounts; bare years are exempt.
- **Word bands**: summary 8–40, developments 25–200, counted after reducing `[label](target)` to
  `label`, so link text costs words and slugs do not.
- **Register**: no `unveiled`, `landed`, `rolled out`, `paves the way`; no `ecosystem`, `unlock`,
  `at scale`, `leapfrog`, `dematerialis`; no `binding constraint`, `it is worth noting`, `turns out
  to be`; no first person. The banned words appear naturally in official announcements, so watch the
  clauses you are quoting rather than the ones you wrote.
- **Slugs**: cite exactly as the ledger's `sources` field carries them, spaces, parentheses and all,
  and never a URL. Citing only slugs that appear on the mapped rows keeps check M clean by
  construction, because the ledger's own sources have already passed it.
- ***Mixed* needs a qualifying clause after a comma**, naming which instruments moved which way.
- **No-evidence rows are never written out**; an indicator absent from the file renders as
  *No evidence*, which is what makes the frame's gaps visible.

## Two judgement calls worth keeping consistent

**One row may serve several indicators, and should where it genuinely answers several** — but never
with the same sentence twice. Where the temptation is to repeat, the second indicator usually wants
a different fact from the same source: the instrument's passage under legislation, what it will
oblige under use, its cost under financing.

**A *Not held* row with no source is a placeholder and is not mapped**; one that carries a source is
a dated, cited statement that a thing is absent, and it is mapped. Most units carry a handful of the
first kind and they are the reason the mapped-row counts above are not higher.
