# CC review — topic reports, the `index/` correction and the wiki junction (2026-08-14)

*(Written from Claude Code on Bill's machine, reviewing Cowork's work of this afternoon. Bill's process: Cowork designs, CC reviews operationally. Commits `44c76d5..8d1317f` plus the whole of `documentation/topic-reports.md`, which Bill flagged as complete; `STATUS-INIT.md` deliberately not reviewed, at his instruction, until tomorrow.)*

*(**Written as findings, then actioned on Bill's instruction** — "would it be easier for you to fix this mess" — in commits `a977616..c31e06d`. The findings below stand as written, unedited; **What was done** at the end says what happened to each and what is left. Two things were Bill's to decide and were put to him: the topic progress report carries movement tables and no prose, and the `outputs/places/` rename is deferred.)*

Everything below was checked against the code and the current `outputs/` rather than read off the documents. The counts are reproducible from the repo as it stands at `8d1317f`.

## Blockers in the drafted stage 6

**1. The progress report has no per-subject narrative block, so step 1 cannot be executed as written.**

The monthly keys its blocks per subject — `dpi--dpi-pay`, `infrastructure--infra-connect` — and the progress report does not. Across all 57 units the progress keys are `summary`, `infrastructure`, `dpi`, `governance`, `ai-tech`, `inclusion`, `finance` and `gaps`, plus `institutions`, `instruments`, `systems`, `coordination` and `capacity` for the three regions. One block per **section**, written at the end of it, covering every subject in that section: KEN's `infrastructure` block runs across cyber-security, satellite broadband and Konza in a single piece of prose.

So "the subject's movement table together with its block" has no block to take. Lifting the section block into `dpi-pay-progress.md` would carry identity, exchange and registry prose into a payments document — the opposite of what the lift is for. The movement tables *are* per subject (`### Connectivity`, `### Data Storage`, …), so the tables half of the step works unchanged.

Three ways out, and the choice is Bill's: the topic progress report carries **tables only** and no prose; or the country progress report is restructured to per-subject blocks first, which is a change to the layer and to every existing progress document; or the topic progress report is dropped and topics issue a monthly only. The first is the one that costs nothing and loses least, since a movement table is already the substance of that document.

**2. `render.py` cannot render a hyphenated slug, and would overwrite one topic document with the other.**

`parse_name()` (`scripts/render.py:98`) is `path.stem.split("-")` returning `parts[0], parts[1]`. `dpi-pay-monthly.md` gives unit `dpi`, kind `pay`. `dpi-pay-progress.md` gives **the same** unit and the same kind. `stem_html` is `f"{unit}-{kind}"`, so both documents write `site/reports/dpi/dpi-pay.html` and the second render replaces the first, silently. Every one of the 38 slugs is hyphenated once the dot is substituted, so this is the whole tree, not an edge case.

The output location is hardcoded on the same lines — `rel_html = f"reports/{unit}/{stem_html}"`, `rel_pdf` likewise, and `--out` defaults to `SITE / "reports"` — so the permalink a topic document would advertise is `/reports/dpi/dpi-pay.html`. The 2026-08-14 BUILD review recorded `parse_name()` as fine and needing no change; that was true of `AGO-monthly.md` and stops being true here.

This is check item 1's answer, and it is larger than the item anticipates: not "does it derive the output location from the parent directory" but "the filename grammar it parses has no room for a multi-word unit".

**3. The taxonomy carries 38 Level-2 slugs, not 39, so the arithmetic is off.**

`outputs/vocab/taxonomy.md` holds 38 across the ten Level-1 categories; its own header says "~36", which is stale in the other direction. All 38 appear in ledgers, and all 38 have at least one narrative block in at least one monthly, so no slug is empty.

38 × 2 = **76** documents, taking the render set from 165 to **241**. The doc says 39, 78 and 243 at lines 23 and 85.

**4. The block key is not derivable from the subject — section overrides are live in today's data.**

`ledger.csv` carries a per-row `section` column, and `report-render.py:945` checks only that its value is a *known* section, never that it agrees with the section map. In `outputs/reports/` as it stands, **170 rows across BEN, ETH, GNB, NGA and ZAF** sit in a section other than the one `report-country-sections.csv` assigns their subject — BEN 35, ETH 23, GNB 2, NGA 69, ZAF 8.

That has a second consequence the drafted step does not allow for: **39 (unit, subject) pairs span more than one section**, BEN's `gov.regional` across four of them. A place can therefore contribute several blocks for one subject, under several different keys. BEN's monthly carries `dpi--gov-policy`, `dpi--gov-regional` and `dpi--gov-standards` — all three subjects governance-mapped, all three rendered under DPI.

So step 1's "the section is the one the place's section map assigns that subject, so the key is derived, never guessed" is false against current data. The collector has to read the section off the row, or off the source document's own markers, and the stage has to say what it does when a place offers more than one block for the subject — concatenate under the one place heading, most likely, but it should say so.

## The wiki junction will break the index freshness check

Not part of the topic design, but it is in the same set of commits and it will stop a build.

`vault_lib.index_state()` calls the index stale when the file count under `INDEX_ROOTS` differs from `meta.json`. Today the Corpus workroot exposes `raw/` alone, walking **10,178** files — and `C:\OSINT\index\meta.json` records exactly **10,178**, so Corpus reads *fresh* and every render resolves its citations.

Add the `wiki` junction that `26943d9` puts in `setup_workroot()` and Corpus walks 10,178 + 2,410 = **12,588** against a meta of 10,178. Stale. `load_index()` → `ensure_fresh()` → `build_index()` → **`ForeignIndex` raised**, on every render, every `--check`, every catalogue build — correctly, because Corpus must not rebuild OSINT's index, but fatally.

Rebuilding the index in an OSINT session does not repair it. OSINT walks **13,580** across all eight roots, because it also holds `new/`, `new-budget/`, `budget-archive/`, `reviews/`, `sweep/` and `queries/`, none of which the workroot junctions. Corpus would then see 12,588 against a meta of 13,580 and raise again. The two views can only agree when the workroot exposes **exactly** the roots `INDEX_ROOTS` names — which is six more lines in `setup_workroot()`, and consistent with Bill's ruling of today that Corpus may read anything in OSINT.

The alternative, if those trees are not wanted in the workroot, is that Corpus's consumers stop calling the auto-refreshing path: `load_index(auto=False)` with an explicit staleness *report* rather than a rebuild attempt. That is the larger change and it weakens the freshness guarantee `_assert_own_index()`'s docstring rests on, so the junctions look right.

**Worth knowing either way:** the fix has to land before or with the junction, not after. The junction does not exist on disk yet — `setup_workroot()` creates it on the next `rebuild.py` run of any kind, since it runs unconditionally in `main()`. So the first BUILD or RENDER after that pull is the one that fails.

### What that arithmetic also exposes

`meta.json` records 10,178 files over roots that include `wiki/`, `sweep/` and `budget-archive/`, built at 2026-08-13T11:39 — and a walk of those roots **in OSINT** counts 13,580. An index built in OSINT could not have produced that number. It was built from Corpus's workroot, where only `raw/` resolves, and written back into `C:\OSINT\index\` — the boundary violation `_assert_own_index()` was added on 2026-08-14 to prevent, committed to disk the day before the guard existed. `files.jsonl` and `links.jsonl` carry that build's timestamp.

OSINT's index is therefore missing all 2,410 `wiki/` files, 632 `budget-archive/`, 310 `sweep/`, and the rest. Corpus is unaffected — `slug_urls()` reads only rows with `folder == "raw"` — but anything in OSINT that asks the index about the wiki is reading a hole. Recorded as `logs/notes-for-osint.md` note 8; the repair is one rebuild in an OSINT session.

## The other two "For CC to check" items

**Item 2 — do the unit documents share one period?** Today, yes: all 54 monthlies read `2026-07-01 to 2026-08-14` and all 57 progress reports `2025-08-01 to 2026-08-14`. But the period is a render-time window and `rebuild.py --reports` takes a unit list, so any partial re-render leaves units on different windows until the next full pass. The clause is live rather than dead weight — keep it.

**Item 4 — should the tree rename go first?** Yes, and finding 2 is the argument that settles it. `render.py` has to be opened for topics regardless of the rename, and its path constants are the same lines the rename touches. Doing the rename first means writing the topic stage once, against final paths, and touching `render.py` once.

## What checks out

The `index/` correction is accurate on every claim I could test. OSINT's `.gitignore` describes the index exactly as quoted, `build_index()` does take `db=False` by default, `_assert_own_index()` and `ForeignIndex` exist and raise rather than degrade, `ensure_fresh()` really does route a stale read into that raise, and on disk `files.jsonl`/`links.jsonl` are dated 2026-08-13 against `vault.db`'s 2026-08-10. No "index/ must be committed" statement survives anywhere in `documentation/`, `BUILD.md` or `RENDER.md`.

The rest of the topic design holds up against the data. There are 57 units and exactly three regions, `XAF`, `XSA`, `XWA`, and `report-render.py`'s region profile does issue the progress report alone. `outputs/reports/` holds 165 markdown documents and no strays, so the coverage assertion's `find`-against-glob comparison is sound as it stands and stays sound with `upstream/topics/` added. The RENDER draft's replacement target, `## Not in this runbook — Topics`, is really there at `RENDER.md:130`. Step 1's mirror does carry a new `outputs/` tree into `upstream/` for free, as line 115 says. And `rebuild.py --reports all` really would hand a ledger-less topic directory to `report-render.py`, which is why the tree has to be separate — line 51 is right about the invariant and right that `country.py` is safe.

## Two wording points

**The standing constraint's mechanism is wrong, though its requirement is right.** It says CORPUS reads OSINT's *committed* `HEAD` for `raw/`, `lookups/` and `wiki/`. It does not: every current reader goes through the `.workroot` junctions into OSINT's **working tree**, exactly as it does for `index/`. The only script that reads `HEAD` is `pull.py`, and what it reads is OSINT's `outputs/`, which the migration retired. Those three trees do still need to stay committed — for recoverability, for the mirror, and because an uncommitted working tree is the one state a rebuild cannot recover — but not for the reason given, and the paragraph now draws a distinction between `index/` and the other three that the code does not make.

**Note 4's correction could go one step further.** Corpus never opens `vault.db` at all: `build_db()` is the only reference to it in `scripts/`, and it writes. Slug resolution runs `load_index()` → `files.jsonl`, which is rebuilt from scratch, so a deleted `raw/` record drops out of Corpus's read path at the next rebuild and cannot reach a Corpus citation. What the dangling slug endangers is a link **already published** in a downloaded PDF, which makes (a) a `raw/`-deletion policy question rather than an index one, and makes (b) sharper still: the DB is not on anyone's read path in Corpus, which is a strong argument that it has stopped earning its keep.

## What was done

Bill's instruction on reading the findings was to fix them. Everything below is committed; the two decisions were put to him rather than guessed.

| | Finding | Outcome |
|---|---|---|
| 1 | Progress report has no per-subject block | **Decided by Bill:** the topic progress report carries movement tables and no prose. `topic-reports.md` rewritten to say so, in the design section and in step 1. |
| 2 | `render.py` cannot parse a hyphenated unit | **Fixed** (`a843fba`). `parse_name()` splits from the right on a known kind; a new `tree_of()` takes the output tree from the source path, so `outputs/topics/…` renders to `site/topics/…`. Unit reports unchanged — verified by rendering `KEN-monthly` to a scratch tree and diffing the permalinks. |
| 3 | 38 slugs, not 39 | **Fixed** (`9d687a3`). Both occurrences, and the render-set arithmetic now reads 165 → 241. |
| 4 | Section overrides make the key underivable | **Fixed** (`9d687a3`). Step 1 reads the section off the ledger row and says what to do when a place holds several blocks for one subject. |
| — | Wiki junction breaks index freshness | **Fixed** (`a977616`). `setup_workroot()` junctions every `INDEX_ROOTS` tree, generated from the constant rather than listed by hand, so the two can no longer drift apart. |
| — | OSINT's index was built from Corpus's workroot | **Routed to OSINT** (`6aa5e62`), note 8. Not Corpus's to repair. |
| — | "Corpus reads committed `HEAD`" | **Fixed** (`6aa5e62`, `91fd4fb`) in the standing constraint and in `migration-report-layer.md`; the requirement stands on its real reason. |
| — | Note 4 could go further | **Fixed** (`6aa5e62`), as a dated addendum rather than an edit to the note. |
| — | Tree rename | **Deferred by Bill.** It no longer blocks anything: `render.py` derives the tree from the path, so the topic stage can be written now and the rename made later without rework. |

Two smaller things fixed in passing, both in `c31e06d`: RENDER Step 2's abort message said "matched no pattern above" when a render *failure* leaves the count short by the same amount, so it named one of two causes and printed a list that could only show the other; and the drafted RENDER text carried the same defect. The runbook now names both.

**What is left, and it is the first thing tomorrow:** `python scripts/build-index.py` in an OSINT session. Until it runs, every Corpus render or check that resolves a citation exits with `ForeignIndex` — correctly, because the index on disk is missing 3,402 files and Corpus may not rebuild it. `BUILD.md`'s prerequisites now say so.

Not reviewed, and untouched: `STATUS-INIT.md`, at Bill's instruction.

## Afterword — the dependency was optional all along

Bill, reading the above: *"I don't like this OSINT dependency. CORPUS can read anything in OSINT. what is the need for index"*. He was right, and the finding above is only half the story.

An index is a **cache of a tree Corpus can already read in full** — 12,588 files of `raw/` and `wiki/`, walked in five seconds. Nothing about it needed to be OSINT's copy of the file. Sharing it bought Corpus one skipped rebuild per run and cost it a build that could be stopped dead by a maintenance step it is forbidden to perform, which is the worst trade in the repo: the coupling ran the wrong way down the dependency, from the derived view back into the store of record.

So `index/` is no longer junctioned. With no link, `INDEX_DIR` resolves to a real directory inside the gitignored workroot, Corpus builds and owns its index, `_assert_own_index()` is satisfied by construction, and `ensure_fresh()` may rebuild whenever `raw/` or `wiki/` moves — because now it is rebuilding Corpus's own file. `python scripts/report-render.py --unit KEN --check` passes G, I, J, L and M against it, and the catalogue it produces is the committed one to the record: 9,407 records, 9,404 with a URL.

That also **reverses the fix above it, which is the better outcome.** Junctioning all eight `INDEX_ROOTS` was the right answer to the question "how do we agree with OSINT's index"; the right answer to "why are we reading OSINT's index" makes the question disappear. `INDEX_ROOTS` in Corpus's `vault_lib` is now `("raw", "wiki")` — what Corpus actually reads — and the workroot junctions three directories instead of nine. Each junction is a directory of OSINT's exposed to a process that can write, so a shorter list is a smaller boundary surface, and `setup_workroot()` now withdraws any link it no longer names rather than leaving it in place.

**One of those six was already a live hazard.** `finance-compile-scope.py` writes its state to `ROOT/reviews/finance-compile-state.json`. Run from the workroot with `reviews/` junctioned — which it was, for four commits this evening — `--commit` would have written that file **into `C:\OSINT\reviews\`**. Nothing invokes the script and neither runbook names it, so nothing had; the file sitting in OSINT today is OSINT's own, from before the script was ported. It is the concrete case for keeping the junction list to what a stage reads: the boundary is not only what the code intends to write, it is what the paths make reachable.

The residue is a note for tomorrow rather than a change: `finance-compile-scope.py` is OSINT-shaped code sitting in Corpus's `scripts/` (its docstring cites OSINT's task 22, its state path assumes OSINT's tree), alongside `pull.py` and `test_pull.py`, which the 2026-08-14 BUILD review already flagged as retired-but-present. None is invoked by either runbook. They should be retired or repointed, and until they are, each is a script that behaves differently depending on which root it is run from.
