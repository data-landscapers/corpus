---
type: doc
title: STATUS-INIT pre-flight
last_reviewed: 2026-08-15
---

# STATUS-INIT pre-flight

*(Written 2026-08-15, before the first `status-init` run. Review of `STATUS-INIT.md` against the code and data that actually exist on this machine. Three items must be settled before the first country; the rest are cheap now and expensive 54 times.)*

## What is already right

The inputs are all present and the numbers hold up.

`prep/africa-dpi-data.csv` (17 MB, 24,872 rows — 460 per country) and `prep/status-indicators-africa-dpi.csv` (453 indicators) are in place, gitignored as intended.
`outputs/non-state-finance/all-nonstate.csv` is there, 1,178 distinct URLs, **every one of them in the published catalogue** — so the finance half of the extraction cites nothing the base does not hold.
The workroot junctions `wiki/`, `raw/` and `lookups/` into OSINT and the index is Corpus's own, rebuilt from `raw/` and `wiki/`; it is fresh (built 2026-08-14 19:49, newest `raw/` file 2026-08-12), so no rebuild is owed.
`documentation/status-outline.md` carries ten Level-1 chapters and 38 Level-2 sub-sections — 37 once `finance.budget` is suspended, exactly as the file says.
Selection on `place: {ISO3}` frontmatter resolves cleanly: **396 of 396** intersection files matched, across 55 units (53 countries — Eritrea has none — plus XEA and XWA).
The tree is clean and nothing is unpushed. No new items are owed to OSINT.

The site renderer will cope with the new shape. `render.py` falls back to frontmatter `title:` when a document has no H1, and HTML comments pass through to HTML unseen, so `<!-- infra.connect -->` is invisible to a reader and still machine-mappable.

## The three blockers

### 1. BUILD overwrites the output

`report-render.py --render --doc status` regenerates `outputs/reports/{ISO3}/{ISO3}-status.md` from `ledger.csv`, and `BUILD.md` step 4 mandates `--doc all` for every unit touched.
So the next BUILD run destroys every status-init report written before it, silently and completely — it is a normal successful render as far as the script is concerned.
BUILD is run by hand rather than on a schedule, so nothing fires unattended, but the instruction that causes it is standing and the loss is total.

The cheapest safe guard is in `render()`: read the existing file's frontmatter and refuse to write, with a message, where `built_by: STATUS-INIT`.
That keeps `--doc all` as a habit and makes the refusal visible at the point of the mistake rather than at the next reader.

### 2. Check G fails every status-init report

`check()` scans **every** `.md` in `outputs/reports/{ISO3}/` and requires each URL to resolve through `outputs/catalogue/raw-catalogue.csv`.
The status report cites the AfDB dataset, which the vault does not hold. Measured: of NGA's 296 distinct DPI-dataset URLs, **16 are in the catalogue**; across all 54 countries it is 668 of 9,685, about 7%.
So a correct status report fails check G with roughly 250 NOT HELD links, and takes the unit's BUILD down with it.

`STATUS-INIT.md` anticipates this — check A widens the set to the three bodies of evidence the process read — but nothing in the code knows that.
The fix is one held-set, built once and used by both: catalogue URLs, plus `Source urls` from `africa-dpi-data.csv`, plus `url` from `all-nonstate.csv`, applied to a file whose frontmatter says `built_by: STATUS-INIT`.

One correction to `STATUS-INIT.md` goes with it. Check A says every URL must appear "in `index/`", and the report layer no longer resolves through the index — `slug_urls()` reads the published catalogue.
The two sets are near-identical (9,443 against 9,404) and the 39 extra are wiki concept pages carrying a `url:`, which are not sources and should not resolve. The catalogue is the right set and the sentence should name it.

### 3. There is no verification tooling

Checks A, D, E, F and G are mechanical and checks B, C and I are close to it, but there is no `status-check.py` and nothing else in `scripts/` covers them.
Check A in particular cannot be done by reading: a URL synthesised from a remembered pattern is indistinguishable from a real one by inspection, which is the entire reason the check exists.
`STATUS-INIT.md` also requires it re-run after every edit pass rather than once at the end, which settles it — a check run that often has to be a script.

Without this the first run has no way to pass its own gate, and a run that fails A, B or G is not issued.

## Worth doing before the first country, not after the tenth

**A scoping helper.** `scripts/status-scope.py {ISO3}` emitting stage 0 and the two non-wiki extraction inputs: name and region from `countries.csv`, the hub's `last_reviewed`, the intersection file list selected on `place:` frontmatter, the country's 460 DPI rows cut to the five columns that matter, and its finance rows.
This is deterministic work being done by a model 54 times, and it removes the single largest failure the design names — an agent constructing an intersection filename instead of selecting on frontmatter. Seven countries use a prefix that is not the country name, and two carry files under two prefixes.

**The country page's status stat and its blurb.** `country.py` reads `ledger_rows` from the status report's frontmatter (lines 309 and 622); STATUS-INIT drops it, so the stat degrades to an em dash on every country page as each country goes through.
It degrades rather than crashes, so this will not stop anything — it will just quietly empty a number on 54 pages. Either the frontmatter keeps a count `country.py` can use, or `country.py` is repointed at `sources_cited`.
The blurb needs changing either way: *"A summary of the status of all known systems and instruments"* describes the ledger table, not a narrative.

## Two stale figures in `STATUS-INIT.md`

Under Inputs: *"It indexes 10,171 files, of which 9,404 carry a URL."* The index now holds **12,588** files over `raw/` and `wiki/`, of which 9,443 carry a URL; **9,404 is the catalogue count**, not the index's.
That matters more than a number being out of date, because the sentence points an extraction agent at the wrong file — and the index now contains wiki pages, a few of which carry a `url:` and would resolve as though they were sources.

Under Inputs, on intersections: *"the median is seven."* It is now 8, and ten countries carry 11 or more — NGA 14, GHA 13, KEN 13, MAR 13, AGO 12, ZAF 12, UGA 12, DZA 11, CIV 11, SEN 11.
Cosmetic; it only sizes the fan-out.

## One question for Bill, needing no action today

A status report will cite on the order of 250 URLs per country that the vault does not hold, so the site publishes provenance links the catalogue cannot back.
`STATUS-INIT.md` rules that correct and gives the reason — the baseline sits outside the collection perimeter, and there is no intention of ingesting ten years of material to bring it inside.
It is still the first time the site links outside its own evidence base, and the catalogue is what a reader is told the provenance runs through. Worth being a decision rather than a consequence.
