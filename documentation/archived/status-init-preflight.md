---
type: doc
title: STATUS-INIT pre-flight
last_reviewed: 2026-08-15
---

# STATUS-INIT pre-flight

*(Written 2026-08-15, before the first `status-init` run. Review of `STATUS-INIT.md` against the code and data that actually exist on this machine. Three items had to be settled before the first country; the rest were cheap then and expensive 54 times.)*

**All of it is done, and the run is clear to start** *(2026-08-15)*. The three blockers are resolved — one of them inverted on Bill's ruling into a new BUILD stage — and both of the cheaper items with them. What remains is the single design question at the foot of this file, which needs no action before the first country.

## What is already right

The inputs are all present and the numbers hold up.

`prep/africa-dpi-data.csv` (17 MB, 24,872 rows — 460 per country) and `prep/status-indicators-africa-dpi.csv` (453 indicators) are in place, gitignored as intended.
`outputs/non-state-finance/all-nonstate.csv` is there, 1,178 distinct URLs, **every one of them in the published catalogue** — so the finance half of the extraction cites nothing the base does not hold.
The workroot junctions `wiki/`, `raw/` and `lookups/` into OSINT and the index is Corpus's own, rebuilt from `raw/` and `wiki/`; it is fresh (built 2026-08-14 19:49, newest `raw/` file 2026-08-12), so no rebuild is owed.
`documentation/status-outline.md` carries ten Level-1 chapters and 38 Level-2 sub-sections — 37 once `finance.budget` is suspended, exactly as the file says.
Selection on `place: {ISO3}` frontmatter resolves cleanly: **396 of 396** intersection files matched, across 55 units (53 countries — Eritrea has none — plus XEA and XWA).
The tree is clean and nothing is unpushed. No new items are owed to OSINT.

The site renderer will cope with the new shape. `render.py` falls back to frontmatter `title:` when a document has no H1, and HTML comments pass through to HTML unseen, so `<!-- infra.connect -->` is invisible to a reader and still machine-mappable.

## The three blockers — all resolved

### 1. BUILD overwrites the output — *resolved 2026-08-15, and inverted*

`report-render.py --render --doc status` regenerates `outputs/reports/{ISO3}/{ISO3}-status.md` from `ledger.csv`, and `BUILD.md` step 4 mandates `--doc all` for every unit touched.
So the next BUILD run destroys every status-init report written before it, silently and completely — it is a normal successful render as far as the script is concerned.
BUILD is run by hand rather than on a schedule, so nothing fires unattended, but the instruction that causes it is standing and the loss is total.

**Bill's ruling turned this the right way up** *(2026-08-15)*: the answer is not a guard on a render that should not happen, it is that **BUILD maintains the baseline**. Once a unit is initialised, each new source is asked whether it changes what a status sub-section can say, and the section is revised where it does — which is the successor `STATUS-INIT.md` names and leaves undesigned. Units not yet initialised are not part of it; their status reports stay ledger renders until initialisation reaches them.

Implemented as a narrowing of the document set rather than a branch in the renderer. `report-render.py` gained `initialised()` and `issues()`: an initialised unit no longer issues a rendered status report, so `--doc all` renders its monthly and progress report and prints the reason for the third. That is the same shape as the existing region rule, so BUILD stage 4 and `rebuild.py --reports` needed no change and no caller has to know which units are which. `render()` carries the same refusal defensively, and check J now skips the baseline — it asks whether a document is behind the ledger it is rendered from, and the baseline is not rendered from that ledger.

`BUILD.md` → *Maintaining the status baseline* has the stage. Verified: all 57 units re-render with zero churn, and checks G, I, J, L and M pass on NGA, ZAF, KEN and XWA.

### 2. Check G fails every status-init report — *resolved 2026-08-15*

`check()` scans **every** `.md` in `outputs/reports/{ISO3}/` and requires each URL to resolve through `outputs/catalogue/raw-catalogue.csv`.
The status report cites the AfDB dataset, which the vault does not hold. Measured: of NGA's 296 distinct DPI-dataset URLs, **16 are in the catalogue**; across all 54 countries it is 668 of 9,685, about 7%.
So a correct status report fails check G with roughly 250 NOT HELD links, and takes the unit's BUILD down with it.

`STATUS-INIT.md` anticipates this — check A widens the set to the three bodies of evidence the process read — but nothing in the code knew that.
**Fixed**: `scripts/status_lib.py` builds the three sets once and both checks use it, so they cannot drift into disagreeing about whether a link is real. `report-render.py` check G applies the widened set per file, keyed on the document actually being a baseline — the monthly and the progress report in the same folder keep the catalogue-only test, because they may cite nothing else. Verified: the status document reports `(baseline set)` and its siblings do not.

