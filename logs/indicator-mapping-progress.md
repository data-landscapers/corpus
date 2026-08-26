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
CAF, CIV, CMR, COD, COG** — 13 of 54, one commit each, all pushed.

Yields so far, as a sense of shape: 21 indicators from GNB's 25 ledger rows, 43 from BDI's 74, 52
from BWA's 107, 57 from BEN's 105, 64 from BFA's 131, 66 from AGO's 122, 43 from CAF's 92, 92 from
CIV's 167, 73 from CMR's 121, 67 from COD's 123, 52 from COG's 103. Between three quarters and nine tenths of ledger rows map; the rest are placeholders with
no source, or real instruments the frame has no question for (a telecoms statute, a broadcasting
transition), and those correctly stay on the ledger and out of the report.

## Remaining

41 country units: COM, CPV, DJI, DZA, EGY, ETH, GAB, GHA, GIN, GMB, GNQ, KEN, LBR, LBY, LSO, MAR,
MDG, MLI, MOZ, MRT, MUS, MWI, NAM, NER, NGA, RWA, SDN, SEN, SLE, SOM, SSD, STP, SWZ, SYC, TCD, TGO,
TUN, TZA, UGA, ZMB, ZWE.

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

## What CIV added, 2026-08-26

The thickest ledger mapped so far — 167 rows, 92 indicators — settled two things.

**The pre-lint the section above asks for now exists: `scripts/lint-indicators-draft.py`.** It reads
a draft and the unit's ledger and applies every rule in that list plus the vocabulary, the frame
membership and the placeholder rule, in about a second and without a render. Run it on the draft
before the file goes into `outputs/`. On this unit it caught the semicolon-inside-a-link-label trap
on its first run and a bare figure on its second, and the two real checks then passed first time —
which is the point of it, because on a 92-indicator unit a failing round trip through the renderer
costs several minutes. It does not replace the real checks: it cannot see the catalogue, so check M
still has work to do.

**Three uses of one ledger row is the ceiling, and each use must be a different fact.** One row here
reaches three, the monetary union's digital financial services report, read once for account uptake,
once for what the central bank supervises and once for the country's share of union transaction
value. Two cells were rewritten to get there: the first draft had the regional instant-payment
mandate opening two different indicators with the same sentence. The test is not a count but a
reading — if the second cell's opening clause could be pasted into the first, that indicator has no
evidence of its own and should say so. Counting uses mechanically is still worth doing, as the prompt
to go and reread them.

## What CMR added, 2026-08-26

**Some units carry unsourced *Not held* placeholders and some do not, and the difference is large.**
Every one of CIV's ten Not-held rows carried a source and all ten were mapped; seven of CMR's carried
none and none could be. Those seven are the whole of CMR's unmapped residue — there is no ledger row
here that the frame simply has no question for. Check the placeholders first: it tells you in one
pass how much of a ledger is mappable, and `lint-indicators-draft.py` refuses the mapping outright
rather than letting it reach check I.

**The register's first-person test fires on place names.** `Limbe I` is a real council and reads to
the check as the first-person pronoun, because the pattern is case-sensitive and unanchored to
context. It is not a bug worth changing — the same case-sensitivity is what stops `US$40m` firing —
so the drafting move is to name the place another way. Expect the same on any `Region I`, `Phase II`
or `Zone I` a source uses.

## What COD added, 2026-08-27

**Check L can fail on the old progress document and still gate nothing.** COD's `COD-progress.md`
carries four unwritten narrative blocks, so `--check` reports `check L: FAIL` on a unit whose three
indicator checks all pass. That document is replaced the next time the renderer runs and the mapping
pass does not touch it. Read the indicator halves — `check I/L/M (indicators)` — and treat a check-L
failure naming only `{ISO}-progress.md` or `{ISO}-status.md` as noise, which the loop above already
says and which this is the first unit to actually demonstrate.

**Fold a stray row into an existing indicator rather than minting one for it.** COD's Mbororo herder
identification is a provincial operation on a named population and the frame has no question shaped
like that. Writing `dpi.id--registration-of-a-named-population` would have been the natural mistake;
the pre-lint refused it against the frame, and the row belongs in
`dpi.id--registration-of-entire-population` as a second development. **The frame is not extended by a
mapping pass** — an indicator is added by editing `lookups/indicators.csv`, which is a decision about
all fifty-four countries and not about one row.