**Bill sharpened the acquire rule with it** *(2026-08-15)*: the test is whether a source is **held**, not which intermediary carried it. A cited URL the catalogue does not resolve, dated 2024 or later, owes an acquire line; before 2024 it owes nothing; and a held source raises nothing whatever its route. That makes the acquire list derivable rather than remembered — the held/not-held split is set membership, so the checker reports the candidates.

One correction to `STATUS-INIT.md` goes with it. Check A says every URL must appear "in `index/`", and the report layer no longer resolves through the index — `slug_urls()` reads the published catalogue.
The two sets are near-identical (9,443 against 9,404) and the 39 extra are wiki concept pages carrying a `url:`, which are not sources and should not resolve. The catalogue is the right set and the sentence should name it.

### 3. There is no verification tooling — *resolved 2026-08-15*

Checks A, D, E, F and G are mechanical and checks B, C and I are close to it, but there is no `status-check.py` and nothing else in `scripts/` covers them.
Check A in particular cannot be done by reading: a URL synthesised from a remembered pattern is indistinguishable from a real one by inspection, which is the entire reason the check exists.
`STATUS-INIT.md` also requires it re-run after every edit pass rather than once at the end, which settles it — a check run that often has to be a script.

**Fixed**: `scripts/status-check.py --unit {ISO3}` implements A to G and I, plus a frontmatter-consistency check — a report that misstates its own source count is wrong in the place a reader is least likely to look. H prints the opening sentences under `--openings` and says plainly that it needs a reader rather than pretending to judge them. C is reported rather than gated, because no regex separates a law's section number from a measurement.

Exercised against a synthetic baseline carrying one planted defect per check: all were caught, and the two legitimate *not established* sub-sections — one plain dated sentence, no link, by design — correctly did not trip check B.

## Worth doing before the first country, not after the tenth

**A scoping helper — *done 2026-08-15*.** `scripts/status-scope.py {ISO3}` prints stage 0 and writes the two non-wiki extraction cuts to `prep/scope/{ISO3}/`, which is gitignored like the CSVs they come from. The parent gets the map — name, region, hub size and `last_reviewed`, the hub's `topics:`, its `## Active topics` and `## Record not held` extracted by line range, and the intersection list with sizes and topic spans. The agents get the mass: Rwanda's DPI cut alone is 140KB, which has no business in the context that assembles the report.
It removes the single largest failure the design names — an agent constructing an intersection filename instead of selecting on frontmatter — and reports how many files do not match the country slug, so the risk is visible rather than assumed. Verified against the awkward cases: CIV (all 11 under `civ--`), COM (mixed `com--` and `comoros--`), ERI (none of its own, regional only) and NGA (14, largest file 54.6KB).

**The country page's status stat and its blurb — *done 2026-08-15*.** `country.py` read `ledger_rows` from the status report's frontmatter; STATUS-INIT drops it, so the stat would have degraded to an em dash on every country page as each went through — quietly, because the read already had a fallback and would not have failed.
Fixed at the cause: the *Systems & instruments* tile now counts `ledger.csv` directly, excluding measures exactly as the renderer does, because the quantity is a property of the ledger and the ledger survives initialisation. The per-report card shows a baseline's own scale — sections and sources — instead of a ledger count that would describe the wrong document, and the blurb switches from *"a summary of all known systems and instruments"* to what a baseline actually is. Verified behaviour-preserving today: RWA's tile reads 89 before and after.
It degrades rather than crashes, so this will not stop anything — it will just quietly empty a number on 54 pages. Either the frontmatter keeps a count `country.py` can use, or `country.py` is repointed at `sources_cited`.
The blurb needs changing either way: *"A summary of the status of all known systems and instruments"* describes the ledger table, not a narrative.

## Two stale figures in `STATUS-INIT.md`

Under Inputs: *"It indexes 10,171 files, of which 9,404 carry a URL."* The index now holds **12,588** files over `raw/` and `wiki/`, of which 9,443 carry a URL; **9,404 is the catalogue count**, not the index's.
That matters more than a number being out of date, because the sentence points an extraction agent at the wrong file — and the index now contains wiki pages, a few of which carry a `url:` and would resolve as though they were sources.

Under Inputs, on intersections: *"Every country but Eritrea has at least four."* Mauritania has two and Lesotho three, so a very thin country is a real outcome rather than a sign the selection went wrong — worth saying, because the run should not go looking for files that are not there. **Corrected in `STATUS-INIT.md`.** *(The median of seven, which this file first reported as stale, is right; that figure was computed here over 55 units including the two regions and was wrong.)*

## One question for Bill, needing no action today

A status report will cite on the order of 250 URLs per country that the vault does not hold, so the site publishes provenance links the catalogue cannot back.
`STATUS-INIT.md` rules that correct and gives the reason — the baseline sits outside the collection perimeter, and there is no intention of ingesting ten years of material to bring it inside.
It is still the first time the site links outside its own evidence base, and the catalogue is what a reader is told the provenance runs through. Worth being a decision rather than a consequence.
